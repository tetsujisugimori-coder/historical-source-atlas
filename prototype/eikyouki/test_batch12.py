"""Batch12 fixed transcription, preserved 4212 typed values, and fault controls."""
import copy,hashlib,json,re,sqlite3,subprocess,tempfile,unittest
from pathlib import Path
from html.parser import HTMLParser
from integrity import same_fields,verify
from validation import FIELDS,validate_data
from document_structure import compare_supplementary
B=Path(__file__).resolve().parent;R=B.parents[1];E=R/'evidence/batch12';BASE='ff4d4ec7714c3753c1a98719528a86bb629757b8'
D=json.loads((B/'eikyouki_records.json').read_text());L=json.loads((E/'article-boundaries.json').read_text());OLD=json.loads((B/'baselines/existing117-batch12.json').read_text())['records'];IDS=[f'EK-{i:04d}' for i in range(118,130)]
BOUNDS=[9,110,127,627,697,722,760,810,865,897,997,1075,1162]
SOURCE_SHA='cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0';CHAPTER_SHA='eaf30216e1fdb714fdbcf3a22dd89c98369de69fc1f2799116747f09eeea6bf5'
def contract(d,l=L):
 rows=validate_data(d);same_fields(OLD,rows[:117],'117 prior records')
 if len(rows)!=129 or [r['id']for r in rows[117:]]!=IDS:raise ValueError('batch12 count/identities')
 if [r['id'] for r in rows[:117]]!=[r['id'] for r in OLD]:raise ValueError('prior ordering')
 chapter=(E/'source/chapter.txt').read_text()
 if hashlib.sha256(chapter.encode()).hexdigest()!=CHAPTER_SHA or l['chapter_sha256']!=CHAPTER_SHA or l['header']!='堀越御所御下向之事' or l['next_chapter']!='京都軍之事':raise ValueError('chapter boundary/hash')
 if len(l['articles'])!=12 or l['historical_recognition']!='NOT_TESTED':raise ValueError('ledger status/count')
 for i,(r,a) in enumerate(zip(rows[117:],l['articles'])):
  same_fields([a['record']],[r],'new values')
  if (a['start_offset'],a['end_offset'])!=(BOUNDS[i],BOUNDS[i+1]) or a['id']!=r['id']:raise ValueError('coverage')
  raw=chapter[BOUNDS[i]:BOUNDS[i+1]]
  if raw!=r['full_original_text'] or raw!=a['source_text']:raise ValueError('source text')
  pub=d['publication']['articles'][r['id']];nar=raw
  for n in a['annotations']:
   if chapter[n['start_offset']:n['end_offset']]!=n['text']:raise ValueError('annotation bounds')
   nar=nar.replace(n['text'],'',1)
  if nar!=a['narrative_text'] or pub['narrative_text']!=nar or pub['annotations']!=a['annotations']:raise ValueError('source layers')
  if any(pub[k]!='NOT_TESTED' for k in ['base_image','variants','transcription_emendation','historical_recognition']):raise ValueError('false scholarly verification')
  if r['id']!='EK-0120' and any(r[k]is not None for k in ['era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','julian_start','julian_end','gregorian_start','gregorian_end','research_date_start','research_date_end']):raise ValueError('date propagation')
 if '堀越御所御下向之事'+''.join(r['full_original_text'] for r in rows[117:])!=chapter:raise ValueError('full coverage')
 if 'EK-0119で御教書として導入' not in d['narrative_references'][3]['evidence_note'] or 'EK-0114' not in d['narrative_references'][3]['evidence_note']:raise ValueError('reference evidence scope')
 if len(d['document_structures'])!=1:raise ValueError('one quoted document')
 if d['document_structures'][0]!=l['quoted_document']:raise ValueError('document ledger mismatch')
 if d['narrative_references']!=l['narrative_references']:raise ValueError('reference ledger mismatch')
 doc=d['document_structures'][0]
 if doc['article_id']!='EK-0120' or (doc['quote']['start_offset'],doc['quote']['end_offset'])!=(127,627):raise ValueError('quote/narrator boundary')
 if [c['start_offset']for c in doc['clauses']]+[doc['clauses'][-1]['end_offset']]!=[158,226,301,392,453,542]:raise ValueError('clause boundaries')
 if [(x['from'],x['to'],x['kind']) for x in d['narrative_references']] != [('EK-0119','EK-0120','document_quote'),('EK-0119','EK-0118','narrative_relative_time'),('EK-0120','EK-0104','same_named_person'),('EK-0120','EK-0114','editorial_cross_reference'),('EK-0123','EK-0104','narrative_continuity'),('EK-0126','EK-0117','same_name_in_transcription'),('EK-0128','EK-0115','narrative_continuity'),('EK-0129','EK-0117','narrative_continuity')]:raise ValueError('reference types')
 return len(rows)
