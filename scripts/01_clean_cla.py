"""清理 BU CLA（Chinese Loans to Africa）→ data/clean/clean_cla.csv（2020–2025）。"""
import pandas as pd
from common import *
x = pd.read_excel(RAW/'CLA-Database-Raw-Data-Public-2025-FIN.xlsx', header=1); x.columns = [str(c).strip() for c in x.columns]
x = x[x['BU ID'].notna()]
iso, failed = to_iso3(x['Country']); print('CLA ISO3 failures:', failed)
df = pd.DataFrame({
    'source': 'BU CLA', 'measure': 'Official & commercial loans to Africa (commitments)',
    'country_iso3': iso, 'country_raw': x['Country'], 'year': pd.to_numeric(x['Year'], errors='coerce').astype('Int64'),
    'amount_usd_mn': pd.to_numeric(x['Loan (USD M)'], errors='coerce'), 'amount_basis': 'nominal',
    'flow_type': 'Loan', 'flow_class': pd.NA, 'sector': x['Sector'], 'energy_source': x['Energy Source'],
    'funder_or_investor': x['Lender'], 'income_group': x['Income Level (WB)'], 'bri_flag': pd.NA, 'status': pd.NA,
    'record_id': 'CLA-' + x['BU ID'].astype(str), 'project_title': x['Project Name'],
})
df = add_names(df); df = df[df['year'].between(2020, 2025)]
df.to_csv(CLEAN/'clean_cla.csv', index=False); print('clean_cla', df.shape, 'sum', round(df.amount_usd_mn.sum(),1), 'years', df.year.value_counts().sort_index().to_dict())
