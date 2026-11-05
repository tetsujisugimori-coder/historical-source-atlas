"""Build the SQLite prototype from article JSON (Python standard library only)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "eikyouki_records.json").read_text(encoding="utf-8"))
RECORDS = DATA["records"]
SCHEMA = (HERE / "schema.sql").read_text(encoding="utf-8")
DB = HERE / "eikyouki.db"

CHAPTERS = [
    ("intro", "序章", "https://ja.wikisource.org/wiki/永享記#永享記"),
    ("kufu", "公方管領不和の事", "https://ja.wikisource.org/wiki/永享記#公方管領不和の事"),
    ("miura", "三浦介逆心事", "https://ja.wikisource.org/wiki/永享記#三浦介逆心事"),
    ("hakone", "箱根早川尻合戦の事", "https://ja.wikisource.org/wiki/永享記#箱根早川尻合戦の事"),
]
ARTICLE_FIELDS = [
    "article_id", "chapter_id", "source_order", "original_date", "era", "era_year",
    "western_year", "lunar_month", "lunar_day", "date_precision", "date_interpretation",
    "date_kind", "historic_calendar", "lunar_is_leap", "julian_start", "julian_end",
    "gregorian_start", "gregorian_end", "gregorian_calendar", "date_conversion_status",
    "date_conversion_source_url", "date_conversion_note", "research_date_start",
    "research_date_end", "research_date_basis", "summary", "location_in_text",
    "people_in_text", "short_locator", "full_original_text", "editorial_note", "entry_status",
]


def main() -> None:
    # Build into a new file: never overwrite a previous database until complete.
    temporary = HERE / "eikyouki.db.tmp"
    if temporary.exists():
        temporary.unlink()
    con = sqlite3.connect(temporary)
    try:
        con.executescript(SCHEMA)
        con.execute("INSERT INTO works VALUES (?,?,?,?,?)", (
            "EIKYOUKI", "永享記", "不詳", "軍記物語", "永享の乱・結城合戦等。史料記述を史実認定しない。"
        ))
        con.execute("INSERT INTO editions VALUES (?,?,?,?,?)", (
            "SHISEKI-SHURAN-12-WIKISOURCE", "EIKYOUKI",
            "近藤瓶城編『史籍集覧』第12冊に基づくWikisource入力本文",
            DATA["metadata"]["base_url"],
            "旧字・異体字を一部変更。全文を校訂・転記していない。",
        ))
        con.executemany(
            "INSERT INTO chapters VALUES (?,?,?,?)",
            [(c, "SHISEKI-SHURAN-12-WIKISOURCE", title, url) for c, title, url in CHAPTERS],
        )
        sql = "INSERT INTO articles (" + ",".join(ARTICLE_FIELDS) + ") VALUES (" + ",".join("?" for _ in ARTICLE_FIELDS) + ")"
        for item in RECORDS:
            row = dict(item, article_id=item["id"])
            row["lunar_is_leap"] = int(row["lunar_is_leap"])
            con.execute(sql, [row[field] for field in ARTICLE_FIELDS])
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []
        assert con.execute("SELECT COUNT(*) FROM articles").fetchone()[0] == len(RECORDS)
        con.commit()
    except BaseException:
        con.close()
        temporary.unlink(missing_ok=True)
        raise
    else:
        con.close()
        temporary.replace(DB)
    print(f"Built {DB.name}: {len(RECORDS)} provisional articles")


if __name__ == "__main__":
    main()