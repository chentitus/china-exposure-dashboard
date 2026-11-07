"""收集四個來源的所有國名，跑 ISO3 轉換，列出失敗清單（需人工確認）。"""
import pandas as pd
from common import *
names = {}
ad = pd.read_parquet(CLEAN/'aiddata_clg_global_1.0_records.parquet')
names['AidData'] = ad['Country_of_Activity'].dropna().unique()
names['CODF'] = pd.read_excel(RAW/'CODF-Database-Dataset-2025-EN.xlsx')['Country'].dropna().unique()
cla = pd.read_excel(RAW/'CLA-Database-Raw-Data-Public-2025-FIN.xlsx', header=1)
cla.columns = [str(c).strip() for c in cla.columns]
names['CLA'] = cla['Country'].dropna().unique()
cg = pd.concat([pd.read_csv(RAW/'cgit'/f, encoding='latin-1') for f in ['CGIT_investment_2005-2026H1.csv','CGIT_construction_2005-2026H1.csv']])
names['CGIT'] = cg['Country'].dropna().unique()
rows = []
for src, arr in names.items():
    s = pd.Series(arr); iso, failed = to_iso3(s)
    for n, i in zip(s, iso): rows.append((src, n, i))
    print(f'{src}: {len(s)} names, {len(failed)} failed -> {failed}')
m = pd.DataFrame(rows, columns=['source','country_raw','country_iso3'])
m.to_csv(CLEAN/'_country_mapping_all_sources.csv', index=False)
print('\nREGIONAL:', m[m.country_iso3=='REGIONAL'].country_raw.unique().tolist())
print('\nAidData ISO3 agreement with file:', end=' ')
chk = ad[['Country_of_Activity','Country_of_Activity_ISO3']].drop_duplicates().dropna()
mm = chk.merge(m[m.source=='AidData'], left_on='Country_of_Activity', right_on='country_raw')
print((mm.Country_of_Activity_ISO3 != mm.country_iso3).sum(), 'mismatches', mm[mm.Country_of_Activity_ISO3 != mm.country_iso3][['Country_of_Activity','Country_of_Activity_ISO3','country_iso3']].to_dict('records'))
