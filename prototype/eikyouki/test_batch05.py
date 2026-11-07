"""Fifth intake: immutable 936 fields, order, appended article and date boundaries."""
import copy
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from integrity import same_fields
from validation import FIELDS, validate_record, validate_data

BASE=Path(__file__).resolve().parent
SOURCE='555ad2d3763d0ae009839d2ac2abbfcd78383228'
BASELINE_SHA='c25768124e256101a22e7630ba937c28336af2f54dedadb924a40b384e06c7c0'
DATA=json.loads((BASE/'eikyouki_records.json').read_text())


def preserve26(rows):
    raw=(BASE/'baselines/existing26-batch05.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=BASELINE_SHA:raise ValueError('baseline hash mismatch')
    b=json.loads(raw)
    if b['source_commit']!=SOURCE or b['field_count']!=36 or len(b['records'])!=26:raise ValueError('baseline provenance/count')
    expected_ids=[f'EK-{n:04d}' for n in range(1,27)]
    if [r['id'] for r in b['records']]!=expected_ids or any(set(r)!=set(FIELDS) for r in b['records']):raise ValueError('baseline identity/fields')
    ids=[r.get('id') for r in rows]
    if any(type(i) is not str for i in ids) or len(set(ids))!=len(ids):raise ValueError('invalid/duplicate ID')
    previous=[r for r in rows if r['id'] in expected_ids]
    if [r['id'] for r in previous]!=expected_ids:raise ValueError('existing array order or missing ID')
    same_fields(b['records'],previous,'fifth intake existing26')
    return 936


class Batch05(unittest.TestCase):
    def test_baseline_matches_actual_merged_main(self):
        source=json.loads(subprocess.check_output(['git','show',SOURCE+':prototype/eikyouki/eikyouki_records.json'],cwd=BASE))['records']
        b=json.loads((BASE/'baselines/existing26-batch05.json').read_text())['records']
        same_fields(source,b,'fixed main baseline')
        self.assertEqual([r['id'] for r in source],[r['id'] for r in b])
        self.assertEqual(936,preserve26(DATA['records']))

    def test_all_936_single_field_corruptions_rejected(self):
        for i in range(26):
            for field in FIELDS:
                with self.subTest(id=DATA['records'][i]['id'],field=field):
                    rows=copy.deepcopy(DATA['records']);v=rows[i][field]
                    rows[i][field]=not v if type(v) is bool else (float(v) if type(v) is int else ('CORRUPTED' if v is None else None))
                    with self.assertRaises(ValueError):preserve26(rows)

    def test_missing_duplicate_order_and_legitimate_append(self):
        for label,rows in [('empty',[]),('missing',DATA['records'][1:]),('duplicate',DATA['records']+[DATA['records'][25]]),('array_order',list(reversed(DATA['records'])))]:
            with self.subTest(case=label):
                with self.assertRaises(ValueError):preserve26(rows)
        rows=copy.deepcopy(DATA['records']);rows[0]['source_order'],rows[1]['source_order']=rows[1]['source_order'],rows[0]['source_order']
        with self.assertRaises(ValueError):preserve26(rows)
        self.assertEqual(936,preserve26(DATA['records']+[dict(DATA['records'][-1],id='EK-9999',source_order=9999)]))

    def test_three_independent_entries_keep_source_and_unknowns(self):
        rows=DATA['records'][26:29]
        self.assertEqual(['EK-0027','EK-0028','EK-0029'],[r['id'] for r in rows])
        self.assertEqual([27,28,29],[r['source_order'] for r in rows])
        for r in rows:
            validate_record(r)
            self.assertEqual(36,len(r));self.assertIsNone(r['full_original_text'])
            self.assertIsNone(r['research_date_start']);self.assertIsNone(r['research_date_basis'])
            self.assertIn('oldid=218476',r['source_url']);self.assertIn('底本未照合',r['entry_status'])
        self.assertIn('欠文アルカ',rows[0]['editorial_note'])
        self.assertEqual(('同二日',10,11,2,'1438-11-19','1438-11-28','provisional'),tuple(rows[0][f] for f in ['original_date','era_year','lunar_month','lunar_day','julian_start','gregorian_start','date_conversion_status']))
        for r in rows[1:]:
            self.assertEqual(('unknown','unresolved'),(r['date_precision'],r['date_conversion_status']))
            for f in ['era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','julian_start','julian_end','gregorian_start','gregorian_end','date_conversion_source_url']:
                self.assertIsNone(r[f])
                bad=copy.deepcopy(r);bad[f]='1438-11-28' if 'start' in f or 'end' in f else 2
                with self.subTest(id=r['id'],unsupported_date=f):
                    with self.assertRaises(ValueError):validate_record(bad)
        d=copy.deepcopy(DATA);d['records'][28]['id']='EK-0028'
        with self.assertRaises(ValueError):validate_data(d)
