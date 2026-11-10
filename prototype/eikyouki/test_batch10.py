"""Batch10 fixed-source contract and independent format/fault checks."""
import copy,hashlib,json,re,subprocess,unittest
from pathlib import Path
from html.parser import HTMLParser
from integrity import same_fields,verify
from validation import FIELDS,validate_data,validate_record
B=Path(__file__).resolve().parent;ROOT=B.parents[1];E=ROOT/'evidence/batch10'
D=json.loads((B/'eikyouki_records.json').read_text());L=json.loads((E/'article-boundaries.json').read_text());IDS=[f'EK-{i:04d}' for i in range(83,103)]
BASE=json.loads((B/'baselines/existing82-batch10.json').read_text())['records']
def preserve(rows):
 if [r['id'] for r in rows[:82]]!=[r['id'] for r in BASE]:raise ValueError('baseline IDs/order')
 same_fields(BASE,rows[:82],'2952 old values');return 2952

def contract(data,ledger=L):
 rows=validate_data(data);preserve(rows)
 if len(rows)<102 or [r['id'] for r in rows[82:102]]!=IDS:raise ValueError('new IDs/count')
 chapter=(E/'source/chapter.txt').read_text()
 if hashlib.sha256(chapter.encode()).hexdigest()!=ledger['chapter_sha256']:raise ValueError('chapter hash')
 if ledger['historical_recognition']!='NOT_TESTED' or [a['id'] for a in ledger['articles']]!=IDS:raise ValueError('ledger identity/history')
 cursor=len('結城落城の事')
 for row,a in zip(rows[82:102],ledger['articles']):
  same_fields([a['record']],[row],'new fields')
  if a['start_offset']!=cursor or not cursor<a['end_offset']<=len(chapter):raise ValueError('gap/overlap/boundary')
  raw=chapter[cursor:a['end_offset']];cursor=a['end_offset']
  if raw!=a['source_text'] or raw!=row['full_original_text']:raise ValueError('raw source')
  narrative=raw
  for annotation in a['annotations']:
   if annotation['kind'] not in ['editorial_annotation','page_marker'] or annotation['text'] not in narrative:raise ValueError('annotation')
   narrative=narrative.replace(annotation['text'],'')
  if narrative!=a['narrative_text'] or '【参ける迄' in narrative:raise ValueError('annotation contamination')
  pub=data['publication']['articles'][row['id']]
  if pub['narrative_text']!=narrative or pub['annotations']!=a['annotations']:raise ValueError('public layer mismatch')
  if any(pub[k]!='NOT_TESTED' for k in ['base_image','variants','historical_recognition']) or pub['location']!='UNRESOLVED':raise ValueError('unwarranted certainty')
  if pub['revision']!=218476 or pub['current_view_checked_at'] is not None or '403' not in pub['acquisition']:raise ValueError('source reuse')
  if a['lunar_day'] is None:
   if any(row[k] is not None for k in ['era','era_year','western_year','lunar_day','gregorian_start','julian_start']):raise ValueError('date propagated')
  elif row['era']!='嘉吉' or row['era_year']!=1 or row['lunar_day']!=a['lunar_day']:raise ValueError('date context')
 if cursor!=len(chapter):raise ValueError('omitted tail')
 if data['article_relationships']!=D['article_relationships']:raise ValueError('candidate relationship')
 return 102
