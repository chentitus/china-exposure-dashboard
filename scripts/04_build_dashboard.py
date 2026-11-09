"""把 panel_long.csv 以 JSON 嵌入 dashboard_template.html → dashboard/index.html（單一自包含檔）。"""
import pandas as pd, json
from common import *
long = pd.read_csv(CLEAN/'panel_long.csv', dtype={'record_id':str})
aid = pd.read_csv(CLEAN/'clean_aiddata.csv', dtype={'record_id':str})[['record_id','rescue','public_liability']]
long = long.merge(aid, on='record_id', how='left')
cols = ['source','measure','country_iso3','country_raw','year','amount_usd_mn','amount_basis','flow_type','flow_class','sector','funder_or_investor','bri_flag','status','record_id','project_title','rescue','public_liability']
d = long[cols].copy()
d['project_title'] = d['project_title'].astype('string').str.slice(0, 160)
d['amount_usd_mn'] = d['amount_usd_mn'].round(3)
d = d.astype(object).where(d.notna(), None)
rows = d.values.tolist()
for r in rows:
    r[4] = int(r[4]); r[11] = int(r[11]) if r[11] is not None else None
names = pd.read_csv(SCRIPTS/'country_names_zh.csv', dtype=str)
en_short = long[['country_iso3','country_name_en']].drop_duplicates('country_iso3').set_index('country_iso3')['country_name_en'].to_dict()
regions = pd.read_csv(SCRIPTS/'country_regions.csv', dtype=str).set_index('country_iso3')
countries = {r.country_iso3: [en_short.get(r.country_iso3, r.country_name_en), r.country_name_zh, regions.loc[r.country_iso3,'region_code']] for r in names.itertuples() if r.country_iso3 in set(long.country_iso3)}
REG_ORDER = ['EAST_ASIA','SOUTH_ASIA','MIDEAST_CASIA','OCEANIA','EUROPE','AFRICA','LATAM_CARIB','NORTH_AMERICA','REGIONAL']
region_names = {c: regions[regions.region_code==c].region_zh.iloc[0] for c in REG_ORDER}
about = (SCRIPTS/'dashboard_about.html').read_text(encoding='utf-8')
dep = pd.read_csv(CLEAN/'dependence_country_year.csv'); dep = dep[dep.year.between(2020,2024)].round(3).astype(object).where(dep.notna(), None)
depcols = ['year','gdp_usd_mn','ppg_debt_china_usd_mn','ppg_debt_china_share_of_ppg','ppg_debt_china_pct_gdp','imf_credit_pct_gdp','oda_gross_all_official_usd_mn','aiddata_odaoof_usd_mn','aiddata_odaoof_pct_gdp','china_vs_all_official_oda_ratio']
dep_by = {k: g[depcols].values.tolist() for k, g in dep.groupby('country_iso3')}
DATA = {'cols': cols, 'rows': rows, 'countries': countries, 'regions': region_names, 'about': about, 'dep': dep_by}
js = 'const DATA = ' + json.dumps(DATA, ensure_ascii=False, separators=(',',':')) + ';'
html = (SCRIPTS/'dashboard_template.html').read_text(encoding='utf-8').replace('/*__DATA__*/', js)
(ROOT/'dashboard/index.html').write_text(html, encoding='utf-8')
html2 = (SCRIPTS/'dashboard_regions_template.html').read_text(encoding='utf-8').replace('/*__DATA__*/', js)
(ROOT/'dashboard/regions.html').write_text(html2, encoding='utf-8')
print('dashboard/index.html', round((ROOT/'dashboard/index.html').stat().st_size/1e6, 2), 'MB; rows', len(rows), 'countries', len(countries))

