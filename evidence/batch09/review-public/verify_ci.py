import argparse,json,hashlib,zipfile,subprocess,itertools
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--artifact-dir',type=Path,required=True);p.add_argument('--repo-root',type=Path,required=True);p.add_argument('--head',required=True);p.add_argument('--zip-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest();root=a.artifact_dir/'extracted';z=a.artifact_dir/'original.zip';checks=[]
def ck(n,v):checks.append({'name':n,'pass':bool(v)});assert v,n
ck('original ZIP SHA256',sha(z.read_bytes())==a.zip_sha256)
with zipfile.ZipFile(z) as f:
 ck('ZIP CRC',f.testzip() is None)
 n=0
 for i in f.infolist():
  if i.is_dir():continue
  ck('original ZIP/extracted '+i.filename,f.read(i)==(root/i.filename).read_bytes());n+=1
m=json.loads((root/'manifest.json').read_text());u=json.loads((root/'ci-checks/results.json').read_text());b=json.loads((root/'ci-browser/results.json').read_text())
git=lambda *s:subprocess.check_output(['git',*s],cwd=a.repo_root)
tree=git('rev-parse',a.head+'^{tree}').decode().strip()
for name,v in [('manifest',m),('unit',u),('browser',b)]:ck(name+' identity',v['head']==a.head and v['tree']==tree)
for path,h in m['files'].items():ck('manifest hash '+path,sha((root/path).read_bytes())==h)
for path,h in m['source'].items():ck('Git source '+path,sha(git('show',a.head+':'+path))==h)
ck('unit status',u['status']=='PASS' and u['methods']==48 and len(u['tests'])==10528 and all(t['status']=='PASS' for t in u['tests']) and all(c['exit']==0 for c in u['commands']) and len(u['commands'])==2)
ck('browser source hash',b['sourceSha256']==sha(git('show',a.head+':prototype/eikyouki/index.html')))
ck('browser 16 unique combinations',{(c['browser'],c['width'],c['motion']) for c in b['cases']}==set(itertools.product(['chromium','webkit'],[375,390,765,1280],['no-preference','reduce'])) and len(b['cases'])==16)
rows=json.loads(git('show',a.head+':prototype/eikyouki/eikyouki_records.json'))['records'];summary=[]
for c in b['cases']:
 tag=f"{c['browser']}-{c['width']}-{c['motion']}";ck(tag+' all checks',c['status']=='PASS' and len(c['checks'])==469 and all(t['actual']==t['expected'] for t in c['checks']))
 ck(tag+' no console errors',not c['consoleErrors'] and not c['pageerrors'])
 ck(tag+' trusted clicks/key events',all(any(e['type']==kind and e['trusted'] for e in c['inputEvents']) for kind in ['click','keydown','keyup']))
 ck(tag+' exported 82 typed records',sorted(json.loads((root/'ci-browser'/f'{tag}-all-download.json').read_text())['records'],key=lambda r:r['source_order'])==rows)
 ck(tag+' saved screenshot evidence',all((root/'ci-browser'/f'{tag}-{rid}.png').is_file() for rid in ['EK-0062','EK-0071','EK-0082']))
 summary.append({'condition':tag,'checks':len(c['checks']),'events':len(c['inputEvents']),'version':c['version']})
ck('browser total status',b['status']=='PASS')
out={'head':a.head,'tree':tree,'artifact_zip_sha256':a.zip_sha256,'zip_files':n,'status':'PASS','check_count':len(checks),'browser_operation_checks':sum(len(c['checks']) for c in b['cases']),'browser_conditions':summary,'unit_methods':48,'unit_records':10528,'CLI':2,'visual_samples':['webkit-375-reduce-EK-0062.png','chromium-1280-no-preference-EK-0071.png'],'visual_note':'Both sampled viewport screenshots are legible and show provisional source/summary distinctions. Viewport-only images do not visually prove offscreen original-text details; corresponding DOM text checks pass. WebKit is not physical Safari.','checks':checks}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2));print({k:v for k,v in out.items() if k not in ['checks','browser_conditions']})
