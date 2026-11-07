"""列出各原始檔的工作表、欄位，印前 5 列；並把 AidData 主表轉成 parquet 快取。"""
import sys, pandas as pd, openpyxl
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; RAW = ROOT/'data/raw'; CLEAN = ROOT/'data/clean'
pd.set_option('display.width', 250, 'display.max_columns', 60, 'display.max_colwidth', 40)

# AidData → parquet (read once)
pq = CLEAN/'aiddata_clg_global_1.0_records.parquet'
if not pq.exists():
    wb = openpyxl.load_workbook(RAW/'aiddata_unzipped/AidDatas_CLG_Global_Dataset_v1.0.xlsx', read_only=True)
    ws = wb['CLG-Global 1.0_Records']
    rows = ws.iter_rows(values_only=True); header = next(rows)
    df = pd.DataFrame(list(rows), columns=header)
    for c in df.columns:
        if df[c].dtype == object: df[c] = df[c].astype("string")
    df.to_parquet(pq, index=False); print('AidData parquet written', df.shape)
ad = pd.read_parquet(pq)
print('=== AidData', ad.shape); print(list(ad.columns)); print(ad.head(5).T.to_string()[:6000])

for f, kw in [('CODF-Database-Dataset-2025-EN.xlsx', {}), ('CLA-Database-Raw-Data-Public-2025-FIN.xlsx', {})]:
    x = pd.read_excel(RAW/f, sheet_name=None, **kw)
    for s, d in x.items():
        print(f'=== {f} / sheet {s}', d.shape); print(list(d.columns)); print(d.head(5).to_string())

for f in ['CGIT_investment_2005-2026H1.csv', 'CGIT_construction_2005-2026H1.csv']:
    d = pd.read_csv(RAW/'cgit'/f, encoding='latin-1')
    print(f'=== {f}', d.shape); print(list(d.columns)); print(d.head(5).to_string())
