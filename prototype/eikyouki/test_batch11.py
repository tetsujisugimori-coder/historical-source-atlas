"""Batch11 full-coverage fixed-source contract and single-fault controls."""
import copy,hashlib,json,re,subprocess,unittest
from pathlib import Path
from html.parser import HTMLParser
from integrity import same_fields,verify
from validation import validate_data,FIELDS
B=Path(__file__).resolve().parent;R=B.parents[1];E=R/'evidence/batch11';BASE='c0dfa1cf4ea4f2b304b0406ac7dfb4730c5c3c41'
D=json.loads((B/'eikyouki_records.json').read_text());L=json.loads((E/'article-boundaries.json').read_text());OLD=json.loads((B/'baselines/existing102-batch11.json').read_text())['records'];IDS=[f'EK-{i:04d}' for i in range(103,118)]
def contract(d,l=L):
 rows=validate_data(d)
 if len(rows)<117 or [r['id'] for r in rows[102:117]]!=IDS:raise ValueError('new identities/count')
 same_fields(OLD,rows[:102],'old values')
 chapter=(E/'source/chapter.txt').read_text();cursor=len('成氏の御事')
 if hashlib.sha256(chapter.encode()).hexdigest()!=l['chapter_sha256']:raise ValueError('chapter hash')
 if l['historical_recognition']!='NOT_TESTED' or len(l['articles'])!=15:raise ValueError('ledger status/count')
 for row,a in zip(rows[102:117],l['articles']):
  same_fields([a['record']],[row],'new values')
  if a['id']!=row['id'] or a['start_offset']!=cursor or not cursor<a['end_offset']<=len(chapter):raise ValueError('boundary')
  raw=chapter[cursor:a['end_offset']];cursor=a['end_offset']
  if raw!=a['source_text'] or raw!=row['full_original_text']:raise ValueError('source mismatch')
  narrative=raw
  for note in a['annotations']:
   if note['kind'] not in ['page_marker','editorial_annotation'] or note['text'] not in narrative:raise ValueError('annotation')
   narrative=narrative.replace(note['text'],'')
  pub=d['publication']['articles'][row['id']]
  if narrative!=a['narrative_text'] or pub['narrative_text']!=narrative or pub['annotations']!=a['annotations']:raise ValueError('annotation layer')
  if any(pub[k]!='NOT_TESTED' for k in ['base_image','variants','historical_recognition']) or pub['current_view_checked_at'] is not None:raise ValueError('false certainty')
  if row['id'] not in ('EK-0105','EK-0111') and any(row[k] is not None for k in ['era','era_year','western_year','lunar_day','julian_start','gregorian_start']):raise ValueError('date propagation')
 if cursor!=len(chapter):raise ValueError('missing chapter tail')
 link=l['narrative_links']
 if len(link)!=1 or (link[0]['from'],link[0]['to'],link[0]['kind'])!=('EK-0106','EK-0107','narrative_juxtaposition_only'):raise ValueError('narrative link')
 for a,b in [('EK-0106','EK-0107'),('EK-0107','EK-0106')]:
  note=d['publication']['articles'][a]['annotation_note']
  if b not in note or '因果関係・同一事件・史実の認定ではない' not in note:raise ValueError('traceability')
 return 117
class Batch11(unittest.TestCase):
 def test_baseline_and_all_formats(self):
  old=json.loads(subprocess.check_output(['git','show',BASE+':prototype/eikyouki/eikyouki_records.json'],cwd=R));same_fields(old['records'],OLD,'baseline');self.assertEqual(117,contract(D));self.assertEqual(len(D['records']),verify(B/'eikyouki_records.json',B/'index.html',B/'eikyouki.db'))
  self.assertEqual(old['article_relationships'],D['article_relationships'])
  for k,v in old['publication']['articles'].items():self.assertEqual(v,D['publication']['articles'][k])
 def test_source_full_coverage(self):
  raw=(R/L['source_file']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),L['source_sha256']);s=raw.decode();a=s.index('<span class="anchor" id="ei-11"');b=s.index('<span class="anchor" id="ei-12"')
  class Parser(HTMLParser):
   def __init__(self):super().__init__();self.t=[]
   def handle_data(self,d):self.t.append(d)
  p=Parser();p.feed(s[a:b]);text=''.join(p.t).replace('\u200b','').replace('\xa0','').strip();self.assertEqual(text,(E/'source/chapter.txt').read_text());self.assertNotIn('堀越御所御下向之事',text)
  self.assertEqual('成氏の御事'+''.join(x['full_original_text'] for x in D['records'][102:117]),text)
 def test_3672_preservation_mutations(self):
  for i in range(102):
   for f in FIELDS:
    with self.subTest(id=i,field=f):
     rows=copy.deepcopy(OLD);v=rows[i][f];rows[i][f]=float(v) if type(v)is int else ('FAULT' if v is None else None)
     with self.assertRaises(ValueError):same_fields(OLD,rows,'mutation')
 def test_faults(self):
  for fault in ['boundary','id','date','old','tail','annotation','causation','traceability','certainty']:
   with self.subTest(fault=fault):
    d=copy.deepcopy(D);l=copy.deepcopy(L)
    if fault=='boundary':l['articles'][-1]['end_offset']+=1
    if fault=='id':d['records'][103]['id']='EK-0103'
    if fault=='date':d['records'][105]['gregorian_start']='1441-07-21'
    if fault=='old':d['records'][0]['summary']='FAULT'
    if fault=='tail':l['articles'][-1]['end_offset']-=1
    if fault=='annotation':d['publication']['articles']['EK-0113']['narrative_text']=d['records'][112]['full_original_text']
    if fault=='causation':l['narrative_links'][0]['kind']='caused'
    if fault=='traceability':d['publication']['articles']['EK-0106']['annotation_note']='none'
    if fault=='certainty':d['publication']['articles']['EK-0106']['historical_recognition']='PASS'
    with self.assertRaises(ValueError):contract(d,l)
 def test_dates_and_narrative(self):
  a,b=D['records'][104],D['records'][110];self.assertEqual((a['julian_start'],a['gregorian_start']),('1441-07-12','1441-07-21'));self.assertEqual((b['western_year'],b['julian_start'],b['gregorian_start']),(1454,'1455-01-15','1455-01-24'));self.assertEqual(13,sum(r['gregorian_start']is None for r in D['records'][102:117]));self.assertIn('とそ聞えし',D['records'][111]['full_original_text']);self.assertIn('伝聞',D['records'][111]['date_interpretation']);self.assertIn('四ヶ年',D['records'][112]['full_original_text']);self.assertIn('三十余年',D['records'][115]['full_original_text'])
 def test_all_prior_evidence_unchanged(self):
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'evidence'],cwd=R,text=True).splitlines()
  for p in paths:
   with self.subTest(path=p):self.assertEqual(subprocess.check_output(['git','show',BASE+':'+p],cwd=R),(R/p).read_bytes())
