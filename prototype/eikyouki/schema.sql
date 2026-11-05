PRAGMA foreign_keys=ON;
CREATE TABLE works (
 work_id TEXT PRIMARY KEY, title TEXT NOT NULL, author TEXT, genre TEXT, scope_note TEXT
);
CREATE TABLE editions (
 edition_id TEXT PRIMARY KEY, work_id TEXT NOT NULL REFERENCES works(work_id),
 edition_label TEXT NOT NULL, base_url TEXT NOT NULL, textual_policy TEXT NOT NULL
);
CREATE TABLE chapters (
 chapter_id TEXT PRIMARY KEY, edition_id TEXT NOT NULL REFERENCES editions(edition_id),
 heading TEXT NOT NULL, chapter_url TEXT NOT NULL
);
CREATE TABLE articles (
 article_id TEXT PRIMARY KEY,
 chapter_id TEXT NOT NULL REFERENCES chapters(chapter_id),
 source_order INTEGER NOT NULL,
 original_date TEXT NOT NULL, era TEXT NOT NULL, era_year INTEGER, western_year INTEGER,
 lunar_month INTEGER CHECK(lunar_month BETWEEN 1 AND 12 OR lunar_month IS NULL),
 lunar_day INTEGER CHECK(lunar_day BETWEEN 1 AND 30 OR lunar_day IS NULL),
 date_precision TEXT NOT NULL CHECK(date_precision IN ('year','month','day','unknown')),
 date_interpretation TEXT NOT NULL, date_kind TEXT NOT NULL,
 historic_calendar TEXT NOT NULL, lunar_is_leap INTEGER NOT NULL CHECK(lunar_is_leap IN (0,1)),
 julian_start TEXT, julian_end TEXT, gregorian_start TEXT, gregorian_end TEXT,
 gregorian_calendar TEXT NOT NULL,
 date_conversion_status TEXT NOT NULL CHECK(date_conversion_status IN ('provisional','verified','unresolved')),
 date_conversion_source_url TEXT, date_conversion_note TEXT,
 research_date_start TEXT, research_date_end TEXT, research_date_basis TEXT,
 summary TEXT NOT NULL, location_in_text TEXT, people_in_text TEXT, short_locator TEXT,
 full_original_text TEXT, editorial_note TEXT, entry_status TEXT NOT NULL,
 UNIQUE(chapter_id,source_order)
);
CREATE INDEX idx_article_chronology ON articles(western_year,lunar_month,lunar_day,source_order);
CREATE INDEX idx_article_chapter_order ON articles(chapter_id,source_order);
-- Articles from other works remain separate. Relationships never merge source articles.
CREATE TABLE article_relationships (
 article_id_a TEXT NOT NULL REFERENCES articles(article_id),
 article_id_b TEXT NOT NULL REFERENCES articles(article_id),
 relation TEXT NOT NULL, evidence_note TEXT,
 PRIMARY KEY(article_id_a,article_id_b,relation),
 CHECK(article_id_a <> article_id_b)
);
