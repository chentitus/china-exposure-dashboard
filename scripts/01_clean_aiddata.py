"""清理 AidData CLG-Global 1.0。
主口徑 clean_aiddata.csv：RfA=Yes、2020–2023、Flow_Class ∈ {ODA, OOF, Vague (ODA or OOF)}（官方發展／援助性融資；排除 OFIC 商業性官方融資）。
clean_aiddata_ofic.csv：同條件但 Flow_Class = OFIC（對照層）。clean_aiddata_all.csv：2020–2023 全部紀錄，不過濾 RfA 與 Flow_Class。"""
import pandas as pd
from common import *
ad = pd.read_parquet(CLEAN/'aiddata_clg_global_1.0_records.parquet')
ad = ad[ad['AidData_Record_ID'].notna()].copy()           # 去掉表尾空列/註記列
ad['AidData_Record_ID'] = ad['AidData_Record_ID'].astype(int)
iso, failed = to_iso3(ad['Country_of_Activity'])
print('AidData ISO3 failures:', failed)
df = pd.DataFrame({
    'source': 'AidData CLG-Global 1.0',
    'measure': ad['Flow_Class'].map(lambda c: 'OFIC (commercial official finance)' if c=='OFIC' else 'ODA+OOF (official development/aid finance)'),
    'country_iso3': iso, 'country_raw': ad['Country_of_Activity'],
    'year': ad['Commitment_Year'].astype('Int64'),
    'amount_usd_mn': ad['Amount_Constant_USD_2023'] / 1e6,
    'amount_basis': 'constant_2023',
    'amount_nominal_usd_mn': ad['Amount_Nominal_USD'] / 1e6,
    'amount_adjusted_constant_usd_mn': ad['Adjusted_Amount_Constant_USD_2023'] / 1e6,   # 扣除非中國共同融資份額後的金額（AidData 另一口徑）
    'flow_type': ad['Flow_Type'], 'flow_type_simplified': ad['Flow_Type_Simplified'],
    'flow_class': ad['Flow_Class'], 'sector': ad['Sector_Name'],
    'funder_or_investor': ad['Funding_Agencies'], 'funder_type': ad['Funding_Agencies_Type'],
    'intent': ad['Intent'], 'income_group': ad['WB_Income_Group_Host_Country'],
    'rescue': ad['Rescue'], 'fxsl': ad['FXSL'], 'bop': ad['BOP'], 'public_liability': ad['Level_of_Public_Liability'],
    'bri_flag': pd.NA, 'status': ad['Status'], 'umbrella': ad['Umbrella'],
    'recommended_for_aggregates': ad['Recommended_for_Aggregates'],
    'record_id': 'AIDDATA-' + ad['AidData_Record_ID'].astype(str), 'project_title': ad['Title'],
})
df = add_names(df)
df = df[df['year'].between(2020, 2023)]
all_ = df.copy()
df = df[df['recommended_for_aggregates'] == 'Yes']
ofic = df[df['flow_class'] == 'OFIC']; df = df[df['flow_class'].isin(['ODA', 'OOF', 'Vague (ODA or OOF)'])]
df.to_csv(CLEAN/'clean_aiddata.csv', index=False); ofic.to_csv(CLEAN/'clean_aiddata_ofic.csv', index=False); all_.to_csv(CLEAN/'clean_aiddata_all.csv', index=False)
print('clean_aiddata (ODA+OOF+Vague)', df.shape, 'sum', round(df.amount_usd_mn.sum()), '| ofic', ofic.shape, round(ofic.amount_usd_mn.sum()), '| _all', all_.shape)
print('  rescue==Yes:', round(df[df.rescue=='Yes'].amount_usd_mn.sum()), 'mn; by class', df.groupby('flow_class').amount_usd_mn.sum().round(0).to_dict())
