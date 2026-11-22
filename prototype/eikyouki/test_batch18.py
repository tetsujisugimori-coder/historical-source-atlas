"""Batch 18 source boundaries, editorial annotations and prior data preservation."""

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import unittest

from integrity import same_fields, verify


PROTOTYPE = Path(__file__).resolve().parent
ROOT = PROTOTYPE.parents[1]
BASE = "644d18f67a6de2f981b36591304ce9309eadd3bf"
RECORDS = "prototype/eikyouki/eikyouki_records.json"
SOURCE = "evidence/batch08/source/wikisource-fixed.html"
SOURCE_SHA = "cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0"
CHAPTER_SHA = "1f1add0ac7daf8abfc03023aeb883ab7a13fdbcc4fc17167fdad581a0649914d"
BOUNDS = (7, 30, 127, 222, 390, 462, 550, 584, 659)
IDS = [f"EK-{number:04d}" for number in range(176, 184)]


class ChapterText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


class Batch18(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / RECORDS).read_text(encoding="utf-8"))
        cls.rows = cls.data["records"][175:183]
        evidence = ROOT / "evidence/batch18"
        cls.ledger = json.loads((evidence / "article-boundaries.json").read_text(encoding="utf-8"))
        cls.chapter = (evidence / "source/chapter.txt").read_text(encoding="utf-8")

    def test_existing_175_preserved_and_generated_formats_agree(self):
        baseline = json.loads(subprocess.check_output(["git", "show", BASE + ":" + RECORDS], cwd=ROOT))
        self.assertEqual(len(baseline["records"]), 175)
        same_fields(baseline["records"], self.data["records"][:175], "existing 175 articles")
        self.assertEqual(set(baseline), set(self.data))
        for key in baseline.keys() - {"records", "publication"}:
            self.assertEqual(json.dumps(baseline[key]), json.dumps(self.data[key]), key)
        old_publication = baseline["publication"]
        new_publication = self.data["publication"]
        self.assertEqual(set(old_publication), set(new_publication))
        for key, old in old_publication.items():
            current = new_publication[key]
            if key == "articles":
                self.assertTrue(set(IDS).issubset(set(current) - set(old)))
                current = {identifier: current[identifier] for identifier in old}
            self.assertEqual(json.dumps(old), json.dumps(current), key)
        self.assertGreaterEqual(len(self.data["records"]), 183)
        self.assertEqual(verify(ROOT / RECORDS, PROTOTYPE / "index.html", PROTOTYPE / "eikyouki.db"), len(self.data["records"]))

    def test_fixed_source_and_article_boundaries(self):
        raw = (ROOT / SOURCE).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA)
        self.assertEqual(self.ledger["source_sha256"], SOURCE_SHA)
        self.assertEqual(self.ledger["base_main"], BASE)
        self.assertEqual(self.ledger["revision"], 218476)
        html = raw.decode("utf-8")
        start = html.index('<span class="anchor" id="ei-18">')
        end = html.index('<span class="anchor" id="ei-19">', start)
        parser = ChapterText()
        parser.feed(html[start:end])
        fixed = "".join(parser.parts).replace("\u200b", "").replace("\xa0", "").strip()
        self.assertEqual(self.chapter, fixed)
        self.assertEqual(hashlib.sha256(self.chapter.encode()).hexdigest(), CHAPTER_SHA)
        self.assertEqual(self.ledger["chapter_sha256"], CHAPTER_SHA)
        self.assertEqual(self.chapter[:BOUNDS[0]], "高見原合戦之事")
        self.assertEqual(len(self.chapter), BOUNDS[-1])
        self.assertEqual(self.ledger["article_count"], len(IDS))
        self.assertEqual([row["id"] for row in self.rows], IDS)
        self.assertEqual([item["id"] for item in self.ledger["articles"]], IDS)
        self.assertEqual("".join(row["full_original_text"] for row in self.rows), self.chapter[BOUNDS[0]:])

        for order, (row, item, start, end) in enumerate(
            zip(self.rows, self.ledger["articles"], BOUNDS, BOUNDS[1:]), 176
        ):
            with self.subTest(article=row["id"]):
                self.assertEqual((row["source_order"], row["chapter_id"]), (order, "takami_hara_battle"))
                self.assertTrue(row["source_url"].endswith("#ei-18"))
                self.assertEqual((item["start_offset"], item["end_offset"]), (start, end))
                self.assertEqual(row["full_original_text"], self.chapter[start:end])
                self.assertEqual(item["source_text"], self.chapter[start:end])
                self.assertEqual(item["layers"], {
                    "SOURCE_STATEMENT": row["full_original_text"],
                    "MODERN_SUMMARY": row["summary"],
                    "HISTORICAL_RECOGNITION": "NOT_TESTED",
                })
                pub = self.data["publication"]["articles"][row["id"]]
                self.assertEqual(pub["annotations"], item["annotations"])
                self.assertEqual(pub["narrative_text"], item["narrative_text"])
                self.assertIn("東乱記", pub["annotation_note"])
                for key in ("base_image", "variants", "transcription_emendation", "historical_recognition"):
                    self.assertEqual(pub[key], "NOT_TESTED")
                self.assertEqual(pub["location"], "UNRESOLVED")

    def test_variant_is_separate_and_illegible_characters_are_retained(self):
        articles = self.ledger["articles"]
        self.assertIn("鳥□の陣", articles[1]["narrative_text"])
        self.assertIn("藤田□□□", articles[4]["narrative_text"])
        for item in articles[:-1]:
            self.assertEqual(item["annotations"], [])
            self.assertEqual(item["narrative_text"], item["source_text"])
        self.assertEqual(self.chapter[641:645], "んイし　")
        final = articles[-1]
        self.assertEqual(final["annotations"], [{
            "kind": "variant_note", "text": "んイ", "start_offset": 641, "end_offset": 643,
        }])
        self.assertEqual(final["narrative_text"], final["source_text"].replace("んイし　", "し"))
        self.assertIn("退治せしに", final["narrative_text"])

    def test_lunar_date_is_limited_to_sugahara_departure(self):
        for row in self.rows:
            with self.subTest(article=row["id"]):
                actual = tuple(row[key] for key in (
                    "original_date", "era", "era_year", "western_year", "lunar_month",
                    "lunar_day", "lunar_is_leap", "date_precision",
                ))
                if row["id"] == "EK-0177":
                    self.assertEqual(actual, ("長亨二年戊申六月八日", "長享", 2, 1488, 6, 8, False, "day"))
                    self.assertIn("須賀原へ出陣", row["full_original_text"])
                else:
                    self.assertEqual(actual, ("記載なし", None, None, None, None, None, None, "unknown"))
                self.assertEqual(row["date_conversion_status"], "unresolved")
                for key in (
                    "julian_start", "julian_end", "gregorian_start", "gregorian_end",
                    "date_conversion_source_url", "research_date_start", "research_date_end", "research_date_basis",
                ):
                    self.assertIsNone(row[key])


if __name__ == "__main__":
    unittest.main()
