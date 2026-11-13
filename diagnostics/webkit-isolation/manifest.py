"""Diagnostic evidence inventory, never a product-acceptance result."""
import hashlib,json,pathlib,sys,subprocess
root=pathlib.Path(sys.argv[1]).resolve()
if not root.is_dir():raise SystemExit('evidence directory missing')
files=[]
for p in sorted(root.rglob('*')):
    if p.is_symlink():raise SystemExit('symlink in evidence')
    if p.is_file() and p.name!='manifest.json':
        b=p.read_bytes();files.append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
if not files:raise SystemExit('empty evidence')
x={'classification':'diagnostic only','head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'tree':subprocess.check_output(['git','rev-parse','HEAD^{tree}'],text=True).strip(),'files':files}
(root/'manifest.json').write_text(json.dumps(x,indent=2)+'\n')