# ---- 曝險儀表板 exposure.html
S = pd.read_csv(CLEAN/'summary_2020_2025.csv'); S = S[S.country_iso3!='REGIONAL'].copy()
g = S['dep_gdp_avg_2020_2023_usd_mn']
ex = pd.DataFrame({'iso3': S.country_iso3, 'name_en': S.country_name_en, 'name_zh': S.country_name_zh, 'region_code': S.region_code, 'region_zh': S.region_zh, 'gdp_usd_mn': g,
    'pub_pct_gdp': S.aiddata_public_liability_2020_2023/g*100, 'private_pct_gdp': S.aiddata_private_debt_2020_2023/g*100,
    'debt_pct_gdp': S.dep_ppg_debt_china_pct_gdp_2023, 'debt_share': S.dep_ppg_debt_china_share_2023, 'china_oda_ratio': S.dep_china_vs_all_official_oda_ratio_2020_2023,
    'rescue_pct_gdp': S.aiddata_rescue_2020_2023/g*100, 'imf_pct_gdp': S.dep_imf_credit_pct_gdp_2023,
    'cgit_pct_gdp': (S.cgit_investment_2020_latest.fillna(0)+S.cgit_construction_2020_latest.fillna(0))/g*100, 'codf_pct_gdp': S.codf_total_2020_2024/g*100})
ex = ex.round(4).astype(object).where(ex.notna(), None)
depf = pd.read_csv(CLEAN/'dependence_country_year.csv').round(4); depf = depf.astype(object).where(depf.notna(), None)
dep_full = {k: g_.drop(columns='country_iso3').to_dict('records') for k, g_ in depf.groupby('country_iso3')}
EXD = {'summary': ex.to_dict('records'), 'dep': dep_full, 'regions': region_names, 'about': (SCRIPTS/'dashboard_exposure_about.html').read_text(encoding='utf-8')}
html3 = (SCRIPTS/'dashboard_exposure_template.html').read_text(encoding='utf-8').replace('/*__DATA__*/', 'const DATA = ' + json.dumps(EXD, ensure_ascii=False, separators=(',',':')) + ';')
(ROOT/'dashboard/exposure.html').write_text(html3, encoding='utf-8'); print('dashboard/exposure.html', round((ROOT/'dashboard/exposure.html').stat().st_size/1e6, 2), 'MB')

# ---- 媒體層 media.html
wk = pd.read_csv(CLEAN/'media_weekly.csv'); sm = pd.read_csv(CLEAN/'media_summary.csv'); art = pd.read_csv(CLEAN/'media_articles_taiwan.csv'); tg = pd.read_csv(SCRIPTS/'media_targets.csv')
TARGETS = [{'iso3':r.country_iso3,'name_en':r.country_name_en,'name_zh':r.country_name_zh,'region_zh':r.region_zh,'score':float(r.score)} for r in tg.itertuples()]
WK = [{'iso3':r.country_iso3,'side':r.side,'source_group':r.source_group,'week':str(r.week)[:10],'n':int(r.n),'n_taiwan':int(r.n_taiwan)} for r in wk.itertuples()]
SUMR = [{'iso3':r.country_iso3,'side':r.side,'source_group':r.source_group,'n':int(r.n),'n_taiwan':int(r.n_taiwan),'n_china':int(r.n_china),'n_one_china':int(r.n_one_china)} for r in sm.itertuples()]
ART = [{'iso3':r.country_iso3,'side':r.side,'source_group':r.source_group,'date':str(r.date)[:10],'title':(r.title if isinstance(r.title,str) else '')[:160],'url':r.url,'taiwan':bool(r.taiwan_flag),'one_china':bool(r.one_china),'china':bool(r.china_flag)} for r in art.itertuples()]
SIDEOF = sm.drop_duplicates('source_group').set_index('source_group').side.to_dict()
jsm = 'const TARGETS='+json.dumps(TARGETS,ensure_ascii=False,separators=(',',':'))+';\nconst WK='+json.dumps(WK,ensure_ascii=False,separators=(',',':'))+';\nconst SUM='+json.dumps(SUMR,ensure_ascii=False,separators=(',',':'))+';\nconst ART='+json.dumps(ART,ensure_ascii=False,separators=(',',':'))+';\nconst SIDEOF='+json.dumps(SIDEOF,ensure_ascii=False)+';\nconst ABOUT='+json.dumps((SCRIPTS/'dashboard_media_about.html').read_text(encoding='utf-8'),ensure_ascii=False)+';'
html4 = (SCRIPTS/'dashboard_media_template.html').read_text(encoding='utf-8').replace('/*__DATA__*/', jsm)
(ROOT/'dashboard/media.html').write_text(html4, encoding='utf-8'); print('dashboard/media.html', round((ROOT/'dashboard/media.html').stat().st_size/1e6,2),'MB; articles', len(ART))
