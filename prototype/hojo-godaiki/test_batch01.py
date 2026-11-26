"""Hojo intake: preservation, source-state, person-link and SQLite checks."""
import copy
import json
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from build import build, validate, read_json, DATA, PERSONS, EIK, HERE

class HojoIntake(unittest.TestCase):
    def setUp(self):
        self.h=read_json(DATA)
        self.p=read_json(PERSONS)
        self.e=read_json(EIK/"eikyouki_records.json")
    def test_ordered_articles_and_preserved_192(self):
        a,b=validate(self.h,self.e,self.p)
        self.assertEqual(len(a),192)
        self.assertEqual(len(b),12)
        self.assertEqual(len(set(x["id"] for x in a+b)),204)
        self.assertTrue(all(x["full_original_text"] is None for x in b))
    def test_catalog_and_static_view(self):
        c=read_json(HERE.parent/"works.json")
        self.assertEqual([(v["work_id"],v["article_count"]) for v in c["works"]],[("EIKYOUKI",192),("HOJO-GODAIKI",12)])
        html=(HERE/"index.html").read_text(encoding="utf-8")
        cards = re.findall(r'<article id="([^"]+)">(.*?)</article>', html, re.DOTALL)
        self.assertEqual([article_id for article_id, _ in cards], [r["id"] for r in self.h["records"]])
        for (_, card), r in zip(cards, self.h["records"]):
            self.assertIn(r["chapter"], card)
            self.assertIn(r["summary"], card)
            self.assertIn(r["source_url"].replace("&", "&amp;"), card)
        self.assertIn("../index.html?ref=EK-0184#EK-0184",html)
        self.assertNotIn("<script",html)
        self.assertIn("指定2箇所のみ画像照合済み、全文未照合", html)
        self.assertIn("EDITORIAL_CORRESPONDENCE_PROVISIONAL", json.dumps(self.p,ensure_ascii=False))
        sources = (self.h["metadata"], self.h["metadata"]["additional_volumes"]["巻第二"])
        for source in sources:
            self.assertIn(source["base_url"].replace("&", "&amp;"), html)

    def test_sqlite_round_trip_all_204_articles(self):
        with tempfile.TemporaryDirectory() as d:
            path=build(Path(d)/"multi.db")
            with sqlite3.connect(path) as con:
                con.row_factory=sqlite3.Row
                rows=[dict(x) for x in con.execute("SELECT * FROM articles ORDER BY CASE WHEN article_id LIKE 'EK-%' THEN 0 ELSE 1 END, article_id")]
                self.assertEqual(len(rows),204)
                for expected,actual in zip(self.e["records"]+self.h["records"],rows):
                    for k,v in expected.items():
                        if k in ("work_id","edition_id","chapter","source_url"):
                            continue  # normalized into works/editions/chapters or retained in immutable JSON
                        got=actual["article_id"] if k=="id" else actual[k]
                        if k=="lunar_is_leap" and v is not None:v=int(v)
                        self.assertEqual(got,v,(expected["id"],k))
                self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(),[])
                stored_urls=dict(con.execute("SELECT article_id,source_url FROM article_source_urls"))
                expected_urls={r["id"]:r["source_url"] for r in self.e["records"]+self.h["records"]}
                self.assertEqual(len(stored_urls),204)
                self.assertEqual(stored_urls,expected_urls)
                chapter_rows = con.execute("""
                    SELECT a.article_id, c.heading, c.edition_id, e.work_id
                    FROM articles a JOIN chapters c USING (chapter_id)
                    JOIN editions e USING (edition_id)
                """)
                self.assertEqual(
                    {row[0]: tuple(row)[1:] for row in chapter_rows},
                    {r["id"]: (r["chapter"], r["edition_id"], r["work_id"])
                     for r in self.e["records"] + self.h["records"]},
                )
                stored_evidence=dict(con.execute("SELECT mention_id,evidence_url FROM person_mentions"))
                self.assertEqual(stored_evidence,{m["mention_id"]:m["evidence_url"] for m in self.p["mentions"]})
                self.assertEqual(con.execute("SELECT COUNT(*) FROM person_mentions").fetchone()[0],len(self.p["mentions"]))
                self.assertEqual([x[0] for x in con.execute("SELECT article_id FROM person_mentions WHERE article_id LIKE 'HG-%' ORDER BY article_id")],["HG-0001","HG-0002"])
    def test_ndl_spelling_negative_controls(self):
        persons = copy.deepcopy(self.p)
        persons["mentions"][1]["surface_form"] = "伊勢新九郎氏茂"
        with self.assertRaisesRegex(ValueError, "spelling does not match the NDL image"):
            validate(self.h, self.e, persons)

        hojo = copy.deepcopy(self.h)
        article = hojo["records"][1]
        article["people_in_text"] = article["people_in_text"].replace("九郡", "九郎")
        with self.assertRaisesRegex(ValueError, "spelling missing from article"):
            validate(hojo, self.e, self.p)
        with self.assertRaisesRegex(ValueError, "spelling does not match the NDL image"):
            validate(hojo, self.e, persons)

        persons = copy.deepcopy(self.p)
        first, second = persons["mentions"][:2]
        first["evidence_url"], second["evidence_url"] = second["evidence_url"], first["evidence_url"]
        with self.assertRaisesRegex(ValueError, "mismatched NDL image evidence"):
            validate(self.h, self.e, persons)

    def test_negative_controls(self):
        cases=[]
        h=copy.deepcopy(self.h);h["records"][0]["id"]="EK-0184";cases.append((h,self.p))
        h=copy.deepcopy(self.h);h["records"][0]["western_year"]=1492;cases.append((h,self.p))
        h=copy.deepcopy(self.h);h["records"][2]["full_original_text"]="uncertified";cases.append((h,self.p))
        h=copy.deepcopy(self.h);h["metadata"]["historical_recognition"]="VERIFIED";cases.append((h,self.p))
        h=copy.deepcopy(self.h);h["metadata"]["revision_id"]=None;cases.append((h,self.p))
        p=copy.deepcopy(self.p);p["mentions"][0]["article_id"]="HG-9999";cases.append((self.h,p))
        p=copy.deepcopy(self.p);p["mentions"].append(p["mentions"][0]);cases.append((self.h,p))
        p=copy.deepcopy(self.p);p["mentions"][2]["surface_form"]="nonexistent";cases.append((self.h,p))
        p=copy.deepcopy(self.p);p["people"][0]["historical_identity"]="VERIFIED";cases.append((self.h,p))
        p=copy.deepcopy(self.p);p["mentions"][0]["evidence_url"]=None;cases.append((self.h,p))
        p=copy.deepcopy(self.p);p["mentions"][1]["evidence_url"]=p["mentions"][0]["evidence_url"];cases.append((self.h,p))
        p=copy.deepcopy(self.p);p["mentions"][2]["evidence_url"]="https://invalid.example/source";cases.append((self.h,p))
        p=copy.deepcopy(self.p);p["mentions"][2].pop("evidence_scope");cases.append((self.h,p))
        h=copy.deepcopy(self.h);h["records"][0]["source_url"]=h["records"][1]["source_url"];cases.append((h,self.p))
        h=copy.deepcopy(self.h);h["metadata"]["base_url"]="https://ja.wikisource.org/wiki/北条五代記/巻第一";cases.append((h,self.p))
        for h,p in cases:
            with self.subTest(reason=str((h["records"][0]["id"],p["people"][0]["historical_identity"]))):
                with self.assertRaises(ValueError):
                    validate(h,self.e,p)

    def test_second_volume_negative_controls(self):
        data = copy.deepcopy(self.h)
        data["records"][5]["source_url"] = data["records"][0]["source_url"]
        with self.assertRaisesRegex(ValueError, "wrong chapter navigation anchor"):
            validate(data, self.e, self.p)

        data = copy.deepcopy(self.h)
        data["metadata"]["additional_volumes"]["巻第二"]["revision_id"] = 217784
        with self.assertRaisesRegex(ValueError, "fixed revision provenance required"):
            validate(data, self.e, self.p)

        data = copy.deepcopy(self.h)
        data["records"].pop()
        with self.assertRaisesRegex(ValueError, "ordered, non-colliding HG article IDs required"):
            validate(data, self.e, self.p)

if __name__=="__main__":unittest.main()
