"""共用工具：路徑、國名→ISO3 轉換（country_converter + 手動 overrides）、中文國名。"""
import re, pandas as pd
from pathlib import Path
import country_converter as coco

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, SCRIPTS = ROOT/'data/raw', ROOT/'data/clean', ROOT/'scripts'
OVERRIDES = SCRIPTS/'country_overrides.csv'      # country_raw,country_iso3
ZH_NAMES  = SCRIPTS/'country_names_zh.csv'
REGIONS   = SCRIPTS/'country_regions.csv'      # country_iso3,region_code,region_zh（自訂分區）       # country_iso3,country_name_en,country_name_zh

REGIONAL_PAT = re.compile(r'(?i)regional|multi[- ]?region|^africa$|^asia$|^europe$|^global$|world|^unknown$|unspecified')

LONG_COLS = ['source','measure','country_iso3','country_name_en','country_name_zh','country_raw','year',
             'amount_usd_mn','amount_basis','flow_type','flow_class','sector','funder_or_investor',
             'bri_flag','status','record_id','project_title','region_code','region_zh']

_cc = coco.CountryConverter()

def load_overrides() -> dict:
    if OVERRIDES.exists():
        o = pd.read_csv(OVERRIDES, dtype=str).dropna()
        return dict(zip(o['country_raw'].str.strip(), o['country_iso3'].str.strip()))
    return {}

def to_iso3(names: pd.Series) -> tuple[pd.Series, list]:
    """回傳 (iso3 series, 轉換失敗清單)。區域性名稱→'REGIONAL'；失敗→NaN（不猜）。"""
    ov = load_overrides()
    uniq = pd.Series(names.dropna().unique())
    out, failed = {}, []
    for n in uniq:
        s = str(n).strip()
        if s in ov: out[n] = ov[s]; continue
        if REGIONAL_PAT.search(s): out[n] = 'REGIONAL'; continue
        r = _cc.convert(s, to='ISO3', not_found='__NF__')
        if isinstance(r, list) or r == '__NF__' or not re.fullmatch(r'[A-Z]{3}', str(r)): failed.append(s); out[n] = None
        else: out[n] = r
    return names.map(out), sorted(set(failed))

def add_names(df: pd.DataFrame) -> pd.DataFrame:
    """加上 country_name_en（ISO 短名）與 country_name_zh。"""
    iso = df['country_iso3']
    en = {}
    for c in iso.dropna().unique():
        if c == 'REGIONAL': en[c] = 'Regional / multi-country'
        else:
            r = _cc.convert(c, src='ISO3', to='name_short', not_found='__NF__')
            en[c] = r if isinstance(r, str) and r != '__NF__' else c
    df['country_name_en'] = iso.map(en)
    zh = {}
    if ZH_NAMES.exists():
        z = pd.read_csv(ZH_NAMES, dtype=str)
        zh = dict(zip(z['country_iso3'], z['country_name_zh']))
    df['country_name_zh'] = iso.map(zh)
    rg = pd.read_csv(REGIONS, dtype=str).set_index('country_iso3')
    df['region_code'] = iso.map(rg['region_code']); df['region_zh'] = iso.map(rg['region_zh'])
    return df

def finalize(df: pd.DataFrame) -> pd.DataFrame:
    for c in LONG_COLS:
        if c not in df.columns: df[c] = pd.NA
    return df[LONG_COLS]
