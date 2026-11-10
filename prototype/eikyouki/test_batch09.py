"""Batch09 source contract, 51-record preservation, independent-format and fault controls."""
import copy,hashlib,json,re,sqlite3,subprocess,unittest
from html.parser import HTMLParser
from pathlib import Path
from integrity import same_fields,verify
from validation import FIELDS,validate_data,validate_record
B=Path(__file__).resolve().parent; ROOT=B.parents[1]; E=ROOT/'evidence/batch09'
D=json.loads((B/'eikyouki_records.json').read_text());L=json.loads((E/'article-boundaries.json').read_text())
IDS=[f'EK-{i:04d}' for i in range(52,83)]
DATE_FIELDS=['era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','date_precision','julian_start','julian_end','gregorian_start','gregorian_end','date_conversion_status','date_conversion_source_url','date_conversion_note']
def preserve(rows):
 raw=(B/'baselines/existing51-batch09.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!='96e9f37ef5e7044b1a80a7afb6d86410ea3f263a00329e80a6b02d4af5329b09':raise ValueError('baseline hash')
 old=json.loads(raw)['records'];ids=[r['id'] for r in rows]
 if len(ids)!=len(set(ids)) or ids[:51]!=[r['id'] for r in old]:raise ValueError('old identities/order')
 same_fields(old,rows[:51],'old 1836 fields');return 1836

def contract(data,ledger=L):
 rows=validate_data(data);new=[r for r in rows if r['id'] in IDS]
 if [r['id'] for r in new]!=IDS or len(rows)!=82:raise ValueError('batch09 IDs/count/order')
 if ledger.get('historical_recognition')!='NOT_TESTED' or [a['id'] for a in ledger['articles']]!=IDS:raise ValueError('ledger identities/history')
 chapters={c['chapter_id']:(E/c['file']).read_text() for c in ledger['chapters']};coverage={c['chapter_id']:set(range(len(c['header']))) for c in ledger['chapters']}
 chapter=chapters['yuki_siege']
 if hashlib.sha256(chapter.encode()).hexdigest()!='e9bb221f6128609aaffbd124323bdb9cf3a968a4ad152c59e4816d5552083400':raise ValueError('chapter hash')
 for r,a in zip(new,ledger['articles']):
  chapter=chapters[a['chapter_id']];covered=coverage[a['chapter_id']]
  if r['source_order']!=int(r['id'][3:]) or r['entry_status']!='仮登録・公開翻刻照合済み・底本未照合':raise ValueError('status/order')
  if r['chapter_id']!=a['chapter_id'] or r['source_url']!=a['source_url']:raise ValueError('chapter/source')
  for f,k in [('summary','summary'),('short_locator','begin'),('original_date','original_date'),('date_interpretation','interpretation'),('full_original_text','source_text'),('people_in_text','people_source_form'),('location_in_text','place_source_form')]:
   if r[f]!=a[k]:raise ValueError('source correspondence '+f)
  if a['end'] not in r['editorial_note'] or a['boundary'] not in r['editorial_note'] or a['annotation_note'] not in r['editorial_note']:raise ValueError('source annotations')
  start,end=a['start_offset'],a['end_offset']
  if type(start) is not int or type(end) is not int or not 5<=start<end<=len(chapter):raise ValueError('range')
  if set(range(start,end))&covered:raise ValueError('overlapping boundaries')
  covered.update(range(start,end));raw=chapter[start:end]
  if raw!=a['source_text'] or not raw.startswith(a['begin']) or not raw.endswith(a['end']):raise ValueError('source offsets')
  if a['layers']!={'source_statement':raw,'modern_summary':a['summary'],'editorial_inference':a['interpretation'],'historical_recognition':'NOT_TESTED'}:raise ValueError('three layers')
  if (r['lunar_month'],r['lunar_day'])!=(a['lunar_month'],a['lunar_day']):raise ValueError('date propagation')
  if a['lunar_day'] is None:
   if r['date_precision']!='unknown' or any(r[f] is not None for f in ['era','era_year','western_year','julian_start','gregorian_start']):raise ValueError('unknown date')
  elif (r['era_year'],r['lunar_is_leap'],r['julian_start'],r['gregorian_start'],r['date_conversion_status'])!=(12,False,a['conversion']['julian'],a['conversion']['gregorian'],'provisional'):raise ValueError('known date')
  if '史実認定NOT_TESTED' not in r['editorial_note']:raise ValueError('historical certainty')
  pub=data['publication']['articles'][r['id']]
  for k in ['base_image','variants','historical_recognition']:
   if pub[k]!='NOT_TESTED':raise ValueError('publication certainty')
  if pub['location']!='UNRESOLVED' or pub['annotation_note']!=a['annotation_note'] or pub['revision']!=218476:raise ValueError('publication provenance')
 for c in ledger['chapters']:
  chapter=chapters[c['chapter_id']];covered=coverage[c['chapter_id']]
  if hashlib.sha256(chapter.encode()).hexdigest()!=c['sha256']:raise ValueError('chapter hash')
  if any(chapter[i] not in '、\n' for i in set(range(len(chapter)))-covered):raise ValueError('unrecorded source span')
 if data['article_relationships']!=D['article_relationships']:raise ValueError('relationship candidate changed')
 return new

class Batch09(unittest.TestCase):
 def test_baseline_source_and_correspondence(self):
  actual=json.loads(subprocess.check_output(['git','show','40a131e60aecf3c24040ba0fdfe84db9fae1b829:prototype/eikyouki/eikyouki_records.json'],cwd=ROOT))['records'];same_fields(actual,D['records'][:51],'git baseline')
  self.assertEqual(1836,preserve(D['records']));self.assertEqual(31,len(contract(D)));self.assertEqual(82,verify(B/'eikyouki_records.json',B/'index.html',B/'eikyouki.db'))
 def test_existing_1836_single_field_faults(self):
  for i in range(51):
   for f in FIELDS:
    with self.subTest(id=i,field=f):
     rows=copy.deepcopy(D['records']);v=rows[i][f];rows[i][f]=not v if type(v) is bool else (float(v) if type(v) is int else ('FAULT' if v is None else None))
     with self.assertRaises(ValueError):preserve(rows)
 def test_new_1116_cross_format_faults(self):
  expected=D['records'][51:]
  for i in range(31):
   for f in FIELDS:
    with self.subTest(id=i,field=f):
     rows=copy.deepcopy(expected);v=rows[i][f];rows[i][f]=not v if type(v) is bool else ('FAULT' if v is None else None)
     with self.assertRaises(ValueError):same_fields(expected,rows,'new fields')
 def test_negative_source_dates_layers(self):
  faults=['duplicate','missing','order','offset','chapter-overrun','summary','original','historical','pub-history','pub-base','pub-variant','pub-location','annotation','date-propagation','source','ledger-missing','event-merging','bad-type','bad-date','source-order']
  for fault in faults:
   with self.subTest(fault=fault):
    d=copy.deepcopy(D);l=copy.deepcopy(L);r=d['records'][52]
    if fault=='duplicate':r['id']=d['records'][51]['id']
    if fault=='missing':d['records'].pop()
    if fault=='order':d['records'][51:]=reversed(d['records'][51:])
    if fault=='offset':l['articles'][0]['end_offset']+=1
    if fault=='chapter-overrun':l['articles'][-1]['end_offset']+=5
    if fault=='summary':r['summary']='史実として確定した。'
    if fault=='original':r['full_original_text']='村岡合戦事'
    if fault=='historical':l['articles'][0]['layers']['historical_recognition']='PASS'
    if fault.startswith('pub-'):
     key={'pub-history':'historical_recognition','pub-base':'base_image','pub-variant':'variants','pub-location':'location'}[fault];d['publication']['articles']['EK-0052'][key]='PASS'
    if fault=='annotation':d['records'][61]['editorial_note']='補記なし'
    if fault=='date-propagation':
     for f in DATE_FIELDS:r[f]=d['records'][51][f]
     validate_record(r)
    if fault=='source':r['source_url']=r['source_url'].replace('ei-8','ei-9')
    if fault=='ledger-missing':l['articles'].pop()
    if fault=='event-merging':d['article_relationships'][0]['relation']='same_event_confirmed'
    if fault=='bad-type':r['source_order']=53.0
    if fault=='bad-date':d['records'][51]['gregorian_start']='1440-02-31'
    if fault=='source-order':r['source_order']=9999
    with self.assertRaises(ValueError):contract(d,l)
 def test_naoj_original_responses(self):
  logs=json.loads((E/'source/naoj-retrieval.json').read_text())+json.loads((E/'source/muraoka-naoj-retrieval.json').read_text());self.assertEqual(34,len(logs))
  for log in logs:
   with self.subTest(file=log['file']):
    raw=(E/'source'/log['file']).read_bytes();self.assertEqual(200,log['status']);self.assertEqual(log['sha256'],hashlib.sha256(raw).hexdigest())
  for r in D['records'][51:]:
   if r['lunar_day']:
    for mode,field in [(0,'julian_start'),(1,'gregorian_start')]:
     raw=(E/f"source/naoj-{r['lunar_month']}-{r['lunar_day']}-{mode}.html").read_bytes().decode('euc-jp')
     self.assertIn(r[field].replace('-','/'),raw);self.assertIn(f"永享12年{r['lunar_month']:02d}月{r['lunar_day']:02d}日",raw)
 def test_raw_source_extract_and_boundary(self):
  class Text(HTMLParser):
   def __init__(self):super().__init__();self.parts=[]
   def handle_data(self,s):self.parts.append(s)
  raw=(E/'source/wikisource-fixed-from-batch08.html').read_text();self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),'cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0')
  start=raw.index('<span class="anchor" id="ei-8"');end=raw.index('<span class="anchor" id="ei-9"');p=Text();p.feed(raw[start:end]);plain=''.join(p.parts).replace('\u200b','').replace('\xa0','').strip();self.assertEqual(plain,(E/'source/chapter.txt').read_text().strip())
  self.assertIn('以大草紙補之',(E/'source/interpolation-annotation.html').read_text());self.assertLess(end,raw.index('<span class="anchor" id="ei-10"'));p=Text();p.feed(raw[end:raw.index('<span class="anchor" id="ei-10"')]);self.assertEqual(''.join(p.parts).replace('\u200b','').replace('\xa0','').strip(),(E/'source/muraoka-chapter.txt').read_text().strip())
 def test_relationship_negative_controls(self):
  for name in ['missing','self','reverse-duplicate','empty-note']:
   with self.subTest(fault=name):
    d=copy.deepcopy(D);r=d['article_relationships'][0]
    if name=='missing':r['article_id_b']='EK-9999'
    if name=='self':r['article_id_b']=r['article_id_a']
    if name=='reverse-duplicate':d['article_relationships'].append(dict(r,article_id_a=r['article_id_b'],article_id_b=r['article_id_a']))
    if name=='empty-note':r['evidence_note']=None
    with self.assertRaises(ValueError):validate_data(d)
 def test_old_evidence_preserved(self):
  baseline=json.loads((E/'baseline/files.json').read_text())
  for path,sha in baseline.items():
   if path.startswith('evidence/'):
    with self.subTest(path=path):self.assertEqual(sha,hashlib.sha256((ROOT/path).read_bytes()).hexdigest())
