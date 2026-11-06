import json,sqlite3,sys
from pathlib import Path
repo=Path(sys.argv[1]).resolve()
c=sqlite3.connect(':memory:'); c.executescript((repo/'prototype/eikyouki/schema.sql').read_text(encoding='utf8'))
res=[]
for v in [None,'','  ','\t','\v','\u3000',123,'A\x00#','A\x00B']:
    try:
        c.execute('INSERT INTO works(work_id,title) VALUES (?,?)',(v,'probe'))
        res.append({'id':repr(v),'accepted':True})
    except Exception as e:res.append({'id':repr(v),'accepted':False,'error':str(e)})
print(json.dumps(res,indent=2))
