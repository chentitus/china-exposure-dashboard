"""核對：我算的 vs 官方公布，輸出 data/clean/validation_results.md（貼進 README「核對結果」段）。"""
import pandas as pd, numpy as np, random
from common import *
rows = []
def add(item, mine, official, note='', fmt='{:,.1f}'):
    diff = (mine-official)/official*100 if (official not in (None, 0) and mine is not None) else np.nan
    rows.append((item, fmt.format(mine) if mine is not None else '—', fmt.format(official) if official is not None else '—',
                 f'{diff:+.1f}%' if pd.notna(diff) else '—', note))

# 1. AidData
ad = pd.read_parquet(CLEAN/'aiddata_clg_global_1.0_records.parquet'); ad = ad[ad.AidData_Record_ID.notna()]
rfa = ad[ad.Recommended_for_Aggregates=='Yes']
add('AidData 筆數（全部紀錄）', len(ad), 33580, '官方：33,580 projects and activities', '{:,.0f}')
add('AidData 2000–2023 總額 RfA=Yes，Amount_Constant_USD_2023（十億美元）', rfa.Amount_Constant_USD_2023.sum()/1e9, 2200, '官方「nearly $2.2 trillion」（2000–2023）')
add('AidData 2000–2023 總額 RfA=Yes，Adjusted_Amount_Constant_USD_2023（十億美元）', rfa.Adjusted_Amount_Constant_USD_2023.sum()/1e9, 2200, '扣除非中國共同融資份額的口徑，供對照')
add('AidData 2000–2023 總額「全部紀錄」Amount_Constant（十億美元）', ad.Amount_Constant_USD_2023.sum()/1e9, 2200, '不過濾 RfA（含 umbrella 重複），供對照')
hic = rfa[rfa.Source_Dataset=='CLG-HIC 1.0']
add('AidData 高所得子集 2000–2023 總額（十億美元）', hic.Amount_Constant_USD_2023.sum()/1e9, 943.4, '官方 CLG-HIC 1.0：nearly $943.4 billion')
us = rfa[rfa.Country_of_Activity_ISO3=='USA']
add('AidData 美國 2000–2023 總額（十億美元）', us.Amount_Constant_USD_2023.sum()/1e9, 200, '官方：「more than $200 billion for nearly 2,500 projects」；以 200 為基準')
add('AidData 美國 2000–2023 筆數', len(us), 2500, '官方「nearly 2,500」', '{:,.0f}')
top_hic = hic.groupby('Country_of_Activity').Amount_Constant_USD_2023.sum().sort_values(ascending=False)
rows.append(('AidData 高所得國家前 3 名', ' / '.join(f'{c} {v/1e9:,.0f}' for c,v in top_hic.head(3).items()), 'United States 第一', '—', '官方：美國為高所得國家中最大受貸國'))
for c, off in [('United Kingdom',60),('France',21.3),('Italy',17.4),('Portugal',11.7),('Netherlands',11.6)]:
    add(f'AidData {c} 2000–2023（十億美元）', rfa[rfa.Country_of_Activity==c].Amount_Constant_USD_2023.sum()/1e9, off, '官方 blog 2025-11-18')

# 2. CODF
codf = pd.read_excel(RAW/'CODF-Database-Dataset-2025-EN.xlsx'); codf = codf[codf['BU ID'].notna()]
add('CODF 筆數 2008–2024', len(codf), 1304, '官方 1,304 loans', '{:,.0f}')
add('CODF 2008–2024 總額（十億美元）', codf['Loan Amount (USD M)'].sum()/1e3, 472, '官方 $472 billion')
c24 = codf[codf['Loan Sign Year']==2024]
add('CODF 2024 筆數', len(c24), 20, '官方 20 loans', '{:,.0f}')
add('CODF 2024 總額（十億美元）', c24['Loan Amount (USD M)'].sum()/1e3, 6.1, '官方 $6.1 billion')

# 3. CLA
cla = pd.read_excel(RAW/'CLA-Database-Raw-Data-Public-2025-FIN.xlsx', header=1); cla.columns=[str(c).strip() for c in cla.columns]; cla = cla[cla['BU ID'].notna()]
cla['Year'] = pd.to_numeric(cla['Year'], errors='coerce'); cla['amt'] = pd.to_numeric(cla['Loan (USD M)'], errors='coerce')
add('CLA 筆數 2000–2024', len(cla), 1319, '官方 1,319 loan commitments', '{:,.0f}')
add('CLA 2000–2024 總額（十億美元）', cla.amt.sum()/1e3, 180.87, '官方 $180.87 billion（Selective Engagement and Strategic Retooling, 2025-11-13）')
add('CLA 2024 總額（十億美元）', cla[cla.Year==2024].amt.sum()/1e3, 2.1, '官方「just under $2.1 billion」')
add('CLA 放款人數', cla['Lender'].nunique(), 42, '官方 42 lenders', '{:,.0f}')
rows.append(('CLA 最大年份', str(int(cla.Year.max())), '2024', '—', '檔案不含 2025 年紀錄'))

