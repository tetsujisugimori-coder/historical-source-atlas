"""Strict boundary for this fixed-source prototype, not a general calendar engine."""
from __future__ import annotations

import re
from urllib.parse import urlsplit

WORK = "EIKYOUKI"
EDITION = "SHISEKI-SHURAN-12-WIKISOURCE"
CHAPTERS = [
    ("muraoka_battle", "村岡合戦事", "https://ja.wikisource.org/w/index.php?oldid=218476&title=永享記#ei-9"),
    ("yuki_siege", "結城籠城事", "https://ja.wikisource.org/w/index.php?oldid=218476&title=永享記#ei-8"),
    ("norizane_tonsure", "憲実出家之事", "https://ja.wikisource.org/w/index.php?oldid=218476&title=永享記#ei-7"),
    ('mochiuji_death', '持氏満貞御最期の事', 'https://ja.wikisource.org/w/index.php?oldid=218476&title=永享記#持氏満貞御最期の事'),
    ('mochiuji_tonsure', '持氏御出家并憲直以下自害の事', 'https://ja.wikisource.org/w/index.php?oldid=218476&title=永享記#持氏御出家并憲直以下自害の事'),
    ('kamakura_return', '持氏鎌倉へ飯給ふ事 附鎌倉合戦事', 'https://ja.wikisource.org/w/index.php?oldid=218476&title=永享記#持氏鎌倉へ飯給ふ事 附鎌倉合戦事'),
    ("intro", "序章", "https://ja.wikisource.org/wiki/永享記#永享記"),
    ("kufu", "公方管領不和の事", "https://ja.wikisource.org/wiki/永享記#公方管領不和の事"),
    ("miura", "三浦介逆心事", "https://ja.wikisource.org/wiki/永享記#三浦介逆心事"),
    ("hakone", "箱根早川尻合戦の事", "https://ja.wikisource.org/wiki/永享記#箱根早川尻合戦の事"),
]
ARTICLE_FIELDS = [
    "article_id", "chapter_id", "source_order", "original_date", "era", "era_year",
    "western_year", "lunar_month", "lunar_day", "date_precision", "date_interpretation",
    "date_kind", "historic_calendar", "lunar_is_leap", "julian_start", "julian_end",
    "gregorian_start", "gregorian_end", "gregorian_calendar", "date_conversion_status",
    "date_conversion_source_url", "date_conversion_note", "research_date_start",
    "research_date_end", "research_date_basis", "summary", "location_in_text",
    "people_in_text", "short_locator", "full_original_text", "editorial_note", "entry_status",
]
FIELDS = ["id" if f == "article_id" else f for f in ARTICLE_FIELDS] + [
    "work_id", "edition_id", "chapter", "source_url"]
NULLABLE_TEXT = {
    "era", "julian_start", "julian_end", "gregorian_start", "gregorian_end",
    "date_conversion_source_url", "date_conversion_note", "research_date_start",
    "research_date_end", "research_date_basis", "location_in_text", "people_in_text",
    "short_locator", "full_original_text", "editorial_note",
}
INTEGERS = {"source_order": (1, 2147483647), "era_year": (1, 9999),
            "western_year": (1, 9999), "lunar_month": (1, 12), "lunar_day": (1, 30)}


def fail(record, field, reason):
    raise ValueError(f"{record.get('id', '<missing id>')!r}: {field}: {reason}")


def calendar_day(value, calendar):
    """Validate Gregorian/Julian separately; return integral Julian day number."""
    if type(value) is not str or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("expected YYYY-MM-DD")
    y, m, d = map(int, value.split("-"))
    leap = y % 4 == 0 and (calendar == "julian" or y % 100 != 0 or y % 400 == 0)
    lengths = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not (1 <= y <= 9999 and 1 <= m <= 12 and 1 <= d <= lengths[m-1]):
        raise ValueError(f"nonexistent {calendar} date")
    a = (14-m)//12
    yy, mm = y+4800-a, m+12*a-3
    base = d + (153*mm+2)//5 + 365*yy + yy//4
    return base - 32083 if calendar == "julian" else base-yy//100+yy//400-32045


