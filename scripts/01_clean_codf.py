"""清理 BU CODF（CDB/CHEXIM 主權貸款）→ data/clean/clean_codf.csv（2020–2024）。"""
import pandas as pd
from common import *
x = pd.read_excel(RAW/'CODF-Database-Dataset-2025-EN.xlsx'); x.columns = [c.strip() for c in x.columns]
x = x[x['BU ID'].notna()]
iso, failed = to_iso3(x['Country']); print('CODF ISO3 failures:', failed)
df = pd.DataFrame({
    'source': 'BU CODF', 'measure': 'Official finance (commitments)',
    'country_iso3': iso, 'country_raw': x['Country'], 'year': x['Loan Sign Year'].astype('Int64'),
    'amount_usd_mn': pd.to_numeric(x['Loan Amount (USD M)'], errors='coerce'), 'amount_basis': 'nominal',
    'flow_type': 'Loan', 'flow_class': pd.NA, 'sector': x['Sector'], 'energy_source': x['Energy Source'],
    'funder_or_investor': x['Lender'], 'borrower': x['Borrower'], 'bri_flag': pd.NA, 'status': pd.NA,
    'record_id': 'CODF-' + x['BU ID'].astype(str), 'project_title': x['Project name'],
})
df = add_names(df); df = df[df['year'].between(2020, 2024)]
df.to_csv(CLEAN/'clean_codf.csv', index=False); print('clean_codf', df.shape, 'sum', round(df.amount_usd_mn.sum(),1))
