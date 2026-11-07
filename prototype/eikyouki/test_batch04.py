"""Fourth intake: immutable prior 684 values and unresolved-date articles."""
import copy
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from integrity import same_fields
from validation import FIELDS, validate_record, validate_data

BASE=Path(__file__).resolve().parent
SOURCE='4adbbba3a2d4c38ad0d27b35c671554050b0eed9'
BASELINE_SHA='1708e557c93ba3b322f07ac2f367652c9fac4036822a60121260ae3d3b19bdb1'
DATA=json.loads((BASE/'eikyouki_records.json').read_text())


def preserve19(rows):
    raw=(BASE/'baselines/existing19-batch04.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=BASELINE_SHA:raise ValueError('baseline hash mismatch')
    b=json.loads(raw)
    if b['source_commit']!=SOURCE or len(b['records'])!=19:raise ValueError('baseline provenance/count')
    ids={f'EK-{n:04d}' for n in range(1,20)}
    if {r['id'] for r in b['records']}!=ids or any(set(r)!=set(FIELDS) for r in b['records']):raise ValueError('baseline identity/fields')
    if len({r.get('id') for r in rows})!=len(rows):raise ValueError('duplicate ID')
    same_fields(b['records'],[r for r in rows if r.get('id') in ids],'fourth intake existing19')
    return 684


class Batch04(unittest.TestCase):
    def test_baseline_matches_actual_main_commit(self):
        source=json.loads(subprocess.check_output(['git','show',SOURCE+':prototype/eikyouki/eikyouki_records.json'],cwd=BASE))['records']
        b=json.loads((BASE/'baselines/existing19-batch04.json').read_text())['records']
        same_fields(source,b,'fixed main baseline')
        self.assertEqual(684,preserve19(DATA['records']))

    def test_preservation_rejects_all_684_value_and_type_mutations(self):
        for i in range(19):
            for field in FIELDS:
                with self.subTest(id=DATA['records'][i]['id'],field=field):
                    rows=copy.deepcopy(DATA['records']);v=rows[i][field]
                    rows[i][field]=not v if type(v) is bool else (float(v) if type(v) is int else ('CORRUPTED' if v is None else None))
                    with self.assertRaises(ValueError):preserve19(rows)
        for rows in ([],DATA['records'][1:],DATA['records']+[DATA['records'][18]]):
            with self.assertRaises(ValueError):preserve19(rows)
        extra=dict(DATA['records'][-1],id='EK-9999',source_order=9999)
        self.assertEqual(684,preserve19(list(reversed(DATA['records']+[extra]))))

    def test_seven_independent_new_records(self):
        rows=DATA['records'][19:26]
        self.assertEqual([f'EK-{n:04d}' for n in range(20,27)],[r['id'] for r in rows])
        self.assertEqual(list(range(20,27)),[r['source_order'] for r in rows])
        for r in rows:
            validate_record(r)
            self.assertEqual(36,len(r));self.assertIsNone(r['full_original_text'])
            self.assertIsNone(r['research_date_start']);self.assertIsNone(r['research_date_basis'])
            self.assertIn('oldid=218476',r['source_url']);self.assertIn('底本未照合',r['entry_status'])

    def test_five_unresolved_dates_keep_partial_original(self):
        rows=DATA['records'][19:24]
        self.assertEqual(['相州へ御動座の時','（日付明記なし・編集注）','同四日','同四日','同月十九日'],[r['original_date'] for r in rows])
        fields=('era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','julian_start','julian_end','gregorian_start','gregorian_end','date_conversion_source_url')
        for r in rows:
            self.assertEqual(('unknown','unresolved'),(r['date_precision'],r['date_conversion_status']))
            for f in fields:
                self.assertIsNone(r[f])
                changed=copy.deepcopy(r);changed[f]='1438-10-01' if 'start' in f or 'end' in f else (False if f=='lunar_is_leap' else 10)
                with self.subTest(id=r['id'],illegal_completion=f):
                    with self.assertRaises(ValueError):validate_record(changed)
        # Valid-looking but unsupported supplementation must still differ from the recorded intake.
        fabricated=copy.deepcopy(rows);fabricated[0]=dict(DATA['records'][24],id='EK-0020',source_order=20)
        with self.assertRaises(ValueError):same_fields(rows,fabricated,'unapproved intake revision')

    def test_november_first_two_separate_entries(self):
        for r in DATA['records'][24:26]:
            self.assertEqual(('同十一月一日',10,11,1,'1438-11-18','1438-11-27','provisional'),(r['original_date'],r['era_year'],r['lunar_month'],r['lunar_day'],r['julian_start'],r['gregorian_start'],r['date_conversion_status']))
        self.assertNotEqual(DATA['records'][24]['summary'],DATA['records'][25]['summary'])
        d=copy.deepcopy(DATA);d['records'][25]['id']=d['records'][24]['id']
        with self.assertRaises(ValueError):validate_data(d)
