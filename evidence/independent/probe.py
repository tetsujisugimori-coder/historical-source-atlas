"""Independent probes: immutable source copy only, no edits to implementation checkout."""
import copy, hashlib, importlib.util, json, re, shutil, sqlite3, subprocess, sys, tempfile
from pathlib import Path

BASE = Path(sys.argv[1]).resolve() / 'prototype/eikyouki'
OUT = Path(sys.argv[2]).resolve()
tempfile.tempdir = str(Path(__file__).resolve().parent)
DATA = json.loads((BASE/'eikyouki_records.json').read_text(encoding='utf8'))
RESULT = {'source': str(BASE), 'python': sys.version, 'sqlite': sqlite3.sqlite_version, 'cases': []}

def run(p, script):
    s = subprocess.run([sys.executable, str(p/script)], capture_output=True, text=True, encoding='utf8', errors='replace')
    return {'exit': s.returncode, 'stdout': s.stdout, 'stderr': s.stderr}

def case(name, mutate=None, after=None):
    with tempfile.TemporaryDirectory(prefix='independent-atlas-') as td:
        p=Path(td)
        for f in BASE.iterdir():
            if f.is_file(): shutil.copy2(f,p/f.name)
        if mutate:
            d=copy.deepcopy(DATA); mutate(d['records'])
            (p/'eikyouki_records.json').write_text(json.dumps(d,ensure_ascii=False),encoding='utf8')
            h=(p/'index.html').read_text(encoding='utf8')
            h=re.sub(r'(<script id="payload" type="application/json">).*?(</script>)',lambda m:m[1]+json.dumps(d['records'],ensure_ascii=False)+m[2],h,flags=re.S)
            (p/'index.html').write_text(h,encoding='utf8')
        b=run(p,'build.py'); item={'name':name,'build':b}
        if b['exit']==0:
            if after: after(p)
            item['check']=run(p,'test_dates.py')
        RESULT['cases'].append(item)

case('baseline')
for name,field,value in [
 ('ignored_work','work_id','NO_SUCH_WORK'),('ignored_edition','edition_id','NO_SUCH_EDITION'),
 ('ignored_chapter','chapter','changed chapter'),('ignored_source','source_url','https://example.invalid/different'),
 ('invalid_julian','julian_start','not-a-date'),('invalid_gregorian','gregorian_start','1437-02-30'),
 ('reversed_julian','julian_start','2000-01-01'),('fractional_month','lunar_month',1.5),
 ('negative_era','era_year',-1),('text_year','western_year','nonsense'),
 ('fractional_leap','lunar_is_leap',0.8),('string_leap','lunar_is_leap','1'),
 ('unknown_with_dates','date_precision','unknown'),('null_id','id',None),
 ('bool_era','era_year',True),('research_invalid','research_date_start','not-a-date'),
 ('research_reversed','research_date_start','2000-01-01'),('whitespace_id','id','  ')]:
    case(name,lambda rows,f=field,v=value:rows[0].__setitem__(f,v))
case('duplicate_id',lambda rows:rows[1].__setitem__('id',rows[0]['id']))

def corrupt(p):
    with sqlite3.connect(p/'eikyouki.db') as c:
        c.execute("UPDATE articles SET summary='CORRUPT',original_date='CORRUPT',julian_start='not-a-date',research_date_start='2000-01-01',research_date_basis='CORRUPT',full_original_text='INVENTED' WHERE article_id='EK-0001'")
    c.close()
case('six_field_corruption',after=corrupt)

# Extract and execute the actual production comparator, not a rewritten equivalent.
h=(BASE/'index.html').read_text(encoding='utf8')
rank='\n'.join(re.findall(r'function (?:dateRank|compareSource|compareChronology)\([^\n]*',h))
sort=re.search(r'filtered\.sort\((.*?)\);',h).group(1)
js="const records="+json.dumps(DATA['records'])+"; let chronological=true; const filtered=records.slice().reverse(); "+rank+"; filtered.sort("+sort+"); console.log(JSON.stringify(filtered.map(r=>r.id)));"
s=subprocess.run(['node','-e',js],capture_output=True,text=True)
RESULT['sort']={'exit':s.returncode,'actual':json.loads(s.stdout) if s.returncode==0 else None,'stderr':s.stderr,'expected':[f'EK-{i:04d}' for i in range(1,13)]+['EK-0015','EK-0013','EK-0014']}

# Direct inserts, including independent whitespace IDs, bypass input validation.
with tempfile.TemporaryDirectory(prefix='independent-id-') as td:
    p=Path(td)
    shutil.copytree(BASE,p/'src'); p=p/'src'; run(p,'build.py')
    sys.path.insert(0,str(p))
    spec=importlib.util.spec_from_file_location('probe_build',p/'build.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    c=sqlite3.connect(p/'eikyouki.db')
    row=dict(DATA['records'][0],article_id=None);row['lunar_is_leap']=0
    sql='INSERT INTO articles('+','.join(mod.ARTICLE_FIELDS)+') VALUES('+','.join('?' for _ in mod.ARTICLE_FIELDS)+')'
    direct=[]
    for i,v in enumerate([None,None,'','  ','EK-independent'],101):
        row.update(article_id=v,source_order=i)
        try: c.execute(sql,[row[k] for k in mod.ARTICLE_FIELDS]); direct.append({'id':v,'accepted':True})
        except Exception as e: direct.append({'id':v,'accepted':False,'error':str(e)})
    RESULT['direct_ids']=direct;c.close()
OUT.write_text(json.dumps(RESULT,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'cases':[(c['name'],c['build']['exit'],c.get('check',{}).get('exit')) for c in RESULT['cases']],'sort':RESULT['sort'],'direct_ids':RESULT['direct_ids']},ensure_ascii=False,indent=2))
