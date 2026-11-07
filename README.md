# 中國對外開發金融與投資國別儀表板（2020–2025）

線上版本（GitHub Pages）：https://chentitus.github.io/china-exposure-dashboard/ — 主儀表板 `dashboard/index.html`、區域排名 `dashboard/regions.html`、對中依賴與曝險 `dashboard/exposure.html`。原始碼：https://github.com/chentitus/china-exposure-dashboard

國家—年面板資料集 + 單檔互動儀表板（`dashboard/index.html`，雙擊開啟，Plotly.js 由 CDN 載入）。
四個公開資料庫**分層呈現、不相加**。所有金額單位為百萬美元。建置日期：2026-11-07。

```
china-finance-dashboard/
  data/raw/          原始下載檔（不修改）+ MANIFEST.md（URL、日期、大小、SHA256）
  data/clean/        清理後 CSV：clean_<source>.csv、panel_long.csv、panel_country_year.csv、summary_2020_2025.csv
  scripts/           00_inspect.py → 01_clean_*.py → 01a_country_check.py → 02_build_panel.py → 03_validate.py → 05_dependence.py → 04_build_dashboard.py
  data/raw/external/ WDI／IDS／OECD API 回應快取（JSON）
  dashboard/         index.html（主儀表板）、regions.html（區域排名）、exposure.html（對中依賴與曝險：指標分債務／依賴兩個概念（企業組可選），各算百分位平均子分數，總分 = 子分數平均；地圖、散點圖（X/Y/顏色各一子分數、形狀＝區域）、雷達圖國家比較（最多 6 國＋中位數基準）、各區域前 N、國家走勢）；皆為單一自包含檔，資料以 JSON 內嵌
```
重跑：`cd scripts && for s in aiddata codf cla cgit; do python3.12 01_clean_$s.py; done && python3.12 02_build_panel.py && python3.12 03_validate.py && python3.12 04_build_dashboard.py`
（`00_inspect.py` 第一次執行時把 AidData 主表轉成 `data/clean/aiddata_clg_global_1.0_records.parquet` 快取。）

## 1. 資料來源與版本

| 來源 | 版本 | 涵蓋期間 | 金額基準 | 本專案使用 |
|---|---|---|---|---|
| AidData — China's Global Loans and Grants Dataset 1.0（CLG-Global 1.0） | 2025-11-18 發布（合併版；含 CLG-HIC 1.0 與 CLG-LMIC 1.0）；附 Field Definitions codebook 與 TUFF 4.0 方法 PDF | 承諾年 2000–2023 | 2023 年不變價美元 | 2020–2023；`Recommended_for_Aggregates == Yes`；**主口徑 `Flow_Class ∈ {ODA, OOF, Vague}`**，OFIC 另存 `clean_aiddata_ofic.csv` 作對照 |
| BU GDP Center — CODF | 2025 年 6 月版（`CODF-Database-Dataset-2025-EN.xlsx`） | 2008–2024 | 名目美元 | 2020–2024 |
| BU GDP Center — CLA | 2025 年 11 月更新（檔案 `CLA-Database-Raw-Data-Public-2025-FIN.xlsx`，2026-02 上線） | 2000–2024 | 名目美元 | 2020–2024（**檔案無 2025 年紀錄**） |
| AEI/Heritage — CGIT | 2026 年 7 月更新，資料截止 **2026 年 6 月** | 2005–2026H1 | 名目美元 | 2020–2026H1 |
| Lowy — Southeast Asia Aid Map | — | — | — | **未取得**（見 §6） |

CGIT 取得方式：AEI 頁面（2026-11-07）已不提供 Excel 下載，改為「contact Derek Scissors」；本專案改抓頁面內嵌互動地圖實際載入的兩個交易層級 CSV（投資、建設），合計 5,050 筆、2.70 兆美元，與 AEI 自述一致（核對見 §5）。缺 Excel 版的 troubled transactions 與彙總工作表。詳見 `data/raw/MANIFEST.md`。

## 2. 欄位定義

