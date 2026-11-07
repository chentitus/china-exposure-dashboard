# data/raw/MANIFEST.md — 原始資料清單

下載日期：2026-11-07（所有檔案）。原始檔不修改。

| # | 來源 | 檔案 | 來源 URL | 大小 (bytes) | SHA256 |
|---|------|------|----------|-------------|--------|
| 1 | AidData CLG-Global 1.0 | `AidDatas_CLG_Global_Dataset_v1.0.zip` | https://docs.aiddata.org/ad4/datasets/AidDatas_CLG_Global_Dataset_v1.0.zip （頁面：https://www.aiddata.org/data/chinas-global-loans-and-grants-dataset-1-0） | 43,766,051 | `f5838f714bde2b537473e8ca6a56aa8c23dccabfe939eebebd6b9ff491a127db` |
| 1a | ↳ zip 內容（解壓至 `aiddata_unzipped/`） | `AidDatas_CLG_Global_Dataset_v1.0.xlsx`（40,586,849 B；工作表：Contents, Overview, Guide, CountryList, **CLG-Global 1.0_Records**, Definitions_Records, Borrower Ownership, Definitions_Borrower Ownership, License）、`Field Definitions_CLG-Global 1.0.pdf`（codebook，816,213 B）、`Tracking_Chinese_Loans_and_Grants_TUFF_4_Methodology.pdf` | 同上 | | |
| 1b | AidData TUFF 4.0 方法文件（獨立下載，與 zip 內同檔） | `Tracking_Chinese_Loans_and_Grants_TUFF_4_Methodology.pdf` | https://docs.aiddata.org/reports/chasing-china/Tracking_Chinese_Loans_and_Grants_TUFF_4_Methodology.pdf （頁面：https://www.aiddata.org/publications/tracking-loans-and-grants-from-china-globally-4-0-methodology） | 4,076,331 | `6eda791295a2bf79e5f8379110efa41935a618fd7b84476b7da573c623806e07` |
| 2 | BU GDP Center — CODF | `CODF-Database-Dataset-2025-EN.xlsx`（工作表 `CODF_2025`，1,307 列 × 37 欄） | https://www.bu.edu/gdp/files/2025/06/CODF-Database-Dataset-2025-EN.xlsx （頁面：https://www.bu.edu/gdp/chinas-overseas-development-finance-database-data-download/ ；頁面另有 `-CN.xlsx` 中文版，未下載） | 521,977 | `e324047ed0de151b15b83b9a2a01bd3030c5f8ed66e00dba3f1baabdc7458960` |
| 3 | BU GDP Center — CLA | `CLA-Database-Raw-Data-Public-2025-FIN.xlsx`（工作表 `2025`，1,320 列 × 13 欄） | https://www.bu.edu/gdp/files/2026/02/CLA-Database-Raw-Data-Public-2025-FIN.xlsx （頁面：https://www.bu.edu/gdp/chinese-loans-to-africa-database-data-download/） | 214,843 | `f96b71579919c4b34e7d9b41c321c3eaeb0227265c1202d274fa4df9d3ba6f8e` |
| 4 | AEI/Heritage CGIT — 投資 | `cgit/CGIT_investment_2005-2026H1.csv`（2,554 筆） | https://kristol2021live.aei.org/plzchina/infographics/worldinvestments/investment.csv | 225,982 | `e4c433940666522c1ac8d0999c13eb42e12a8d1141b0a2e6732d37a3a1d8a6ea` |
| 4 | AEI/Heritage CGIT — 建設 | `cgit/CGIT_construction_2005-2026H1.csv`（2,494 筆） | https://kristol2021live.aei.org/plzchina/infographics/worldinvestments/construction.csv | 252,550 | `43996cb3b7d017f86ad5feeff1246099d712d2e808291b04e1ef2a44770ebb13` |
| 4 | AEI/Heritage CGIT — 母公司側寫表 | `cgit/CGIT_investment_profile.csv`（74 家母公司；僅供參考） | https://kristol2021live.aei.org/plzchina/infographics/worldinvestments/investment_profile.csv | 10,830 | `42eb64fc5b76d6e4f7a1baca86e3dcea11b1498b7a4200e36107588c7f30a7ed` |
| 5 | Lowy Southeast Asia Aid Map | **未取得** | https://seamap.lowyinstitute.org/ | — | — |

## CGIT 取得方式說明（重要）

AEI 的 CGIT 頁面（https://www.aei.org/china-global-investment-tracker/ ）在 2026-11-07 已**不再提供 Excel 下載連結**；頁面文字改為「For the full data set, please contact Derek Scissors」。頁面內嵌地圖（iframe `https://kristol2021live.aei.org/plzchina/`）上的「Download the Dataset」連結指向 `/data/China-Global-Investment-Tracker/`，回傳 404 / 轉回首頁。

因此改取該互動地圖實際載入的兩個交易層級 CSV（投資 + 建設），欄位：
`Year, Month, Investor, Millions, Share Size, Partner/Target, Sector, Subsector, Country, Region, BRI`，
時間範圍 2005-01 至 **2026-06**（資料截止：2026 年上半年；對應 AEI 2026 年 7 月更新）。
兩檔合計 5,048 筆、約 2.70 兆美元（投資 1,603 + 建設 1,093 十億美元），與頁面自述「$2.7 trillion … over 5000 large transactions」一致，故視為等同 Excel 的 `Dataset 1+2`。
**缺少**：Excel 版才有的「troubled transactions」表與彙總工作表。檔案編碼為 latin-1/cp1252（非 UTF-8）。

## Lowy 說明

網站為 SvelteKit 單頁應用，資料由 Supabase REST API（`…supabase.co/rest/v1/rpc/…`）即時供給；Map / Data / Graphing tool / Compare 各頁與選單均無 CSV/Excel 全量下載，只有 PDF 報告（2026 Key Findings、Methodology、各國簡介）。依規格略過，README 註明。

## 外部 API（依賴指標，2026-11-07 抓取，快取於 `external/`）
| 來源 | 端點 | 內容 |
|---|---|---|
| World Bank WDI | `https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD`、`GC.REV.XGRT.GD.ZS`（2018–2024） | GDP current USD；政府歲入 % GDP（lastupdated 2026-10-08） |
| World Bank IDS（source 6） | `https://api.worldbank.org/v2/sources/6/country/all/series/DT.DOD.DPPG.CD/counterpart-area/730|WLD/time/YR2018;…;YR2024`；`DT.DOD.DIMF.CD/counterpart-area/WLD` | PPG 外債存量（債權人中國／全部）；IMF 信用使用額（lastupdated 2026-11-05） |
| OECD DAC2A | `https://sdmx.oecd.org/public/rest/data/OECD.DCD.FSD,DSD_DAC2@DF_DAC2A,1.2/ALLD|DAC..240.USD.V` | Gross ODA 撥付額，current USD，所有官方捐助者／DAC 國家，2018–2024 |
| IMF MONA | https://www.imf.org/external/np/pdr/mona/index.aspx | **未取得**（HTTP 403 拒絕自動下載） |