# Limited month anchors transcribed in the independent review 5793714253.
# These are historical verification evidence, not a claim of textual collation.
# End sentinel 1439-01-16 permits the final supported year's endpoint.
ANCHORS = {
    8: [(1,False,"1436-01-19"),(2,False,"1436-02-17"),(3,False,"1436-03-18"),
        (4,False,"1436-04-17"),(5,False,"1436-05-16"),(5,True,"1436-06-15"),
        (6,False,"1436-07-14"),(7,False,"1436-08-13"),(8,False,"1436-09-11"),
        (9,False,"1436-10-10"),(10,False,"1436-11-09"),(11,False,"1436-12-08"),
        (12,False,"1437-01-07")],
    9: [(1,False,"1437-02-06"),(2,False,"1437-03-07"),(3,False,"1437-04-06"),
        (4,False,"1437-05-05"),(5,False,"1437-06-04"),(6,False,"1437-07-04"),
        (7,False,"1437-08-02"),(8,False,"1437-09-01"),(9,False,"1437-09-30"),
        (10,False,"1437-10-30"),(11,False,"1437-11-28"),(12,False,"1437-12-27")],
    10: [(1,False,"1438-01-26"),(2,False,"1438-02-24"),(3,False,"1438-03-26"),
         (4,False,"1438-04-25"),(5,False,"1438-05-24"),(6,False,"1438-06-23"),
         (7,False,"1438-07-22"),(8,False,"1438-08-21"),(9,False,"1438-09-20"),
         (10,False,"1438-10-19"),(11,False,"1438-11-18"),(12,False,"1438-12-17")],
    11: [(1,False,"1439-01-16")],
}


def lunar_range(r):
    year, precision = r["era_year"], r["date_precision"]
    # Batch09: exact retrieved NAOJ dates only; no inferred month/year anchors.
    if r["era"] == "永享" and year == 12 and precision == "day" and r["lunar_is_leap"] is False:
        exact = {(1, 13): '1440-02-16', (1, 22): '1440-02-25', (3, 15): '1440-04-16', (4, 4): '1440-05-05', (4, 9): '1440-05-10', (4, 20): '1440-05-21', (5, 1): '1440-05-31', (4, 19): '1440-05-20', (4, 6): '1440-05-07', (5, 11): '1440-06-10', (7, 1): '1440-07-29', (7, 3): '1440-07-31', (7, 4): '1440-08-01', (7, 25): '1440-08-22', (7, 8): '1440-08-05', (8, 9): '1440-09-05', (7, 29): '1440-08-26'}.get((r['lunar_month'],r['lunar_day']))
        if exact:
            day=calendar_day(exact,'julian');return day,day
    # Batch08: directly verified exact days, no unverified annual extrapolation.
    if r["era"] == "永享" and year == 11 and precision == "day" and r["lunar_is_leap"] is False:
        exact = {(6,28): "1439-08-07", (11,20): "1439-12-26", (12,6): "1440-01-10"}.get((r["lunar_month"],r["lunar_day"]))
        if exact:
            day = calendar_day(exact, "julian")
            return day, day
    # Batch07: only these two directly retrieved NAOJ dates are supported for year11.
    # Do not extrapolate an unverified month/year range.
    if r["era"] == "永享" and year == 11 and precision == "day" and r["lunar_month"] == 2 and r["lunar_is_leap"] is False:
        exact = {10: "1439-03-24", 28: "1439-04-11"}.get(r["lunar_day"])
        if exact:
            day = calendar_day(exact, "julian")
            return day, day
    if r["era"] != "永享" or year not in (8,9,10):
        return None  # unsupported: must remain unresolved, never certified
    months = ANCHORS[year] + ANCHORS[year+1][:1]
    if precision == "year":
        return calendar_day(months[0][2], "julian"), calendar_day(months[-1][2], "julian")-1
    index = next((i for i,a in enumerate(months[:-1]) if a[:2] == (r["lunar_month"],r["lunar_is_leap"])), None)
    if index is None:
        fail(r, "lunar_is_leap", "month/leap combination absent from supported anchors")
    start, following = (calendar_day(months[i][2], "julian") for i in (index,index+1))
    if precision == "month":
        return start, following-1
    if r["lunar_day"] > following-start:
        fail(r, "lunar_day", "day exceeds this anchored lunar month's length")
    day = start+r["lunar_day"]-1
    return day, day


