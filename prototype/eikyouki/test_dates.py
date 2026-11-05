"""Smoke-test the provisional v0.2 article timeline and the rebuilt database."""
from pathlib import Path
import json
import re
import sqlite3
from datetime import date
BASE = Path(__file__).resolve().parent
data = json.loads((BASE/'eikyouki_records.json').read_text(encoding='utf-8'))
rows = data['records']
assert len(rows)==15==len({r['id'] for r in rows})
assert [r['source_order'] for r in rows]==list(range(1,16))
expected={
 'EK-0001':('1436-01-28','1437-02-14'),
 'EK-0002':('1437-05-14','1437-06-12'),
 'EK-0003':('1437-07-18','1437-07-18'),
 'EK-0004':('1437-07-19','1437-07-19'),
 'EK-0005':('1437-07-27','1437-07-27'),
 'EK-0006':('1437-08-08','1437-08-08'),
 'EK-0007':('1437-09-22','1437-09-22'),
 'EK-0008':('1438-07-02','1438-07-30'),
 'EK-0009':('1438-09-10','1438-09-10'),
 'EK-0010':('1438-09-12','1438-09-12'),
 'EK-0011':('1438-09-13','1438-09-13'),
 'EK-0012':('1438-09-14','1438-09-14'),
 'EK-0013':('1438-10-30','1438-10-30'),
 'EK-0014':('1438-11-13','1438-11-13'),
 'EK-0015':('1438-09-27','1438-09-27'),
}
for r in rows:
    assert (r['gregorian_start'],r['gregorian_end'])==expected[r['id']]
    assert r['date_conversion_status']=='provisional'
    assert r['gregorian_calendar']=='先発グレゴリオ暦'
    assert r['historic_calendar']=='宣明暦'
    assert all(r[x] is None for x in ('research_date_start','research_date_end','research_date_basis'))
    assert date.fromisoformat(r['gregorian_start'])<=date.fromisoformat(r['gregorian_end'])
    assert r['julian_start'] and r['julian_end'] and r['date_conversion_source_url']
    if r['date_precision']=='day': assert r['gregorian_start']==r['gregorian_end']
html=(BASE/'index.html').read_text(encoding='utf-8')
m=re.search(r'<script id="payload" type="application/json">(.*?)</script>',html,re.S)
assert m and json.loads(m.group(1))==rows
with sqlite3.connect(BASE/'eikyouki.db') as db:
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
    assert db.execute('SELECT COUNT(*) FROM articles').fetchone()[0]==15
    for r in rows:
        row=db.execute('SELECT gregorian_start,gregorian_end,date_conversion_status FROM articles WHERE article_id=?',(r['id'],)).fetchone()
        assert row==(r['gregorian_start'],r['gregorian_end'],'provisional')
print('PASS: 15 provisional articles / JSON / HTML / SQLite / Gregorian date fixtures')
