import hashlib,json,shutil,sqlite3,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();here=Path(__file__).resolve().parent
dst=here/sys.argv[2];dst.mkdir(exist_ok=True)
shutil.copytree(root/'prototype',dst/'prototype',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.db','*.tmp'))
(dst/'.git').write_text('gitdir: '+str(root/'.git').replace('\\','/')+'\n')
base=dst/'prototype/eikyouki'
p=subprocess.run([sys.executable,str(base/'build.py')],capture_output=True,text=True)
assert p.returncode==0,p.stderr
c=sqlite3.connect(base/'eikyouki.db');c.execute("UPDATE articles SET summary='INDEPENDENT-PERSISTED-CORRUPTION' WHERE article_id='EK-0001'");c.commit();c.close()
sha=lambda:hashlib.sha256((base/'eikyouki.db').read_bytes()).hexdigest()
before=sha();p=subprocess.run([sys.executable,str(base/'run_checks.py'),str(dst/'checks')],capture_output=True,text=True,encoding='utf8',errors='replace');after=sha()
result={'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'before':before,'after':after,'preserved':before==after,'sourceSha256':hashlib.sha256((base/'run_checks.py').read_bytes()).hexdigest()}
(here/(sys.argv[2]+'-results.json')).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
