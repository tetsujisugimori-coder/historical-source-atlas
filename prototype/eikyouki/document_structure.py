"""Supplemental quoted-document contract; article fields remain unchanged."""
import json
import re

SUPPLEMENT_KEYS = ['publication', 'article_relationships', 'document_structures', 'narrative_references']

def supplementary(data):
    return {k:data.get(k, {} if k == 'publication' else []) for k in SUPPLEMENT_KEYS}

def validate_supplementary(data):
    docs=data.get('document_structures',[]); refs=data.get('narrative_references',[])
    if type(docs) is not list or type(refs) is not list: raise ValueError('supplement lists required')
    rows={r['id']:r for r in data['records']}; seen=set()
    if 'EK-0120' in rows and (len(docs)!=1 or docs[0].get('article_id')!='EK-0120'):raise ValueError('batch12 document required')
    for doc in docs:
        aid=doc['article_id']; did=doc['document_id']
        if aid not in rows or did in seen or not re.fullmatch(re.escape(aid)+r'-D[0-9]{2}',did):raise ValueError('document identity')
        seen.add(did);r=rows[aid];q=doc['quote']
        if q['original_text'] != r['full_original_text'] or doc['source_url'] != r['source_url'] or r['date_kind']!='document_date':raise ValueError('document quote/article mismatch')
        def part(p):
            a,b=p['start_offset'],p['end_offset']
            if type(a)is not int or type(b)is not int or not q['start_offset']<=a<b<=q['end_offset']:raise ValueError('quote bounds')
            if p['original_text']!=q['original_text'][a-q['start_offset']:b-q['start_offset']]:raise ValueError('quote text')
        part(q)
        if doc['verification']['historical_issuance']!='NOT_TESTED':raise ValueError('issuance not established')
        clauses=doc['clauses']
        if len(clauses)!=5:raise ValueError('five clauses required')
        parts=[doc['preamble'],*clauses,doc['conclusion'],doc['date']];cursor=q['start_offset']
        for p in parts:
            part(p)
            if p['start_offset']!=cursor:raise ValueError('document gap/overlap')
            cursor=p['end_offset']
        if cursor!=q['end_offset']:raise ValueError('document end')
        for i,c in enumerate(clauses,1):
            if c['order']!=i or c['clause_id']!=f'{aid}-C{i:02d}' or c['clause_id'] in seen:raise ValueError('clause order/id')
            if not c['original_text'].startswith('一') or not c['summary'].strip():raise ValueError('clause text/summary')
            if c['verification']!=doc['verification']:raise ValueError('clause status')
            seen.add(c['clause_id'])
        if r['original_date'] not in doc['date']['original_text']:raise ValueError('document date text')
    kinds={'document_quote','narrative_relative_time','same_named_person','same_name_in_transcription','narrative_continuity','editorial_cross_reference'}
    for ref in refs:
        if ref['reference_id'] in seen or ref['from'] not in rows or ref['to'] not in rows or ref['from']==ref['to']:raise ValueError('supplement reference identity')
        if ref['kind'] not in kinds or ref['status']!='EDITORIAL_REFERENCE_ONLY' or ref['historical_identity']!='NOT_TESTED' or not ref['evidence_note'].strip():raise ValueError('supplement reference claim')
        seen.add(ref['reference_id'])
    return docs,refs

def insert_supplementary(data,con):
    docs,refs=validate_supplementary(data)
    for d in docs:
        con.execute('INSERT INTO quoted_documents VALUES (?,?,?)',(d['document_id'],d['article_id'],json.dumps(d,ensure_ascii=False)))
        for c in d['clauses']:
            con.execute('INSERT INTO document_clauses VALUES (?,?,?,?,?,?,?,?)',(c['clause_id'],d['document_id'],c['order'],c['summary'],c['original_text'],c['start_offset'],c['end_offset'],json.dumps(c,ensure_ascii=False)))
    for r in refs:con.execute('INSERT INTO narrative_references VALUES (?,?,?,?,?)',(r['reference_id'],r['from'],r['to'],r['kind'],json.dumps(r,ensure_ascii=False)))

def compare_supplementary(data,con):
    docs,refs=validate_supplementary(data)
    actual=[json.loads(row[0]) for row in con.execute('SELECT payload FROM quoted_documents ORDER BY document_id')]
    if actual!=sorted(docs,key=lambda d:d['document_id']):raise ValueError('DB documents mismatch')
    want=[(c['clause_id'],d['document_id'],c['order'],c['summary'],c['original_text'],c['start_offset'],c['end_offset'],c) for d in docs for c in d['clauses']]
    got=[(*r[:-1],json.loads(r[-1])) for r in con.execute('SELECT * FROM document_clauses ORDER BY clause_id')]
    if got!=sorted(want):raise ValueError('DB clauses mismatch')
    actual=[(r[0],r[1],r[2],r[3],json.loads(r[4])) for r in con.execute('SELECT * FROM narrative_references ORDER BY reference_id')]
    wanted=[(r['reference_id'],r['from'],r['to'],r['kind'],r) for r in refs]
    if actual!=sorted(wanted):raise ValueError('DB references mismatch')
