"""First Hojo batch: preservation, source-state, person-link and DB negative controls."""
import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from build import build, validate, read_json, DATA, PERSONS, EIK, HERE

class FirstBatch(unittest.TestCase):
    def setUp(self):
        self.h=read_json(DATA)
        self.p=read_json(PERSONS)
        self.e=read_json(EIK/"eikyouki_records.json")
    def test_exact_five_and_preserved_192(self):
        a,b=validate(self.h,self.e,self.p)
        self.assertEqual(len(a),192)
        self.assertEqual(len(b),5)
        self.assertEqual(len(set(x["id"] for x in a+b)),197)
        self.assertTrue(all(x["full_original_text"] is None for x in b))
    def test_catalog_and_static_view(self):
        c=read_json(HERE.parent/"works.json")
        self.assertEqual([(v["work_id"],v["article_count"]) for v in c["works"]],[("EIKYOUKI",192),("HOJO-GODAIKI",5)])
        html=(HERE/"index.html").read_text(encoding="utf-8")
        for r in self.h["records"]:
            self.assertIn('id="'+r["id"]+'"',html)
            self.assertIn(r["chapter"],html)
            self.assertIn(r["summary"],html)
        self.assertIn("../index.html?ref=EK-0184#EK-0184",html)
        self.assertNotIn("<script",html)
    def test_sqlite_round_trip_all_197_articles(self):
        with tempfile.TemporaryDirectory() as d:
            path=build(Path(d)/"multi.db")
            with sqlite3.connect(path) as con:
                con.row_factory=sqlite3.Row
                rows=[dict(x) for x in con.execute("SELECT * FROM articles ORDER BY CASE WHEN article_id LIKE 'EK-%' THEN 0 ELSE 1 END, article_id")]
                self.assertEqual(len(rows),197)
                for expected,actual in zip(self.e["records"]+self.h["records"],rows):
                    for k,v in expected.items():
                        if k in ("work_id","edition_id","chapter","source_url"):
                            continue  # normalized into works/editions/chapters or retained in immutable JSON
                        got=actual["article_id"] if k=="id" else actual[k]
                        if k=="lunar_is_leap" and v is not None:v=int(v)
                        self.assertEqual(got,v,(expected["id"],k))
                self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(),[])
                self.assertEqual(con.execute("SELECT COUNT(*) FROM person_mentions").fetchone()[0],len(self.p["mentions"]))
                self.assertEqual([x[0] for x in con.execute("SELECT article_id FROM person_mentions WHERE article_id LIKE 'HG-%' ORDER BY article_id")],["HG-0001","HG-0002"])
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
        for h,p in cases:
            with self.subTest(reason=str((h["records"][0]["id"],p["people"][0]["historical_identity"]))):
                with self.assertRaises(ValueError):
                    validate(h,self.e,p)

if __name__=="__main__":unittest.main()