### panel_long.csv（一列一筆交易／計畫，10,895 列）
| 欄位 | 定義 |
|---|---|
| `source` | `AidData CLG-Global 1.0` / `BU CODF` / `BU CLA` / `AEI CGIT` |
| `measure` | AidData：`ODA+OOF (official development/aid finance)`（主口徑）或 `OFIC (commercial official finance)`（對照）；CODF：`Official finance (commitments)`；CLA：`Official & commercial loans to Africa (commitments)`；CGIT：`Investment` 或 `Construction` |
| `country_iso3` | ISO3；區域性／多國紀錄為 `REGIONAL` |
| `country_name_en` / `country_name_zh` | ISO 短名（country_converter）／台灣慣用繁體中文國名（`scripts/country_names_zh.csv`，手建） |
| `country_raw` | 原檔國名 |
| `year` | AidData：Commitment_Year；CODF：Loan Sign Year；CLA：Year；CGIT：Year |
| `amount_usd_mn` | 百萬美元。AidData = `Amount_Constant_USD_2023`/1e6；其餘為原檔名目值 |
| `amount_basis` | `constant_2023` 或 `nominal` |
| `flow_type` | AidData：Flow_Type（Loan / Grant / Free-standing technical assistance / Scholarships… / Debt rescheduling / Debt forgiveness / Vague TBD）；CODF、CLA：`Loan`；CGIT：`Investment`/`Construction` |
| `flow_class` | 僅 AidData：ODA / OOF / OFIC / Vague (ODA or OOF) |
| `sector` | 各來源原始部門欄位 |
| `funder_or_investor` | AidData：Funding_Agencies；CODF／CLA：Lender；CGIT：Investor |
| `bri_flag` | 僅 CGIT：1/0 |
| `status` | 僅 AidData：Completion / Implementation / Pipeline: Commitment / Pipeline: Pledge / Cancelled / Suspended |
| `record_id` | `AIDDATA-<AidData_Record_ID>`、`CODF-<BU ID>`、`CLA-<BU ID>`、`CGIT-INV-<列號>` / `CGIT-CON-<列號>`（CGIT CSV 無 ID，列號為原 CSV 的 1-based 列序） |
| `project_title` | AidData：Title；CODF／CLA：Project name；CGIT：Partner/Target（交易對象） |
| `region_code` / `region_zh` | 自訂分區（`scripts/country_regions.csv`）：EAST_ASIA 東亞（東北亞＋東南亞）、SOUTH_ASIA 南亞、MIDEAST_CASIA 中東＋中亞（含高加索、土耳其）、OCEANIA 大洋洲、EUROPE 歐洲（含俄羅斯）、AFRICA 非洲（含北非）、LATAM_CARIB 拉丁美洲與加勒比海、NORTH_AMERICA 北美、REGIONAL |

`clean_aiddata.csv`（5,928 列）另保留 `amount_nominal_usd_mn`、`amount_adjusted_constant_usd_mn`（AidData 扣除非中國共同融資份額的 Adjusted 口徑）、`flow_type_simplified`、`intent`、`income_group`、`rescue`／`fxsl`／`bop`、`public_liability`、`umbrella`、`recommended_for_aggregates`。`clean_aiddata_ofic.csv`（3,162 列）為 OFIC 對照層；`clean_aiddata_all.csv` 為 2020–2023 全部紀錄、不過濾 RfA 與 Flow_Class（9,408 列），僅供核對。

### panel_country_year.csv（1,481 列）
`country_iso3, country_name_en, country_name_zh, region_code, region_zh, year, source, measure, amount_usd_mn, n_records`

### summary_2020_2025.csv（每國一列，189 列）
AidData 欄位皆為 2020–2023、constant 2023、RfA = Yes：
- `aiddata_total_2020_2023`：**主口徑** Flow_Class ∈ {ODA, OOF, Vague}；`aiddata_oda_…`、`aiddata_oof_…`、`aiddata_vague_…` 為其分項
- `aiddata_loans_…`（Flow_Type = Loan）、`aiddata_grants_…`（Flow_Type ≠ Loan：贈與、技術協助、獎學金、債務重整／免除、vague）、`aiddata_grants_strict_…`（Flow_Type = Grant）
- `aiddata_rescue_2020_2023`：主口徑內 `Rescue = Yes` 的紓困貸款（FXSL 貨幣互換動撥、BoP 貸款、一般預算支持）；`aiddata_total_excl_rescue_2020_2023` = 主口徑 − 紓困
- `aiddata_public_liability_2020_2023`：主口徑扣除 `Level_of_Public_Liability = Private debt`（保留中央政府、政府擔保、其他公部門、潛在公部門、無法歸類）；`aiddata_private_debt_2020_2023`：主口徑內的私人債務（借款人為私企／合資／SPV，如掛馬紹爾旗船公司的船舶租賃；2020–23 共 430 億，土耳其、印尼、菲律賓、秘魯、巴西居前）。兩種算法皆保留：公部門債務測政府直接被套住，私人債務測中資企業在地利益的影響管道。
- `aiddata_ofic_2020_2023`：對照，OFIC 商業性官方融資（不在主口徑）
依賴指標 `dep_*`（由 `05_dependence.py` 併入，見 §2b）。
其他：`codf_total_2020_2024`、`cla_total_2020_2025`（實際止於 2024）、`cgit_investment_2020_latest`、`cgit_construction_2020_latest`（至 2026H1）、`cgit_bri_share`、`lowy_china_disbursement_2020_2023`（全空）。**沒有跨來源總計欄。**

