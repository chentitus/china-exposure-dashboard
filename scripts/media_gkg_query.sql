WITH base AS (
  SELECT DATE, SourceCommonName AS source, DocumentIdentifier AS url,
         REGEXP_EXTRACT(Extras, r'<PAGE_TITLE>(.*?)</PAGE_TITLE>') AS title,
         V2Locations, V2Themes,
         (V2Locations LIKE '%#TW#%' OR V2Themes LIKE '%TAIWAN%') AS taiwan_flag,
         (V2Locations LIKE '%#CH#%') AS china_flag,
         (TranslationInfo IS NULL OR TranslationInfo = '') AS english_original
  FROM `gdelt-bq.gdeltv2.gkg_partitioned`
  WHERE _PARTITIONTIME >= TIMESTAMP('2026-01-01')
    AND SourceCommonName IN ('xinhuanet.com','news.cn','english.news.cn','chinadaily.com.cn','people.cn','en.people.cn','globaltimes.cn','cgtn.com','fmprc.gov.cn','reuters.com','apnews.com','france24.com','barrons.com','bbc.com','bbc.co.uk','theguardian.com','aljazeera.com','dw.com','euronews.com','scmp.com','channelnewsasia.com','straitstimes.com','abc.net.au','bloomberg.com','nytimes.com','thediplomat.com','voanews.com','rfa.org')
)
SELECT DATE, source, url, title, taiwan_flag, china_flag, english_original, cc AS country_fips
FROM base, UNNEST(ARRAY(SELECT DISTINCT REGEXP_EXTRACT(x, r'^[^#]*#[^#]*#([A-Z]{2})#') FROM UNNEST(SPLIT(V2Locations, ';')) AS x)) AS cc
WHERE cc IN ('AO','AR','BG','BK','BM','BO','BP','CB','CE','CF','CG','DO','EC','GV','GY','ID','IZ','KG','KZ','LA','LT','MG','MJ','MK','MV','NH','NP','NS','PK','PP','RI','TI','TN','UZ','WS')
