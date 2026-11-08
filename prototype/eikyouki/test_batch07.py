"""Seventh intake: field-by-field baseline and source-specific boundary contract."""
import copy, hashlib, json, subprocess, unittest
from pathlib import Path
from integrity import same_fields
from validation import FIELDS, validate_data, validate_record
BASE=Path(__file__).resolve().parent
SOURCE='c0263c333c571f95e5cdad103483b1c05f98a79d'
BASELINE_SHA='6d787bcfb42a9ef3e389d3c43c97ac0f37687aa5a79b463654651eb6727b3293'
DATA=json.loads((BASE/'eikyouki_records.json').read_text())
LEDGER=json.loads((BASE.parents[1]/'evidence/batch07/article-boundaries.json').read_text())

def preserve40(rows):
    raw=(BASE/'baselines/existing40-batch07.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=BASELINE_SHA:raise ValueError('baseline hash mismatch')
    b=json.loads(raw)
    if b['source_commit']!=SOURCE or b['field_count']!=36 or len(b['records'])!=40:raise ValueError('baseline provenance')
    expected=[f'EK-{n:04d}' for n in range(1,41)]
    ids=[r.get('id') for r in rows]
    if any(type(i) is not str for i in ids) or len(ids)!=len(set(ids)):raise ValueError('invalid/duplicate ID')
    previous=[r for r in rows if r['id'] in expected]
    if [r['id'] for r in previous]!=expected:raise ValueError('existing order/missing')
    same_fields(b['records'],previous,'seventh intake existing40')
    return 1440

def intake_contract(rows):
    expected=[f'EK-{n:04d}' for n in range(41,47)]
    new=[r for r in rows if r['id'] in expected]
    if [r['id'] for r in new]!=expected:raise ValueError('batch07 identity/order')
    validate_data(dict(DATA,records=rows))
    for r,e in zip(new,LEDGER['articles']):
        if r['source_order']!=int(r['id'][3:]):raise ValueError('batch07 source order')
        if r['chapter_id']!='mochiuji_death' or r['source_url']!=LEDGER['source_url']:raise ValueError('batch07 chapter/source')
        for f,ef in [('short_locator','begin'),('summary','summary'),('original_date','original_date'),('date_interpretation','interpretation')]:
            if r[f]!=e[ef]:raise ValueError('batch07 source boundary '+f)
        if e['end'] not in r['editorial_note'] or e['boundary'] not in r['editorial_note']:raise ValueError('batch07 endpoint/reason')
        if e['lunar_day'] is None and r['date_precision']!='unknown':raise ValueError('batch07 forbidden date propagation')
        if e['lunar_day'] is not None and (r['era_year'],r['lunar_month'],r['lunar_day'],r['date_conversion_status'])!=(11,2,e['lunar_day'],'provisional'):raise ValueError('batch07 explicit date')
    return new

class Batch07(unittest.TestCase):
    def test_baseline_matches_merged_main(self):
        actual=json.loads(subprocess.check_output(['git','show',SOURCE+':prototype/eikyouki/eikyouki_records.json'],cwd=BASE))['records']
        b=json.loads((BASE/'baselines/existing40-batch07.json').read_text())['records']
        same_fields(actual,b,'fixed main');self.assertEqual(1440,preserve40(DATA['records']))
    def test_all_1440_single_field_corruptions(self):
        for i in range(40):
            for f in FIELDS:
                with self.subTest(id=DATA['records'][i]['id'],field=f):
                    rows=copy.deepcopy(DATA['records']);v=rows[i][f];rows[i][f]=not v if type(v) is bool else (float(v) if type(v) is int else ('CORRUPTED' if v is None else None))
                    with self.assertRaises(ValueError):preserve40(rows)
    def test_ids_order_and_append(self):
        for i in range(46):
            with self.subTest(id=DATA['records'][i]['id']):
                rows=copy.deepcopy(DATA['records']);del rows[i]
                with self.assertRaises(ValueError):(preserve40 if i<40 else intake_contract)(rows)
                with self.assertRaises(ValueError):preserve40(DATA['records']+[DATA['records'][i]])
        with self.assertRaises(ValueError):preserve40(list(reversed(DATA['records'])))
        with self.assertRaises(ValueError):intake_contract(DATA['records'][:40]+list(reversed(DATA['records'][40:])))
        self.assertEqual(1440,preserve40(DATA['records']+[dict(DATA['records'][-1],id='EK-9999',source_order=9999)]))
    def test_source_contract_and_unknown_date_propagation(self):
        new=intake_contract(DATA['records']);self.assertEqual(6,len(new))
        for n in [40,42,43,44]:
            r=DATA['records'][n];self.assertEqual('unknown',r['date_precision'])
            for f in ['era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','julian_start','julian_end','gregorian_start','gregorian_end','date_conversion_source_url']:
                self.assertIsNone(r[f])
            rows=copy.deepcopy(DATA['records'])
            for f in ['original_date','era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','date_precision','date_conversion_status','julian_start','julian_end','gregorian_start','gregorian_end','date_conversion_source_url','date_conversion_note']:rows[n][f]=rows[41][f]
            validate_record(rows[n]) # schema-valid date injection must reach the source contract
            with self.assertRaisesRegex(ValueError,'batch07'):intake_contract(rows)
        self.assertIn('御舎弟満貞',new[3]['summary']);self.assertEqual('伝本・校合についての末尾注記。物語内事件ではないため記事数に含めない。',LEDGER['paratext']['classification'])
    def test_calendar_faults_and_naoj_raw(self):
        for index,day,j,g in [(41,10,'1439-03-24','1439-04-02'),(45,28,'1439-04-11','1439-04-20')]:
            r=DATA['records'][index];self.assertEqual((j,g),(r['julian_start'],r['gregorian_start']))
            for mode,value in [(0,j),(1,g)]:
                raw=(BASE.parents[1]/f'evidence/batch07/source/naoj-{day}-{mode}.html').read_bytes().decode('euc-jp')
                self.assertIn(value.replace('-','/'),raw);self.assertIn(f'永享11年02月{day}日',raw)
            for field,value in [('lunar_day',11),('lunar_month',3),('lunar_is_leap',True),('julian_start','1439-03-25'),('gregorian_end','1439-04-03')]:
                bad=copy.deepcopy(r);bad[field]=value
                with self.subTest(id=r['id'],field=field):
                    with self.assertRaises(ValueError):validate_record(bad)
    def test_new_all_216_field_mismatch_detection(self):
        expected=DATA['records'][40:46]
        for i in range(6):
            for f in FIELDS:
                rows=copy.deepcopy(expected);v=rows[i][f];rows[i][f]=not v if type(v) is bool else (float(v) if type(v) is int else ('CORRUPTED' if v is None else None))
                with self.subTest(id=expected[i]['id'],field=f):
                    with self.assertRaises(ValueError):same_fields(expected,rows,'new JSON/SQLite/HTML values')
        for f,v in [('source_url',DATA['records'][39]['source_url']),('chapter_id','mochiuji_tonsure'),('short_locator','憲実出家之事')]:
            rows=copy.deepcopy(DATA['records']);rows[40][f]=v
            with self.assertRaises(ValueError):intake_contract(rows)