### 2b. dependence_country_year.csv（2018–2024，`05_dependence.py`）
把金額轉成「依賴」。來源與欄位：
| 欄位 | 來源 | 定義 |
|---|---|---|
| `gdp_usd_mn` | WDI `NY.GDP.MKTP.CD` | GDP，current USD |
| `gov_revenue_pct_gdp` | WDI `GC.REV.XGRT.GD.ZS` | 政府歲入（不含贈與）% GDP |
| `ppg_debt_china_usd_mn` / `ppg_debt_total_usd_mn` | IDS `DT.DOD.DPPG.CD`，counterpart China (730) / World | 公共及公共擔保外債存量，債權人為中國／全部 |
| `ppg_debt_china_share_of_ppg`、`ppg_debt_china_pct_gdp` | 計算 | 對中債務占 PPG 外債比、占 GDP % |
| `imf_credit_usd_mn`、`imf_credit_pct_gdp` | IDS `DT.DOD.DIMF.CD` | IMF 信用使用額（IMF 方案的代理變數；MONA 網站 403 拒絕自動下載） |
| `oda_gross_all_official_usd_mn` / `oda_gross_dac_countries_usd_mn` | OECD DAC2A measure 240，current USD | 所有官方捐助者（含多邊）／DAC 國家的 Gross ODA 撥付額（「西方替代選項」） |
| `aiddata_odaoof_usd_mn`、`codf_usd_mn` | 本專案 | 中國主口徑承諾額、CODF 承諾額 |
| `aiddata_odaoof_pct_gdp`、`aiddata_odaoof_pct_gov_revenue`、`china_vs_all_official_oda_ratio` | 計算 | 中國承諾額占 GDP、占政府歲入、相對於全部官方 ODA 撥付的倍數 |

summary 的 `dep_*` 欄：`dep_gdp_avg_2020_2023_usd_mn`、`dep_aiddata_odaoof_pct_gdp_2020_2023`（四年合計／四年 GDP 合計）、`dep_aiddata_odaoof_pct_gov_revenue_2020_2023`、`dep_ppg_debt_china_2023_usd_mn`、`dep_ppg_debt_china_share_2023`、`dep_ppg_debt_china_pct_gdp_2023`、`dep_imf_credit_pct_gdp_2023`、`dep_oda_gross_all_official_2020_2023_usd_mn`、`dep_china_vs_all_official_oda_ratio_2020_2023`。紓困貸款已另列 `aiddata_rescue_2020_2023`。
限制：IDS 只涵蓋 134 個中低所得報告國（2023 年有對中債務值的 99 國），高所得國無資料；OECD 為撥付額、AidData 為承諾額，倍數只供相對比較；主權信評未納入。

