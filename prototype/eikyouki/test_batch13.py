"""Batch13: two narrative records, typed preservation, source/date fault controls."""
import copy,hashlib,json,subprocess,unittest
from pathlib import Path
from html.parser import HTMLParser
from integrity import same_fields,verify
from validation import FIELDS,validate_data,calendar_day
B=Path(__file__).resolve().parent;R=B.parents[1];E=R/'evidence/batch13'
BASE='3e56d13d77048d056e79c6971e6e7d24ad92b4ff'
D=json.loads((B/'eikyouki_records.json').read_text());L=json.loads((E/'article-boundaries.json').read_text());OLD=json.loads((B/'baselines/existing129-batch13.json').read_text())
SOURCE_SHA='cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0'
CHAPTER_SHA='c5e57af30f58c5f99c57f44444a278c62be11630c4f4fd4c7733205701a53a16'
def contract(d,l=L):
 rows=validate_data(d);same_fields(OLD['records'],rows[:129],'129 prior records')
 if len(rows)!=131 or [r['id'] for r in rows[129:]]!=['EK-0130','EK-0131']:raise ValueError('batch13 identities/count')
 for key in ['metadata','article_relationships','document_structures']:
  if d[key]!=OLD[key]:raise ValueError('prior supplementary data')
 if d['narrative_references'][:8]!=OLD['narrative_references']:raise ValueError('prior references')
 for k,v in OLD['publication'].items():
  if k!='articles' and d['publication'][k]!=v:raise ValueError('prior publication metadata')
 for k,v in OLD['publication']['articles'].items():
  if d['publication']['articles'][k]!=v:raise ValueError('prior publication article')
 chapter=(E/'source/chapter.txt').read_text()
 if (l['source_file'],l['source_sha256'],l['revision'])!=('evidence/batch08/source/wikisource-fixed.html',SOURCE_SHA,218476):raise ValueError('fixed source provenance')
 if hashlib.sha256(chapter.encode()).hexdigest()!=CHAPTER_SHA or l['chapter_sha256']!=CHAPTER_SHA:raise ValueError('chapter hash')
 if (l['header'],l['previous_chapter'],l['next_chapter'])!=('京都軍之事','堀越御所御下向之事','古河城の事'):raise ValueError('chapter boundaries')
 if len(l['articles'])!=2 or l['historical_recognition']!='NOT_TESTED':raise ValueError('ledger status/count')
 for r,a,bounds in zip(rows[129:],l['articles'],[(5,58),(58,300)]):
  same_fields([a['record']],[r],'new values')
  if a['id']!=r['id'] or (a['start_offset'],a['end_offset'])!=bounds:raise ValueError('article boundaries')
  if a['source_text']!=chapter[slice(*bounds)] or r['full_original_text']!=a['source_text']:raise ValueError('source transcription')
  pub=d['publication']['articles'][r['id']]
  if pub!=a['publication']:raise ValueError('publication ledger')
  nar=a['source_text']
  for n in a['annotations']:
   if chapter[n['start_offset']:n['end_offset']]!=n['text']:raise ValueError('annotation bounds')
   nar=nar.replace(n['text'],'',1)
  if nar!=a['narrative_text'] or pub['narrative_text']!=nar or pub['annotations']!=a['annotations']:raise ValueError('annotation separation')
  if any(pub[k]!='NOT_TESTED' for k in ['base_image','variants','transcription_emendation','historical_recognition']) or pub['location']!='UNRESOLVED':raise ValueError('unverified claims')
  if a['layers']!={'SOURCE_STATEMENT':r['full_original_text'],'MODERN_SUMMARY':r['summary'],'HISTORICAL_RECOGNITION':'NOT_TESTED'}:raise ValueError('three layers')
 if '京都軍之事'+''.join(r['full_original_text'] for r in rows[129:])!=chapter:raise ValueError('full coverage')
 if d['narrative_references'][8:]!=l['narrative_references'] or len(d['narrative_references'])!=9:raise ValueError('new reference ledger')
 ref=d['narrative_references'][-1]
 if (ref['from'],ref['to'],ref['kind'])!=('EK-0131','EK-0130','narrative_continuity'):raise ValueError('reference direction/type')
 r=rows[130]
 for k in ['era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap','julian_start','julian_end','gregorian_start','gregorian_end','research_date_start','research_date_end']:
  if r[k]is not None:raise ValueError('hearsay date propagation')
 if not r['full_original_text'].startswith('其由来を伝聞くに') or not r['full_original_text'].endswith('とそ聞えし、'):raise ValueError('hearsay envelope')
 return len(rows)

