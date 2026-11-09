"""媒體層（第一階段：計數）。GDELT GKG（BigQuery）2026 年起，來源 = 中國官媒／外交部英文站 + 國際通訊社；對象 = 七區域各前五高曝險國（scripts/media_targets.csv）。
輸出：media_weekly.csv（國家×來源群×週：篇數、涉台篇數、提及中國篇數）、media_articles.csv（涉台文章清單）、media_summary.csv（國家×來源群 2026 合計）。只用英文原文（TranslationInfo 空）。"""
import pandas as pd, html, re
from common import *
g = pd.read_csv(RAW/'gdelt/gkg_2026_targets.csv', dtype={'DATE':str})
g = g[g.english_original.astype(str).str.lower()=='true'].copy()
g['date'] = pd.to_datetime(g.DATE.str[:8]); g['week'] = g.date.dt.to_period('W-SUN').dt.start_time
g['title'] = g.title.fillna('').map(html.unescape).str.replace(r'\s+',' ',regex=True).str.strip()
GROUP = {'xinhuanet.com':'新華社','news.cn':'新華社','english.news.cn':'新華社','chinadaily.com.cn':'China Daily','people.cn':'人民日報(英文)','en.people.cn':'人民日報(英文)','globaltimes.cn':'環球時報','cgtn.com':'CGTN','fmprc.gov.cn':'外交部','reuters.com':'Reuters','apnews.com':'AP','france24.com':'France 24 (AFP)','barrons.com':"Barron's (AFP)",'bbc.com':'BBC','bbc.co.uk':'BBC','theguardian.com':'Guardian','aljazeera.com':'Al Jazeera','dw.com':'DW','euronews.com':'Euronews','scmp.com':'SCMP','channelnewsasia.com':'CNA','straitstimes.com':'Straits Times','abc.net.au':'ABC (AU)','bloomberg.com':'Bloomberg','nytimes.com':'NYT','thediplomat.com':'The Diplomat','voanews.com':'VOA','rfa.org':'RFA'}
SIDE = {'新華社':'官媒','China Daily':'官媒','人民日報(英文)':'官媒','環球時報':'官媒','CGTN':'官媒','外交部':'官方','Reuters':'通訊社','AP':'通訊社','France 24 (AFP)':'通訊社',"Barron's (AFP)":'通訊社','BBC':'國際媒體','Guardian':'國際媒體','Al Jazeera':'國際媒體','DW':'國際媒體','Euronews':'國際媒體','SCMP':'國際媒體','CNA':'國際媒體','Straits Times':'國際媒體','ABC (AU)':'國際媒體','Bloomberg':'國際媒體','NYT':'國際媒體','The Diplomat':'國際媒體','VOA':'國際媒體','RFA':'國際媒體'}
g['source_group'] = g.source.map(GROUP); g['side'] = g.source_group.map(SIDE)
t = pd.read_csv(SCRIPTS/'media_targets.csv'); g = g.merge(t[['fips','country_iso3','country_name_en','country_name_zh','region_zh']], left_on='country_fips', right_on='fips')
g['taiwan_flag'] = g.taiwan_flag.astype(str).str.lower()=='true'; g['china_flag'] = g.china_flag.astype(str).str.lower()=='true'
g['one_china'] = g.title.str.contains(r'one[- ]china|one China', case=False, regex=True)
g = g.drop_duplicates(['url','country_iso3'])
# ---- 收錄標準（2026-11-09 改）：官媒 = 對象國名出現在標題（避免只是彙整稿順帶提及）；國際媒體／通訊社 = 文章同時標到中國（CH），即「關於中國與該國」的報導
ALIAS={'LAO':['Laos','Lao'],'KHM':['Cambodia','Cambodian'],'MNG':['Mongolia','Mongolian'],'MMR':['Myanmar','Burma'],'IDN':['Indonesia','Indonesian'],'PAK':['Pakistan','Pakistani'],'LKA':['Sri Lanka','Sri Lankan'],'MDV':['Maldives','Maldivian'],'BGD':['Bangladesh','Bangladeshi'],'NPL':['Nepal','Nepali','Nepalese'],'TJK':['Tajikistan','Tajik'],'KGZ':['Kyrgyzstan','Kyrgyz'],'UZB':['Uzbekistan','Uzbek'],'KAZ':['Kazakhstan','Kazakh'],'IRQ':['Iraq','Iraqi'],'TON':['Tonga','Tongan'],'VUT':['Vanuatu'],'WSM':['Samoa','Samoan'],'PNG':['Papua New Guinea','PNG'],'SLB':['Solomon Islands'],'SUR':['Suriname'],'ARG':['Argentina','Argentine','Argentinian'],'GUY':['Guyana'],'DMA':['Dominica'],'ECU':['Ecuador','Ecuadorian'],'SRB':['Serbia','Serbian'],'BLR':['Belarus','Belarusian'],'MNE':['Montenegro'],'MKD':['North Macedonia','Macedonia'],'BIH':['Bosnia'],'COG':['Republic of Congo','Republic of the Congo','Congo-Brazzaville','Brazzaville'],'GIN':['Guinea'],'COD':['DR Congo','DRC','Democratic Republic of Congo','Democratic Republic of the Congo','Kinshasa'],'AGO':['Angola','Angolan'],'LSO':['Lesotho']}
g['in_title'] = [any(re.search(r'\b'+re.escape(a)+r'\b', ti, re.I) for a in ALIAS.get(c,[n])) for c,n,ti in zip(g.country_iso3, g.country_name_en, g.title)]
g_all = g.copy()
g = g[((g.side=='官媒') & g.in_title) | ((g.side!='官媒') & g.china_flag)].copy()
print('after inclusion rule:', len(g), 'of', len(g_all), '| 官媒', (g.side=='官媒').sum(), '國際媒體', (g.side=='國際媒體').sum(), '通訊社', (g.side=='通訊社').sum())
wk = g.groupby(['country_iso3','country_name_en','country_name_zh','region_zh','side','source_group','week']).agg(n=('url','nunique'), n_taiwan=('taiwan_flag','sum'), n_china=('china_flag','sum'), n_one_china=('one_china','sum')).reset_index()
wk.to_csv(CLEAN/'media_weekly.csv', index=False)
art = g[g.taiwan_flag | g.one_china][['country_iso3','country_name_zh','side','source_group','date','title','url','taiwan_flag','one_china','china_flag']].sort_values('date', ascending=False)
art.to_csv(CLEAN/'media_articles_taiwan.csv', index=False)
sm = g.groupby(['country_iso3','country_name_en','country_name_zh','region_zh','side','source_group']).agg(n=('url','nunique'), n_taiwan=('taiwan_flag','sum'), n_china=('china_flag','sum'), n_one_china=('one_china','sum')).reset_index()
sm['taiwan_share'] = sm.n_taiwan/sm.n; sm['china_share'] = sm.n_china/sm.n
sm.to_csv(CLEAN/'media_summary.csv', index=False)
print('articles (en, deduped):', len(g), '| date range', g.date.min().date(), g.date.max().date()); print(g.groupby('source_group').url.nunique().sort_values(ascending=False).to_dict())
piv = sm.groupby(['country_name_zh','side']).n.sum().unstack().fillna(0).astype(int); piv['taiwan']=sm.groupby('country_name_zh').n_taiwan.sum(); print(piv.sort_values('官媒',ascending=False).head(12).to_string())
