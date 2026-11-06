import hashlib,json,sys
from pathlib import Path
folder=Path(sys.argv[1]);data=json.loads((folder/'results.json').read_text(encoding='utf8'))
expected=[f'EK-{i:04d}' for i in range(1,13)]+['EK-0015','EK-0013','EK-0014']
rows=[]
for r in data['cases']:
    checks={
        'executed':r.get('status')=='EXECUTED',
        'focused_visible':r.get('document')=={'focus':True,'visibility':'visible'},
        'chronology':r.get('chronological')==expected,
        'sourceOrder':r.get('sourceOrder')==[f'EK-{i:04d}' for i in range(1,16)],
        'search':r.get('search')==['EK-0015'],
        'EnterDetails':r.get('detailOpen') is True,
        'focus':r.get('keyboardFocus',{}).get('tag')=='SUMMARY' and r.get('keyboardFocus',{}).get('outline')!='none',
        'tabForward':r.get('tabForward',{}).get('tag')=='A' and r.get('tabForward',{}).get('href')==r.get('sourceLink') and r.get('tabForward',{}).get('focus') is True,
        'tabBackward':r.get('tabBack')=={'tag':'SUMMARY','focus':True},
        'SpaceDetails':r.get('spaceOpen') is True,
        'sourceLink':r.get('sourceLink')=='https://ja.wikisource.org/wiki/永享記#箱根早川尻合戦の事',
        'download':r.get('download',{}).get('records') and [x['id'] for x in r['download']['records']]==['EK-0015'],
        'empty':r.get('emptyCount')==0 and r.get('emptyVisible') is True,
        'yearFilter':r.get('yearIds')==[f'EK-{i:04d}' for i in range(2,8)],
        'chapterFilter':r.get('chapterIds')==['EK-0015'],
        'overflow':r.get('overflow',{}).get('scroll',99999)<=r.get('width',0),
        'errors':r.get('errors')==[],
    }
    rows.append({'engine':r['engine'],'width':r.get('width'),'checks':checks,'pass':all(checks.values())})
report={'cases':rows,'pass':len(rows)==4 and all(r['pass'] for r in rows),'files':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(folder.iterdir()) if p.is_file()]}
(folder/'judgment.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,indent=2));raise SystemExit(0 if report['pass'] else 1)
