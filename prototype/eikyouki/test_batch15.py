"""Check the Dokan intake against the fixed transcription and main."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import unittest

from integrity import same_fields, verify
from validation import validate_data

PROTOTYPE = Path(__file__).resolve().parent
ROOT = PROTOTYPE.parents[1]
EVIDENCE = ROOT / "evidence/batch15"
BASE = "86e9127184cd5cf08da3555dfa2f6193b137d617"
SOURCE_SHA = "cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0"
CHAPTER_SHA = "1828ff0f591e322256053f654e49eeecf0adee679ab435bca7af46ed1a0381be"
BOUNDS = (
    6, 95, 198, 367, 474, 659, 825, 943, 956, 985, 1369, 1473, 1549,
    1727, 1778, 1814, 1892, 1943, 2005, 2045, 2092, 2231,
)
DATES = {
    "EK-0146": ("康正二年丙子", "康正", 2, 1456, None, None),
    "EK-0147": ("長禄元年〈丁丑〉四月八日", "長禄", 1, 1457, 4, 8),
    "EK-0150": ("長禄元年", "長禄", 1, 1457, None, None),
    "EK-0153": ("文明十年戊戌六月五日", "文明", 10, 1478, 6, 5),
    "EK-0156": ("文明八年丙申四月廿三日", "文明", 8, 1476, 4, 23),
    "EK-0157": ("同十年戊戌正月五日", "文明", 10, 1478, 1, 5),
    "EK-0158": ("同十一年己亥七月十五日", "文明", 11, 1479, 7, 15),
    "EK-0159": ("文明十五年癸卯十月五日", "文明", 15, 1483, 10, 5),
}
UNRESOLVED_LABELS = {
    "EK-0152": "文明年中",
    "EK-0155": "推古天皇御宇定居二年戊子",
}


class ChapterText(HTMLParser):
    """Collect text between chapter anchors without serializing the markup."""

    def __init__(self):
        super().__init__()
        self.parts = []
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        if tag == "span" and dict(attrs).get("class") == "anchor":
            ident = dict(attrs).get("id")
            if ident in ("ei-15", "ei-16"):
                self.anchors.append(ident)

    def handle_data(self, data):
        if self.anchors == ["ei-15"]:
            self.parts.append(data)


class Batch15(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((PROTOTYPE / "eikyouki_records.json").read_text(encoding="utf-8"))
        cls.rows = validate_data(cls.data)
        cls.ledger = json.loads((EVIDENCE / "article-boundaries.json").read_text(encoding="utf-8"))
        cls.chapter = (EVIDENCE / "source/chapter.txt").read_text(encoding="utf-8")

    def test_main_preservation_and_generated_formats(self):
        raw = subprocess.check_output(
            ["git", "show", BASE + ":prototype/eikyouki/eikyouki_records.json"], cwd=ROOT
        )
        old = json.loads(raw)
        self.assertEqual(len(old["records"]), 138)
        same_fields(old["records"], self.rows[:138], "existing 138 articles")
        for key in ("metadata", "article_relationships", "document_structures", "narrative_references"):
            self.assertEqual(old[key], self.data[key])
        for key, value in old["publication"].items():
            if key == "articles":
                for ident, record in value.items():
                    self.assertEqual(self.data["publication"]["articles"][ident], record)
            else:
                self.assertEqual(self.data["publication"][key], value)
        self.assertEqual(
            set(self.data["publication"]["articles"]) & {row["id"] for row in self.rows[:159]},
            set(old["publication"]["articles"]) | {f"EK-{i:04d}" for i in range(139, 160)},
        )
        self.assertEqual(len(self.rows), verify(
            PROTOTYPE / "eikyouki_records.json", PROTOTYPE / "index.html", PROTOTYPE / "eikyouki.db"
        ))

    def test_fixed_chapter_and_contiguous_articles(self):
        self.assertEqual(self.ledger["base_main"], BASE)
        self.assertEqual(self.ledger["source_file"], "evidence/batch08/source/wikisource-fixed.html")
        self.assertEqual(self.ledger["revision"], 218476)
        raw = (ROOT / self.ledger["source_file"]).read_bytes()
        self.assertEqual(self.ledger["source_sha256"], SOURCE_SHA)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA)
        parser = ChapterText()
        parser.feed(raw.decode("utf-8"))
        self.assertEqual(parser.anchors, ["ei-15", "ei-16"])
        expected = "".join(parser.parts).replace("\u200b", "").replace("\xa0", "").strip()
        self.assertEqual(self.chapter, expected)
        self.assertEqual(self.ledger["chapter_sha256"], CHAPTER_SHA)
        self.assertEqual(hashlib.sha256(self.chapter.encode()).hexdigest(), CHAPTER_SHA)
        self.assertEqual(self.chapter[:BOUNDS[0]], "太田道灌之事")
        self.assertEqual(len(self.chapter), BOUNDS[-1])
        self.assertNotIn("太田最後之事", self.chapter)

        articles = self.ledger["articles"]
        self.assertEqual(self.ledger["article_count"], 21)
        self.assertEqual(len(articles), 21)
        self.assertGreaterEqual(len(self.rows), 159)
        for number, item, row, start, end in zip(
            range(139, 160), articles, self.rows[138:159], BOUNDS, BOUNDS[1:]
        ):
            with self.subTest(article=number):
                self.assertEqual(item["id"], f"EK-{number:04d}")
                self.assertEqual((row["id"], row["source_order"]), (item["id"], number))
                self.assertEqual((item["start_offset"], item["end_offset"]), (start, end))
                original = self.chapter[start:end]
                self.assertEqual(item["source_text"], original)
                self.assertEqual(row["full_original_text"], original)
                self.assertEqual(item["layers"], {
                    "SOURCE_STATEMENT": original,
                    "MODERN_SUMMARY": row["summary"],
                    "HISTORICAL_RECOGNITION": "NOT_TESTED",
                })

                pub = self.data["publication"]["articles"][row["id"]]
                self.assertEqual(pub["annotations"], item["annotations"])
                cursor = start
                narrative = []
                for note in pub["annotations"]:
                    a, b = note["start_offset"], note["end_offset"]
                    self.assertTrue(cursor <= a < b <= end)
                    self.assertEqual(note["text"], self.chapter[a:b])
                    narrative.append(self.chapter[cursor:a])
                    cursor = b
                narrative = "".join(narrative + [self.chapter[cursor:end]])
                self.assertEqual(narrative, pub["narrative_text"])
                self.assertEqual(narrative, item["narrative_text"])
                for field in ("base_image", "variants", "transcription_emendation", "historical_recognition"):
                    self.assertEqual(pub[field], "NOT_TESTED")
                self.assertEqual(pub["location"], "UNRESOLVED")

        poems, waka = articles[9:11]
        self.assertTrue(poems["source_text"].endswith("見（有イ）人聞者賞歎するに堪たり、"))
        self.assertEqual(poems["annotations"][-1]["text"], "（有イ）")
        self.assertTrue(waka["source_text"].startswith("太田資長、"))
        self.assertEqual(waka["annotations"], [])

        self.assertEqual(sum(len(item["annotations"]) for item in articles), 15)
        final = articles[-1]
        self.assertEqual([a["kind"] for a in final["annotations"]], ["closing_marker", "editorial_annotation"])
        self.assertEqual(final["annotations"][0]["text"], "永享記終（イ）")
        self.assertIn("以下東乱記ニ同シ", final["annotations"][1]["text"])
        self.assertNotIn("永享記終", final["narrative_text"])
        self.assertNotIn("以下東乱記ニ同シ", final["narrative_text"])

    def test_date_scope_and_unconverted_chronology(self):
        for row in self.rows[138:159]:
            ident = row["id"]
            with self.subTest(article=ident):
                expected = DATES.get(
                    ident, (UNRESOLVED_LABELS.get(ident, "記載なし"), None, None, None, None, None)
                )
                fields = ("original_date", "era", "era_year", "western_year", "lunar_month", "lunar_day")
                self.assertEqual(tuple(row[field] for field in fields), expected)
                self.assertEqual(row["date_precision"], "day" if expected[-1] else "year" if expected[3] else "unknown")
                self.assertEqual(row["date_conversion_status"], "unresolved")
                for field in ("julian_start", "julian_end", "gregorian_start", "gregorian_end",
                              "research_date_start", "research_date_end"):
                    self.assertIsNone(row[field])
        self.assertIn("長禄への改元時期より前", self.rows[146]["date_interpretation"])
