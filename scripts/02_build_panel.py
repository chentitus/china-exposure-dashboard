"""合併四個來源 → panel_long.csv、panel_country_year.csv、summary_2020_2025.csv。各來源分層，不相加。"""
import pandas as pd, json
from common import *
frames = [pd.read_csv(CLEAN/f'clean_{s}.csv', dtype={'record_id': str}) for s in ['aiddata','aiddata_ofic','codf','cla','cgit']]
aid_full = pd.read_csv(CLEAN/'clean_aiddata.csv', dtype={'record_id': str})   # 主口徑（含 rescue 等欄）
long = pd.concat(frames, ignore_index=True)
long['bri_flag'] = long['bri_flag'].astype('Int64'); long['year'] = long['year'].astype('Int64')
long = finalize(long)
assert long['country_iso3'].notna().all(), long[long.country_iso3.isna()].country_raw.unique()
long.to_csv(CLEAN/'panel_long.csv', index=False)

cy = (long.groupby(['country_iso3','country_name_en','country_name_zh','region_code','region_zh','year','source','measure'], dropna=False)
          .agg(amount_usd_mn=('amount_usd_mn','sum'), n_records=('record_id','count')).reset_index())
cy.to_csv(CLEAN/'panel_country_year.csv', index=False)

def tot(src, meas=None, y0=2020, y1=2099, extra=None):
    d = long[(long.source==src) & long.year.between(y0,y1)]
    if meas: d = d[d.measure==meas]
    if extra is not None: d = d[extra(d)]
    return d.groupby('country_iso3').amount_usd_mn.sum()
countries = long[['country_iso3','country_name_en','country_name_zh','region_code','region_zh']].drop_duplicates('country_iso3').set_index('country_iso3')
S = pd.DataFrame(index=countries.index)
AIDM = 'ODA+OOF (official development/aid finance)'
S['aiddata_total_2020_2023']  = tot('AidData CLG-Global 1.0', AIDM, y1=2023)                       # 主口徑：ODA+OOF+Vague
S['aiddata_oda_2020_2023']    = tot('AidData CLG-Global 1.0', AIDM, y1=2023, extra=lambda d: d.flow_class=='ODA')
S['aiddata_oof_2020_2023']    = tot('AidData CLG-Global 1.0', AIDM, y1=2023, extra=lambda d: d.flow_class=='OOF')
S['aiddata_vague_2020_2023']  = tot('AidData CLG-Global 1.0', AIDM, y1=2023, extra=lambda d: d.flow_class=='Vague (ODA or OOF)')
S['aiddata_loans_2020_2023']  = tot('AidData CLG-Global 1.0', AIDM, y1=2023, extra=lambda d: d.flow_type=='Loan')
S['aiddata_grants_2020_2023'] = tot('AidData CLG-Global 1.0', AIDM, y1=2023, extra=lambda d: d.flow_type!='Loan')  # 贈與、技術協助、獎學金、債務重整/免除、vague
S['aiddata_grants_strict_2020_2023'] = tot('AidData CLG-Global 1.0', AIDM, y1=2023, extra=lambda d: d.flow_type=='Grant')
_r = aid_full[aid_full.year.between(2020,2023)]
S['aiddata_rescue_2020_2023'] = _r[_r.rescue=='Yes'].groupby('country_iso3').amount_usd_mn.sum()    # 紓困貸款（FXSL/BoP/一般預算支持）
S['aiddata_total_excl_rescue_2020_2023'] = S['aiddata_total_2020_2023'].fillna(0) - S['aiddata_rescue_2020_2023'].fillna(0)
S.loc[S['aiddata_total_2020_2023'].isna(), 'aiddata_total_excl_rescue_2020_2023'] = pd.NA
S['aiddata_public_liability_2020_2023'] = _r[_r.public_liability!='Private debt'].groupby('country_iso3').amount_usd_mn.sum()   # 主口徑扣除私人債務（中央政府/擔保/其他公部門/潛在公部門/無法歸類）
S['aiddata_private_debt_2020_2023']    = _r[_r.public_liability=='Private debt'].groupby('country_iso3').amount_usd_mn.sum()   # 主口徑內借款人為私企/SPV 的私人債務
S['aiddata_ofic_2020_2023']   = tot('AidData CLG-Global 1.0', 'OFIC (commercial official finance)', y1=2023)   # 對照：商業性官方融資（不在主口徑）
S['codf_total_2020_2024'] = tot('BU CODF', y1=2024)
S['cla_total_2020_2025']  = tot('BU CLA', y1=2025)
S['cgit_investment_2020_latest']   = tot('AEI CGIT', 'Investment')
S['cgit_construction_2020_latest'] = tot('AEI CGIT', 'Construction')
cg = long[long.source=='AEI CGIT']
cgt = cg.groupby('country_iso3').amount_usd_mn.sum(); S['cgit_bri_share'] = (cg[cg.bri_flag==1].groupby('country_iso3').amount_usd_mn.sum().reindex(cgt.index).fillna(0) / cgt).where(cgt>0)
S['lowy_china_disbursement_2020_2023'] = pd.NA   # Lowy 未取得（無全量下載）
S = countries.join(S).reset_index()
S.to_csv(CLEAN/'summary_2020_2025.csv', index=False)
print('panel_long', long.shape, '| country_year', cy.shape, '| summary', S.shape)
print(long.groupby(['source','measure']).agg(n=('record_id','count'), amt=('amount_usd_mn','sum'), y0=('year','min'), y1=('year','max')).round(0))