### 原檔欄位對應（預期 → 實際）
| 來源 | 規格預期 | 實際欄名 |
|---|---|---|
| AidData | Recipient / Recipient ISO-3 / Commitment Year / Amount (Constant USD) / Amount (Nominal USD) / Flow Type / Flow Class / Recommended For Aggregates / Umbrella / Status / Sector Name / Funding Agencies / Intent / Recipient Income Level | `Country_of_Activity` / `Country_of_Activity_ISO3` / `Commitment_Year` / `Amount_Constant_USD_2023` / `Amount_Nominal_USD` / `Flow_Type`（另有 `Flow_Type_Simplified`）/ `Flow_Class` / `Recommended_for_Aggregates` / `Umbrella` / `Status` / `Sector_Name` / `Funding_Agencies` / `Intent` / `WB_Income_Group_Host_Country`；主表工作表 `CLG-Global 1.0_Records`，175 欄 |
| CODF | Country / Year / Amount / Lender / Sector / Borrower / Project | `Country` / `Loan Sign Year` / `Loan Amount (USD M)` / `Lender` / `Sector` / `Borrower` / `Project name`；工作表 `CODF_2025` |
| CLA | Country / Year / Loan amount / Lender / Lender type / Sector / Project | `Country` / `Year` / `Loan (USD M)` / `Lender` / **無 Lender type 欄** / `Sector` / `Project Name`；表頭在第 2 列（`header=1`），欄名尾端有空白 |
| CGIT | Dataset 1+2 工作表、Quantity in Millions、Transaction Party、BRI | 兩個 CSV（investment / construction）；`Millions`（字串 ` $1,740 `）、`Partner/Target`、`BRI`（1/0；2005–2013 前期多為空白）；編碼 latin-1 |

### 國名轉換
`country_converter` 轉 ISO3；AidData 自帶 ISO3 與轉換結果 0 筆不一致。唯一失敗：CGIT `UAE` → 經確認寫入 `scripts/country_overrides.csv` 為 `ARE`。自動解析但已人工確認：`Congo`→COG、`Democratic Republic of the Congo`→COD、`Korea`→KOR、`Britain`→GBR、`Micronesia`→FSM、`Ivory Coast`/`Côte d’Ivoire`→CIV、`Cape Verde`/`Cabo Verde`→CPV、`Türkiye`/`Turkey`→TUR。`Regional`、`Regional, Africa`、`Multi-Region`、`*, regional` → `REGIONAL`。四個來源皆無 Hong Kong / Macau / Kosovo 紀錄（Taiwan 僅見於 CGIT）。

## 3. 口徑差異（不要相加）
- **AidData**：中國所有官方部門機構（政策性銀行、國有商業銀行、央行、部會、地方政府）的貸款與贈與**承諾額**，constant USD。
- **BU CODF**：只有國開行與進出口銀行對主權／公共擔保借款人的貸款承諾額，nominal。是 AidData 的子集，但兩者對同一筆貸款的認列與金額可能不同。
- **BU CLA**：非洲限定，含官方與商業放款人，nominal。與 CODF 和 AidData 部分重疊。
- **CGIT**：企業層級的對外直接投資與工程承包合約，≥1 億美元，nominal。與開發金融完全不同的概念（工程承包的業主可能正是用中國貸款付款，所以 CGIT 建設金額與 AidData 貸款金額之間有實質重疊）。

## 4. 已知問題與限制
0. **AidData 主口徑（2026-11-07 改）**：Flow_Class = OFIC（官方機構對私部門／商業對象的商業性融資，2000–2023 共 959 十億）不屬於「可影響對方政府政策的官方援助／貸款」，已自主口徑排除，僅作對照層。美國 2000–2023 的 201.9 十億 100% 是 OFIC（中銀、工行對 CME、AT&T、迪士尼等的商業放款），在主口徑下為 0。主口徑 2000–2023 合計 1,449 十億、2020–2023 合計 295 十億。
1. AidData 止於 2023 年承諾額；**無 2024–2025**。承諾額含 Pipeline 紀錄，不是撥付額。
2. **AidData 金額口徑**：官方「nearly $2.2 trillion」對應的是 `Adjusted_Amount_Constant_USD_2023`（扣除非中國共同融資份額；本專案算得 2,167.8 十億，−1.5%），而非規格指定的 `Amount_Constant_USD_2023`（2,408.5 十億，+9.5%）。但官方公布的國別數字（美國 >200、英國 60.0、法國 21.3、義大利 17.4 十億等）與**未調整**的 `Amount_Constant` 完全吻合。本專案依規格以 `Amount_Constant_USD_2023` 為 `amount_usd_mn`，並把 Adjusted 口徑保留在 `clean_aiddata.csv` 的 `amount_adjusted_constant_usd_mn`，未自行改動。
3. AidData 阿根廷 2020–2023 為第一名（764 億）幾乎全是人民銀行與阿根廷央行的貨幣互換動撥，AidData 標記為 `Rescue = Yes`（2000–2023 全球紓困貸款共 354 十億：阿根廷 151、巴基斯坦 79、埃及 22、蒙古 19、厄瓜多 12）。summary 另列 `aiddata_rescue_…` 與 `…_excl_rescue_…`，儀表板可切換含／排除／僅紓困。
4. CLA 本版檔案最大年份為 2024；`cla_total_2020_2025` 實為 2020–2024。CLA 放款人數算得 46（官方簡報 42），差異來自同一放款人的不同寫法（如 "The Export–Import Bank of China" 與含子公司／聯貸註記的變體），未合併。
5. CGIT 只收 ≥1 億美元（AEI 報告稱 ≥9,500 萬美元）；2026 年僅上半年；公開 CSV 無 troubled transactions 表與年度彙總表；AEI 已無官方 Excel 下載連結（若日後需要正式版需聯繫 AEI）。
6. Lowy 東南亞援助地圖無全量下載（SvelteKit 單頁應用，資料由 Supabase REST API 分頁供給），未取得；`lowy_china_disbursement_2020_2023` 全空。
7. `REGIONAL` 紀錄計入合計與趨勢，但不在地圖與排名。
8. 中文國名為手建對照表（`scripts/country_names_zh.csv`），採台灣慣用譯名。

