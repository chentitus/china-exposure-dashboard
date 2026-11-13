# 更新手冊（世界各國對中依賴與曝險儀表板）

觸發：Titus 說「更新世界儀表板」。目標：四個來源與依賴指標推進到最新版本，三個 HTML 重建並上線，回報變動。

## 0. 前置
專案路徑：`…/Admin_Docs_since_0716_2024/china-finance-dashboard/`；不需 API key（WDI／IDS／OECD 為公開端點）。原始檔在 `data/raw/`（不進 repo），`data/raw/MANIFEST.md` 記錄 URL 與 SHA256。

## 1. 來源檢查（每次都做）
| 來源 | 檢查處 | 有新版時 |
|---|---|---|
| AidData CLG-Global | https://www.aiddata.org/data/chinas-global-loans-and-grants-dataset-1-0 （版本號、zip 連結） | 下載 zip → 解壓 `data/raw/aiddata_unzipped/` → 刪 `data/clean/aiddata_clg_global_1.0_records.parquet` → `00_inspect.py`；欄位若改名，對照 `01_clean_aiddata.py` |
| BU CODF | https://www.bu.edu/gdp/chinas-overseas-development-finance-database-data-download/ （xlsx 檔名含年份） | 下載 → 檔名改進 `01_clean_codf.py`、`03_validate.py` |
| BU CLA | https://www.bu.edu/gdp/chinese-loans-to-africa-database-data-download/ | 同上（注意 header 列位置） |
| AEI CGIT | `https://kristol2021live.aei.org/plzchina/infographics/worldinvestments/{investment,construction}.csv`（每年 1 月、7 月更新） | 直接重下載到 `data/raw/cgit/`（latin-1） |
| WDI／IDS／OECD | API | 刪 `data/raw/external/*.json` 重抓；`05_dependence.py` 的 `Y1` 推進一年 |
| Lowy SEA Aid Map | https://seamap.lowyinstitute.org/ | 仍無全量下載則略過 |

## 2. 重跑
`cd scripts && for s in aiddata codf cla cgit; do python3.12 01_clean_$s.py; done && python3.12 01a_country_check.py`（新國名失敗 → 問 Titus → `country_overrides.csv`）→ `02_build_panel.py` → `03_validate.py` → `05_dependence.py` → `04_build_dashboard.py`。

## 3. 檢查與發布
本機開 `dashboard/index.html`、`regions.html`、`exposure.html`：地圖、分面趨勢（年份延伸）、曝險分數表、雷達圖；console 無錯誤。README §1 版本表、§5 核對表、§6 前 15 名；MANIFEST 日期與 SHA256。`git add -A && git commit && git push`，等 Pages 回 200，回報：各來源版本／期間、核對差異、前幾名變動。

## 4. 媒體層（GDELT）
1. `gcloud auth login`（token 常過期）；`bq query --use_legacy_sql=false --format=csv --max_rows=5000000 < scripts/media_gkg_query.sql > data/raw/gdelt/gkg_2026_targets.csv`（約 150 GB 掃描；每月前 1 TB 免費）。要擴年份改 SQL 的 `_PARTITIONTIME`。
2. 對象國若要跟著曝險分數更新，重算 `scripts/media_targets.csv`（七區域各前五，FIPS 對照表在 `06_media.py` 之前的建表程式）；否則維持固定名單以保留時間序列。
3. `python3.12 scripts/06_media.py` → `04_build_dashboard.py`；檢查 `media.html`。

## 英文版（每次重建頁面後都要做）
`python3.12 scripts/make_en.py` → 產生 `dashboard/en/{index,regions,exposure,media}.html`。英文版由中文頁自動轉換：說明頁換成 `scripts/*_about_en.html`，其餘中文依 `scripts/i18n_en.json` 取代，國名與區域名取自 `country_names_zh.csv`、`country_regions.csv`。若輸出列出「leftover Chinese segments」不為 0，未翻譯的字串會寫在 `scripts/i18n_en_todo.txt`，補進 `i18n_en.json` 後重跑。改了中文說明頁時，也要同步改英文版。
