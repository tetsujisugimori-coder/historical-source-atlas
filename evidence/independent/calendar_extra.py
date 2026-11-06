import copy,datetime,json,sys
from pathlib import Path
base=Path(sys.argv[1]).resolve()/'prototype/eikyouki';sys.path.insert(0,str(base))
from validation import validate_record,calendar_day
data=json.loads((base/'eikyouki_records.json').read_text(encoding='utf8'))
res=[]
def attempt(name,r,expected):
    try:validate_record(r);accepted=True;error=None
    except Exception as e:accepted=False;error=str(e)
    res.append({'name':name,'expected':expected,'accepted':accepted,'pass':accepted==expected,'error':error})
r=copy.deepcopy(data['records'][2]);r.update(era_year=8,western_year=1436,lunar_month=5,lunar_is_leap=True,lunar_day=29,julian_start='1436-07-13',julian_end='1436-07-13',gregorian_start='1436-07-22',gregorian_end='1436-07-22')
attempt('supported leap month day29',r,True)
bad=copy.deepcopy(r);bad['lunar_day']=30;attempt('supported leap month day30 does not exist',bad,False)
bad=copy.deepcopy(r);bad.update(lunar_is_leap=False);attempt('ordinary month cannot reuse leap conversion',bad,False)
bad=copy.deepcopy(r);bad.update(lunar_month=6);attempt('leap6 absent even though leap5 exists',bad,False)
bad=copy.deepcopy(r);bad.update(date_conversion_status='unresolved',julian_start=None,julian_end=None,gregorian_start=None,gregorian_end=None,lunar_day=30);attempt('unresolved does not excuse impossible supported date',bad,False)
assert calendar_day('2000-01-01','gregorian')==2451545
assert calendar_day('2000-01-01','julian')==2451558
for s in ['1436-01-28','1437-07-18','1438-09-27','1900-03-01','2000-02-29']:
    assert calendar_day(s,'gregorian')-calendar_day('0001-01-01','gregorian')==datetime.date.fromisoformat(s).toordinal()-1
res.append({'name':'Gregorian ordinal crosscheck + fixed astronomical JDN anchors','pass':True})
Path(sys.argv[2]).write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(res,indent=2));raise SystemExit(0 if all(r['pass'] for r in res) else 1)
