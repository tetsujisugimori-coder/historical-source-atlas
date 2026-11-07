"""Regression and destructive negative controls in isolated temporary outputs only."""
from contextlib import contextmanager
import copy
import hashlib
import json
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import re
from sync_html import embed
from pathlib import Path
import sys

from build import build_database, ARTICLE_FIELDS, SCHEMA
from integrity import compare_connection, same_fields, verify
from validation import calendar_day, validate_data, FIELDS, validate_record

BASE = Path(__file__).resolve().parent
DATA = json.loads((BASE/'eikyouki_records.json').read_text(encoding='utf8'))


@contextmanager
def connection(path):
    con=sqlite3.connect(path)
    try:
        with con:
            yield con
    finally:
        con.close()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unknown(r):
    r.update(date_precision='unknown', date_conversion_status='unresolved',
             date_conversion_note='Date not established; no conversion certified.')
    for f in ('era','era_year','western_year','lunar_month','lunar_day','lunar_is_leap',
              'julian_start','julian_end','gregorian_start','gregorian_end',
              'date_conversion_source_url'):
        r[f] = None
    return r


class Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=BASE)
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.db = self.folder/'atlas.db'
        build_database(DATA,self.db)

    def test_all_36_fields_and_existing_15(self):
        self.assertEqual(36,len(FIELDS))
        self.assertEqual(len(DATA['records']), verify(BASE/'eikyouki_records.json',BASE/'index.html',self.db))
        # Preserve the frozen original 15 records; compare only their historic 36 fields.
        old = json.loads(subprocess.check_output(['git','show','ec347901dc4b688927bb3002121ff58e6b7dbd40:prototype/eikyouki/eikyouki_records.json'],cwd=BASE,encoding='utf8'))
        changes = {(r['id'],f) for r,o in zip(DATA['records'][:len(old['records'])],old['records']) for f in FIELDS if r[f]!=o[f]}
        self.assertEqual({('EK-0010','date_interpretation'),('EK-0010','editorial_note'),('EK-0015','location_in_text'),('EK-0015','editorial_note')}, changes)
        self.assertEqual([r['id'] for r in old['records']],[r['id'] for r in DATA['records'][:len(old['records'])]])


    def test_new_hakone_articles_remain_distinct_provisional_entries(self):
        self.assertGreaterEqual(len(DATA['records']),17)
        self.assertEqual(['EK-0016','EK-0017'],[r['id'] for r in DATA['records'][15:17]])
        self.assertEqual([16,17],[r['source_order'] for r in DATA['records'][15:17]])
        self.assertEqual(['同九月十日','九月廿七日'],[r['original_date'] for r in DATA['records'][15:17]])
        self.assertEqual(['1438-10-08','1438-10-25'],[r['gregorian_start'] for r in DATA['records'][15:17]])
        for article in DATA['records'][15:17]:
            self.assertEqual('hakone',article['chapter_id'])
            self.assertEqual('provisional',article['date_conversion_status'])
            self.assertIsNone(article['full_original_text'])
            self.assertIsNone(article['research_date_start'])
            validate_record(article)

    def test_reject_input_mutations_without_replacing_good_db(self):
        cases = [
            ('date_conversion_source_url','https://@example.com/x'),('date_conversion_source_url','https://example.com/\x7f'),('date_conversion_source_url','javascript:alert(1)'),('date_conversion_source_url','data:text/html,unsafe'),('date_conversion_source_url','/relative'),('date_conversion_source_url','https://user:pass@example.com'),('date_conversion_source_url','https://example.com\n/path'),('date_conversion_source_url','https://example.com:bad'),('work_id','NO_SUCH_WORK'),('edition_id','NO_SUCH_EDITION'),
            ('chapter_id','missing'),('chapter','changed chapter'),
            ('source_url','https://example.com/different-source'),
            ('julian_start','not-a-date'),('gregorian_start','1437-02-30'),
            ('julian_start','2000-01-01'),('gregorian_start','2000-01-01'),
            ('lunar_month',1.5),('lunar_month','1'),('lunar_month',True),
            ('era_year',-1),('era_year',1.5),('era_year','8'),('era_year',True),
            ('western_year','nonsense'),('western_year',1436.0),('western_year',False),
            ('lunar_is_leap',0.8),('lunar_is_leap','false'),('lunar_is_leap',0),
            ('date_precision','day'),('lunar_day',1),('lunar_is_leap',True),
            ('gregorian_end','1436-02-01'),('julian_end','1436-02-01'),
            ('research_date_start','not-a-date'),('research_date_start','1437-02-30'),
            ('date_conversion_status','verified'),('id',None),('id',''),('id',' \t\n'),
            ('id',123),('source_order',True),('source_order',1.5),('summary',None),
            ('source_order',0),('date_precision','unknown'),('era',None),
        ]
        before = digest(self.db)
        for field,value in cases:
            with self.subTest(field=field,value=value):
                d=copy.deepcopy(DATA);d['records'][0][field]=value
                with self.assertRaises(ValueError) as caught:
                    build_database(d,self.db)
                self.assertIn('EK-0001' if field!='id' else 'id',str(caught.exception))
                self.assertEqual(before,digest(self.db))
                self.assertEqual([],list(self.folder.glob('*.tmp')))
        for field in FIELDS:
            with self.subTest(missing=field):
                d=copy.deepcopy(DATA);del d['records'][0][field]
                with self.assertRaises(ValueError):build_database(d,self.db)
        for mutate in ('duplicate','extra_field'):
            d=copy.deepcopy(DATA)
            if mutate=='duplicate':d['records'][1]['id']=d['records'][0]['id']
            else:d['records'][0]['unrecognized']='silently lost?'
            with self.assertRaises(ValueError):build_database(d,self.db)

    def test_calendars_precision_unknown_and_research(self):
        # Julian 1500 is leap, Gregorian 1500 is not; no Python date shortcut.
        self.assertIsInstance(calendar_day('1500-02-29','julian'),int)
        for value,calendar in [('1500-02-29','gregorian'),('1437-02-30','julian'),('0000-01-01','julian'),('1437-2-03','gregorian')]:
            with self.assertRaises(ValueError):calendar_day(value,calendar)
        d=copy.deepcopy(DATA);unknown(d['records'][0]);build_database(d,self.db)
        with connection(self.db) as db:compare_connection(d['records'],db)
        # Known-but-unconverted dates outside anchor support may remain unresolved.
        r=copy.deepcopy(DATA['records'][0]);r.update(era_year=12,western_year=1440,date_conversion_status='unresolved')
        for f in ('julian_start','julian_end','gregorian_start','gregorian_end'):r[f]=None
        validate_record(r)
        # Supported month absence and the small lunar month endpoint are checked even unresolved.
        r=copy.deepcopy(DATA['records'][2]);r['lunar_day']=30
        with self.assertRaises(ValueError):validate_record(r)  # year 9 month 6 has 29 days
        r=copy.deepcopy(DATA['records'][2]);r['lunar_is_leap']=True
        with self.assertRaises(ValueError):validate_record(r)
        r=copy.deepcopy(DATA['records'][0]);r.update(research_date_start='1500-02-28',research_date_end='1500-03-01',research_date_basis='Synthetic test, not a product assertion')
        validate_record(r)
        for field,value in [('research_date_end','1500-02-27'),('research_date_start','1500-02-29'),('research_date_basis',None)]:
            bad=copy.deepcopy(r);bad[field]=value
            with self.assertRaises(ValueError):validate_record(bad)

    def test_direct_id_constraints_and_separate_same_content(self):
        # All four primary IDs reject NULL/empty/whitespace/nontext; uniqueness too.
        with connection(self.db) as db:
            for table,field in [('works','work_id'),('editions','edition_id'),('chapters','chapter_id'),('articles','article_id')]:
                columns=[r[1] for r in db.execute('PRAGMA table_info('+table+')')]
                values=list(db.execute('SELECT * FROM '+table+' LIMIT 1').fetchone())
                sql='INSERT INTO '+table+' VALUES ('+','.join('?' for _ in columns)+')'
                for invalid in (None,'',' \t\r\n','\v','\u3000','A\x00B','A\x00#',123,b'bytes',values[0]):
                    with self.subTest(table=table,invalid=invalid):
                        row=values.copy();row[0]=invalid
                        if table=='articles':row[columns.index('source_order')]=100
                        with self.assertRaises(sqlite3.IntegrityError):db.execute(sql,row)
            # Independent articles retain equal content/date, distinguished only by ID/order.
            row=dict(DATA['records'][0],article_id='EK-9999',source_order=9999)
            row['lunar_is_leap']=int(row['lunar_is_leap'])
            db.execute('INSERT INTO articles ('+','.join(ARTICLE_FIELDS)+') VALUES ('+','.join('?' for _ in ARTICLE_FIELDS)+')',[row[k] for k in ARTICLE_FIELDS])
            self.assertEqual(2,db.execute('SELECT COUNT(*) FROM articles WHERE summary=?',(row['summary'],)).fetchone()[0])
        d=copy.deepcopy(DATA);r=copy.deepcopy(d['records'][0]);r.update(id='EK-9999',source_order=9999);d['records'].append(r)
        build_database(d,self.db)
        with connection(self.db) as db:compare_connection(d['records'],db)

    def test_each_db_field_mutation_detected_read_only(self):
        for field in FIELDS:
            with self.subTest(field=field):
                build_database(DATA,self.db)
                with connection(self.db) as db:
                    if field in ('work_id','edition_id','chapter','source_url'):
                        table,column={'work_id':('editions','work_id'),'edition_id':('chapters','edition_id'),'chapter':('chapters','heading'),'source_url':('chapters','chapter_url')}[field]
                        db.execute('UPDATE '+table+' SET '+column+'=?',('CORRUPTED',))
                    else:
                        column='article_id' if field=='id' else field
                        value=DATA['records'][0][field]
                        if field=='lunar_is_leap':new=1
                        elif type(value) is int:new=value+1
                        elif field in ('lunar_month','lunar_day'):new=1
                        elif value is None:new='CORRUPTED'
                        else:new='CORRUPTED'
                        if field in ('date_precision','date_conversion_status'):new='unknown' if field=='date_precision' else 'unresolved'
                        db.execute('UPDATE articles SET '+column+'=? WHERE article_id=?',(new,'EK-0001'))
                before=digest(self.db)
                with self.assertRaises(ValueError):verify(BASE/'eikyouki_records.json',BASE/'index.html',self.db)
                self.assertEqual(before,digest(self.db))

    def test_each_html_field_and_missing_extra_duplicate(self):
        for field in FIELDS:
            with self.subTest(field=field):
                changed=copy.deepcopy(DATA['records']);v=changed[0][field]
                changed[0][field]=None if v is not None else 'CORRUPTED'
                html=BASE.joinpath('index.html').read_text(encoding='utf8')
                bad_html=re.sub(r'(<script id="payload" type="application/json">).*?(</script>)',lambda m:m[1]+json.dumps(changed)+m[2],html,flags=re.S)
                path=self.folder/'bad.html';path.write_text(bad_html,encoding='utf8')
                with self.assertRaises(ValueError):verify(BASE/'eikyouki_records.json',path,self.db)
                d=copy.deepcopy(DATA);d['records']=changed
                path=self.folder/'bad.json';path.write_text(json.dumps(d),encoding='utf8')
                with self.assertRaises(ValueError):verify(path,BASE/'index.html',self.db)
        for rows in (DATA['records'][:-1],DATA['records']+[DATA['records'][0]],DATA['records'][:-1]+[DATA['records'][0]]):
            with self.assertRaises(ValueError):same_fields(DATA['records'],rows,'HTML')
        with connection(self.db) as db:db.execute("DELETE FROM articles WHERE article_id='EK-0015'")
        with self.assertRaises(ValueError):verify(BASE/'eikyouki_records.json',BASE/'index.html',self.db)
        build_database(DATA,self.db)
        d=copy.deepcopy(DATA);r=copy.deepcopy(d['records'][0]);r.update(id='EK-9999',source_order=9999);d['records'].append(r)
        build_database(d,self.db)
        with self.assertRaises(ValueError):verify(BASE/'eikyouki_records.json',BASE/'index.html',self.db)
        self.db.unlink()
        with self.assertRaises(sqlite3.OperationalError):verify(BASE/'eikyouki_records.json',BASE/'index.html',self.db)
        self.assertFalse(self.db.exists())

    def test_check_runner_does_not_regenerate(self):
        # Run its command preamble against a deliberately corrupt fixture, in isolation.
        folder=self.folder/'cli';folder.mkdir()
        for p in BASE.iterdir():
            if p.is_file() and p.suffix in ('.py','.cjs','.html','.json','.sql'):
                (folder/p.name).write_bytes(p.read_bytes())
        database=folder/'eikyouki.db';build_database(DATA,database)
        with connection(database) as db:db.execute("UPDATE articles SET summary='CORRUPTED' WHERE article_id='EK-0001'")
        before=digest(database)
        p=subprocess.run([sys.executable,str(folder/'test_dates.py')],capture_output=True)
        self.assertNotEqual(0,p.returncode)
        self.assertEqual(before,digest(database))
        # The suite entry must have no build command; inner tests build only their temp DBs.
        self.assertNotIn("str(BASE/'build.py')",(BASE/'run_checks.py').read_text(encoding='utf8'))

    def test_script_boundary_escaping(self):
        d=copy.deepcopy(DATA);d['records'][0]['summary']='</script><script>globalThis.INJECTED=true</script>'
        html=embed(BASE.joinpath('index.html').read_text(encoding='utf8'),d)
        payload=re.search(r'<script id="payload" type="application/json">(.*?)</script>',html,re.S)[1]
        self.assertNotIn('<',payload)
        self.assertEqual(d['records'],json.loads(payload))

    def test_failure_stages_preserve_existing_and_cleanup(self):
        for stage in ('opened','article:EK-0001','article:EK-0015','validated','committed','before_replace'):
            with self.subTest(stage=stage):
                before=digest(self.db)
                def inject(actual):
                    if actual==stage:raise OSError('synthetic failure: '+stage)
                with self.assertRaises(OSError):build_database(DATA,self.db,checkpoint=inject)
                self.assertEqual(before,digest(self.db))
                self.assertEqual([],list(self.folder.glob('*.tmp')))
        before=digest(self.db)
        with patch.object(Path,'replace',side_effect=OSError('synthetic OS replacement failure')):
            with self.assertRaises(OSError):build_database(DATA,self.db)
        self.assertEqual(before,digest(self.db))
        self.assertEqual([],list(self.folder.glob('*.tmp')))
        d=copy.deepcopy(DATA);d['records'][0]['summary']+=' [synthetic replacement test]'
        before=digest(self.db);build_database(d,self.db)
        self.assertNotEqual(before,digest(self.db))
        with connection(self.db) as db:compare_connection(d['records'],db)


if __name__=='__main__':
    unittest.main(verbosity=2)
