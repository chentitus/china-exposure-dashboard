"""清理 AEI CGIT（投資 + 建設 CSV）→ data/clean/clean_cgit.csv（2020–2026H1）。金額 nominal 百萬美元；僅含 ≥1 億美元交易。"""
import pandas as pd
from common import *
MON = {m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
parts = []
for f, meas in [('CGIT_investment_2005-2026H1.csv','Investment'), ('CGIT_construction_2005-2026H1.csv','Construction')]:
    x = pd.read_csv(RAW/'cgit'/f, encoding='latin-1'); x['measure'] = meas
    x['row'] = range(1, len(x)+1); x['src_file'] = f; parts.append(x)
x = pd.concat(parts, ignore_index=True)
for c in ['Country','Investor','Sector','Subsector','Region','Partner/Target']: x[c] = x[c].astype('string').str.strip()
iso, failed = to_iso3(x['Country']); print('CGIT ISO3 failures:', failed)
amt = pd.to_numeric(x['Millions'].astype(str).str.replace(r'[\$,\s]', '', regex=True), errors='coerce')
df = pd.DataFrame({
    'source': 'AEI CGIT', 'measure': x['measure'], 'country_iso3': iso, 'country_raw': x['Country'],
    'year': x['Year'].astype('Int64'), 'month': x['Month'].map(MON).astype('Int64'),
    'amount_usd_mn': amt, 'amount_basis': 'nominal', 'flow_type': x['measure'], 'flow_class': pd.NA,
    'sector': x['Sector'], 'subsector': x['Subsector'], 'funder_or_investor': x['Investor'],
    'share_size': x['Share Size'], 'cgit_region': x['Region'],
    'bri_flag': pd.to_numeric(x['BRI'], errors='coerce').astype('Int64'), 'status': pd.NA,
    'record_id': 'CGIT-' + x['measure'].str[:3].str.upper() + '-' + x['row'].astype(str), 'project_title': x['Partner/Target'],
})
df = add_names(df); df = df[df['year'] >= 2020]
df.to_csv(CLEAN/'clean_cgit.csv', index=False)
print('clean_cgit', df.shape, df.groupby('measure').amount_usd_mn.sum().round(0).to_dict(), 'latest', df[['year','month']].max().tolist())