def validate_record(r):
    if type(r) is not dict:
        raise ValueError("article: expected object")
    if set(r) != set(FIELDS):
        fail(r, "fields", f"missing={sorted(set(FIELDS)-set(r))}, extra={sorted(set(r)-set(FIELDS))}")
    for f in FIELDS:
        value = r[f]
        if f in INTEGERS:
            low, high = INTEGERS[f]
            if value is None and f != "source_order":
                continue
            if type(value) is not int or not low <= value <= high:
                fail(r, f, f"expected integer {low}..{high}, got {value!r}")
        elif f == "lunar_is_leap":
            if value is not None and type(value) is not bool:
                fail(r, f, "expected boolean or null; coercion is forbidden")
        elif value is None and f in NULLABLE_TEXT:
            continue
        elif type(value) is not str or not value.strip():
            fail(r, f, "expected nonempty string" + (" or null" if f in NULLABLE_TEXT else ""))
    for f in ("id", "work_id", "edition_id", "chapter_id"):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", r[f]):
            fail(r, f, "ID must be nonempty ASCII alphanumeric with _ or - separators")
    url = r["date_conversion_source_url"]
    if url is not None:
        try:
            parts = urlsplit(url)
            safe = parts.scheme == "https" and parts.hostname and parts.username is None and parts.password is None
            safe = safe and not any(ord(c) < 33 or 127 <= ord(c) <= 159 or c.isspace() for c in url)
            _ = parts.port  # malformed ports are not accepted as provenance URLs
        except ValueError:
            safe = False
        if not safe:
            fail(r, "date_conversion_source_url", "absolute HTTPS URL without credentials/control characters required")
    for f, expected in (("work_id",WORK),("edition_id",EDITION)):
        if r[f] != expected:
            fail(r, f, "unsupported fixed-source affiliation")
    chapter = next((c for c in CHAPTERS if c[0] == r["chapter_id"]), None)
    if chapter is None:
        fail(r, "chapter_id", "unsupported chapter")
    for f, expected in (("chapter",chapter[1]),("source_url",chapter[2])):
        if r[f] != expected:
            fail(r, f, "does not match chapter affiliation/source")
    if r["date_kind"] not in ("described_event", "document_date"):
        fail(r, "date_kind", "unsupported kind")
    if r["historic_calendar"] != "宣明暦" or r["gregorian_calendar"] != "先発グレゴリオ暦":
        fail(r, "historic_calendar/gregorian_calendar", "unsupported calendar")
    p = r["date_precision"]
    if p not in ("year", "month", "day", "unknown"):
        fail(r, "date_precision", "unsupported precision")
    required = {"year": (True,False,False), "month": (True,True,False),
                "day": (True,True,True), "unknown": (False,False,False)}[p]
    for f, present in zip(("era_year","lunar_month","lunar_day"), required):
        if (r[f] is not None) != present:
            fail(r, f, f"inconsistent with {p} precision")
    if p == "unknown":
        for f in ("era", "western_year", "lunar_is_leap"):
            if r[f] is not None:
                fail(r, f, "unknown precision requires null")
    else:
        if r["era"] != "永享" or r["western_year"] != 1428+r["era_year"]:
            fail(r, "era/western_year", "fixed era/year correspondence required")
        if type(r["lunar_is_leap"]) is not bool or (p == "year" and r["lunar_is_leap"]):
            fail(r, "lunar_is_leap", "known date requires boolean; year precision cannot designate leap month")
    ranges = {}
    for prefix, calendar in (("julian","julian"),("gregorian","gregorian"),("research_date","gregorian")):
        fields = [prefix+"_start", prefix+"_end"]
        values = [r[f] for f in fields]
        if (values[0] is None) != (values[1] is None):
            fail(r, "/".join(fields), "both endpoints or both null required")
        if values[0] is not None:
            days = []
            for f,v in zip(fields,values):
                try:
                    days.append(calendar_day(v,calendar))
                except ValueError as exc:
                    fail(r, f, str(exc))
            if days[0] > days[1]:
                fail(r, "/".join(fields), "start is after end")
            ranges[prefix] = tuple(days)
    if ("research_date" in ranges) != (r["research_date_basis"] is not None):
        fail(r, "research_date_basis", "research dates and basis must be supplied together")
    status = r["date_conversion_status"]
    if status not in ("provisional", "unresolved"):
        fail(r, "date_conversion_status", "prototype supports provisional or unresolved, not certification")
    expected = None if p == "unknown" else lunar_range(r)
    if status == "unresolved":
        if "julian" in ranges or "gregorian" in ranges:
            fail(r, "date_conversion_status", "unresolved requires null conversion endpoints")
        if not r["date_conversion_note"]:
            fail(r, "date_conversion_note", "unresolved reason required")
    else:
        if expected is None:
            fail(r, "date_conversion_status", "unsupported/unknown lunar date must remain unresolved")
        if not r["date_conversion_source_url"] or not r["date_conversion_note"]:
            fail(r, "date_conversion_source_url/date_conversion_note", "conversion provenance required")
        for prefix in ("julian","gregorian"):
            if ranges.get(prefix) != expected:
                fail(r, prefix+"_start/end", "conversion range contradicts anchored lunar date/precision")


