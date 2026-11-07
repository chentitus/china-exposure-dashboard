"""依賴指標：把金額轉成依賴。
來源（API，原始 JSON 快取於 data/raw/external/）：
 - World Bank WDI：GDP (current US$) NY.GDP.MKTP.CD；政府歲入(不含贈與) % GDP GC.REV.XGRT.GD.ZS
 - World Bank IDS (source 6)：PPG 外債存量 DT.DOD.DPPG.CD，債權人 China (730) 與 World (WLD)；IMF 信用使用額 DT.DOD.DIMF.CD（IMF 方案代理變數；MONA 網站拒絕自動下載）
 - OECD DAC2A：Gross ODA (240) 撥付額，current USD，捐助者 = DAC 國家 (DAC) 與所有官方捐助者含多邊 (ALLD)
輸出 data/clean/dependence_country_year.csv，並把 2020–2023 的依賴比率併入 summary_2020_2025.csv。"""
import json, time, requests, pandas as pd, numpy as np
from common import *
EXT = RAW/'external'; EXT.mkdir(exist_ok=True)
Y0, Y1 = 2018, 2024
def get(url, name, params=None, headers=None):
    f = EXT/f'{name}.json'
    if f.exists(): return json.loads(f.read_text())
    for i in range(3):
        r = requests.get(url, params=params, headers=headers, timeout=120)
        if r.ok: f.write_text(r.text); return r.json()
        time.sleep(3)
    raise RuntimeError(f'{url} -> {r.status_code}')

# --- WDI
def wdi(ind, name):
    rows = []
    for page in range(1, 20):
        d = get(f'https://api.worldbank.org/v2/country/all/indicator/{ind}', f'wdi_{name}_p{page}', {'date': f'{Y0}:{Y1}', 'format': 'json', 'per_page': 2000, 'page': page})
        rows += [(x['countryiso3code'], int(x['date']), x['value']) for x in d[1] if x['countryiso3code']]
        if page >= d[0]['pages']: break
    return pd.DataFrame(rows, columns=['country_iso3', 'year', name])
gdp = wdi('NY.GDP.MKTP.CD', 'gdp_usd'); rev = wdi('GC.REV.XGRT.GD.ZS', 'gov_revenue_pct_gdp')

# --- IDS
def ids(series, cp, name):
    yrs = ';'.join(f'YR{y}' for y in range(Y0, Y1+1))
    d = get(f'https://api.worldbank.org/v2/sources/6/country/all/series/{series}/counterpart-area/{cp}/time/{yrs}', f'ids_{name}', {'format': 'json', 'per_page': 5000})
    rows = [(x['variable'][0]['id'], int(x['variable'][1]['value']), x['value']) for x in d['source']['data']]
    return pd.DataFrame(rows, columns=['country_iso3', 'year', name])
china = ids('DT.DOD.DPPG.CD', '730', 'ppg_debt_china_usd'); world = ids('DT.DOD.DPPG.CD', 'WLD', 'ppg_debt_total_usd'); imf = ids('DT.DOD.DIMF.CD', 'WLD', 'imf_credit_usd')

# --- OECD DAC2A gross ODA disbursements, current USD
def oecd(donor, name):
    d = get(f'https://sdmx.oecd.org/public/rest/data/OECD.DCD.FSD,DSD_DAC2@DF_DAC2A,1.2/{donor}..240.USD.V', f'oecd_{name}', {'startPeriod': Y0, 'endPeriod': Y1, 'dimensionAtObservation': 'AllDimensions'}, {'Accept': 'application/vnd.sdmx.data+json'})
    st = d['data']['structures'][0]['dimensions']['observation']; dims = {x['id']: [v['id'] for v in x['values']] for x in st}; ri = [x['id'] for x in st].index('RECIPIENT'); ti = [x['id'] for x in st].index('TIME_PERIOD')
    rows = [(dims['RECIPIENT'][int(k.split(':')[ri])], int(dims['TIME_PERIOD'][int(k.split(':')[ti])]), v[0]) for k, v in d['data']['dataSets'][0]['observations'].items()]
    df = pd.DataFrame(rows, columns=['oecd_code', 'year', name])
    df = df[df.oecd_code.str.fullmatch(r'[A-Z]{3}')].rename(columns={'oecd_code': 'country_iso3'})   # 只留 ISO3 國家碼（去掉區域彙總）
    df[name] = df[name].astype(float)   # 百萬美元
    return df
oda_all = oecd('ALLD', 'oda_gross_all_official_usd_mn'); oda_dac = oecd('DAC', 'oda_gross_dac_countries_usd_mn')

