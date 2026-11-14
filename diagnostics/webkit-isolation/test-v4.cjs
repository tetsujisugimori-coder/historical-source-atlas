'use strict';
const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const v=require('./isolate-v4.cjs'),old=require('./isolate-v3.cjs');
const html=fs.readFileSync('prototype/eikyouki/index.html','utf8'),hash=x=>crypto.createHash('sha256').update(x).digest('hex');
test('v4 frozen order, viewport, budgets, no instrumentation intervention',()=>{
 a.deepEqual(v.PLANS.map(x=>[x.fixture,x.engine,x.rep]),[['A','webkit',1],['B','webkit',1],['A','webkit',2],['B','webkit',2],['A','webkit',3],['B','webkit',3],['A','chromium',1],['B','chromium',1]]);
 a.equal(v.DOC.version,4);a.equal(v.DOC.trialLimit,8);a.equal(v.DOC.retries,0);a.equal(v.DOC.apiTimeoutMs,30000);a.equal(v.DOC.trialWallMs,150000);a.deepEqual(v.DOC.viewport,{width:375,height:1000});a(v.PLANS.every(x=>x.route==='bridge-no-filters'&&!x.sample&&!x.debugger));a.deepEqual(v.EXPECTED_WEBKIT,old.EXPECTED_WEBKIT);
});
test('A is archived v3 fixture; B only removes one style element at fixed byte offsets',()=>{
 const A=Buffer.from(v.fixture(html,'A')),B=Buffer.from(v.fixture(html,'B'));
 a.equal(A.length,107012);a.equal(B.length,101991);a.equal(hash(A),v.V3_FIXTURE_SHA);a.equal(hash(B),v.B_SHA);a.deepEqual(B,Buffer.concat([A.subarray(0,225),A.subarray(5246)]));a.equal(v.checkFixture(A.toString()).articles,3);a.equal(v.checkFixture(B.toString()).articles,3);
});
test('altered source, extra style and unknown condition rejected rather than repaired',()=>{
 for(const x of [html+' ',html.replace('<style>','<style></style><style>')])a.throws(()=>v.fixture(x,'B'));
 a.throws(()=>v.fixture(html,'C'));
});
test('v4 reuses v3 classification and preserves incomplete post-state distinction',()=>{
 const r={browserStarted:true,targetReloadStarted:true,targetReloadCompleted:true,finished:'yes'};
 for(const x of [r,{...r,error:'TimeoutError'},{browserStarted:true,error:'TimeoutError'}]){a.deepEqual(v.classify(x,''),old.classify(x,''));a.equal(v.evidenceState({code:0},x),old.evidenceState({code:0},x));}
});
test('worker action and measurement implementation is unchanged from v3',()=>{
 const section=p=>fs.readFileSync(require.resolve(p),'utf8').split('async function worker(')[1].split('async function main(')[0];a.equal(section('./isolate-v4.cjs'),section('./isolate-v3.cjs'));
});
