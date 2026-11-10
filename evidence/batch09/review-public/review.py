import json,re,html,hashlib,subprocess,sqlite3,sys,copy,datetime
from pathlib import Path
from urllib.parse import urlparse,parse_qs
import argparse
ap=argparse.ArgumentParser(description='Independent batch09 source/data review; does not edit implementation')
ap.add_argument('--repo-root',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args(); R=args.repo_root.resolve(); O=args.output.resolve(); O.mkdir(parents=True,exist_ok=True)
if (O/'independent-results.json').exists(): raise SystemExit('Refusing to overwrite existing independent-results.json; choose a fresh output directory')
P=R/'prototype/eikyouki'; E=R/'evidence/batch09'
D=json.loads((P/'eikyouki_records.json').read_text()); rows=D['records']; L=json.loads((E/'article-boundaries.json').read_text())
checks=[]
def check(name,condition,detail=None):
 checks.append({'name':name,'pass':bool(condition),'detail':detail}); assert condition,name
sha=lambda b:hashlib.sha256(b).hexdigest()
def plain(s):return html.unescape(re.sub(r'<[^>]*>','',s)).replace('\u200b','').replace('\xa0','').strip()
raw=(E/'source/wikisource-fixed-from-batch08.html').read_text()
anchors=[raw.index('<span class="anchor" id="ei-%d"'%n) for n in [8,9,10]]
check('raw anchor positions',anchors==[106713,119859,124067],anchors)
chapters=[plain(raw[anchors[i]:anchors[i+1]]) for i in [0,1]]
check('chapter headings',all(t.startswith(h) for t,h in zip(chapters,['結城籠城事','村岡合戦事'])))
check('excluded heading absent',all('結城落城の事' not in t for t in chapters))
check('chapter counts',[sum(r['chapter_id']==c for r in rows) for c in ['yuki_siege','muraoka_battle']]==[17,14])
for c,text,rs in zip(['yuki_siege','muraoka_battle'],chapters,[rows[51:68],rows[68:]]):
 end=len("結城籠城事" if c=="yuki_siege" else "村岡合戦事")
 for r in rs:
  s=r['full_original_text']; hits=[m.start() for m in re.finditer(re.escape(s),text)]
  check(r['id']+' unique exact source match',len(hits)==1,hits)
  start=hits[0];check(r['id']+' contiguous coverage',all(ch in '、\n' for ch in text[end:start]) and start>=end)
  a=next(a for a in L['articles'] if a['id']==r['id'])
  check(r['id']+' independent offsets',[start,start+len(s)]==[a['start_offset'],a['end_offset']])
  end=start+len(s)
 check(c+' tail coverage',all(ch in '、\n' for ch in text[end:]))
check('all source annotations survive',all(x in ''.join(r['full_original_text'] for r in rows[51:]) for x in ['苦又芳イ','一（上イ）州','以大草紙補之','捨て大双紙','无イ勝']))
check('sup not silently interpreted as source sentence','<sup>以大草紙補之</sup>' in raw and '<sup>大双紙</sup>' in raw)
old=json.loads(subprocess.check_output(['git','show','40a131e60aecf3c24040ba0fdfe84db9fae1b829:prototype/eikyouki/eikyouki_records.json'],cwd=R))['records']
check('old IDs/order',[r['id'] for r in rows[:51]]==[r['id'] for r in old]);n=0
for a,b in zip(old,rows):
 check(a['id']+' field names',a.keys()==b.keys())
 for k,v in a.items():check(a['id']+'.'+k,type(v)==type(b[k]) and v==b[k]);n+=1
check('old 1836 values',n==1836,n)
payload=json.loads(re.search(r'<script id="payload" type="application/json">(.*?)</script>',(P/'index.html').read_text(),re.S)[1])
check('HTML all 2952 values/order/types',json.dumps(rows,ensure_ascii=False)==json.dumps(payload,ensure_ascii=False))
con=sqlite3.connect((P/'eikyouki.db').as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
actual=[dict(r) for r in con.execute('SELECT a.*,c.heading,c.chapter_url,c.edition_id,e.work_id FROM articles a JOIN chapters c USING(chapter_id) JOIN editions e USING(edition_id) ORDER BY source_order')]
for r,a in zip(rows,actual):
 a['id']=a.pop('article_id');a['chapter']=a.pop('heading');a['source_url']=a.pop('chapter_url');a['lunar_is_leap']=None if a['lunar_is_leap'] is None else bool(a['lunar_is_leap'])
 check(r['id']+' independent SQL fields',r==a and all(type(r[k])==type(a[k]) for k in r))
check('SQL article count',len(actual)==82)
logs=json.loads((E/'source/naoj-retrieval.json').read_text())+json.loads((E/'source/muraoka-naoj-retrieval.json').read_text());check('34 raw NAOJ responses',len(logs)==34)
for l in logs:
 b=(E/'source'/l['file']).read_bytes();p=plain(b.decode('euc-jp'));q=parse_qs(urlparse(l['url']).query)
 check(l['file']+' original hash',sha(b)==l['sha256']);check(l['file']+' request parameters',q['gengo']==['b208'] and q['year']==['12'] and l['status']==200)
 table=re.search(r'<table[^>]*class="result".*?</table>',b.decode('euc-jp'),re.S)[0]
 cells=[plain(x) for x in re.findall(r'<td[^>]*>(.*?)</td>',table,re.S)]
 m,d=int(q['month'][0]),int(q['day'][0]);mode=int(q['jg'][0]);r=next(r for r in rows[51:] if (r['lunar_month'],r['lunar_day'])==(m,d))
 check(l['file']+' result row',cells[:2]==[r['julian_start' if mode==0 else 'gregorian_start'].replace('-','/'),f'永享12年{m:02d}月{d:02d}日'],cells[:2])
 check(l['file']+' calendar label',f'西暦の日付はすべて{"ユリウス" if mode==0 else "グレゴリオ"}暦によります。' in p)
# independent Julian/Gregorian equivalence formula, not implementation calendar helper
for r in rows[51:]:
 if r['lunar_day'] is None:
  check(r['id']+' no inferred dates',r['date_precision']=='unknown' and all(r[k] is None for k in ['era','era_year','western_year','lunar_month','julian_start','julian_end','gregorian_start','gregorian_end']))
 else:
  def jdn(s,g):
   y,m,d=map(int,s.split('-'));a=(14-m)//12;y+=4800-a;m+=12*a-3
   return d+(153*m+2)//5+365*y+y//4-(y//100 if g else 0)+(y//400 if g else 0)-(32045 if g else 32083)
  check(r['id']+' independent JDN',jdn(r['julian_start'],False)==jdn(r['gregorian_start'],True))
check('known/unknown',[sum(r['lunar_day'] is not None for r in rows[51:]),sum(r['lunar_day'] is None for r in rows[51:])]==[17,14])
# Target independent mutations against production contract; imports read only
sys.path.insert(0,str(P));from test_batch09 import contract,preserve
faults={}
def rejection(name,fn):
 try:fn();faults[name]='ACCEPTED'
 except ValueError as e:faults[name]='REJECTED: '+str(e)
for kind in ['boundary_crossing','month_leak','old_bool_type','source_annotation','confirmed_history','confirmed_relationship','unsupported_day']:
 d=copy.deepcopy(D);l=copy.deepcopy(L)
 if kind=='boundary_crossing':l['articles'][16]['end_offset']+=10
 if kind=='month_leak':d['records'][52]['lunar_month']=1
 if kind=='old_bool_type':d['records'][0]['lunar_is_leap']=0
 if kind=='source_annotation':d['records'][61]['full_original_text']=d['records'][61]['full_original_text'].replace('以大草紙補之','')
 if kind=='confirmed_history':d['publication']['articles']['EK-0071']['historical_recognition']='PASS'
 if kind=='confirmed_relationship':d['article_relationships'][0]['relation']='same_event_confirmed'
 if kind=='unsupported_day':d['records'][51]['lunar_day']=14
 rejection(kind,lambda:preserve(d['records']) if kind=='old_bool_type' else contract(d,l))
check('seven independent negative controls',all(v.startswith('REJECTED') for v in faults.values()),faults)
# Explicit limit: a coordinated wrong summary passes correspondence checks. Human original-source review remains needed.
d=copy.deepcopy(D);l=copy.deepcopy(L);bad='一色伊予守が村岡で勝利した。';d['records'][70]['summary']=bad;l['articles'][19]['summary']=bad;l['articles'][19]['layers']['modern_summary']=bad
try:contract(d,l);coupled='ACCEPTED: correspondence is not semantic truth verification'
except ValueError as e:coupled='REJECTED: '+str(e)
report={'reviewed_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'tree':subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=R,text=True).strip(),'checks':checks,'negative_controls':faults,'coupled_semantic_limit':coupled,'source_sha256':sha(raw.encode()),'test_script_sha256':sha(Path(__file__).read_bytes()),'status':'PASS'}
(O/'independent-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS',len(checks),'checks;',coupled)