## 5. 核對結果（`scripts/03_validate.py`，2026-11-07）

| 項目 | 我算的 | 官方公布 | 差異 | 備註 |
|---|---|---|---|---|
| AidData 筆數（全部紀錄） | 33,580 | 33,580 | +0.0% | 官方：33,580 projects and activities |
| AidData 2000–2023 總額 RfA=Yes，Amount_Constant_USD_2023（十億美元） | 2,408.5 | 2,200.0 | +9.5% | 官方「nearly $2.2 trillion」（2000–2023） |
| AidData 2000–2023 總額 RfA=Yes，Adjusted_Amount_Constant_USD_2023（十億美元） | 2,167.8 | 2,200.0 | -1.5% | 扣除非中國共同融資份額的口徑，供對照 |
| AidData 2000–2023 總額「全部紀錄」Amount_Constant（十億美元） | 3,736.4 | 2,200.0 | +69.8% | 不過濾 RfA（含 umbrella 重複），供對照 |
| AidData 高所得子集 2000–2023 總額（十億美元） | 959.5 | 943.4 | +1.7% | 官方 CLG-HIC 1.0：nearly $943.4 billion |
| AidData 美國 2000–2023 總額（十億美元） | 201.9 | 200.0 | +1.0% | 官方：「more than $200 billion for nearly 2,500 projects」；以 200 為基準 |
| AidData 美國 2000–2023 筆數 | 2,437 | 2,500 | -2.5% | 官方「nearly 2,500」 |
| AidData 高所得國家前 3 名 | United States 202 / Russia 172 / Australia 130 | United States 第一 | — | 官方：美國為高所得國家中最大受貸國 |
| AidData United Kingdom 2000–2023（十億美元） | 60.0 | 60.0 | -0.1% | 官方 blog 2025-11-18 |
| AidData France 2000–2023（十億美元） | 21.3 | 21.3 | -0.2% | 官方 blog 2025-11-18 |
| AidData Italy 2000–2023（十億美元） | 17.4 | 17.4 | +0.2% | 官方 blog 2025-11-18 |
| AidData Portugal 2000–2023（十億美元） | 11.7 | 11.7 | +0.4% | 官方 blog 2025-11-18 |
| AidData Netherlands 2000–2023（十億美元） | 11.6 | 11.6 | -0.2% | 官方 blog 2025-11-18 |
| CODF 筆數 2008–2024 | 1,304 | 1,304 | +0.0% | 官方 1,304 loans |
| CODF 2008–2024 總額（十億美元） | 472.1 | 472.0 | +0.0% | 官方 $472 billion |
| CODF 2024 筆數 | 20 | 20 | +0.0% | 官方 20 loans |
| CODF 2024 總額（十億美元） | 6.1 | 6.1 | +0.0% | 官方 $6.1 billion |
| CLA 筆數 2000–2024 | 1,319 | 1,319 | +0.0% | 官方 1,319 loan commitments |
| CLA 2000–2024 總額（十億美元） | 180.9 | 180.9 | -0.0% | 官方 $180.87 billion（Selective Engagement and Strategic Retooling, 2025-11-13） |
| CLA 2024 總額（十億美元） | 2.1 | 2.1 | +1.4% | 官方「just under $2.1 billion」 |
| CLA 放款人數 | 46 | 42 | +9.5% | 官方 42 lenders |
| CLA 最大年份 | 2024 | 2024 | — | 檔案不含 2025 年紀錄 |
| CGIT 2005–2026H1 投資+建設總額（十億美元） | 2,696.2 | 2,700.0 | -0.1% | AEI 頁面：「$2.7 trillion」；AEI 2026-07 報告同 |
| CGIT 2005–2025 投資+建設總額（十億美元） | 2,634.6 | 2,500.0 | +5.4% | AEI 2026-01 報告：「more than $2.5 trillion」（下限） |
| CGIT 筆數 2005–2026H1 | 5,050 | 5,000 | +1.0% | AEI：「over 5000 large transactions」（下限） |
| CGIT BRI 國家建設 2013–2026H1（十億美元） | 720.1 | 720.0 | +0.0% | AEI 2026-07：construction $720 billion in BRI countries since inception |
| CGIT BRI 國家投資 2013–2026H1（十億美元） | 479.5 | 480.0 | -0.1% | AEI 2026-07：investment $480 billion |
| CGIT BRI 國家建設 2013–2025（十億美元） | 692.7 | 687.0 | +0.8% | AEI 2026-01：$687 billion |
| CGIT BRI 國家投資 2013–2025（十億美元） | 463.4 | 468.0 | -1.0% | AEI 2026-01：$468 billion |
| CGIT 美國投資 2020–2025（十億美元） | 17.3 | 16.6 | +4.2% | AEI 2026-01：$16.6 billion |
| CGIT 美國投資 2020–2026H1（十億美元） | 18.7 | 18.0 | +3.8% | AEI 2026-07：「only $18 billion」 |

