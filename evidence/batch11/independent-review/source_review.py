import json,hashlib,subprocess,copy
from pathlib import Path
from html.parser import HTMLParser
R=Path(__file__).resolve().parents[3]; O=Path(__file__).parent
class Extract(HTMLParser):
 def __init__(self):super().__init__();self.active=False;self.parts=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id')=='ei-11':self.active=True
  elif a.get('id')=='ei-12':self.active=False
 def handle_data(self,s):
  if self.active:self.parts.append(s)
p=R/'evidence/batch08/source/wikisource-fixed.html'; x=Extract();x.feed(p.read_text());chapter=''.join(x.parts).replace('\n','').replace('\u200b','').replace('\xa0','').strip()
b=json.loads((R/'evidence/batch11/article-boundaries.json').read_text());d=json.loads((R/'prototype/eikyouki/eikyouki_records.json').read_text());prev=json.loads(subprocess.check_output(['git','show','c0dfa1c:prototype/eikyouki/eikyouki_records.json'],cwd=R)); rows={r['id']:r for r in d['records']};tests=[]
def check(name,ok):tests.append({'check':name,'pass':bool(ok)})
check('saved fixed HTML SHA-256',hashlib.sha256(p.read_bytes()).hexdigest()==b['source_sha256'])
check('independent HTMLParser whole chapter extraction',chapter==(R/'evidence/batch11/source/chapter.txt').read_text())
check('whole chapter covered exactly once in order',chapter==b['header']+''.join(a['source_text'] for a in b['articles']))
check('existing 102 records all fields unchanged from pre-batch git object',prev['records']==d['records'][:102])
check('existing 102 publication metadata unchanged',all(v==d['publication']['articles'][k] for k,v in prev['publication']['articles'].items()))
for a in b['articles']:
 r=rows[a['id']];pub=d['publication']['articles'][a['id']]
 check(a['id']+' independent source slice',chapter[a['start_offset']:a['end_offset']]==r['full_original_text']==a['source_text'])
 check(a['id']+' ledger versus production record',r==a['record'])
 check(a['id']+' separated annotations match publication',pub['annotations']==a['annotations'] and pub['narrative_text']==a['narrative_text'])
def semantic(rs):
 errs=[]
 for n in range(103,118):
  r=rs[f'EK-{n:04d}']
  if n not in (105,111) and any(r[k] is not None for k in ('julian_start','julian_end','gregorian_start','gregorian_end','era_year','western_year','lunar_month','lunar_day')):errs.append(f'{n}: invented absolute date')
 if '聞こえた' not in rs['EK-0112']['summary']:errs.append('112: hearsay lost')
 for n,period in [(113,'四ヶ年'),(116,'三十余年')]:
  if period not in rs[f'EK-{n:04d}']['full_original_text']:errs.append(f'{n}: period lost')
 for n,j,g,y in [(105,'1441-07-12','1441-07-21',1441),(111,'1455-01-15','1455-01-24',1454)]:
  r=rs[f'EK-{n:04d}']
  if (r['julian_start'],r['gregorian_start'],r['western_year'])!=(j,g,y):errs.append(f'{n}: calendar/era year conflation')
 return errs
check('targeted semantic invariants',not semantic(rows))
cases=[]
for label,id,key,val in [('propagate summary date to undated killing','EK-0107','gregorian_start','1441-07-21'),('conflate era corresponding year with converted year','EK-0111','western_year',1455),('convert four-year duration to invented date','EK-0113','gregorian_start','1459-01-24'),('drop hearsay qualifier','EK-0112','summary','成氏は父の復讐のため憲忠を殺した。'),('convert thirty-year rhetoric into dated interval','EK-0116','gregorian_end','1485-01-24')]:
 m=copy.deepcopy(rows);m[id][key]=val;errs=semantic(m);cases.append({'mutation':label,'target':id,'field':key,'value':val,'rejected':bool(errs),'reasons':errs})
result={'reviewed_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'extraction_normalization':'remove LF, U+200B, U+00A0, trim outer whitespace; preserve U+3000 and ordinary internal spaces','checks':tests,'counterexamples':cases,'counterexample_scope':'Independent review oracle only; these are not claims about production validator rejection.','historical_recognition':'NOT_TESTED'}
(O/'source-review-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(O/'independently-extracted-chapter.txt').write_text(chapter)
print(json.dumps({'checks':len(tests),'failures':[t for t in tests if not t['pass']],'counterexamples_rejected':sum(c['rejected'] for c in cases)},ensure_ascii=False))
