"""English versions of the four pages -> dashboard/en/{index,regions,exposure,media}.html.
Built from the Chinese pages after they are generated, so the two languages always share code and data:
  1. the "about" sections are swapped for their English files (scripts/*_about_en.html);
  2. remaining Chinese text (UI labels, notes, embedded names) is replaced from scripts/i18n_en.json, longest first,
     then country and region names (scripts/country_names_zh.csv, country_regions.csv);
  3. lang="en" is set and a link back to the Chinese page is added.
Chinese text that is still left is written to scripts/i18n_en_todo.txt so the dictionary can be completed.
Run after the Chinese pages are built: python3.12 scripts/make_en.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; S = ROOT / "scripts"; D = ROOT / "dashboard"
PAGES = {"index": "dashboard_about", "regions": "dashboard_about", "exposure": "dashboard_exposure_about", "media": "dashboard_media_about"}
REGIONS_EN = {"AFRICA": "Africa", "EAST_ASIA": "East Asia (Northeast + Southeast Asia)", "EUROPE": "Europe", "LATAM_CARIB": "Latin America and the Caribbean",
              "MIDEAST_CASIA": "Middle East + Central Asia", "NORTH_AMERICA": "North America", "OCEANIA": "Oceania", "REGIONAL": "Regional / multi-country", "SOUTH_ASIA": "South Asia"}
WIDE_CHARS = "　-〿㐀-鿿＀-￯"
# a Chinese segment starts with a CJK / full-width character and runs until markup, a quote or a line break;
# trailing ASCII after the last CJK / full-width character is trimmed
SEG = re.compile("[" + WIDE_CHARS + "][^<>\"'`\n{}]*")
WIDE = re.compile("[" + WIDE_CHARS + "]")

def segments(h):
    out = set()
    for m in SEG.finditer(h):
        t = m.group(0); last = max(i for i, ch in enumerate(t) if WIDE.match(ch)); out.add(t[:last + 1])
    return out

def load_dict():
    """(phrases, names); phrases go first so that names inside phrases are translated with them"""
    import csv
    names = {r["country_name_zh"]: r["country_name_en"] for r in csv.DictReader(open(S / "country_names_zh.csv", encoding="utf-8")) if r["country_name_zh"]}
    for r in csv.DictReader(open(S / "country_regions.csv", encoding="utf-8")):
        if r["region_zh"]: names[r["region_zh"]] = REGIONS_EN.get(r["region_code"], r["region_code"])
    f = S / "i18n_en.json"
    phrases = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    # translations land inside JS strings and HTML attributes: use typographic quotes so they cannot end a string
    safe = lambda v: re.sub(r'"([^"]*)"', "\u201c\\1\u201d", v).replace("'", "\u2019")
    return {k: safe(v) for k, v in phrases.items()}, names

def to_en(h, about, d):
    h = re.sub(r'<a href="en/[a-z]+\.html" lang="en">English</a>', "", h)   # the Chinese page's own switch link
    if about:
        zh, en = (S / f"{about}.html").read_text(encoding="utf-8"), (S / f"{about}_en.html").read_text(encoding="utf-8")
        for a, b in ((zh, en), (json.dumps(zh, ensure_ascii=False)[1:-1], json.dumps(en, ensure_ascii=False)[1:-1]),
                     (json.dumps(zh)[1:-1], json.dumps(en)[1:-1])):
            h = h.replace(a, b)
    phrases, names = d
    # order: phrases of 3+ characters, then names, then 1–2-character fragments (so that fragments
    # such as 群 or 年 cannot break names like 馬紹爾群島)
    for k in sorted((k for k in phrases if len(k) >= 3), key=len, reverse=True):
        h = h.replace(k, phrases[k])
    for k in sorted(names, key=len, reverse=True):
        h = h.replace(k, names[k])
    for k in sorted((k for k in phrases if len(k) < 3), key=len, reverse=True):
        h = h.replace(k, phrases[k])
    return h.replace('lang="zh-Hant"', 'lang="en"')

def add_switch(h, href, label):
    """language link as the first item of the page's top-right nav (idempotent)"""
    if f'href="{href}"' in h: return h
    link = f'<a href="{href}" lang="{"en" if label == "English" else "zh-Hant"}">{label}</a>'
    if "<nav>" in h:
        return h.replace("<nav>", "<nav>" + link, 1)
    return h.replace("</header>", f'<div class="lang">{link}</div></header>', 1)

if __name__ == "__main__":
    d = load_dict(); (D / "en").mkdir(exist_ok=True); todo = set()
    for page, about in PAGES.items():
        zh = (D / f"{page}.html").read_text(encoding="utf-8")
        (D / f"{page}.html").write_text(add_switch(zh, f"en/{page}.html", "English"), encoding="utf-8")
        h = add_switch(to_en(zh, about, d), f"../{page}.html", "中文")
        (D / "en" / f"{page}.html").write_text(h, encoding="utf-8")
        left = segments(h) - {"中文", "请宁夏卫健委与"}; todo |= left   # the latter is original-language text inside an AidData field
        print(page, "leftover Chinese segments:", len(left))
    (S / "i18n_en_todo.txt").write_text("\n".join(sorted(todo, key=len, reverse=True)), encoding="utf-8")
