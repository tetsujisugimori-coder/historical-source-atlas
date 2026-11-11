"""Read-only comparison of every article field, including normalized affiliations."""
from contextlib import closing
import json
import re
import sqlite3
from validation import ARTICLE_FIELDS, FIELDS, validate_data
from document_structure import supplementary, compare_supplementary


def same_fields(expected, actual, label):
    if len(expected) != len(actual):
        raise ValueError(f"{label}: record count {len(actual)} != {len(expected)}")
    def index(rows):
        result = {}
        for r in rows:
            identifier = r.get("id")
            if type(identifier) is not str or not identifier.strip() or identifier in result:
                raise ValueError(f"{label}: invalid/duplicate id {identifier!r}")
            result[identifier] = r
        return result
    left, right = index(expected), index(actual)
    if left.keys() != right.keys():
        raise ValueError(f"{label}: missing/extra IDs")
    for identifier,r in left.items():
        other = right[identifier]
        if r.keys() != other.keys():
            raise ValueError(f"{label}: {identifier}: missing/extra fields")
        for f,v in r.items():
            if type(v) is not type(other[f]) or v != other[f]:
                raise ValueError(f"{label}: {identifier}: {f}: {other[f]!r} != {v!r} (type/value)")


def compare_connection(records, db):
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("DB integrity_check failed")
    if db.execute("PRAGMA foreign_key_check").fetchall():
        raise ValueError("DB foreign_key_check failed")
    sql = "SELECT " + ",".join("a."+f for f in ARTICLE_FIELDS) + ",e.work_id,c.edition_id,c.heading,c.chapter_url FROM articles a JOIN chapters c ON a.chapter_id=c.chapter_id JOIN editions e ON c.edition_id=e.edition_id JOIN works w ON e.work_id=w.work_id"
    actual = []
    for values in db.execute(sql):
        row = dict(zip(FIELDS,values))
        leap = row["lunar_is_leap"]
        # The sole permitted type normalization: SQLite INTEGER 0/1 -> JSON boolean.
        if leap is not None:
            if type(leap) is not int or leap not in (0,1):
                raise ValueError(f"DB: {row['id']}: invalid lunar_is_leap")
            row["lunar_is_leap"] = bool(leap)
        actual.append(row)
    if db.execute("SELECT COUNT(*) FROM articles").fetchone()[0] != len(actual):
        raise ValueError("DB: unjoinable articles")
    same_fields(records, actual, "DB")


def verify(data_path, html_path, db_path):
    data = json.loads(data_path.read_text(encoding="utf-8"))
    records = validate_data(data)
    match = re.search(r'<script id="payload" type="application/json">(.*?)</script>', html_path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError("HTML: missing payload")
    same_fields(records, json.loads(match.group(1)), "HTML")
    provenance = re.search(r'<script id="provenance" type="application/json">(.*?)</script>',html_path.read_text(encoding='utf8'),re.S)
    if provenance is None or json.loads(provenance[1]) != supplementary(data):
        raise ValueError('HTML: provenance/relationships mismatch')
    # mode=ro prevents creating a missing DB or changing/rebuilding a corrupt DB.
    with closing(sqlite3.connect(db_path.resolve().as_uri()+"?mode=ro", uri=True)) as db:
        compare_connection(records, db)
        compare_supplementary(data, db)
        actual = [dict(zip(['article_id_a','article_id_b','relation','evidence_note'],row)) for row in db.execute('SELECT * FROM article_relationships')]
        expected=data.get('article_relationships',[])
        if sorted(actual,key=lambda x:sorted(x.items())) != sorted(expected,key=lambda x:sorted(x.items())):
            raise ValueError('DB: relationships mismatch')
    return len(records)