**CGIT 2020 年以後各年總額（十億美元，nominal）**：AEI 未公布可機讀的年度彙總表（Excel 版的彙總工作表不在公開 CSV 中），以下為本專案由交易層級 CSV 加總的結果，供對照 AEI 各期報告敘述。

|   Year |   Construction |   Investment |
|-------:|---------------:|-------------:|
|   2020 |           43.8 |         45.4 |
|   2021 |           48.8 |         54   |
|   2022 |           43   |         44.3 |
|   2023 |           50.6 |         63.6 |
|   2024 |           60.7 |         59.4 |
|   2025 |           56.6 |         67.3 |
|   2026 |           29.9 |         31.7 |

**隨機 10 國一致性核對（panel_country_year vs panel_long 加總，所有 year×source×measure 格）**

| ISO3 | long 加總 | country_year 加總 | 結果 |
|---|---|---|---|
| RUS | 28,170.1 | 28,170.1 | OK |
| TLS | 15.6 | 15.6 | OK |
| LCA | 0.0 | 0.0 | OK |
| MNG | 10,449.0 | 10,449.0 | OK |
| AUS | 38,884.0 | 38,884.0 | OK |
| CPV | 22.6 | 22.6 | OK |
| ZWE | 3,768.4 | 3,768.4 | OK |
| SSD | 686.9 | 686.9 | OK |
| IRQ | 26,215.1 | 26,215.1 | OK |
| GEO | 901.1 | 901.1 | OK |

差異超過 5% 的項目說明：
- **AidData 2000–2023 總額 +9.5%**：口徑差異（官方總額用 Adjusted 口徑；見 §4-2）。「全部紀錄」+69.8% 是因為未排除 umbrella 與不建議加總的紀錄，僅供對照。
- **CLA 放款人數 +9.5%**：放款人名稱寫法未合併（見 §4-4）；金額與筆數皆 0.0%。
- **CGIT 2005–2025 +5.4%**：官方只說「more than $2.5 trillion」（下限），非精確值；2005–2026H1 對「$2.7 trillion」為 −0.1%。

## 6. summary_2020_2025.csv 前 15 名

