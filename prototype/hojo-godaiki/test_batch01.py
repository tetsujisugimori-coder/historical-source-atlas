"""Hojo intake: preservation, source-state, person-link and SQLite checks."""
import copy
import json
import re
import sqlite3
import tempfile
import unittest
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from build import build, validate, read_json, DATA, PERSONS, EIK, HERE

# Fixed independently of build.py and the generated inputs, from the
# Wikisource revisions recorded in the two intake ledgers.
VOLUME_ONE_URL = "https://ja.wikisource.org/w/index.php?oldid=217784&title=北条五代記/巻第一"
VOLUME_TWO_URL = "https://ja.wikisource.org/w/index.php?oldid=214082&title=北条五代記/巻第二"
EXPECTED_FIXED_SOURCES = {
    f"HG-{number:04d}": VOLUME_ONE_URL if number <= 5 else VOLUME_TWO_URL
    for number in range(1, 13)
}
REVIEWED_TEXT = HERE / "batch02_reviewed_text.json"


def cards_in(html):
    return re.findall(r'<article id="([^"]+)">(.*?)</article>', html, re.DOTALL)


class VolumeSources(HTMLParser):
    """Read actual links and article IDs in each volume section."""

    def __init__(self, html):
        super().__init__()
        self.sections = []
        self.section = None
        self.link = None
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self.section = ([], [])
            self.sections.append(self.section)
        elif self.section is not None:
            article_ids, _ = self.section
            if tag == "article":
                article_ids.append(attrs.get("id"))
            elif tag == "a" and not article_ids:
                self.link = (attrs.get("href"), [])

    def handle_data(self, data):
        if self.link is not None:
            self.link[1].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.link is not None:
            href, label = self.link
            if "".join(label).strip() in {
                "採録時のWikisource固定版（巻第一）", "採録時のWikisource固定版（巻第二）"
            }:
                self.section[1].append(href)
            self.link = None
        elif tag == "section":
            self.section = None
            self.link = None


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
        cards = cards_in(html)
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

    def assert_fixed_sources(self, hojo, html, con):
        metadata = hojo["metadata"]
        json_sources = {
            r["id"]: (
                metadata if r["chapter_id"].startswith("HG-V1-")
                else metadata["additional_volumes"].get("巻第二", {})
            ).get("base_url")
            for r in hojo["records"]
        }
        self.assertEqual(json_sources, EXPECTED_FIXED_SOURCES, "JSON fixed source by article ID")

        html_sources = {}
        for article_ids, urls in VolumeSources(html).sections:
            self.assertEqual(len(urls), 1, "HTML volume fixed link missing or duplicated")
            for article_id in article_ids:
                self.assertNotIn(article_id, html_sources)
                html_sources[article_id] = urls[0]
        self.assertEqual(html_sources, EXPECTED_FIXED_SOURCES, "HTML fixed source by article ID")

        sqlite_sources = dict(con.execute("SELECT article_id, fixed_source_url FROM article_fixed_sources"))
        self.assertEqual(sqlite_sources, EXPECTED_FIXED_SOURCES, "SQLite fixed source by article ID")

    def test_fixed_sources_by_article_id(self):
        html = (HERE / "index.html").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(build(Path(directory) / "multi.db")) as con:
                self.assert_fixed_sources(self.h, html, con)

    def test_fixed_source_negative_controls(self):
        html = (HERE / "index.html").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            with sqlite3.connect(build(Path(directory) / "multi.db")) as con:
                con.execute(
                    "UPDATE article_fixed_sources SET fixed_source_url=? WHERE article_id='HG-0006'",
                    (VOLUME_ONE_URL,),
                )
                with self.assertRaisesRegex(AssertionError, "SQLite fixed source by article ID"):
                    self.assert_fixed_sources(self.h, html, con)
                con.rollback()

                con.execute("DELETE FROM article_fixed_sources WHERE article_id='HG-0012'")
                with self.assertRaisesRegex(AssertionError, "SQLite fixed source by article ID"):
                    self.assert_fixed_sources(self.h, html, con)
                con.rollback()

                with self.assertRaisesRegex(AssertionError, "HTML fixed source by article ID"):
                    self.assert_fixed_sources(self.h, html.replace("oldid=214082", "oldid=217784"), con)

                commented_html, count = re.subn(
                    r'(<a href="[^"]*oldid=214082[^"]*"[^>]*>[^<]+</a>)',
                    lambda match: f"<!-- {match[0]} -->",
                    html,
                )
                self.assertEqual(count, 1)
                with self.assertRaisesRegex(AssertionError, "HTML volume fixed link missing"):
                    self.assert_fixed_sources(self.h, commented_html, con)

                # All three outputs agree on the injected error. The checker
                # still rejects it using its independently fixed expectations.
                hojo = copy.deepcopy(self.h)
                hojo["metadata"]["additional_volumes"]["巻第二"].update(
                    revision_id=217784, base_url=VOLUME_ONE_URL
                )
                broken_html = html.replace(
                    VOLUME_TWO_URL.replace("&", "&amp;"), VOLUME_ONE_URL.replace("&", "&amp;")
                )
                con.execute(
                    "UPDATE article_fixed_sources SET fixed_source_url=? WHERE fixed_source_url=?",
                    (VOLUME_ONE_URL, VOLUME_TWO_URL),
                )
                with self.assertRaisesRegex(AssertionError, "JSON fixed source by article ID"):
                    self.assert_fixed_sources(hojo, broken_html, con)

    def assert_reviewed_text(self, records, html, reviewed):
        cards = dict(cards_in(html))
        by_id = {r["id"]: r for r in records}
        for ordinal, (article_id, article) in zip("一二三四五六七", reviewed["articles"].items(), strict=True):
            record = by_id[article_id]
            expected = {**reviewed["shared"], **article,
                        "short_locator": f"巻第二・{ordinal}「{article['chapter']}」"}
            self.assertEqual({field: record[field] for field in expected}, expected,
                             f"{article_id}: unreviewed editorial text or attribution")
            self.assertEqual(
                " ".join(unescape(re.sub(r"<[^>]+>", "", cards[article_id])).split()),
                f"{article_id} 巻第二・{ordinal} 本文未収録・仮登録"
                f"{article['chapter']}{article['summary']}"
                "Wikisource原節を読む | 原文日付：記事全体として未確定",
                f"{article_id}: unreviewed HTML article text",
            )

    def test_second_volume_reviewed_text(self):
        html = (HERE / "index.html").read_text(encoding="utf-8")
        self.assert_reviewed_text(self.h["records"], html, read_json(REVIEWED_TEXT))
        source = self.h["metadata"]["additional_volumes"]["巻第二"]
        self.assertEqual(source["date_conversion"], "UNRESOLVED")

    def test_unsupported_date_and_identification_negative_controls(self):
        html = (HERE / "index.html").read_text(encoding="utf-8")
        reviewed = read_json(REVIEWED_TEXT)
        cases = (
            ("HG-0006", "summary", "天文十年七月十九日をこの節の代表日付とする。"),
            ("HG-0008", "editorial_note", "この早雲は永享記の伊勢新九郎と同一人物である。"),
            ("HG-0009", "editorial_note", "福島伊賀守は福島正成に当たる。"),
            ("HG-0010", "date_conversion_note", "1608年4月3日とする。"),
        )
        for article_id, field, claim in cases:
            with self.subTest(article_id=article_id, field=field, claim=claim):
                records = copy.deepcopy(self.h["records"])
                record = next(r for r in records if r["id"] == article_id)
                text = record[field]
                record[field] += claim
                # For summaries the JSON and HTML can agree and still be wrong.
                altered_html = html.replace(text, text + claim) if field == "summary" else html
                with self.assertRaisesRegex(AssertionError, article_id + ": unreviewed editorial text"):
                    self.assert_reviewed_text(records, altered_html, reviewed)
        summary = reviewed["articles"]["HG-0008"]["summary"]
        with self.assertRaisesRegex(AssertionError, "HG-0008: unreviewed HTML article text"):
            self.assert_reviewed_text(self.h["records"], html.replace(summary, summary + cases[1][2]), reviewed)

    def test_reviewed_quote_and_uncertainty_are_allowed(self):
        html = (HERE / "index.html").read_text(encoding="utf-8")
        reviewed = read_json(REVIEWED_TEXT)
        records = copy.deepcopy(self.h["records"])
        summary = reviewed["articles"]["HG-0006"]["summary"]
        with_quote = summary + "史料に「天文十年七月十九日」とある。節全体の代表日付と人物比定は保留する。"
        # Model an independently approved revision of editorial wording.
        reviewed["articles"]["HG-0006"]["summary"] = with_quote
        records[5]["summary"] = with_quote
        self.assert_reviewed_text(records, html.replace(summary, with_quote), reviewed)

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
