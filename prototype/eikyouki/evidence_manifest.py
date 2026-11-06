"""Hash evidence bytes plus exact checked-out source, without self-reference."""
import hashlib
import json
import platform
import sqlite3
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[2]
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
git=lambda *args:subprocess.check_output(['git',*args],cwd=root,encoding='utf8').strip()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'head':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),
          'dirty':git('status','--porcelain'),'os':platform.platform(),'python':sys.version,
          'sqlite':sqlite3.sqlite_version,'node':subprocess.check_output(['node','--version'],encoding='utf8').strip(),
          'source':{str(p.relative_to(root)).replace('\\','/'):sha(p) for p in (root/'prototype/eikyouki').iterdir() if p.is_file() and p.suffix in ('.py','.cjs','.json','.html','.sql')},
          'files':{str(p.relative_to(out)).replace('\\','/'):sha(p) for p in out.rglob('*') if p.is_file() and p.name!='manifest.json'}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps({'head':manifest['head'],'tree':manifest['tree'],'files':len(manifest['files'])}))