def validate_data(data):
    if type(data) is not dict or type(data.get("records")) is not list or not data["records"]:
        raise ValueError("records: nonempty list required")
    if type(data.get("metadata")) is not dict or data["metadata"].get("base_url") != "https://ja.wikisource.org/wiki/%E6%B0%B8%E4%BA%AB%E8%A8%98":
        raise ValueError("metadata.base_url: unsupported source")
    seen, orders = set(), set()
    for r in data["records"]:
        validate_record(r)
        if r["id"] in seen:
            fail(r, "id", "duplicate permanent ID")
        seen.add(r["id"])
        if r["source_order"] in orders:
            fail(r, "source_order", "duplicate source order")
        orders.add(r["source_order"])
    validate_relationships(data)
    return data["records"]


def validate_relationships(data):
    """Existing relationship schema: source links, never event consolidation."""
    relations = data.get('article_relationships', [])
    if type(relations) is not list: raise ValueError('relationships must be list')
    ids = {r['id'] for r in data['records']}; seen = set()
    for rel in relations:
        if type(rel) is not dict or set(rel) != {'article_id_a','article_id_b','relation','evidence_note'}:
            raise ValueError('relationship fields')
        if any(type(v) is not str or not v.strip() for v in rel.values()):raise ValueError('relationship types')
        a,b = rel['article_id_a'],rel['article_id_b']
        if a not in ids or b not in ids or a == b:raise ValueError('relationship identity')
        if rel['relation'] != 'related_candidate' or '未照合' not in rel['evidence_note']:
            raise ValueError('unverified relation must stay candidate')
        key=tuple(sorted((a,b)))+(rel['relation'],)
        if key in seen:raise ValueError('duplicate relation')
        seen.add(key)
    return relations
