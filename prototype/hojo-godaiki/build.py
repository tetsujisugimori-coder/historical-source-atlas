"""Build a separate multi-work SQLite snapshot without editing the Eikyouki files."""
from __future__ import annotations
import json
import os
import sqlite3
from pathlib import Path
from urllib.parse import unquote
from tempfile import mkstemp

HERE = Path(__file__).resolve().parent
EIK = HERE.parent / "eikyouki"
DATA = HERE / "hojo_godaiki_records.json"
PERSONS = HERE / "person_links.json"
DB = HERE / "hojo_godaiki.db"
SCHEMA = (EIK / "schema.sql").read_text(encoding="utf-8")
WIKISOURCE = "https://ja.wikisource.org"
VOLUMES = (
    (1, "巻第一", "一", "一二三四五", 217784),
    (2, "巻第二", "二", "一二三四五六七", 214082),
)
# Only these two spellings were checked against the printed pages.
NDL_SPELLINGS = {
    "HG-0001": ("いせ新九郎氏茂", "R0000441"),  # p. 843
    "HG-0002": ("伊勢新九郡氏茂", "R0000447"),  # p. 854
}

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate(hojo, eik, persons):
    old, new = eik["records"], hojo["records"]
    if len(old) != 192 or [r["id"] for r in old] != [f"EK-{i:04d}" for i in range(1,193)]:
        raise ValueError("Eikyouki baseline must be 192 ordered articles")
    metadata = hojo["metadata"]
    additional_volumes = metadata.get("additional_volumes", {})
    if additional_volumes.keys() not in (set(), {"巻第二"}):
        raise ValueError("unexpected Hojo volumes")
    sections = []
    for number, volume, ordinal, section_ordinals, revision in VOLUMES:
        if number == 1:
            source = metadata
        elif volume in additional_volumes:
            source = additional_volumes[volume]
        else:
            continue
        title = f"北条五代記/{volume}"
        fixed_url = f"{WIKISOURCE}/w/index.php?oldid={revision}&title={title}"
        if source["revision_id"] != revision or source["base_url"] != fixed_url:
            raise ValueError("fixed revision provenance required")
        if any(source[key] != "NOT_TESTED" for key in
               ("transcription_check", "base_image_check", "variant_check", "historical_recognition")):
            raise ValueError("verification escalation")
        for section_number, section in enumerate(section_ordinals, 1):
            chapter_id = f"HG-V{number}-{section_number:02d}"
            source_url = f"{WIKISOURCE}/wiki/{title}#{ordinal}-{section}"
            sections.append((chapter_id, source_url))
    if [r["id"] for r in new] != [f"HG-{i:04d}" for i in range(1, len(sections) + 1)]:
        raise ValueError("ordered, non-colliding HG article IDs required")
    expected_fields = set(old[0])
    for i, (r, (chapter_id, source_url)) in enumerate(zip(new, sections), 1):
        if set(r) != expected_fields or r["source_order"] != i or r["work_id"] != "HOJO-GODAIKI":
            raise ValueError("schema, order or work mismatch")
        if r["edition_id"] != "HAKUBUNKAN-1899-WIKISOURCE" or r["chapter_id"] != chapter_id:
            raise ValueError("edition or chapter")
        page, marker, anchor = r["source_url"].partition("#")
        if page + marker + unquote(anchor) != source_url:
            raise ValueError("wrong chapter navigation anchor")
        if r["full_original_text"] is not None or r["date_precision"] != "unknown":
            raise ValueError("uncertified original text/date")
        if r["date_conversion_status"] != "unresolved" or any(r[f] is not None for f in
            ("western_year","era","era_year","lunar_month","lunar_day","lunar_is_leap","julian_start","julian_end","gregorian_start","gregorian_end","research_date_start","research_date_end")):
            raise ValueError("date propagation")
    identities = persons["people"]
    if len(identities) != 1 or identities[0]["identity_status"] != "EDITORIAL_CORRESPONDENCE_PROVISIONAL" or identities[0]["historical_identity"] != "NOT_TESTED":
        raise ValueError("identity status")
    by_id = {r["id"]:r for r in old+new}
    mids = set()
    checked_ndl_articles = set()
    for m in persons["mentions"]:
        if m["mention_id"] in mids or m["article_id"] not in by_id or m["person_id"] != identities[0]["person_id"]:
            raise ValueError("duplicate/dangling person mention")
        mids.add(m["mention_id"])
        if m["article_id"].startswith("EK-"):
            if m["verification"] != "FIXED_TRANSCRIPTION_MENTION" or m["surface_form"] not in (by_id[m["article_id"]]["full_original_text"] or ""):
                raise ValueError("Eikyouki mention not grounded in exact source")
        elif m["verification"] != "PROVISIONAL_HEADER_SECTION_READING":
            raise ValueError("unverified Hojo source marked as fixed")
        if m["article_id"].startswith("HG-"):
            article_id = m["article_id"]
            if article_id not in NDL_SPELLINGS or article_id in checked_ndl_articles:
                raise ValueError("unexpected or duplicate NDL spelling mention")
            spelling, image_id = NDL_SPELLINGS[article_id]
            image_url = f"https://dl.ndl.go.jp/api/iiif/1882605/{image_id}/full/full/0/default.jpg"
            if m.get("evidence_url") != image_url or m.get("evidence_scope") != "NDL_IMAGE_SURFACE_ONLY":
                raise ValueError("unverified or mismatched NDL image evidence")
            if m.get("surface_form") != spelling:
                raise ValueError("person spelling does not match the NDL image")
            article_people = by_id[article_id]["people_in_text"] or ""
            if spelling not in article_people.split("・"):
                raise ValueError("NDL spelling missing from article people")
            checked_ndl_articles.add(article_id)
        elif m.get("evidence_url") != by_id[m["article_id"]]["source_url"] or m.get("evidence_scope") != "FIXED_TRANSCRIPTION_CHAPTER_AND_ARTICLE_TEXT":
            raise ValueError("Eikyouki mention evidence not matching fixed article URL")
    if checked_ndl_articles != NDL_SPELLINGS.keys():
        raise ValueError("both NDL spelling mentions are required")
    return old, new

