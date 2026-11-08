"""Batch08 immutable prior fields and explicit three-layer/source contract."""
import copy,hashlib,json,subprocess,unittest
from pathlib import Path
from integrity import same_fields
from validation import validate_data,FIELDS,validate_record
B=Path(__file__).resolve().parent
D=json.loads((B/'eikyouki_records.json').read_text())
L=json.loads((B.parents[1]/'evidence/batch08/article-boundaries.json').read_text())
def preserve(rows):
 raw=(B/'baselines/existing46-batch08.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!='cb2340a47409f80ebf8c6f0032ff60625c993ea68d767e0d52c73a87c9db8220':raise ValueError('baseline hash')
 old=json.loads(raw)['records']; ids=[r['id'] for r in rows]
 if len(ids)!=len(set(ids)) or ids[:46]!=[r['id'] for r in old]:raise ValueError('old identity/order')
 same_fields(old,rows[:46],'existing 1656');return 1656
def contract(rows,ledger=L):
 validate_data(dict(D,records=rows));new=rows[46:]
 if [r['id'] for r in new]!=[f'EK-{i:04d}' for i in range(47,52)]:raise ValueError('batch08 IDs/order')
 if ledger.get('historical_recognition')!='NOT_TESTED' or [e.get('id') for e in ledger.get('articles',[])]!=[r['id'] for r in new]:raise ValueError('ledger identities/history')
 chapter=(B.parents[1]/'evidence/batch08/source/chapter.txt').read_text()
 for r,e in zip(new,ledger['articles']):
  if r['source_order']!=int(r['id'][3:]) or r['entry_status']!='仮登録・公開翻刻照合済み・底本未照合':raise ValueError('status/order')
  if r['chapter_id']!='norizane_tonsure' or r['source_url']!=ledger['source_url']:raise ValueError('chapter/source')
  for f,k in [('summary','summary'),('short_locator','begin'),('original_date','original_date'),('date_interpretation','interpretation')]:
   if r[f]!=e[k]:raise ValueError('source correspondence')
  if e['end'] not in r['editorial_note'] or e['boundary'] not in r['editorial_note']:raise ValueError('boundary')
  raw=chapter[e['start_offset']:e['end_offset']]
  if raw!=e['source_text'] or not raw.startswith(e['begin']) or not raw.endswith(e['end']):raise ValueError('source offsets')
  if e['layers']!={'source_statement':raw,'modern_summary':e['summary'],'editorial_inference':e['interpretation'],'historical_recognition':'NOT_TESTED'}:raise ValueError('three layers')
  if r['lunar_month']!=e['lunar_month'] or r['lunar_day']!=e['lunar_day']:raise ValueError('date propagation')
  if '史実認定NOT_TESTED' not in r['editorial_note']:raise ValueError('historical certainty')
 return new
class Batch08(unittest.TestCase):
 def test_baseline_and_source(self):
  old=json.loads(subprocess.check_output(['git','show','df53040457571722320669307025317ef263c764:prototype/eikyouki/eikyouki_records.json'],cwd=B))['records'];same_fields(old,D['records'][:46],'git baseline');self.assertEqual(preserve(D['records']),1656);self.assertEqual(len(contract(D['records'])),5)
 def test_1656_corruptions(self):
  for i in range(46):
   for f in FIELDS:
    with self.subTest(id=i,field=f):
     rows=copy.deepcopy(D['records']);v=rows[i][f];rows[i][f]=not v if type(v) is bool else ('FAULT' if v is None else None)
     with self.assertRaises(ValueError):preserve(rows)
 def test_new_values(self):
  expected=D['records'][46:]
  for i in range(5):
   for f in FIELDS:
    with self.subTest(id=i,field=f):
     rows=copy.deepcopy(expected);rows[i][f]='FAULT' if rows[i][f] is None else None
     with self.assertRaises(ValueError):same_fields(expected,rows,'new cross-format')
 def test_negative_source_and_dates(self):
  for change in ['id','order','source','motive','truth','date','offset','entry-status','source-order','ledger-missing','ledger-history']:
   with self.subTest(change=change):
    rows=copy.deepcopy(D['records']);ledger=copy.deepcopy(L)
    if change=='id':rows[-1]['id']=rows[-2]['id']
    if change=='order':rows[46:]=reversed(rows[46:])
    if change=='source':rows[-1]['source_url']=rows[45]['source_url']
    if change=='motive':rows[46]['summary']='憲実は罪を謝すために出家した。'
    if change=='truth':ledger['articles'][0]['layers']['historical_recognition']='PASS'
    if change=='date':
     for f in ['era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','date_precision','julian_start','julian_end','gregorian_start','gregorian_end','date_conversion_status','date_conversion_source_url','date_conversion_note']:rows[46][f]=rows[48][f]
     validate_record(rows[46])
    if change=='entry-status':rows[46]['entry_status']='校訂済み・史実確認済み'
    if change=='source-order':rows[46]['source_order']=147
    if change=='ledger-missing':ledger['articles'].pop()
    if change=='ledger-history':ledger['historical_recognition']='PASS'
    if change=='offset':ledger['articles'][0]['end_offset']+=1
    with self.assertRaises(ValueError):contract(rows,ledger)
 def test_naoj_and_missing(self):
  for r in D['records'][48:]:
   for mode,field in [(0,'julian_start'),(1,'gregorian_start')]:
    text=(B.parents[1]/f"evidence/batch08/source/naoj-{r['lunar_month']}-{r['lunar_day']}-{mode}.html").read_bytes().decode('euc-jp')
    self.assertIn(r[field].replace('-','/'),text)
   bad=dict(r,julian_start='1439-01-01')
   with self.assertRaises(ValueError):validate_record(bad)
  for i in range(51):
   with self.subTest(missing=i):
    rows=copy.deepcopy(D['records']);del rows[i]
    with self.assertRaises(ValueError):(preserve if i<46 else contract)(rows)
