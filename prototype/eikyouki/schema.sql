PRAGMA foreign_keys=ON;
CREATE TABLE works (
 work_id ANY PRIMARY KEY NOT NULL CHECK(typeof(work_id)='text' AND instr(work_id,char(0))=0 AND length(work_id)>0 AND work_id NOT GLOB '*[^A-Za-z0-9_-]*' AND substr(work_id,1,1) GLOB '[A-Za-z0-9]'), title TEXT NOT NULL, author TEXT, genre TEXT, scope_note TEXT
) STRICT;
CREATE TABLE editions (
 edition_id ANY PRIMARY KEY NOT NULL CHECK(typeof(edition_id)='text' AND instr(edition_id,char(0))=0 AND length(edition_id)>0 AND edition_id NOT GLOB '*[^A-Za-z0-9_-]*' AND substr(edition_id,1,1) GLOB '[A-Za-z0-9]'), work_id TEXT NOT NULL REFERENCES works(work_id),
 edition_label TEXT NOT NULL, base_url TEXT NOT NULL, textual_policy TEXT NOT NULL
) STRICT;
CREATE TABLE chapters (
 chapter_id ANY PRIMARY KEY NOT NULL CHECK(typeof(chapter_id)='text' AND instr(chapter_id,char(0))=0 AND length(chapter_id)>0 AND chapter_id NOT GLOB '*[^A-Za-z0-9_-]*' AND substr(chapter_id,1,1) GLOB '[A-Za-z0-9]'), edition_id TEXT NOT NULL REFERENCES editions(edition_id),
 heading TEXT NOT NULL, chapter_url TEXT NOT NULL
) STRICT;
CREATE TABLE articles (
 article_id ANY PRIMARY KEY NOT NULL CHECK(typeof(article_id)='text' AND instr(article_id,char(0))=0 AND length(article_id)>0 AND article_id NOT GLOB '*[^A-Za-z0-9_-]*' AND substr(article_id,1,1) GLOB '[A-Za-z0-9]'),
 chapter_id TEXT NOT NULL REFERENCES chapters(chapter_id),
 source_order INTEGER NOT NULL CHECK(typeof(source_order)='integer' AND source_order>0),
 original_date TEXT NOT NULL, era TEXT, era_year INTEGER, western_year INTEGER,
 lunar_month INTEGER CHECK(lunar_month BETWEEN 1 AND 12 OR lunar_month IS NULL),
 lunar_day INTEGER CHECK(lunar_day BETWEEN 1 AND 30 OR lunar_day IS NULL),
 date_precision TEXT NOT NULL CHECK(date_precision IN ('year','month','day','unknown')),
 date_interpretation TEXT NOT NULL, date_kind TEXT NOT NULL,
 historic_calendar TEXT NOT NULL, lunar_is_leap INTEGER CHECK(lunar_is_leap IS NULL OR (typeof(lunar_is_leap)='integer' AND lunar_is_leap IN (0,1))),
 julian_start TEXT, julian_end TEXT, gregorian_start TEXT, gregorian_end TEXT,
 gregorian_calendar TEXT NOT NULL,
 date_conversion_status TEXT NOT NULL CHECK(date_conversion_status IN ('provisional','verified','unresolved')),
 date_conversion_source_url TEXT, date_conversion_note TEXT,
 research_date_start TEXT, research_date_end TEXT, research_date_basis TEXT,
 summary TEXT NOT NULL, location_in_text TEXT, people_in_text TEXT, short_locator TEXT,
 full_original_text TEXT, editorial_note TEXT, entry_status TEXT NOT NULL,
 UNIQUE(chapter_id,source_order)
) STRICT;
CREATE INDEX idx_article_chronology ON articles(western_year,lunar_month,lunar_day,source_order);
CREATE INDEX idx_article_chapter_order ON articles(chapter_id,source_order);
-- Articles from other works remain separate. Relationships never merge source articles.
CREATE TABLE article_relationships (
 article_id_a TEXT NOT NULL REFERENCES articles(article_id),
 article_id_b TEXT NOT NULL REFERENCES articles(article_id),
 relation TEXT NOT NULL, evidence_note TEXT,
 PRIMARY KEY(article_id_a,article_id_b,relation),
 CHECK(article_id_a <> article_id_b)
) STRICT;