def build(destination=DB, hojo=None, persons=None):
    hojo = read_json(DATA) if hojo is None else hojo
    persons = read_json(PERSONS) if persons is None else persons
    eik = read_json(EIK / "eikyouki_records.json")
    old, new = validate(hojo, eik, persons)
    destination = Path(destination)
    fd, temp_name = mkstemp(prefix=destination.name+".",suffix=".tmp",dir=destination.parent)
    os.close(fd)
    temp=Path(temp_name)
    con=None
    try:
        con = sqlite3.connect(temp)
        con.executescript(SCHEMA)
        con.execute("INSERT INTO works VALUES (?,?,?,?,?)",("EIKYOUKI","永享記","不詳","軍記物語","既存192記事・原文と付随情報は元JSONを参照"))
        con.execute("INSERT INTO works VALUES (?,?,?,?,?)",("HOJO-GODAIKI","北条五代記","三浦茂正（三浦浄心）","仮名草子",f"{len(new)}節、全文未収録、史実未認定"))
        con.execute("INSERT INTO editions VALUES (?,?,?,?,?)",("SHISEKI-SHURAN-12-WIKISOURCE","EIKYOUKI",eik["metadata"]["edition"],eik["metadata"]["base_url"],eik["metadata"]["transcription_note"]))
        con.execute("INSERT INTO editions VALUES (?,?,?,?,?)",("HAKUBUNKAN-1899-WIKISOURCE","HOJO-GODAIKI",hojo["metadata"]["edition"],hojo["metadata"]["base_url"],hojo["metadata"]["transcription_policy"]))
        chapters = {}
        for r in old+new:
            cid=r["chapter_id"]
            row=(cid,r["edition_id"],r["chapter"],r["source_url"].split("#")[0])
            if cid in chapters and chapters[cid][:3] != row[:3]:
                raise ValueError("chapter collision: "+cid)
            chapters[cid]=row
        con.executemany("INSERT INTO chapters VALUES (?,?,?,?)",chapters.values())
        fields=[x[1] for x in con.execute("PRAGMA table_info(articles)")]
        if set(fields) != (set(old[0]) - {"id","work_id","edition_id","chapter","source_url"} | {"article_id"}):
            raise ValueError("underlying 36-field schema mismatch")
        sql = "INSERT INTO articles ("+",".join(fields)+") VALUES ("+",".join("?" for _ in fields)+")"
        for r in old+new:
            row={**r,"article_id":r["id"]}
            if row["lunar_is_leap"] is not None: row["lunar_is_leap"]=int(row["lunar_is_leap"])
            con.execute(sql,[row[f] for f in fields])
        # Store one exact URL per article, rather than reconstructing it from the
        # chapter URL (which discards individual fragments and mixed work bases).
        con.executescript("""CREATE TABLE article_source_urls (
          article_id TEXT PRIMARY KEY REFERENCES articles(article_id),
          source_url TEXT NOT NULL CHECK(substr(source_url,1,8)='https://')
        ) STRICT;""")
        con.executemany(
            "INSERT INTO article_source_urls (article_id, source_url) VALUES (?,?)",
            [(r["id"], r["source_url"]) for r in old+new]
        )
        con.executescript("""CREATE TABLE persons (
          person_id TEXT PRIMARY KEY, display_label TEXT NOT NULL,
          identity_status TEXT NOT NULL CHECK(identity_status='EDITORIAL_CORRESPONDENCE_PROVISIONAL'),
          historical_identity TEXT NOT NULL CHECK(historical_identity='NOT_TESTED'),
          payload TEXT NOT NULL CHECK(json_valid(payload))) STRICT;
          CREATE TABLE person_mentions (
          mention_id TEXT PRIMARY KEY, person_id TEXT NOT NULL REFERENCES persons(person_id),
          article_id TEXT NOT NULL REFERENCES articles(article_id), surface_form TEXT NOT NULL,
          verification TEXT NOT NULL, evidence_url TEXT NOT NULL CHECK(substr(evidence_url,1,8)='https://'),
          payload TEXT NOT NULL CHECK(json_valid(payload))) STRICT;""")
        for p in persons["people"]:
            con.execute("INSERT INTO persons VALUES (?,?,?,?,?)",(p["person_id"],p["display_label"],p["identity_status"],p["historical_identity"],json.dumps(p,ensure_ascii=False)))
        for m in persons["mentions"]:
            con.execute("INSERT INTO person_mentions VALUES (?,?,?,?,?,?,?)",(m["mention_id"],m["person_id"],m["article_id"],m["surface_form"],m["verification"],m["evidence_url"],json.dumps(m,ensure_ascii=False)))
        con.commit()
        if con.execute("PRAGMA foreign_key_check").fetchall(): raise ValueError("broken SQLite links")
        total = len(old) + len(new)
        if con.execute("SELECT COUNT(*) FROM articles").fetchone()[0] != total:
            raise ValueError(f"{total} records expected")
        if con.execute("SELECT COUNT(*) FROM article_source_urls").fetchone()[0] != total:
            raise ValueError(f"{total} individual source URLs expected")
        con.close();con=None
        temp.replace(destination)
    finally:
        if con is not None:con.close()
        temp.unlink(missing_ok=True)
    return destination

if __name__=="__main__":
    hojo = read_json(DATA)
    path = build(hojo=hojo)
    print(f"Created {path.name}: 192 preserved EK records + {len(hojo['records'])} HG records")
