'use strict';
const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs');
const {PLANS,DOC,fixture,classify,tiny,evidenceState}=require('./isolate.cjs');
const html=fs.readFileSync('prototype/eikyouki/index.html','utf8');
test('22 immutable planned cases, no retries',()=>{a.equal(PLANS.length,22);a.equal(new Set(PLANS.map(x=>x.id)).size,22);a.equal(DOC.retries,0);a.equal(PLANS.filter(x=>x.head==='main').length,2);a.equal(PLANS.filter(x=>x.debugger).length,1)});
test('unchanged original and only one record in reduced data',()=>{a.equal(fixture(html,'original'),html);const f=fixture(html,'one-record');const m=f.match(/<script[^>]*id="payload"[^>]*>([\s\S]*?)<\/script>/);a.deepEqual(JSON.parse(m[1]).map(x=>x.id),['EK-0120']);a(f.includes('EK-0120-C05'));a(!fixture(html,'no-css').includes('<style>'))});
test('tiny is standalone and syntactically valid',()=>{for(const f of ['tiny','tiny-direct','no-restore','native-only','no-focus','no-scroll']){const s=fixture(html,f);a(s.length<3000);new Function(s.match(/<script>([\s\S]*?)<\/script>/)[1]);}a(!fixture(html,'no-focus').includes('t.focus'));a(!fixture(html,'no-scroll').includes('t.scrollIntoView'));a(!fixture(html,'no-restore').includes("addEventListener('load'"));});
test('signature conjunctive: other errors cannot become matching assertion',()=>{const r={browserStarted:true,targetReloadStarted:true,targetReloadCompleted:true,finished:'2026-11-13T00:00:00Z'};const s="optional:479 _M_get<unsigned long> Assertion 'this->_M_is_engaged()' failed.";a.equal(classify(r,s).classification,'MATCHING_NATIVE_ASSERTION');for(const token of ['optional:479','_M_get','unsigned long','this->_M_is_engaged()','failed'])a.notEqual(classify(r,s.replace(token,'')).classification,'MATCHING_NATIVE_ASSERTION');a.equal(classify({...r,pageCrash:true},'').classification,'OTHER_PAGE_CRASH');a.equal(classify({...r,targetReloadCompleted:false,error:'TimeoutError'},'').classification,'RELOAD_TIMEOUT');a.equal(classify({browserStarted:true,error:'TimeoutError'},'').classification,'PRECONDITION_TIMEOUT');a.equal(classify({},'').classification,'LAUNCH_BLOCKED');a.equal(classify(r,'').classification,'NO_REPRODUCTION');});

test('interrupted or pre-target evidence is not a completed target observation',()=>{a.equal(classify({browserStarted:true,targetReloadStarted:true,targetReloadCompleted:false},'').classification,'INCOMPLETE');a.equal(classify({browserStarted:true,targetReloadStarted:true,targetReloadCompleted:true},'').classification,'INCOMPLETE');a.equal(classify({browserStarted:true,targetReloadStarted:false},"optional:479 _M_get<unsigned long> this->_M_is_engaged() failed").classification,'PRE_TARGET_NATIVE_ASSERTION')});

test('v2 fixed route allocation',()=>{a.equal(PLANS.filter(x=>x.route==='bridge').length,5);a.equal(PLANS.filter(x=>x.route==='prior-reload').length,7);a.equal(PLANS.filter(x=>x.route==='synthetic-prior-reload').length,4);a.equal(DOC.version,2)});

test('post-observation failure does not rewrite completed primary reload; evidence incomplete',()=>{
 const r={browserStarted:true,targetReloadStarted:true,targetReloadCompleted:true,finished:'now',error:'TimeoutError: state-after'};
 const c=classify(r,'');a.equal(c.classification,'NO_REPRODUCTION');a.equal(evidenceState({code:0,...c},r),'INCOMPLETE');
});
test('sampling/event-limit loss is incomplete, never collected',()=>{
 const row={code:0,classification:'NO_REPRODUCTION'};
 for(const error of ['EVENT_LIMIT','ps failed'])a.equal(evidenceState(row,{errors:[{kind:'sampling',error}]}),'INCOMPLETE');
 a.equal(evidenceState(row,{errors:[]}),'COLLECTED');
});