class Batch10(unittest.TestCase):
 def test_preservation_and_all_formats(self):
  old=json.loads(subprocess.check_output(['git','show','f823640e25ded60e16c9eb7585904327be9406e3:prototype/eikyouki/eikyouki_records.json'],cwd=ROOT))
  same_fields(old['records'],BASE,'baseline authenticity');self.assertEqual(2952,preserve(D['records']));self.assertEqual(102,contract(D));self.assertEqual(len(D['records']),verify(B/'eikyouki_records.json',B/'index.html',B/'eikyouki.db'))
  for k,v in old['publication']['articles'].items():self.assertEqual(v,D['publication']['articles'][k])
  self.assertEqual(old['article_relationships'],D['article_relationships'][:len(old['article_relationships'])])
 def test_2952_existing_value_faults(self):
  for i in range(82):
   for field in FIELDS:
    with self.subTest(id=i,field=field):
     rows=copy.deepcopy(D['records']);v=rows[i][field];rows[i][field]=not v if type(v) is bool else (float(v) if type(v) is int else ('FAULT' if v is None else None))
     with self.assertRaises(ValueError):preserve(rows)
 def test_720_new_value_faults(self):
  for i in range(20):
   for field in FIELDS:
    with self.subTest(id=i,field=field):
     rows=copy.deepcopy(D['records'][82:102]);v=rows[i][field];rows[i][field]='FAULT' if v is None else None
     with self.assertRaises(ValueError):same_fields(D['records'][82:102],rows,'new values')
 def test_source_boundary_and_reuse(self):
  raw=(ROOT/L['source_file']).read_bytes();self.assertEqual(L['source_sha256'],hashlib.sha256(raw).hexdigest());s=raw.decode();a=s.index('<span class="anchor" id="ei-10"');b=s.index('<span class="anchor" id="ei-11"');self.assertIn('成氏の御事',s[b:b+400])
  class Parser(HTMLParser):
   def __init__(self):super().__init__();self.parts=[]
   def handle_data(self,x):self.parts.append(x)
  p=Parser();p.feed(s[a:b]);text=''.join(p.parts).replace('\u200b','').replace('\xa0','').strip();self.assertEqual(text,(E/'source/chapter.txt').read_text());self.assertNotIn('成氏の御事',text)
  logs=json.loads((E/'source/retrieval.json').read_text());self.assertEqual(403,logs[0]['status'])
 def test_naoj_five_exact_days(self):
  expected={(4,15):('1441/05/05','1441/05/14'),(4,16):('1441/05/06','1441/05/15'),(4,17):('1441/05/07','1441/05/16'),(5,4):('1441/05/24','1441/06/02'),(5,16):('1441/06/05','1441/06/14')}
  logs=json.loads((E/'source/retrieval.json').read_text())[1:];self.assertEqual(10,len(logs))
  for log in logs:
   with self.subTest(file=log['file']):
    raw=(E/'source'/log['file']).read_bytes();self.assertEqual(200,log['status']);self.assertEqual(log['sha256'],hashlib.sha256(raw).hexdigest());m,d,g=map(int,re.findall(r'\d+',log['file']));self.assertIn(f'<td>{expected[m,d][g]}</td> <td>嘉吉元年{m:02d}月{d:02d}日',raw.decode('euc-jp'))
  self.assertEqual(14,sum(r['gregorian_start'] is None for r in D['records'][82:102]));self.assertEqual(6,sum(r['gregorian_start'] is not None for r in D['records'][82:102]))
 def test_all_source_chapters_and_years_selectable(self):
  html=(B/'index.html').read_text()
  for year in sorted({r['western_year'] for r in D['records'] if r['western_year'] is not None}):
   with self.subTest(year=year):self.assertIn(f'<option value="{year}">',html)
  for chapter in sorted({r['chapter_id'] for r in D['records']}):
   with self.subTest(chapter=chapter):self.assertIn(f'<option value="{chapter}">',html)
 def test_fault_controls(self):
  for fault in ['missing','duplicate','order','offset','overrun','omitted-tail','annotation','pub-annotation','certainty','date','live-claim','era','fire','relationship']:
   with self.subTest(fault=fault):
    d=copy.deepcopy(D);l=copy.deepcopy(L)
    if fault=='missing':d['records'].pop(101)
    if fault=='duplicate':d['records'][101]['id']='EK-0083'
    if fault=='order':d['records'][82:]=reversed(d['records'][82:])
    if fault=='offset':l['articles'][0]['end_offset']+=1
    if fault=='overrun':l['articles'][-1]['end_offset']+=1
    if fault=='omitted-tail':l['articles'][-1]['end_offset']-=1
    if fault=='annotation':l['articles'][15]['narrative_text']=l['articles'][15]['source_text']
    if fault=='pub-annotation':d['publication']['articles']['EK-0098']['annotations']=[]
    if fault=='certainty':d['publication']['articles']['EK-0083']['historical_recognition']='PASS'
    if fault=='date':d['records'][92]['gregorian_start']='1441-05-15'
    if fault=='live-claim':d['publication']['articles']['EK-0083']['current_view_checked_at']='2026-11-10'
    if fault=='era':d['records'][90]['era']='永享'
    if fault=='fire':d['records'][92]['summary']='特定の人物が放火したことは史実である。'
    if fault=='relationship':d['article_relationships'][-1]['relation']='same_event_confirmed'
    with self.assertRaises(ValueError):contract(d,l)
 def test_old_source_evidence_unchanged(self):
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only','f823640e25ded60e16c9eb7585904327be9406e3','evidence'],cwd=ROOT,text=True).splitlines()
  for p in paths:
   with self.subTest(path=p):self.assertEqual(subprocess.check_output(['git','show','f823640e25ded60e16c9eb7585904327be9406e3:'+p],cwd=ROOT), (ROOT/p).read_bytes())
