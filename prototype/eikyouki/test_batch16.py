"""Verify the intake against the fixed transcription and the merged batch 15."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import unittest

from integrity import same_fields, verify

PROTOTYPE = Path(__file__).resolve().parent
ROOT = PROTOTYPE.parents[1]
EVIDENCE = ROOT / "evidence/batch16"
BASE = "4fc74a0b6a531397914b16d8d38768ac8107803c"
RECORDS = "prototype/eikyouki/eikyouki_records.json"
SOURCE = "evidence/batch08/source/wikisource-fixed.html"
SOURCE_SHA = "cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0"
CHAPTER_SHA = "b9296363a5ee4e215468564383d69769b3ec072cff26b2b6ad02b61b83773300"
BOUNDS = (6, 189, 343, 434, 518, 591, 650, 687, 727)
IDS = [f"EK-{number:04d}" for number in range(160, 168)]
PAGE = {"kind": "page_marker", "text": "【 NDLJP:384】", "start_offset": 91, "end_offset": 103}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


class Batch16(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / RECORDS).read_text(encoding="utf-8"))
        cls.rows = cls.data["records"][159:167]
        cls.ledger = json.loads((EVIDENCE / "article-boundaries.json").read_text(encoding="utf-8"))
        cls.chapter = (EVIDENCE / "source/chapter.txt").read_text(encoding="utf-8")

    def test_preservation_and_generated_formats(self):
        baseline = json.loads(subprocess.check_output(["git", "show", BASE + ":" + RECORDS], cwd=ROOT))
        self.assertEqual(len(baseline["records"]), 159)
        old_rows = self.data["records"][:159]
        self.assertEqual([row["id"] for row in baseline["records"]], [row["id"] for row in old_rows])
        same_fields(baseline["records"], old_rows, "existing 159 articles")

        old_ids = {row["id"] for row in old_rows}
        self.assertEqual(set(baseline), set(self.data))
        for key in baseline.keys() - {"records", "publication"}:
            self.assertEqual(json.dumps(baseline[key]), json.dumps(self.data[key]), key)
        self.assertEqual(set(baseline["publication"]), set(self.data["publication"]))
        for key, old in baseline["publication"].items():
            current = self.data["publication"][key]
            if key == "articles":
                current = {ident: pub for ident, pub in current.items() if ident in old_ids}
            self.assertEqual(json.dumps(old, sort_keys=True), json.dumps(current, sort_keys=True), key)
        self.assertEqual(len(self.data["records"]), verify(
            ROOT / RECORDS, PROTOTYPE / "index.html", PROTOTYPE / "eikyouki.db"
        ))

    def test_fixed_source_and_article_boundaries(self):
        self.assertEqual((self.ledger["base_main"], self.ledger["source_file"], self.ledger["revision"]),
                         (BASE, SOURCE, 218476))
        raw = (ROOT / SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA)
        self.assertEqual(self.ledger["source_sha256"], SOURCE_SHA)
        html = raw.decode("utf-8")
        start = html.index('<span class="anchor" id="ei-16">')
        end = html.index('<span class="anchor" id="ei-17">', start)
        parser = Text()
        parser.feed(html[start:end])
        fixed = "".join(parser.parts).replace("\u200b", "").replace("\xa0", "").strip()
        self.assertEqual(self.chapter, fixed)
        self.assertEqual(hashlib.sha256(self.chapter.encode()).hexdigest(), CHAPTER_SHA)
        self.assertEqual(self.ledger["chapter_sha256"], CHAPTER_SHA)
        self.assertEqual(self.chapter[:BOUNDS[0]], "太田最後之事")
        self.assertEqual(len(self.chapter), BOUNDS[-1])
        self.assertEqual(self.ledger["article_count"], len(IDS))

        articles = self.ledger["articles"]
        self.assertEqual([item["id"] for item in articles], IDS)
        self.assertEqual([row["id"] for row in self.rows], IDS)
        self.assertEqual("".join(row["full_original_text"] for row in self.rows), self.chapter[6:])
        for num, row, item, a, b in zip(range(160, 168), self.rows, articles, BOUNDS, BOUNDS[1:]):
            with self.subTest(article=row["id"]):
                self.assertEqual((row["source_order"], row["chapter_id"]), (num, "ota_death"))
                self.assertTrue(row["source_url"].endswith("#ei-16"))
                self.assertEqual((item["start_offset"], item["end_offset"]), (a, b))
                original = self.chapter[a:b]
                self.assertEqual(item["source_text"], original)
                self.assertEqual(row["full_original_text"], original)
                self.assertEqual(item["layers"], {
                    "SOURCE_STATEMENT": original,
                    "MODERN_SUMMARY": row["summary"],
                    "HISTORICAL_RECOGNITION": "NOT_TESTED",
                })
                pub = self.data["publication"]["articles"][row["id"]]
                notes = [PAGE] if num == 160 else []
                self.assertEqual(item["annotations"], notes)
                self.assertEqual(pub["annotations"], notes)
                if notes:
                    start, end = PAGE["start_offset"], PAGE["end_offset"]
                    self.assertEqual(self.chapter[start:end], PAGE["text"])
                    original = self.chapter[a:start] + self.chapter[end:b]
                self.assertEqual(item["narrative_text"], original)
                self.assertEqual(pub["narrative_text"], original)
                self.assertIn("東乱記", pub["annotation_note"])
                self.assertEqual(pub["location"], "UNRESOLVED")
                for field in ("base_image", "variants", "transcription_emendation", "historical_recognition"):
                    self.assertEqual(pub[field], "NOT_TESTED")

        self.assertTrue(self.rows[4]["full_original_text"].endswith("思ひしらすは"))
        self.assertTrue(self.rows[5]["full_original_text"].startswith("只忠のみ有て"))
        self.assertIn("相州扇谷", self.rows[3]["location_in_text"])
        self.assertIn("同豊後守", self.rows[-1]["people_in_text"])

    def test_date_scope(self):
        for row in self.rows:
            with self.subTest(article=row["id"]):
                fields = ("original_date", "era", "era_year", "western_year",
                          "lunar_month", "lunar_day", "lunar_is_leap", "date_precision")
                if row["id"] == "EK-0163":
                    expected = ("文明十八年丙午七月廿六日", "文明", 18, 1486, 7, 26, False, "day")
                else:
                    expected = ("記載なし", None, None, None, None, None, None, "unknown")
                self.assertEqual(tuple(row[field] for field in fields), expected)
                self.assertEqual(row["date_conversion_status"], "unresolved")
                for field in ("julian_start", "julian_end", "gregorian_start", "gregorian_end",
                              "research_date_start", "research_date_end", "research_date_basis"):
                    self.assertIsNone(row[field])
