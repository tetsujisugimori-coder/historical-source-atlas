"""Run reproducible non-browser acceptance with per-subtest evidence and exit status."""
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
import platform
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
OUT=Path(sys.argv[1] if len(sys.argv)>1 else 'evidence/checks').resolve()
OUT.mkdir(parents=True,exist_ok=True)
git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,encoding='utf8').strip()
report={'head':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),
        'dirty':git('status','--porcelain'),'python':sys.version,'sqlite':sqlite3.sqlite_version,
        'os':platform.platform(),'commands':[],'tests':[]}
failed=False
for command in ([sys.executable,str(BASE/'test_dates.py')],['node',str(BASE/'test_sort.cjs')]):
    p=subprocess.run(command,cwd=ROOT,capture_output=True,encoding='utf8',errors='replace')
    report['commands'].append({'command':command,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    failed=failed or p.returncode!=0


class Result(unittest.TextTestResult):
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        report['tests'].append({'test':test.id(),'params':str(subtest.params),'status':'PASS' if err is None else 'FAIL','error':None if err is None else self._exc_info_to_string(err,test)})
    def addSuccess(self,test):
        super().addSuccess(test)
        report['tests'].append({'test':test.id(),'status':'PASS'})
    def addError(self,test,err):
        super().addError(test,err)
        report['tests'].append({'test':test.id(),'status':'ERROR','error':self._exc_info_to_string(err,test)})
    def addFailure(self,test,err):
        super().addFailure(test,err)
        report['tests'].append({'test':test.id(),'status':'FAIL','error':self._exc_info_to_string(err,test)})


suite=unittest.defaultTestLoader.discover(str(BASE),pattern='test_*.py')
log=io.StringIO()
with redirect_stdout(log),redirect_stderr(log):
    result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
report['unit_log']=log.getvalue();report['methods']=result.testsRun
failed=failed or not result.wasSuccessful()
report['status']='FAIL' if failed else 'PASS'
report['source']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.iterdir() if p.is_file() and p.suffix in ('.py','.cjs','.json','.html','.sql')}
(OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(f"{report['status']}: {result.testsRun} test methods; {len(report['tests'])} method/subtest records; {len(report['commands'])} CLI commands")
sys.exit(1 if failed else 0)