# 4. CGIT
cg = pd.concat([pd.read_csv(RAW/'cgit'/f, encoding='latin-1').assign(measure=m) for f,m in [('CGIT_investment_2005-2026H1.csv','Investment'),('CGIT_construction_2005-2026H1.csv','Construction')]])
cg['amt'] = pd.to_numeric(cg['Millions'].astype(str).str.replace(r'[\$,\s]','',regex=True), errors='coerce'); cg['Country']=cg['Country'].str.strip()
add('CGIT 2005–2026H1 投資+建設總額（十億美元）', cg.amt.sum()/1e3, 2700, 'AEI 頁面：「$2.7 trillion」；AEI 2026-07 報告同')
add('CGIT 2005–2025 投資+建設總額（十億美元）', cg[cg.Year<=2025].amt.sum()/1e3, 2500, 'AEI 2026-01 報告：「more than $2.5 trillion」（下限）')
add('CGIT 筆數 2005–2026H1', len(cg), 5000, 'AEI：「over 5000 large transactions」（下限）', '{:,.0f}')
bri = cg[(cg.Year>=2013)&(cg.BRI==1)]
add('CGIT BRI 國家建設 2013–2026H1（十億美元）', bri[bri.measure=='Construction'].amt.sum()/1e3, 720, 'AEI 2026-07：construction $720 billion in BRI countries since inception')
add('CGIT BRI 國家投資 2013–2026H1（十億美元）', bri[bri.measure=='Investment'].amt.sum()/1e3, 480, 'AEI 2026-07：investment $480 billion')
bri25 = bri[bri.Year<=2025]
add('CGIT BRI 國家建設 2013–2025（十億美元）', bri25[bri25.measure=='Construction'].amt.sum()/1e3, 687, 'AEI 2026-01：$687 billion')
add('CGIT BRI 國家投資 2013–2025（十億美元）', bri25[bri25.measure=='Investment'].amt.sum()/1e3, 468, 'AEI 2026-01：$468 billion')
usc = cg[(cg.Country=='USA')&(cg.measure=='Investment')]
add('CGIT 美國投資 2020–2025（十億美元）', usc[usc.Year.between(2020,2025)].amt.sum()/1e3, 16.6, 'AEI 2026-01：$16.6 billion')
add('CGIT 美國投資 2020–2026H1（十億美元）', usc[usc.Year>=2020].amt.sum()/1e3, 18, 'AEI 2026-07：「only $18 billion」')
yr = cg[cg.Year>=2020].groupby(['Year','measure']).amt.sum().unstack().fillna(0)/1e3
yearly_md = yr.round(1).to_markdown()

# 5. 隨機 10 國：panel_country_year == panel_long 加總
long = pd.read_csv(CLEAN/'panel_long.csv'); cy = pd.read_csv(CLEAN/'panel_country_year.csv')
random.seed(20261107); picks = random.sample(sorted(c for c in long.country_iso3.unique() if c!='REGIONAL'), 10)
chk = []
for c in picks:
    a = long[long.country_iso3==c].groupby(['year','source','measure']).amount_usd_mn.sum().round(3)
    b = cy[cy.country_iso3==c].set_index(['year','source','measure']).amount_usd_mn.round(3)
    ok = a.sort_index().equals(b.sort_index()); chk.append((c, round(a.sum(),1), round(b.sum(),1), 'OK' if ok else 'MISMATCH'))

md = ['| 項目 | 我算的 | 官方公布 | 差異 | 備註 |','|---|---|---|---|---|'] + [f'| {a} | {b} | {c} | {d} | {e} |' for a,b,c,d,e in rows]
md += ['', '**CGIT 2020 年以後各年總額（十億美元，nominal）**：AEI 未公布可機讀的年度彙總表（Excel 版的彙總工作表不在公開 CSV 中），以下為本專案由交易層級 CSV 加總的結果，供對照 AEI 各期報告敘述。', '', yearly_md, '',
       '**隨機 10 國一致性核對（panel_country_year vs panel_long 加總，所有 year×source×measure 格）**', '', '| ISO3 | long 加總 | country_year 加總 | 結果 |', '|---|---|---|---|'] + [f'| {a} | {b:,} | {c:,} | {d} |' for a,b,c,d in chk]
(CLEAN/'validation_results.md').write_text('\n'.join(md), encoding='utf-8'); print('\n'.join(md))
