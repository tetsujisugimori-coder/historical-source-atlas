"""Independent reviewer checks; deliberately imports no application/test modules."""
import copy,html,json,re,sqlite3,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; P=ROOT/'prototype/eikyouki'; E=ROOT/'evidence/batch10'
D=json.loads((P/'eikyouki_records.json').read_text()); L=json.loads((E/'article-boundaries.json').read_text())
OLD=json.loads(subprocess.check_output(['git','show','f823640:prototype/eikyouki/eikyouki_records.json'],cwd=ROOT))
raw=(ROOT/'evidence/batch08/source/wikisource-fixed.html').read_text()
fragment=raw.split('<span class="anchor" id="ei-10"></span>',1)[1].split('<span class="anchor" id="ei-11"></span>',1)[0]
# Independent HTML lexical stripping, rather than the implementation HTMLParser.
chapter=html.unescape(re.sub(r'<[^>]*>','',fragment)).replace('\u200b','').replace('\xa0','').strip()
assert chapter.startswith('結城落城の事') and chapter.endswith('若君の乳夫二人、徳利文左衛門漆桶三四郎共に出家す')
assert chapter==(E/'source/chapter.txt').read_text()
EXPECTED={91:(4,15),92:(4,16),97:(4,17),98:(4,17),99:(5,4),100:(5,16)}
DATES={}
for m,d in set(EXPECTED.values()):
 DATES[m,d]={}
 for g,cal in [(0,'julian'),(1,'gregorian')]:
  text=(E/f'source/naoj-{m}-{d}-{g}.html').read_bytes().decode('euc-jp')
  table=re.search(r'<tr><td>(\d{4}/\d{2}/\d{2})</td>\s*<td>嘉吉元年(\d{2})月(\d{2})日</td>',text)
  assert table and tuple(map(int,table.groups()[1:]))==(m,d)
  assert ('すべてユリウス暦' if g==0 else 'すべてグレゴリオ暦') in text
  DATES[m,d][cal]=table[1].replace('/','-')
def check(data,ledger):
 rows=data['records']; assert len(rows)==102
 assert json.dumps(rows[:82],ensure_ascii=False,sort_keys=True)==json.dumps(OLD['records'],ensure_ascii=False,sort_keys=True)
 assert [r['id'] for r in rows]==[f'EK-{i:04}' for i in range(1,103)]
 for r in rows:assert len(r)==36 and set(r)==set(OLD['records'][0])
 assert ''.join(r['full_original_text'] for r in rows[82:])==chapter[6:]
 cursor=6
 for r,a in zip(rows[82:],ledger['articles']):
  assert a['start_offset']==cursor
  cursor+=len(r['full_original_text']);assert a['end_offset']==cursor
  assert r['full_original_text']==a['source_text']==chapter[a['start_offset']:cursor]
  n=r['source_order']; pub=data['publication']['articles'][r['id']]
  # Annotation oracle derived from the raw text, not the ledger list.
  expected_annotations=re.findall(r'【[^】]*】|○〔以下大〕',r['full_original_text'])
  assert [x['text'] for x in a['annotations']]==expected_annotations
  narrative=re.sub(r'【[^】]*】|○〔以下大〕','',r['full_original_text'])
  assert narrative==a['narrative_text']==pub['narrative_text']
  if n in EXPECTED:
   m,d=EXPECTED[n];assert (r['era'],r['era_year'],r['lunar_month'],r['lunar_day'])==('嘉吉',1,m,d)
   for cal in ['julian','gregorian']:assert r[cal+'_start']==r[cal+'_end']==DATES[m,d][cal]
  else:
   assert all(r[k] is None for k in ['era','era_year','western_year','lunar_month','lunar_day','julian_start','julian_end','gregorian_start','gregorian_end'])
 assert cursor==len(chapter)
check(D,L)
controls={}
for kind in ['source-and-ledger-corruption','old-value','undated-date','dated-end','missing-record','duplicate-id','offset-gap','annotation-misclassification']:
 d=copy.deepcopy(D); l=copy.deepcopy(L)
 if kind=='source-and-ledger-corruption':d['records'][82]['full_original_text']=l['articles'][0]['source_text']='偽文'
 if kind=='old-value':d['records'][0]['summary']='changed'
 if kind=='undated-date':d['records'][92]['gregorian_start']='1441-05-15'
 if kind=='dated-end':d['records'][90]['gregorian_end']='1441-05-15'
 if kind=='missing-record':d['records'].pop()
 if kind=='duplicate-id':d['records'][-1]['id']='EK-0083'
 if kind=='offset-gap':l['articles'][0]['start_offset']=7
 if kind=='annotation-misclassification':l['articles'][15]['annotations']=[]
 try:check(d,l)
 except AssertionError:controls[kind]='REJECTED'
 else:raise AssertionError('missed fault '+kind)
h=(P/'index.html').read_text(); embedded=json.loads(re.search(r'<script[^>]+id="payload"[^>]*>(.*?)</script>',h,re.S)[1]);assert embedded==D['records']
con=sqlite3.connect('file:'+str(P/'eikyouki.db')+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
sql=[dict(r) for r in con.execute('select * from articles order by source_order')]
for r,s in zip(D['records'],sql):
 s['id']=s.pop('article_id')
 c=dict(con.execute('select * from chapters where chapter_id=?',(s['chapter_id'],)).fetchone())
 e=dict(con.execute('select * from editions where edition_id=?',(c['edition_id'],)).fetchone())
 s.update(work_id=e['work_id'],edition_id=c['edition_id'],chapter=c['heading'],source_url=c['chapter_url'])
 if s['lunar_is_leap'] is not None:s['lunar_is_leap']=bool(s['lunar_is_leap'])
 assert json.dumps(r,sort_keys=True)==json.dumps(s,sort_keys=True)
assert len(sql)==102
result={'result':'PASS','base_commit':'f823640','reviewed_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'records':102,'old_records_preserved':82,'old_values_preserved':2952,'new_records':20,'fields_per_record':36,'source_characters':len(chapter)-6,'date_oracle':{f'{m}-{d}':v for (m,d),v in DATES.items()},'dated_records':6,'null_date_records':14,'independent_fault_controls':controls,'json_html_sqlite':'PASS','browser':'NOT_RUN_BY_THIS_REVIEWER'}
print(json.dumps(result,ensure_ascii=False,indent=2))
