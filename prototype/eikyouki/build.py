"""Build the SQLite prototype from article JSON (Python standard library only)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA = (HERE / "schema.sql").read_text(encoding="utf-8")
DB = HERE / "eikyouki.db"

from tempfile import mkstemp
import os
from validation import CHAPTERS, ARTICLE_FIELDS, validate_data
from integrity import compare_connection


def build_database(data, destination=DB, *, checkpoint=lambda stage: None):
    records = validate_data(data)  # before opening/creating any output
    destination = Path(destination)
    fd, name = mkstemp(prefix=destination.name+".", suffix=".tmp", dir=destination.parent)
    os.close(fd)
    temporary = Path(name)
    con = None
    try:
        con = sqlite3.connect(temporary)
        checkpoint("opened")
        con.executescript(SCHEMA)
        con.execute("INSERT INTO works VALUES (?,?,?,?,?)", (
            "EIKYOUKI", "永享記", "不詳", "軍記物語", "永享の乱・結城合戦等。史料記述を史実認定しない。"
        ))
        con.execute("INSERT INTO editions VALUES (?,?,?,?,?)", (
            "SHISEKI-SHURAN-12-WIKISOURCE", "EIKYOUKI",
            "近藤瓶城編『史籍集覧』第12冊に基づくWikisource入力本文",
            data["metadata"]["base_url"],
            "旧字・異体字を一部変更。全文を校訂・転記していない。",
        ))
        con.executemany(
            "INSERT INTO chapters VALUES (?,?,?,?)",
            [(c, "SHISEKI-SHURAN-12-WIKISOURCE", title, url) for c, title, url in CHAPTERS],
        )
        sql = "INSERT INTO articles (" + ",".join(ARTICLE_FIELDS) + ") VALUES (" + ",".join("?" for _ in ARTICLE_FIELDS) + ")"
        for item in records:
            row = dict(item, article_id=item["id"])
            row["lunar_is_leap"] = None if row["lunar_is_leap"] is None else int(row["lunar_is_leap"])
            con.execute(sql, [row[field] for field in ARTICLE_FIELDS])
            checkpoint("article:"+item["id"])
        compare_connection(records, con)
        checkpoint("validated")
        con.commit()
        checkpoint("committed")
        con.close()
        con = None
        checkpoint("before_replace")
        temporary.replace(destination)
    finally:
        if con is not None:
            con.close()
        temporary.unlink(missing_ok=True)
    return len(records)


def main():
    data = json.loads((HERE / "eikyouki_records.json").read_text(encoding="utf-8"))
    count = build_database(data)
    print(f"Built {DB.name}: {count} provisional articles")


if __name__ == "__main__":
    main()