### AidData 主口徑 ODA+OOF+Vague（2020–2023，constant 2023，百萬美元）
| country_iso3   | country_name_zh   | region_zh              |   aiddata_total_2020_2023 |   aiddata_oda_2020_2023 |   aiddata_oof_2020_2023 |   aiddata_rescue_2020_2023 |   aiddata_total_excl_rescue_2020_2023 |
|:---------------|:------------------|:-----------------------|--------------------------:|------------------------:|------------------------:|---------------------------:|--------------------------------------:|
| ARG            | 阿根廷            | 拉丁美洲與加勒比海     |                    76,425 |                      19 |                  76,190 |                     74,637 |                                 1,787 |
| PAK            | 巴基斯坦          | 南亞                   |                    47,947 |                     405 |                  46,541 |                     41,622 |                                 6,325 |
| MYS            | 馬來西亞          | 東亞（東北亞＋東南亞） |                    17,832 |                      65 |                  17,766 |                        nan |                                17,832 |
| TUR            | 土耳其            | 中東＋中亞             |                    14,384 |                       6 |                  13,556 |                      5,004 |                                 9,380 |
| EGY            | 埃及              | 非洲                   |                    13,964 |                     252 |                  13,677 |                     11,323 |                                 2,641 |
| IDN            | 印尼              | 東亞（東北亞＋東南亞） |                    10,278 |                      74 |                   7,346 |                        nan |                                10,278 |
| MNG            | 蒙古              | 東亞（東北亞＋東南亞） |                     8,678 |                      98 |                   8,580 |                      6,678 |                                 2,001 |
| BRA            | 巴西              | 拉丁美洲與加勒比海     |                     6,897 |                       2 |                   5,248 |                        nan |                                 6,897 |
| IRQ            | 伊拉克            | 中東＋中亞             |                     6,785 |                      32 |                   6,753 |                        nan |                                 6,785 |
| NGA            | 奈及利亞          | 非洲                   |                     6,287 |                      83 |                   6,204 |                      1,109 |                                 5,178 |
| PER            | 秘魯              | 拉丁美洲與加勒比海     |                     6,035 |                      57 |                   5,828 |                        nan |                                 6,035 |
| LKA            | 斯里蘭卡          | 南亞                   |                     5,980 |                   1,304 |                   4,532 |                      5,509 |                                   471 |
| BGD            | 孟加拉            | 南亞                   |                     5,024 |                      85 |                   4,874 |                        nan |                                 5,024 |
| PHL            | 菲律賓            | 東亞（東北亞＋東南亞） |                     5,018 |                     576 |                   4,351 |                        nan |                                 5,018 |
| KHM            | 柬埔寨            | 東亞（東北亞＋東南亞） |                     3,606 |                     784 |                   2,730 |                        nan |                                 3,606 |

### AidData 主口徑排除紓困貸款（Rescue = Yes）
| country_iso3   | country_name_zh   | region_zh              |   aiddata_total_excl_rescue_2020_2023 |
|:---------------|:------------------|:-----------------------|--------------------------------------:|
| MYS            | 馬來西亞          | 東亞（東北亞＋東南亞） |                                17,832 |
| IDN            | 印尼              | 東亞（東北亞＋東南亞） |                                10,278 |
| TUR            | 土耳其            | 中東＋中亞             |                                 9,380 |
| BRA            | 巴西              | 拉丁美洲與加勒比海     |                                 6,897 |
| IRQ            | 伊拉克            | 中東＋中亞             |                                 6,785 |
| PAK            | 巴基斯坦          | 南亞                   |                                 6,325 |
| PER            | 秘魯              | 拉丁美洲與加勒比海     |                                 6,035 |
| NGA            | 奈及利亞          | 非洲                   |                                 5,178 |
| BGD            | 孟加拉            | 南亞                   |                                 5,024 |
| PHL            | 菲律賓            | 東亞（東北亞＋東南亞） |                                 5,018 |
| KHM            | 柬埔寨            | 東亞（東北亞＋東南亞） |                                 3,606 |
| KAZ            | 哈薩克            | 中東＋中亞             |                                 3,518 |
| COD            | 剛果民主共和國    | 非洲                   |                                 3,411 |
| UZB            | 烏茲別克          | 中東＋中亞             |                                 3,384 |
| MEX            | 墨西哥            | 拉丁美洲與加勒比海     |                                 2,889 |

### AidData 區域合計（主口徑／其中紓困／OFIC 對照）
| region_zh              |   aiddata_total_2020_2023 |   aiddata_rescue_2020_2023 |   aiddata_ofic_2020_2023 |
|:-----------------------|--------------------------:|---------------------------:|-------------------------:|
| 拉丁美洲與加勒比海     |                    97,326 |                     74,925 |                    1,802 |
| 南亞                   |                    60,589 |                     47,131 |                        0 |
| 東亞（東北亞＋東南亞） |                    51,235 |                      8,382 |                   21,192 |
| 非洲                   |                    44,267 |                     12,582 |                        1 |
| 中東＋中亞             |                    32,424 |                      5,004 |                   22,009 |
| 大洋洲                 |                     3,110 |                          0 |                   19,558 |
| 歐洲                   |                     2,895 |                          0 |                   71,423 |
| 北美                   |                         0 |                          0 |                   71,501 |

