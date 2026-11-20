"""Batch 14: fixed-text Koga intake, 131-record freeze and negative controls."""
import copy
import hashlib
import json
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

from integrity import same_fields, verify
from validation import FIELDS, validate_data

B = Path(__file__).resolve().parent
R = B.parents[1]
E = R / "evidence" / "batch14"
BASE = "a6bf46eabc7a2e703cbd7bffc059da1db4ffef57"
SOURCE_SHA = "cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0"
CHAPTER_SHA = "87c01182f910f2e5a5c88fe335c21c66ebe5c8d2659740464eb0010fea07777c"
D = json.loads((B / "eikyouki_records.json").read_text(encoding="utf-8"))
OLD = json.loads((B / "baselines" / "existing131-batch14.json").read_text(encoding="utf-8"))
L = json.loads((E / "article-boundaries.json").read_text(encoding="utf-8"))


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, text):
        self.parts.append(text)


def extracted_chapter():
    raw = (R / L["source_file"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("fixed original HTML changed")
    html = raw.decode("utf-8")
    beginning = '<span class="anchor" id="ei-14"'
    end = '<span class="anchor" id="ei-15"'
    if html.count(beginning) != 1 or html.count(end) != 1:
        raise ValueError("source chapter anchors absent/duplicated")
    span = html[html.index(beginning):html.index(end)]
    parser = TextOnly()
    parser.feed(span)
    return "".join(parser.parts).replace("\u200b", "").replace("\u00a0", "").strip()


def contract(d, ledger=L):
    rows = validate_data(d)
    same_fields(OLD["records"], rows[:131], "131 previous articles")
    if len(rows) != 138 or [r["id"] for r in rows[131:]] != [
        f"EK-{x:04d}" for x in range(132, 139)
    ]:
        raise ValueError("new article IDs and count")
    for key in ("metadata", "article_relationships", "document_structures", "narrative_references"):
        if d[key] != OLD[key]:
            raise ValueError("original supplementary input altered: " + key)
    for key, value in OLD["publication"].items():
        if key == "articles":
            for ident, prior in value.items():
                if d["publication"]["articles"][ident] != prior:
                    raise ValueError("prior publication changed: " + ident)
        elif d["publication"][key] != value:
            raise ValueError("prior publication metadata changed: " + key)
    if set(d["publication"]["articles"]) != set(OLD["publication"]["articles"]) | {
        x["id"] for x in ledger["articles"]
    }:
        raise ValueError("unexpected publication entries")

    chapter = (E / "source" / "chapter.txt").read_text(encoding="utf-8")
    if (ledger["source_sha256"], ledger["revision"], ledger["source_file"]) != (
        SOURCE_SHA, 218476, "evidence/batch08/source/wikisource-fixed.html"
    ):
        raise ValueError("fixed source identity changed")
    if chapter != extracted_chapter() or hashlib.sha256(chapter.encode()).hexdigest() != CHAPTER_SHA:
        raise ValueError("chapter not re-extracted from fixed source")
    if ledger["chapter_sha256"] != CHAPTER_SHA or len(chapter) != 923:
        raise ValueError("chapter length or hash")
    if (ledger["header"], ledger["previous_chapter"], ledger["next_chapter"]) != (
        "古河城の事", "京都軍之事", "太田道灌之事"
    ):
        raise ValueError("chapter headings")
    if chapter[:5] != "古河城の事" or len(ledger["articles"]) != 7:
        raise ValueError("chapter heading/article count")
    if ledger["historical_recognition"] != "NOT_TESTED":
        raise ValueError("chapter recognition status")

    cursor = 5
    for i, item in enumerate(ledger["articles"]):
        article = rows[131+i]
        start, end = item["start_offset"], item["end_offset"]
        if type(start) is not int or type(end) is not int or not cursor == start < end <= len(chapter):
            raise ValueError("article gap, overlap or invalid boundary")
        cursor = end
        if article["id"] != item["id"] or article["source_order"] != 132+i:
            raise ValueError("article identity")
        if item["source_text"] != chapter[start:end] or article["full_original_text"] != item["source_text"]:
            raise ValueError("article text mismatch")
        same_fields([item["record"]], [article], "article ledger")
        publication = d["publication"]["articles"][article["id"]]
        if publication != item["publication"]:
            raise ValueError("publication/ledger mismatch")
        narrative = item["source_text"]
        for note in item["annotations"]:
            a, b = note["start_offset"], note["end_offset"]
            if not start <= a < b <= end or chapter[a:b] != note["text"]:
                raise ValueError("annotation outside original text")
            narrative = narrative.replace(note["text"], "", 1)
        if item["narrative_text"] != narrative or publication["narrative_text"] != narrative:
            raise ValueError("annotations not separated")
        if publication["annotations"] != item["annotations"]:
            raise ValueError("annotation ledger mismatch")
        if any(publication[k] != "NOT_TESTED" for k in (
            "base_image", "variants", "transcription_emendation", "historical_recognition"
        )) or publication["location"] != "UNRESOLVED":
            raise ValueError("unsupported historical or geographic claim")
        if item["layers"] != {
            "SOURCE_STATEMENT": article["full_original_text"],
            "MODERN_SUMMARY": article["summary"],
            "HISTORICAL_RECOGNITION": "NOT_TESTED",
        }:
            raise ValueError("three layers")
    if cursor != len(chapter) or "".join(a["source_text"] for a in ledger["articles"]) != chapter[5:]:
        raise ValueError("chapter coverage incomplete")

    a, c = rows[131], rows[133]
    if (a["era"], a["era_year"], a["western_year"], a["date_precision"]) != (
        "文明", 3, 1471, "year"
    ):
        raise ValueError("Bunmei 3")
    if (c["era"], c["era_year"], c["western_year"], c["lunar_month"],
        c["lunar_day"], c["date_precision"]) != ("文明", 9, 1477, 7, 17, "day"):
        raise ValueError("Bunmei 9/7/17")
    for i, article in enumerate(rows[131:]):
        for key in ("julian_start", "julian_end", "gregorian_start", "gregorian_end",
                    "research_date_start", "research_date_end", "research_date_basis"):
            if article[key] is not None:
                raise ValueError("unsupported date propagation: " + key)
        if article["date_conversion_status"] != "unresolved":
            raise ValueError("unverified conversion elevated")
        if i not in (0, 2) and any(article[k] is not None for k in (
            "era", "era_year", "western_year", "lunar_month", "lunar_day", "lunar_is_leap"
        )):
            raise ValueError("neighbor date propagated")
    return len(rows)


class Batch14(unittest.TestCase):
    def test_original_baseline_and_formats(self):
        original = json.loads(subprocess.check_output(
            ["git", "show", BASE + ":prototype/eikyouki/eikyouki_records.json"], cwd=R
        ))
        self.assertEqual(original, OLD)
        self.assertEqual(36, len(FIELDS))
        self.assertEqual(131, len(OLD["records"]))
        self.assertEqual(138, contract(D))
        self.assertEqual(138, verify(B/"eikyouki_records.json", B/"index.html", B/"eikyouki.db"))

    def test_exact_source_and_annotation_boundaries(self):
        chapter = extracted_chapter()
        self.assertEqual(chapter, (E/"source/chapter.txt").read_text(encoding="utf-8"))
        self.assertNotIn("太田道灌之事", chapter)
        self.assertIn("【 NDLJP:382】", chapter)
        self.assertIn("（味方イ）", chapter)
        self.assertIn("〈一説伊豆守仲綱〉", chapter)
        self.assertTrue(L["articles"][-1]["source_text"].endswith(
            "【信名蔵本太田道灌条以下無之為是以下宜削去】"
        ))

    def test_4716_old_typed_values_mutation_rejection(self):
        self.assertEqual(131*36, 4716)
        for i, record in enumerate(OLD["records"]):
            for field in FIELDS:
                altered = [dict(item) for item in OLD["records"]]
                v = altered[i][field]
                altered[i][field] = float(v) if type(v) is int else ("FAULT" if v is None else None)
                with self.subTest(index=i, field=field):
                    with self.assertRaises(ValueError):
                        same_fields(OLD["records"], altered, "prior value mutation")

    def test_negative_controls(self):
        faults = ["missing", "duplicate", "prior-order", "prior-null", "prior-reference",
                  "prior-publication", "gap", "overlap", "source-hash", "wrong-original",
                  "wrong-ledger", "wrong-annotation", "false-recognition", "date-propagation",
                  "unverified-conversion", "missing-publication"]
        for fault in faults:
            d = copy.deepcopy(D)
            ledger = copy.deepcopy(L)
            with self.subTest(fault=fault):
                if fault == "missing":
                    d["records"].pop()
                elif fault == "duplicate":
                    d["records"].append(copy.deepcopy(d["records"][-1]))
                elif fault == "prior-order":
                    d["records"][0]["source_order"] = 131
                elif fault == "prior-null":
                    d["records"][130]["western_year"] = 1467
                elif fault == "prior-reference":
                    d["narrative_references"][8]["to"] = "EK-0120"
                elif fault == "prior-publication":
                    d["publication"]["articles"]["EK-0131"]["location"] = "CONFIRMED"
                elif fault == "gap":
                    ledger["articles"][2]["start_offset"] += 1
                elif fault == "overlap":
                    ledger["articles"][2]["start_offset"] -= 1
                elif fault == "source-hash":
                    ledger["source_sha256"] = "0"*64
                elif fault == "wrong-original":
                    d["records"][-1]["full_original_text"] += "追記"
                elif fault == "wrong-ledger":
                    ledger["articles"][3]["source_text"] += "追記"
                elif fault == "wrong-annotation":
                    ledger["articles"][-1]["annotations"][-1]["end_offset"] -= 1
                elif fault == "false-recognition":
                    d["publication"]["articles"]["EK-0138"]["historical_recognition"] = "PASS"
                elif fault == "date-propagation":
                    d["records"][-1]["western_year"] = 1477
                elif fault == "unverified-conversion":
                    d["records"][133]["gregorian_start"] = "1477-09-03"
                elif fault == "missing-publication":
                    del d["publication"]["articles"]["EK-0138"]
                with self.assertRaises((ValueError, KeyError)):
                    contract(d, ledger)
