import copy,json,sys
from pathlib import Path
base=Path(sys.argv[1]).resolve()/'prototype/eikyouki';sys.path.insert(0,str(base))
from validation import validate_record
data=json.loads((base/'eikyouki_records.json').read_text(encoding='utf8'))
cases=[('javascript:alert(1)',False),('JaVaScRiPt:alert(1)',False),(' javascript:alert(1)',False),('data:text/html,x',False),('http://example.com/x',False),('//example.com/x',False),('https://user:password@example.com/x',False),('https://@example.com/x',False),('https://example.com:65536/x',False),('https://example.com/x\x00',False),('https://example.com/x\n',False),('https://example.com/x\x7f',False),('https://example.com/x\x85',False),('https://example.com/x\u2028',False),('https://example.com/path?q=1#part',True),('HTTPS://example.com/path',True)]
results=[]
for value,expected in cases:
    r=copy.deepcopy(data['records'][0]);r['date_conversion_source_url']=value
    try:validate_record(r);accepted=True;error=None
    except ValueError as e:accepted=False;error=str(e)
    results.append({'url':value,'expected':expected,'accepted':accepted,'pass':expected==accepted,'error':error})
Path(sys.argv[2]).write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(results,indent=2));raise SystemExit(0 if all(r['pass'] for r in results) else 1)