# --- 合併成 country-year
dep = gdp.merge(rev, how='outer').merge(china, how='outer').merge(world, how='outer').merge(imf, how='outer').merge(oda_all, how='outer').merge(oda_dac, how='outer')
dep = dep[dep.country_iso3.isin(set(pd.read_csv(CLEAN/'panel_long.csv').country_iso3))].sort_values(['country_iso3', 'year'])
for c in ['ppg_debt_china_usd', 'ppg_debt_total_usd', 'imf_credit_usd']: dep[c.replace('_usd', '_usd_mn')] = dep[c]/1e6
dep['gdp_usd_mn'] = dep.gdp_usd/1e6
dep['ppg_debt_china_share_of_ppg'] = dep.ppg_debt_china_usd/dep.ppg_debt_total_usd
dep['ppg_debt_china_pct_gdp'] = dep.ppg_debt_china_usd/dep.gdp_usd*100
dep['imf_credit_pct_gdp'] = dep.imf_credit_usd/dep.gdp_usd*100
# 加上本專案的中國年度流量
cy = pd.read_csv(CLEAN/'panel_country_year.csv')
aid = cy[(cy.source=='AidData CLG-Global 1.0')&(cy.measure.str.startswith('ODA+OOF'))].groupby(['country_iso3','year']).amount_usd_mn.sum().rename('aiddata_odaoof_usd_mn')
codf = cy[cy.source=='BU CODF'].groupby(['country_iso3','year']).amount_usd_mn.sum().rename('codf_usd_mn')
dep = dep.merge(aid.reset_index(), how='left').merge(codf.reset_index(), how='left')
dep['aiddata_odaoof_pct_gdp'] = dep.aiddata_odaoof_usd_mn/dep.gdp_usd_mn*100
dep['aiddata_odaoof_pct_gov_revenue'] = dep.aiddata_odaoof_usd_mn/(dep.gdp_usd_mn*dep.gov_revenue_pct_gdp/100)*100
dep['china_vs_all_official_oda_ratio'] = dep.aiddata_odaoof_usd_mn/dep.oda_gross_all_official_usd_mn
cols = ['country_iso3','year','gdp_usd_mn','gov_revenue_pct_gdp','ppg_debt_china_usd_mn','ppg_debt_total_usd_mn','ppg_debt_china_share_of_ppg','ppg_debt_china_pct_gdp','imf_credit_usd_mn','imf_credit_pct_gdp','oda_gross_all_official_usd_mn','oda_gross_dac_countries_usd_mn','aiddata_odaoof_usd_mn','codf_usd_mn','aiddata_odaoof_pct_gdp','aiddata_odaoof_pct_gov_revenue','china_vs_all_official_oda_ratio']
dep = dep[cols]; dep.to_csv(CLEAN/'dependence_country_year.csv', index=False)

# --- summary 併入（2020–2023）
w = dep[dep.year.between(2020, 2023)].groupby('country_iso3')
S = pd.read_csv(CLEAN/'summary_2020_2025.csv')
S = S.drop(columns=[c for c in S.columns if c.startswith('dep_')])
add = pd.DataFrame({
    'dep_gdp_avg_2020_2023_usd_mn': w.gdp_usd_mn.mean(),
    'dep_aiddata_odaoof_pct_gdp_2020_2023': w.aiddata_odaoof_usd_mn.sum()/w.gdp_usd_mn.sum()*100,       # 四年合計 / 四年 GDP 合計
    'dep_aiddata_odaoof_pct_gov_revenue_2020_2023': w.aiddata_odaoof_usd_mn.sum()/(w.gdp_usd_mn.sum()*w.gov_revenue_pct_gdp.mean()/100)*100,
    'dep_ppg_debt_china_2023_usd_mn': dep[dep.year==2023].set_index('country_iso3').ppg_debt_china_usd_mn,
    'dep_ppg_debt_china_share_2023': dep[dep.year==2023].set_index('country_iso3').ppg_debt_china_share_of_ppg,
    'dep_ppg_debt_china_pct_gdp_2023': dep[dep.year==2023].set_index('country_iso3').ppg_debt_china_pct_gdp,
    'dep_imf_credit_pct_gdp_2023': dep[dep.year==2023].set_index('country_iso3').imf_credit_pct_gdp,
    'dep_oda_gross_all_official_2020_2023_usd_mn': w.oda_gross_all_official_usd_mn.sum(min_count=1),
    'dep_china_vs_all_official_oda_ratio_2020_2023': w.aiddata_odaoof_usd_mn.sum()/w.oda_gross_all_official_usd_mn.sum(min_count=1),
}).reset_index()
S = S.merge(add, how='left'); S.to_csv(CLEAN/'summary_2020_2025.csv', index=False)
print('dependence rows', dep.shape, '| coverage 2023: gdp', dep[dep.year==2023].gdp_usd_mn.notna().sum(), 'ids china', dep[dep.year==2023].ppg_debt_china_usd_mn.notna().sum(), 'oda', dep[dep.year==2023].oda_gross_all_official_usd_mn.notna().sum())
print(S.sort_values('dep_ppg_debt_china_share_2023', ascending=False).head(15)[['country_iso3','country_name_zh','dep_ppg_debt_china_2023_usd_mn','dep_ppg_debt_china_share_2023','dep_ppg_debt_china_pct_gdp_2023','dep_aiddata_odaoof_pct_gdp_2020_2023','dep_china_vs_all_official_oda_ratio_2020_2023','dep_imf_credit_pct_gdp_2023']].round(2).to_string(index=False))
