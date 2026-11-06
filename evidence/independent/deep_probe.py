"""Independent semantic probes, not a rerun of implementation unit tests."""
import copy, hashlib, importlib, json, re, shutil, sqlite3, sys, tempfile
from pathlib import Path
root=Path(sys.argv[1]).resolve(); out=Path(sys.argv[2]).resolve()
base=root/'prototype/eikyouki';sys.path.insert(0,str(base))
import build, integrity, validation
data=json.loads((base/'eikyouki_records.json').read_text(encoding='utf8'))
tempfile.tempdir=str(Path(__file__).resolve().parent)
result={'cases':[]}
def case(name,fn,expect_error=False):
    try:
        value=fn(); result['cases'].append({'name':name,'pass':not expect_error,'value':value})
    except Exception as e:
        result['cases'].append({'name':name,'pass':expect_error,'error':type(e).__name__+': '+str(e)})
def unknown():
    d=copy.deepcopy(data);r=d['records'][0]
    r.update(date_precision='unknown',date_conversion_status='unresolved',era=None,era_year=None,western_year=None,lunar_month=None,lunar_day=None,lunar_is_leap=None,julian_start=None,julian_end=None,gregorian_start=None,gregorian_end=None,date_conversion_source_url=None,date_conversion_note='Unknown date; no invented conversion')
    with tempfile.TemporaryDirectory(prefix='independent-unknown-') as td:
        db=Path(td)/'u.db';build.build_database(d,db)
        c=sqlite3.connect(db);integrity.compare_connection(d['records'],c)
        actual=c.execute('SELECT era_year,lunar_is_leap,julian_start FROM articles WHERE article_id=?',(r['id'],)).fetchone();c.close()
        assert actual==(None,None,None);return 'valid unknown preserved'
case('legitimate_unknown',unknown)

def all_fields():
    detected=[]
    for f in validation.FIELDS:
        with tempfile.TemporaryDirectory(prefix='independent-field-') as td:
            p=Path(td); db=p/'d.db';build.build_database(data,db)
            c=sqlite3.connect(db)
            table,column='articles','article_id' if f=='id' else f
            if f=='work_id':table,column='editions','work_id'
            if f in ('edition_id','chapter','source_url'):
                table,column='chapters',{'edition_id':'edition_id','chapter':'heading','source_url':'chapter_url'}[f]
            old=data['records'][0][f]
            v=(2 if type(old) is int else 1 if type(old) is bool else 'INDEPENDENT-MUTATION')
            v={'lunar_month':1,'lunar_day':1,'date_precision':'month','date_conversion_status':'unresolved'}.get(f,v)
            try:
                c.execute(f'UPDATE {table} SET {column}=? WHERE rowid=(SELECT min(rowid) FROM {table})',(v,));c.commit()
                try:integrity.compare_connection(data['records'],c)
                except ValueError as e:detected.append({'field':f,'reason':str(e)})
                else:raise AssertionError('undetected DB mutation: '+f)
            finally:c.close()
    return detected
case('all_36_database_fields',all_fields)

def html_fields():
    detected=[]
    for f in validation.FIELDS:
        rows=copy.deepcopy(data['records']);old=rows[0][f]
        rows[0][f]=(99 if type(old) is int else not old if type(old) is bool else 'INDEPENDENT-MUTATION')
        try:integrity.same_fields(data['records'],rows,'HTML')
        except ValueError as e:detected.append({'field':f,'reason':str(e)})
        else:raise AssertionError('undetected payload mutation: '+f)
    return detected
case('all_36_payload_fields',html_fields)

def document_fields():
    detected=[]
    with tempfile.TemporaryDirectory(prefix='independent-documents-') as td:
        p=Path(td);db=p/'d.db';build.build_database(data,db)
        original_html=(base/'index.html').read_text(encoding='utf8')
        html=p/'index.html';json_path=p/'records.json'
        before=hashlib.sha256(db.read_bytes()).hexdigest()
        for f in validation.FIELDS:
            changed=copy.deepcopy(data);v=changed['records'][0][f]
            changed['records'][0][f]=None if v is not None else 'INDEPENDENT-MUTATION'
            for surface in ['HTML','JSON']:
                html.write_text(re.sub(r'(<script id="payload" type="application/json">).*?(</script>)',lambda m:m[1]+json.dumps((changed if surface=='HTML' else data)['records'])+m[2],original_html,flags=re.S),encoding='utf8')
                json_path.write_text(json.dumps(changed if surface=='JSON' else data),encoding='utf8')
                try:integrity.verify(json_path,html,db)
                except ValueError as e:detected.append({'field':f,'surface':surface,'reason':str(e)})
                else:raise AssertionError('undetected parsed '+surface+' field '+f)
                assert hashlib.sha256(db.read_bytes()).hexdigest()==before
    return detected
