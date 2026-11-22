"""Batch 17 fixed transcription and preservation checks."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import unittest
from integrity import same_fields, verify

PROTOTYPE=Path(__file__).resolve().parent
ROOT=PROTOTYPE.parents[1]
BASE="e37eff567edab0d0b864776997dc7c5e5d6b5414"
RECORDS="prototype/eikyouki/eikyouki_records.json"
SOURCE="evidence/batch08/source/wikisource-fixed.html"
SOURCE_SHA="cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0"
CHAPTER_SHA="28a952843c517b75d7ebb03abad77fdbdf98b3a5a40d8132cc73d4dd3430a9fe"
BOUNDS=(8,100,163,227,453,552,598,725,791)
IDS=[f"EK-{n:04d}" for n in range(168,176)]

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts=[]
    def handle_data(self,data):
        self.parts.append(data)

class Batch17(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/RECORDS).read_text(encoding="utf-8"))
        cls.rows=cls.data["records"][167:175]
        cls.ledger=json.loads((ROOT/"evidence/batch17/article-boundaries.json").read_text(encoding="utf-8"))
        cls.chapter=(ROOT/"evidence/batch17/source/chapter.txt").read_text(encoding="utf-8")
    def test_existing_167_preserved_and_generated_formats(self):
        baseline=json.loads(subprocess.check_output(["git","show",BASE+":"+RECORDS],cwd=ROOT))
        self.assertEqual(len(baseline["records"]),167)
        same_fields(baseline["records"],self.data["records"][:167],"existing 167 articles")
        self.assertEqual(set(baseline),set(self.data))
        for key in baseline.keys()-{"records","publication"}:
            self.assertEqual(json.dumps(baseline[key]),json.dumps(self.data[key]),key)
        self.assertEqual(set(baseline["publication"]),set(self.data["publication"]))
        for key,old in baseline["publication"].items():
            current=self.data["publication"][key]
            if key=="articles":
                current={i:pub for i,pub in current.items() if i in old}
            self.assertEqual(json.dumps(old,sort_keys=True),json.dumps(current,sort_keys=True),key)
        self.assertEqual(verify(ROOT/RECORDS,PROTOTYPE/"index.html",PROTOTYPE/"eikyouki.db"),len(self.data["records"]))
    def test_fixed_source_exact_boundaries_and_annotation(self):
        raw=(ROOT/SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),SOURCE_SHA)
        self.assertEqual(self.ledger["source_sha256"],SOURCE_SHA)
        self.assertEqual(self.ledger["base_main"],BASE)
        html=raw.decode("utf-8")
        start=html.index('<span class="anchor" id="ei-17">')
        end=html.index('<span class="anchor" id="ei-18">',start)
        parser=Text()
        parser.feed(html[start:end])
        fixed="".join(parser.parts).replace("\u200b","").replace("\xa0","").strip()
        self.assertEqual(self.chapter,fixed)
        self.assertEqual(hashlib.sha256(self.chapter.encode()).hexdigest(),CHAPTER_SHA)
        self.assertEqual(self.ledger["chapter_sha256"],CHAPTER_SHA)
        self.assertEqual(self.chapter[:8],"山内扇谷不和之事")
        self.assertEqual(len(self.chapter),791)
        self.assertEqual(self.ledger["article_count"],8)
        self.assertEqual([r["id"] for r in self.rows],IDS)
        self.assertEqual([a["id"] for a in self.ledger["articles"]],IDS)
        self.assertEqual("".join(r["full_original_text"] for r in self.rows),self.chapter[8:])
        for idx,(row,item,a,b) in enumerate(zip(self.rows,self.ledger["articles"],BOUNDS,BOUNDS[1:])):
            with self.subTest(id=row["id"]):
                self.assertEqual((row["source_order"],row["chapter_id"]),(168+idx,"yamanouchi_ogigayatsu_discord"))
                self.assertTrue(row["source_url"].endswith("#ei-17"))
                self.assertEqual((item["start_offset"],item["end_offset"]),(a,b))
                self.assertEqual(row["full_original_text"],self.chapter[a:b])
                self.assertEqual(item["source_text"],self.chapter[a:b])
                self.assertEqual(item["layers"],{
                    "SOURCE_STATEMENT":row["full_original_text"],
                    "MODERN_SUMMARY":row["summary"],
                    "HISTORICAL_RECOGNITION":"NOT_TESTED"})
                pub=self.data["publication"]["articles"][row["id"]]
                self.assertEqual(pub["annotations"],item["annotations"])
                self.assertEqual(pub["narrative_text"],item["narrative_text"])
                self.assertIn("東乱記",pub["annotation_note"])
                for k in ("base_image","variants","transcription_emendation","historical_recognition"):
                    self.assertEqual(pub[k],"NOT_TESTED")
        marker="【 NDLJP:385】"
        self.assertEqual(self.chapter[779:791],marker)
        self.assertEqual(self.ledger["articles"][-1]["annotations"],[{
            "kind":"page_marker","text":marker,"start_offset":779,"end_offset":791}])
        self.assertNotIn(marker,self.ledger["articles"][-1]["narrative_text"])
    def test_year_and_date_not_propagated(self):
        self.assertEqual((self.rows[0]["original_date"],self.rows[0]["era"],self.rows[0]["era_year"],self.rows[0]["western_year"],self.rows[0]["date_precision"]),
                         ("長亨元年〈丁未〉","長享",1,1487,"year"))
        self.assertEqual((self.rows[5]["original_date"],self.rows[5]["era"],self.rows[5]["era_year"],self.rows[5]["western_year"],self.rows[5]["lunar_month"],self.rows[5]["lunar_day"],self.rows[5]["date_precision"]),
                         ("長亨二年戊申二月五日","長享",2,1488,2,5,"day"))
        for i,row in enumerate(self.rows):
            with self.subTest(id=row["id"]):
                if i not in (0,5):
                    self.assertEqual((row["original_date"],row["western_year"],row["date_precision"],row["lunar_is_leap"]),("記載なし",None,"unknown",None))
                self.assertEqual(row["date_conversion_status"],"unresolved")
                for f in ("julian_start","julian_end","gregorian_start","gregorian_end","research_date_start","research_date_end","research_date_basis"):
                    self.assertIsNone(row[f])

if __name__=="__main__":
    unittest.main()
