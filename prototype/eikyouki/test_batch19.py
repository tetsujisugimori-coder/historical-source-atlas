"""Batch 19 fixed transcription, article boundaries, date scope and preservation."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import unittest

from integrity import same_fields, verify

PROTOTYPE = Path(__file__).resolve().parent
ROOT = PROTOTYPE.parents[1]
BASE = "a21b9bf39a82a00de75e1482a9689fd951bbf382"
RECORDS = "prototype/eikyouki/eikyouki_records.json"
SOURCE = "evidence/batch08/source/wikisource-fixed.html"
SOURCE_SHA = "cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0"
CHAPTER_SHA = "63887d1cef571c4676bcee662465d418e2ebbb79d15c1e4e021fab678e6e7059"
BOUNDS = (6, 68, 248, 442, 505, 523, 720, 853, 936, 1007)
IDS = [f"EK-{n:04d}" for n in range(184, 193)]

class ChapterText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

class Batch19(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / RECORDS).read_text(encoding="utf-8"))
        cls.rows = cls.data["records"][183:192]
        cls.evidence = ROOT / "evidence/batch19"
        cls.chapter = (cls.evidence / "source/chapter.txt").read_text(encoding="utf-8")
        cls.ledger = json.loads((cls.evidence / "article-boundaries.json").read_text(encoding="utf-8"))

    def test_previous_183_articles_and_metadata_preserved(self):
        previous = json.loads(subprocess.check_output(["git", "show", BASE + ":" + RECORDS], cwd=ROOT))
        self.assertEqual(len(previous["records"]), 183)
        same_fields(previous["records"], self.data["records"][:183], "existing 183 articles")
        self.assertEqual(set(previous), set(self.data))
        for key in previous.keys() - {"records", "publication"}:
            self.assertEqual(previous[key], self.data[key], key)
        self.assertEqual(set(previous["publication"]), set(self.data["publication"]))
        for key, value in previous["publication"].items():
            current = self.data["publication"][key]
            if key == "articles":
                self.assertEqual(set(current) - set(value), set(IDS))
                self.assertEqual({old_id: current[old_id] for old_id in value}, value)
            else:
                self.assertEqual(current, value, key)
        self.assertEqual(len(self.data["records"]), 192)
        self.assertEqual(verify(ROOT / RECORDS, PROTOTYPE / "index.html", PROTOTYPE / "eikyouki.db"), 192)

    def test_fixed_source_and_nonoverlapping_boundaries(self):
        raw = (ROOT / SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA)
        self.assertEqual(self.ledger["source_sha256"], SOURCE_SHA)
        self.assertEqual(self.ledger["base_main"], BASE)
        self.assertEqual(self.ledger["revision"], 218476)
        html = raw.decode("utf-8")
        begin = html.index('<span class="anchor" id="ei-19">')
        end = html.index("<p>　　明治十七年八月", begin)
        parser = ChapterText()
        parser.feed(html[begin:end])
        actual = "".join(parser.parts).replace("\u200b", "").replace("\xa0", "").strip()
        self.assertEqual(self.chapter, actual)
        self.assertEqual(hashlib.sha256(actual.encode()).hexdigest(), CHAPTER_SHA)
        self.assertEqual(self.ledger["chapter_sha256"], CHAPTER_SHA)
        self.assertEqual(self.chapter[:6], "早雲蜂記之事")
        self.assertEqual(len(self.chapter), BOUNDS[-1])
        self.assertEqual([r["id"] for r in self.rows], IDS)
        self.assertEqual([r["id"] for r in self.ledger["articles"]], IDS)
        self.assertEqual(self.ledger["article_count"], 9)
        self.assertEqual("".join(r["full_original_text"] for r in self.rows), actual[6:])
        self.assertNotIn("近藤瓶城校", actual)
        self.assertNotIn("近藤圭造", actual)
        for i, (row, entry) in enumerate(zip(self.rows, self.ledger["articles"])):
            with self.subTest(article=row["id"]):
                self.assertEqual((entry["start_offset"], entry["end_offset"]), (BOUNDS[i], BOUNDS[i+1]))
                self.assertEqual(row["full_original_text"], actual[BOUNDS[i]:BOUNDS[i+1]])
                self.assertEqual(entry["source_text"], row["full_original_text"])
                self.assertEqual((row["source_order"], row["chapter_id"]), (i+184, "soun_chapter"))
                self.assertTrue(row["source_url"].endswith("#ei-19"))
                self.assertEqual(entry["layers"], {
                    "SOURCE_STATEMENT": row["full_original_text"],
                    "MODERN_SUMMARY": row["summary"],
                    "HISTORICAL_RECOGNITION": "NOT_TESTED",
                })
                pub = self.data["publication"]["articles"][row["id"]]
                self.assertEqual(pub["narrative_text"], entry["narrative_text"])
                self.assertEqual(pub["annotations"], entry["annotations"])
                self.assertIn("東乱記", pub["annotation_note"])
                for f in ("base_image", "variants", "transcription_emendation", "historical_recognition"):
                    self.assertEqual(pub[f], "NOT_TESTED")
                self.assertEqual(pub["location"], "UNRESOLVED")

    def test_month_does_not_propagate_into_attack_or_suicide(self):
        for row in self.rows:
            with self.subTest(article=row["id"]):
                fields = tuple(row[f] for f in ("original_date","era","era_year","western_year","lunar_month","lunar_day","lunar_is_leap","date_precision"))
                if row["id"] == "EK-0188":
                    self.assertEqual(fields, ("長亨二年戊申十月","長享",2,1488,10,None,False,"month"))
                    self.assertIn("韮山へ移ける",row["full_original_text"])
                else:
                    self.assertEqual(fields, ("記載なし",None,None,None,None,None,None,"unknown"))
                self.assertEqual(row["date_conversion_status"], "unresolved")
                for f in ("julian_start","julian_end","gregorian_start","gregorian_end","date_conversion_source_url","research_date_start","research_date_end","research_date_basis"):
                    self.assertIsNone(row[f])
        self.assertIn("伊豆へ急発向せり", self.rows[6]["full_original_text"])
        self.assertIn("自害あり", self.rows[8]["full_original_text"])
        self.assertIsNone(self.rows[6]["western_year"])
        self.assertIsNone(self.rows[8]["western_year"])

    def test_pagination_and_legend_retained_without_making_them_facts(self):
        pub = self.data["publication"]["articles"]
        chapter = self.chapter
        position = chapter.index("【 NDLJP:386】")
        ann = pub["EK-0189"]["annotations"]
        self.assertEqual(ann, [{"kind":"page_marker","text":"【 NDLJP:386】",
                               "start_offset":position,"end_offset":position+len("【 NDLJP:386】")}])
        self.assertNotIn("NDLJP:386", pub["EK-0189"]["narrative_text"])
        self.assertIn("NDLJP:386", self.rows[5]["full_original_text"])
        self.assertIn("七人", self.rows[2]["full_original_text"])
        self.assertIn("五代", self.rows[8]["full_original_text"])
        for row in self.rows:
            self.assertIn("史実認定せず",row["editorial_note"])

if __name__ == "__main__":
    unittest.main()