case('parsed_HTML_and_JSON_72_mutations',document_fields)

def preserve():
    results=[]
    with tempfile.TemporaryDirectory(prefix='independent-preserve-') as td:
        p=Path(td);db=p/'prior.db';build.build_database(data,db)
        before=hashlib.sha256(db.read_bytes()).hexdigest()
        for stage in ['opened','article:EK-0001','article:EK-0015','validated','committed','before_replace']:
            def fail(s):
                if s==stage:raise OSError('independent injected '+s)
            try:build.build_database(data,db,checkpoint=fail)
            except OSError:pass
            else:raise AssertionError('not injected '+stage)
            after=hashlib.sha256(db.read_bytes()).hexdigest();assert before==after
            assert list(p.glob('*.tmp'))==[]
            results.append({'stage':stage,'before':before,'after':after,'temporaryFiles':0})
        d=copy.deepcopy(data);d['records'][0]['summary']+=' [independent valid replacement]'
        build.build_database(d,db);c=sqlite3.connect(db);integrity.compare_connection(d['records'],c);c.close()
        assert hashlib.sha256(db.read_bytes()).hexdigest()!=before
    return results
case('preserve_all_failure_stages',preserve)

def duplicate_content():
    d=copy.deepcopy(data);r=copy.deepcopy(d['records'][0]);r.update(id='EK-independent',source_order=16);d['records'].append(r)
    with tempfile.TemporaryDirectory(prefix='independent-separate-') as td:
        db=Path(td)/'d.db';build.build_database(d,db);c=sqlite3.connect(db);integrity.compare_connection(d['records'],c);n=c.execute('SELECT count(*) FROM articles').fetchone()[0];c.close();assert n==16
    return '16 independent records retained'
case('same_content_separate_id',duplicate_content)

def direct_ids_all():
    results=[]
    with tempfile.TemporaryDirectory(prefix='independent-direct-all-') as td:
        db=Path(td)/'d.db';build.build_database(data,db);c=sqlite3.connect(db)
        try:
            for table in ['works','editions','chapters','articles']:
                columns=[row[1] for row in c.execute('PRAGMA table_info('+table+')')]
                initial=list(c.execute('SELECT * FROM '+table+' LIMIT 1').fetchone())
                for v in [None,'','  ','\v','\u3000',123,b'bytes','A\x00#','A\x00B',initial[0]]:
                    values=initial.copy();values[0]=v
                    if table=='articles':values[columns.index('source_order')]=99
                    try:c.execute('INSERT INTO '+table+' VALUES('+','.join('?' for _ in values)+')',values)
                    except sqlite3.IntegrityError as e:results.append({'table':table,'id':repr(v),'rejected':True,'reason':str(e)})
                    else:raise AssertionError('invalid/duplicate direct id accepted: '+table+' '+repr(v))
        finally:c.close()
    return results
case('all_four_primary_id_constraints',direct_ids_all)

def calendar_rules():
    for s in ['1500-02-29','1900-02-29']:
        validation.calendar_day(s,'julian')
        try:validation.calendar_day(s,'gregorian')
        except ValueError:pass
        else:raise AssertionError('Gregorian accepted '+s)
    validation.calendar_day('2000-02-29','gregorian')
    return 'Julian 1500/1900 leap independently distinguished'
case('separate_calendar_rules',calendar_rules)

old=json.loads((Path(__file__).resolve().parent/'old/prototype/eikyouki/eikyouki_records.json').read_text(encoding='utf8'))
result['retention']=[{'id':a['id'],'field':f,'old':a[f],'new':b[f]} for a,b in zip(old['records'],data['records']) for f in a if a[f]!=b[f]]
result['pass']=all(x['pass'] for x in result['cases'])
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pass':result['pass'],'cases':[{k:v for k,v in x.items() if k!='value'} for x in result['cases']],'retention':result['retention']},ensure_ascii=False,indent=2))
raise SystemExit(0 if result['pass'] else 1)
