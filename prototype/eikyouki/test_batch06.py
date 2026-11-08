"""Sixth intake: immutable 1044 fields, order, appended article and date boundaries."""
import copy
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from integrity import same_fields
from validation import FIELDS, validate_record, validate_data

BASE=Path(__file__).resolve().parent
SOURCE='3d3a701881afcee5d0b35ca1e8716f4de229211c'
BASELINE_SHA='982144b284d26405f0d4f4067e86d150c38ac47e4338585e54c95d88ca8876da'
DATA=json.loads((BASE/'eikyouki_records.json').read_text())


def preserve29(rows):
    raw=(BASE/'baselines/existing29-batch06.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=BASELINE_SHA:raise ValueError('baseline hash mismatch')
    b=json.loads(raw)
    if b['source_commit']!=SOURCE or b['field_count']!=36 or len(b['records'])!=29:raise ValueError('baseline provenance/count')
    expected_ids=[f'EK-{n:04d}' for n in range(1,30)]
    if [r['id'] for r in b['records']]!=expected_ids or any(set(r)!=set(FIELDS) for r in b['records']):raise ValueError('baseline identity/fields')
    ids=[r.get('id') for r in rows]
    if any(type(i) is not str for i in ids) or len(set(ids))!=len(ids):raise ValueError('invalid/duplicate ID')
    previous=[r for r in rows if r['id'] in expected_ids]
    if [r['id'] for r in previous]!=expected_ids:raise ValueError('existing array order or missing ID')
    same_fields(b['records'],previous,'sixth intake existing29')
    return 1044


class Batch06(unittest.TestCase):
    def test_baseline_matches_actual_merged_main(self):
        source=json.loads(subprocess.check_output(['git','show',SOURCE+':prototype/eikyouki/eikyouki_records.json'],cwd=BASE))['records']
        b=json.loads((BASE/'baselines/existing29-batch06.json').read_text())['records']
        same_fields(source,b,'fixed main baseline')
        self.assertEqual([r['id'] for r in source],[r['id'] for r in b])
        self.assertEqual(1044,preserve29(DATA['records']))

    def test_all_1044_single_field_corruptions_rejected(self):
        for i in range(29):
            for field in FIELDS:
                with self.subTest(id=DATA['records'][i]['id'],field=field):
                    rows=copy.deepcopy(DATA['records']);v=rows[i][field]
                    rows[i][field]=not v if type(v) is bool else (float(v) if type(v) is int else ('CORRUPTED' if v is None else None))
                    with self.assertRaises(ValueError):preserve29(rows)

    def test_missing_duplicate_order_and_legitimate_append(self):
        for label,rows in [('empty',[]),('missing',DATA['records'][1:]),('duplicate',DATA['records']+[DATA['records'][28]]),('array_order',list(reversed(DATA['records'])))]:
            with self.subTest(case=label):
                with self.assertRaises(ValueError):preserve29(rows)
        rows=copy.deepcopy(DATA['records']);rows[0]['source_order'],rows[1]['source_order']=rows[1]['source_order'],rows[0]['source_order']
        with self.assertRaises(ValueError):preserve29(rows)
        self.assertEqual(1044,preserve29(DATA['records']+[dict(DATA['records'][-1],id='EK-9999',source_order=9999)]))

    def test_eleven_independent_entries_and_explicit_dates(self):
        rows=DATA['records'][29:40]
        self.assertEqual([f'EK-{n:04d}' for n in range(30,41)],[r['id'] for r in rows])
        self.assertEqual(list(range(30,41)),[r['source_order'] for r in rows])
        ledger=json.loads((BASE.parents[1]/'evidence/batch06/article-boundaries.json').read_text())['articles']
        self.assertEqual(11,len(ledger))
        self.assertEqual([f'EK-{n:04d}' for n in range(30,41)],[entry['id'] for entry in ledger])
        for r,entry in zip(rows,ledger):
            validate_record(r)
            self.assertEqual(36,len(r));self.assertEqual(entry['id'],r['id'])
            self.assertEqual(entry['begin'],r['short_locator']);self.assertIn(entry['end'],r['editorial_note'])
            self.assertEqual(entry['summary'],r['summary']);self.assertEqual(entry['original_date'],r['original_date'])
            self.assertIsNone(r['full_original_text']);self.assertIsNone(r['research_date_start']);self.assertIsNone(r['research_date_basis'])
            self.assertIn('oldid=218476',r['source_url']);self.assertIn('底本未照合',r['entry_status'])
        for index,day,j,g in [(0,4,'1438-11-21','1438-11-30'),(1,5,'1438-11-22','1438-12-01'),(2,7,'1438-11-24','1438-12-03'),(10,11,'1438-11-28','1438-12-07')]:
            r=rows[index]
            self.assertEqual((10,11,day,j,g,'provisional'),tuple(r[f] for f in ['era_year','lunar_month','lunar_day','julian_start','gregorian_start','date_conversion_status']))
        self.assertIn('伝聞',rows[9]['summary']);self.assertIn('人道',rows[7]['people_in_text'])
        self.assertIn('乳母',rows[5]['editorial_note']);self.assertIn('とにや',rows[1]['editorial_note'])

    def test_unknown_dates_do_not_inherit_seventh_or_eleventh(self):
        for r in DATA['records'][32:39]:
            self.assertEqual(('unknown','unresolved'),(r['date_precision'],r['date_conversion_status']))
            for f in ['era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','julian_start','julian_end','gregorian_start','gregorian_end','date_conversion_source_url']:
                self.assertIsNone(r[f])
                bad=copy.deepcopy(r);bad[f]='1438-12-03' if 'start' in f or 'end' in f else 7
                with self.subTest(id=r['id'],unsupported_date=f):
                    with self.assertRaises(ValueError):validate_record(bad)

    def test_new_article_missing_duplicate_and_order_rejected(self):
        expected=[f'EK-{n:04d}' for n in range(30,41)]
        def check(rows):
            ids=[r['id'] for r in rows if r['id'] in expected]
            if ids != expected:raise ValueError('new article identity/order contract')
            validate_data(dict(DATA,records=rows))
        for i in range(29,40):
            for label,rows in [('missing',DATA['records'][:i]+DATA['records'][i+1:]),('duplicate',DATA['records']+[DATA['records'][i]])]:
                with self.subTest(id=DATA['records'][i]['id'],fault=label):
                    with self.assertRaises(ValueError):check(rows)
        check(DATA['records'])
        with self.assertRaises(ValueError):check(DATA['records'][:29]+list(reversed(DATA['records'][29:])))