class Batch12(unittest.TestCase):
 def test_baseline_and_all_formats(self):
  original=json.loads(subprocess.check_output(['git','show',BASE+':prototype/eikyouki/eikyouki_records.json'],cwd=R));same_fields(original['records'],OLD,'baseline freeze');self.assertEqual(129,contract(D));self.assertEqual(129,verify(B/'eikyouki_records.json',B/'index.html',B/'eikyouki.db'))
  self.assertEqual(original['article_relationships'],D['article_relationships'])
  for key,value in original['publication']['articles'].items():self.assertEqual(value,D['publication']['articles'][key])
 def test_source_boundaries_independent_extraction(self):
  raw=(R/L['source_file']).read_bytes();self.assertEqual(SOURCE_SHA,hashlib.sha256(raw).hexdigest());s=raw.decode();a=s.index('<span class="anchor" id="ei-12"');b=s.index('<span class="anchor" id="ei-13"')
  class Parser(HTMLParser):
   def __init__(self):super().__init__();self.t=[]
   def handle_data(self,d):self.t.append(d)
  p=Parser();p.feed(s[a:b]);txt=''.join(p.t).replace('\u200b','').replace('\xa0','').strip();self.assertEqual(txt,(E/'source/chapter.txt').read_text());self.assertNotIn('京都軍之事',txt)
  self.assertIn('其書曰',s[a:b]);self.assertIn('class="wst-left"',s[a:b]);self.assertEqual(5,len(D['document_structures'][0]['clauses']))
 def test_4212_preservation_mutations(self):
  for i in range(117):
   for field in FIELDS:
    with self.subTest(article=i,field=field):
     other=copy.deepcopy(OLD);v=other[i][field];other[i][field]=float(v)if type(v)is int else ('FAULT'if v is None else None)
     with self.assertRaises(ValueError):same_fields(OLD,other,'mutated baseline')
 def test_ten_required_fault_categories_and_more(self):
  faults=['chapter-boundary','missing-range','overlap','missing-clause','clause-order','narrator-in-quote','date-propagation','existing-record','invalid-reference','quantity-as-fact','evaluation-as-fact','issuance-as-fact','bad-clause-text','same-event-fabrication','annotation-mixed','corrected-original-date','wrong-reference-evidence','false-base-image','false-source-hash','wrong-document-annotations','clause-meaning-inversion']
  for f in faults:
   with self.subTest(fault=f):
    d=copy.deepcopy(D);l=copy.deepcopy(L)
    if f=='clause-meaning-inversion':d['document_structures'][0]['clauses'][3]['summary']='官軍は互いの遺恨を保ち、和融を拒むよう命じられた。'
    if f=='false-base-image':d['document_structures'][0]['verification']['base_image']='PASS'
    if f=='false-source-hash':d['document_structures'][0]['source_sha256']='0'*64
    if f=='wrong-document-annotations':d['document_structures'][0]['annotations']=[]
    if f=='wrong-reference-evidence':d['narrative_references'][3]['evidence_note']='双方に京都・御教書の記述があるが、同一文書・同一発給とは認定しない。'
    if f=='chapter-boundary':l['next_chapter']='成氏の御事'
    if f=='missing-range':l['articles'][4]['start_offset']+=1
    if f=='overlap':l['articles'][4]['start_offset']-=1
    if f=='missing-clause':d['document_structures'][0]['clauses'].pop()
    if f=='clause-order':d['document_structures'][0]['clauses'].reverse()
    if f=='narrator-in-quote':d['document_structures'][0]['quote']['original_text']='其書曰'+d['document_structures'][0]['quote']['original_text']
    if f=='date-propagation':d['records'][120]['gregorian_start']='1461-11-12'
    if f=='existing-record':d['records'][3]['summary']='FAULT'
    if f=='invalid-reference':d['narrative_references'][0]['to']='EK-9999'
    if f=='quantity-as-fact':d['records'][123]['summary']='山内家の軍勢は実測で二十万騎だった。'
    if f=='evaluation-as-fact':d['records'][126]['summary']='太田氏は確実に智仁勇を兼ね、善政を行った。'
    if f=='issuance-as-fact':d['document_structures'][0]['verification']['historical_issuance']='PASS'
    if f=='bad-clause-text':d['document_structures'][0]['clauses'][0]['original_text']='FAULT'
    if f=='same-event-fabrication':d['narrative_references'][0]['kind']='same_event'
    if f=='annotation-mixed':d['publication']['articles']['EK-0120']['narrative_text']=d['records'][119]['full_original_text']
    if f=='corrected-original-date':d['records'][119]['original_date']='寛正二年〈辛巳〉十月日'
    with self.assertRaises((ValueError,KeyError)):contract(d,l)
 def test_month_not_day_and_naoj_evidence(self):
  r=D['records'][119];self.assertEqual((r['date_kind'],r['date_precision'],r['western_year'],r['lunar_day']),('document_date','month',1461,None));self.assertEqual((r['julian_start'],r['julian_end'],r['gregorian_start'],r['gregorian_end']),('1461-11-03','1461-12-01','1461-11-12','1461-12-10'));self.assertEqual('寛正二年〈幸巳〉十月日',r['original_date']);self.assertEqual(11,sum(x['western_year']is None for x in D['records'][117:]));self.assertIn('辛巳',r['date_conversion_note'])
  for m in json.loads((E/'calendar/retrieval.json').read_text()):
   raw=(E/'calendar'/m['file']).read_bytes();self.assertEqual(m['status'],200);self.assertEqual(m['sha256'],hashlib.sha256(raw).hexdigest());self.assertIn('辛巳',raw.decode('euc_jp'));self.assertIn('寛正',raw.decode('euc_jp'))
  for patch in [{'date_precision':'day','lunar_day':1},{'gregorian_end':'1461-12-11'},{'gregorian_start':'1461-11-11'},{'western_year':1462}]:
   d=copy.deepcopy(D);d['records'][119].update(patch)
   with self.assertRaises(ValueError):validate_data(d)
 def test_sqlite_clause_search_and_tamper(self):
  with sqlite3.connect(B/'eikyouki.db') as con:
   self.assertEqual([('EK-0120-C04',)],con.execute("SELECT clause_id FROM document_clauses WHERE summary LIKE '%和融%' ORDER BY clause_order").fetchall())
   self.assertEqual(5,con.execute('SELECT count(*) FROM document_clauses').fetchone()[0]);compare_supplementary(D,con)
   mem=sqlite3.connect(':memory:');con.backup(mem)
  mem.execute("UPDATE document_clauses SET summary='FAULT' WHERE clause_order=1")
  with self.assertRaises(ValueError):compare_supplementary(D,mem)
  mem.close()
 def test_prior_evidence_unchanged(self):
  for path in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'evidence'],cwd=R,text=True).splitlines():
   with self.subTest(path=path):self.assertEqual(subprocess.check_output(['git','show',BASE+':'+path],cwd=R),(R/path).read_bytes())
