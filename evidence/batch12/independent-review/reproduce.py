"""Independent extraction/preservation plus isolated in-memory adversarial probes.
Run from any directory. Never writes candidate inputs. No network requests.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,subprocess,sys,copy,os,datetime
O=Path(__file__).resolve().parent; R=O.parents[2]; B=R/'prototype/eikyouki'
os.environ['TMPDIR']=str(O/'tmp');(O/'tmp').mkdir(exist_ok=True)
sys.dont_write_bytecode=True;sys.path.insert(0,str(B))
from test_batch12 import contract
D=json.loads((B/'eikyouki_records.json').read_text());L=json.loads((R/'evidence/batch12/article-boundaries.json').read_text())
class Extract(HTMLParser):
 def __init__(self):super().__init__();self.active=False;self.parts=[];self.anchors=[]
 def handle_starttag(self,t,a):
  attrs=dict(a)
  if attrs.get('id') in ['ei-12','ei-13']:
   self.active=attrs['id']=='ei-12';self.anchors.append(attrs['id'])
 def handle_data(self,s):
  if self.active:self.parts.append(s)
raw=(R/'evidence/batch08/source/wikisource-fixed.html').read_bytes();p=Extract();p.feed(raw.decode());chapter=''.join(p.parts).replace('\xa0','').replace('\u200b','').strip()
(O/'independent-chapter.txt').write_text(chapter)
assert p.anchors==['ei-12','ei-13'];assert len(chapter)==1162
assert hashlib.sha256(raw).hexdigest()=='cd120c44ccd7fbd69fbad81d1d5578c91574bdd2e70f21e5c086e915fe2abae0'
assert chapter==(R/'evidence/batch12/source/chapter.txt').read_text()
assert chapter=='堀越御所御下向之事'+''.join(r['full_original_text'] for r in D['records'][117:])
cur=9
for a,r in zip(L['articles'],D['records'][117:]):
 assert a['start_offset']==cur;cur=a['end_offset'];assert chapter[a['start_offset']:cur]==r['full_original_text']==a['source_text']
assert cur==1162
base=json.loads(subprocess.check_output(['git','show','ff4d4ec7714c3753c1a98719528a86bb629757b8:prototype/eikyouki/eikyouki_records.json'],cwd=R))
values=0
for old,new in zip(base['records'],D['records']):
 assert list(old)==list(new)
 for k in old:assert type(old[k]) is type(new[k]) and old[k]==new[k],(old['id'],k);values+=1
assert len(base['records'])==117 and values==4212
assert base['article_relationships']==D['article_relationships']
for k,v in base['publication']['articles'].items():assert v==D['publication']['articles'][k]
results=[]
def probe(name,edit):
 d=copy.deepcopy(D);l=copy.deepcopy(L);edit(d,l)
 try: contract(d,l);result='ACCEPTED'
 except (ValueError,KeyError) as e:result='REJECTED: '+str(e)
 results.append({'probe':name,'result':result})
def summary(d,l):
 bad='山内家の軍勢は実測で二十万騎だった。';d['records'][123]['summary']=bad;l['articles'][6]['record']['summary']=bad;l['articles'][6]['summary']=bad
probe('quantity promotion, synchronized record/ledger',summary)
probe('C04 meaning inverted, no source change',lambda d,l:d['document_structures'][0]['clauses'][3].update(summary='遺恨を保持し互いに争うよう官軍に命じたと記す。'))
probe('reference evidence invented, valid IDs/status',lambda d,l:d['narrative_references'][3].update(evidence_note='双方の原文に同じ署名と花押があり、同一文書である。'))
probe('reference fabricated while preserving checked scope words',lambda d,l:d['narrative_references'][3].update(evidence_note='EK-0119で御教書として導入される引用とEK-0114は、同じ署名と花押によって同一文書と実証済み。'))
def synchronized_clause(d,l):
 bad='遺恨を保持し互いに争うよう官軍に命じたと記す。'
 d['document_structures'][0]['clauses'][3]['summary']=bad
 l['quoted_document']['clauses'][3]['summary']=bad
probe('C04 meaning inverted in both document and ledger',synchronized_clause)
def synchronized_reference(d,l):
 bad='EK-0119で御教書として導入される引用とEK-0114は、同じ署名と花押によって同一文書と実証済み。'
 d['narrative_references'][3]['evidence_note']=bad
 l['narrative_references'][3]['evidence_note']=bad
probe('reference fabricated in both data and ledger, scope words preserved',synchronized_reference)
probe('single-sided summary edit',lambda d,l:d['records'][123].update(summary='軍勢は実測二十万騎。'))
probe('document clause missing',lambda d,l:d['document_structures'][0]['clauses'].pop())
probe('date propagated to death, synchronized ledger',lambda d,l:(d['records'][120].update(western_year=1461),l['articles'][3]['record'].update(western_year=1461)))
probe('old integer changed to float',lambda d,l:d['records'][0].update(source_order=float(d['records'][0]['source_order'])))
probe('historical issuance promoted',lambda d,l:d['document_structures'][0]['verification'].update(historical_issuance='PASS'))
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
calendar=[]
for m in json.loads((R/'evidence/batch12/calendar/retrieval.json').read_text()):
 b=(R/'evidence/batch12/calendar'/m['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==m['sha256'];assert m['status']==200
 q=Text();q.feed(b.decode('euc_jp'));t=' '.join(' '.join(q.parts).split());t=t[t.index('結果 西暦'):];t=t[:t.index('ご利用にあたって')];calendar.append({'file':m['file'],'result_text':t,'sha256':m['sha256']})
report={'input_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [B/'eikyouki_records.json', B/'test_batch12.py', B/'document_structure.py',R/'evidence/batch12/article-boundaries.json']},'working_tree_status':subprocess.check_output(['git','status','--short'],cwd=R,text=True),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'tree':subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=R,text=True).strip(),'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'raw_source_sha256':hashlib.sha256(raw).hexdigest(),'chapter_sha256':hashlib.sha256(chapter.encode()).hexdigest(),'chapter_codepoints':len(chapter),'preserved_typed_values':values,'coverage':'12 contiguous records, one quote, five internal clauses; PASS','calendar':calendar,'probes':results}
(O/'machine-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