class Batch13(unittest.TestCase):
 def test_baseline_and_formats(self):
  raw=subprocess.check_output(['git','show',BASE+':prototype/eikyouki/eikyouki_records.json'],cwd=R)
  self.assertEqual(json.loads(raw),OLD);self.assertEqual(hashlib.sha256(raw).hexdigest(),json.loads((E/'baseline.json').read_text())['original_data_sha256'])
  self.assertEqual(131,contract(D));self.assertEqual(131,verify(B/'eikyouki_records.json',B/'index.html',B/'eikyouki.db'))
 def test_4644_typed_preservation_mutations(self):
  self.assertEqual(36,len(FIELDS));self.assertEqual(129,len(OLD['records']))
  for i in range(129):
   for field in FIELDS:
    with self.subTest(article=i,field=field):
     other=copy.deepcopy(OLD['records']);v=other[i][field];other[i][field]=float(v) if type(v)is int else ('FAULT' if v is None else None)
     with self.assertRaises(ValueError):same_fields(OLD['records'],other,'mutation')
 def test_direct_source_reextraction(self):
  raw=(R/L['source_file']).read_bytes();self.assertEqual(SOURCE_SHA,hashlib.sha256(raw).hexdigest());s=raw.decode()
  class P(HTMLParser):
   def __init__(self):super().__init__();self.t=[]
   def handle_data(self,d):self.t.append(d)
  p=P();p.feed(s[s.index('<span class="anchor" id="ei-13"'):s.index('<span class="anchor" id="ei-14"')]);txt=''.join(p.t).replace('\u200b','').replace('\xa0','').strip()
  self.assertEqual(txt,(E/'source/chapter.txt').read_text());self.assertEqual(300,len(txt));self.assertNotIn('古河城の事',txt)
  self.assertIn('class="inline-note">〈号今出川義視〉',s);self.assertNotIn('義尚',txt)
 def test_date_independent_response_bytes(self):
  for m,date,calendar in zip(json.loads((E/'calendar/retrieval.json').read_text()),['1467/06/27','1467/07/06'],['ユリウス','グレゴリオ']):
   raw=(E/'calendar'/m['file']).read_bytes();self.assertEqual(200,m['status']);self.assertEqual(m['sha256'],hashlib.sha256(raw).hexdigest());txt=raw.decode('euc_jp')
   for text in [date,'応仁元年05月26日','丁亥',calendar]:self.assertIn(text,txt)
  a,b=D['records'][129:];self.assertEqual(a['original_date'],'応仁元年丁亥五月二十六日');self.assertEqual(a['gregorian_start'],'1467-07-06');self.assertEqual(a['julian_start'],'1467-06-27');self.assertEqual(calendar_day(a['gregorian_start'],'gregorian'),calendar_day(a['julian_start'],'julian'));self.assertIsNone(b['western_year']);self.assertEqual(b['date_precision'],'unknown')
 def test_negative_controls(self):
  faults=['gap','overlap','missing','duplicate','old-type','old-relation','old-publication','date-propagation','calendar-confusion','wrong-day','hearsay-cut','asserted-motive','asserted-rebellion','modern-name-in-original','annotation-mixed','false-recognition','false-location','wrong-reference','false-source-hash','false-original-hash','false-revision','false-source-file']
  for f in faults:
   with self.subTest(fault=f):
    d=copy.deepcopy(D);l=copy.deepcopy(L)
    if f=='gap':l['articles'][1]['start_offset']+=1
    if f=='overlap':l['articles'][1]['start_offset']-=1
    if f=='missing':d['records'].pop()
    if f=='duplicate':d['records'].append(copy.deepcopy(d['records'][-1]))
    if f=='old-type':d['records'][0]['source_order']=1.0
    if f=='old-relation':d['article_relationships'].reverse()
    if f=='old-publication':d['publication']['articles']['EK-0129']['location']='CONFIRMED'
    if f=='date-propagation':d['records'][130]['gregorian_start']=d['records'][130]['gregorian_end']='1467-07-06'
    if f=='calendar-confusion':d['records'][129]['gregorian_start']=d['records'][129]['gregorian_end']='1467-06-27'
    if f=='wrong-day':d['records'][129]['lunar_day']=27
    if f=='hearsay-cut':d['records'][130]['full_original_text']=d['records'][130]['full_original_text'][9:]
    if f=='asserted-motive':d['records'][130]['summary']='義政は実子への継承を確実に望んだ。'
    if f=='asserted-rebellion':d['records'][130]['summary']='細川勝元が謀叛したのは史実である。'
    if f=='modern-name-in-original':d['records'][130]['full_original_text']=d['records'][130]['full_original_text'].replace('若君','義尚')
    if f=='annotation-mixed':d['publication']['articles']['EK-0131']['narrative_text']=d['records'][130]['full_original_text']
    if f=='false-recognition':d['publication']['articles']['EK-0131']['historical_recognition']='PASS'
    if f=='false-location':d['publication']['articles']['EK-0130']['location']='CONFIRMED'
    if f=='wrong-reference':d['narrative_references'][-1]['to']='EK-0129'
    if f=='false-source-hash':l['chapter_sha256']='0'*64
    if f=='false-original-hash':l['source_sha256']='0'*64
    if f=='false-revision':l['revision']=1
    if f=='false-source-file':l['source_file']='evidence/batch13/source/chapter.txt'
    with self.assertRaises((ValueError,KeyError)):contract(d,l)
 def test_prior_evidence_byte_preservation(self):
  for path in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'evidence'],cwd=R,text=True).splitlines():
   with self.subTest(path=path):self.assertEqual(subprocess.check_output(['git','show',BASE+':'+path],cwd=R),(R/path).read_bytes())