### CGIT（2020–2026H1，nominal，百萬美元；投資與建設同屬 CGIT 可合計）
| country_iso3   | country_name_zh   |   cgit_investment_2020_latest |   cgit_construction_2020_latest |   cgit_total |   cgit_bri_share |
|:---------------|:------------------|------------------------------:|--------------------------------:|-------------:|-----------------:|
| SAU            | 沙烏地阿拉伯      |                     10,120.00 |                       36,690.00 |    46,810.00 |             1.00 |
| IDN            | 印尼              |                     23,720.00 |                       11,710.00 |    35,430.00 |             1.00 |
| BRA            | 巴西              |                     24,510.00 |                        1,110.00 |    25,620.00 |             0.00 |
| SGP            | 新加坡            |                     10,720.00 |                       12,240.00 |    22,960.00 |             1.00 |
| AUS            | 澳大利亞          |                      7,510.00 |                       14,700.00 |    22,210.00 |             0.00 |
| ARE            | 阿拉伯聯合大公國  |                        320.00 |                       20,440.00 |    20,760.00 |             1.00 |
| IRQ            | 伊拉克            |                      2,640.00 |                       16,790.00 |    19,430.00 |             1.00 |
| USA            | 美國              |                     18,680.00 |                          nan    |    18,680.00 |             0.00 |
| MYS            | 馬來西亞          |                     11,400.00 |                        7,280.00 |    18,680.00 |             1.00 |
| VNM            | 越南              |                      8,840.00 |                        7,920.00 |    16,760.00 |             1.00 |
| KAZ            | 哈薩克            |                      6,150.00 |                        8,860.00 |    15,010.00 |             1.00 |
| SRB            | 塞爾維亞          |                      3,000.00 |                       11,680.00 |    14,680.00 |             1.00 |
| GUY            | 蓋亞那            |                     11,590.00 |                        1,260.00 |    12,850.00 |             1.00 |
| GBR            | 英國              |                     12,370.00 |                          nan    |    12,370.00 |             0.00 |
| EGY            | 埃及              |                      3,700.00 |                        8,020.00 |    11,720.00 |             1.00 |

## 7. 線上版本與授權

本 repo 的程式碼與衍生資料（`scripts/`、`data/clean/`、`dashboard/`）以 MIT 授權釋出。原始資料檔不隨 repo 發布（見 `data/raw/MANIFEST.md` 的下載連結與 SHA256）。各來源資料的使用條款與建議引用：

| 來源 | 授權／條款 | 引用 |
|---|---|---|
| AidData CLG-Global 1.0 | Open Data Commons Attribution License (ODC-By 1.0)；使用與再發布須標註 AidData 並保留授權聲明 | AidData. 2025. *China's Global Loans and Grants Dataset, Version 1.0*. Williamsburg, VA: AidData at William & Mary. https://www.aiddata.org/data/chinas-global-loans-and-grants-dataset-1-0 |
| BU GDP Center — CODF | 頁面提供建議引用格式 | Boston University Global Development Policy Center. 2025. *China's Overseas Development Finance Database*. https://www.bu.edu/gdp/chinas-overseas-development-finance-database/ |
| BU GDP Center — CLA | 頁面提供建議引用格式 | Boston University Global Development Policy Center. 2025. *Chinese Loans to Africa Database*. https://www.bu.edu/gdp/chinese-loans-to-africa-database/ |
| AEI／Heritage — CGIT | 「available for public use with proper citation」 | American Enterprise Institute and The Heritage Foundation. 2026. *China Global Investment Tracker*. https://www.aei.org/china-global-investment-tracker/ |
| World Bank WDI／IDS | CC BY 4.0 | World Bank. *World Development Indicators*; *International Debt Statistics*. https://data.worldbank.org |
| OECD DAC2A | CC BY 4.0 | OECD. *Aid (ODA) disbursements to countries and regions [DAC2A]*. https://data-explorer.oecd.org |

儀表板內嵌的紀錄層級資料（計畫名稱、放款人、投資者）為上述來源的衍生整理；若來源方要求移除，請開 issue。
