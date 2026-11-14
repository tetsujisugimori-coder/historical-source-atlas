'use strict';
const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),v=require('./isolate-v5.cjs'),old=require('./isolate-v4.cjs');
const html=fs.readFileSync('prototype/eikyouki/index.html','utf8');
test('fixed eight order and no retry; identical worker and budgets',()=>{
 a.deepEqual(v.PLANS,old.PLANS);a.equal(v.DOC.trialLimit,8);a.equal(v.DOC.retries,0);a.equal(v.DOC.apiTimeoutMs,30000);a.equal(v.DOC.trialWallMs,150000);a.deepEqual(v.EXPECTED_WEBKIT,old.EXPECTED_WEBKIT);
 const worker=p=>fs.readFileSync(require.resolve(p),'utf8').split('async function worker(')[1].split('async function main(')[0];a.equal(worker('./isolate-v5.cjs'),worker('./isolate-v4.cjs'));
});
test('only call bytes removed, semicolon retained to preserve if/return control flow',()=>{
 const A=Buffer.from(v.fixture(html,'A')), B=Buffer.from(v.fixture(html,'B')),t=v.transformFocus(A);
 a.deepEqual(A,Buffer.from(old.fixture(html,'B')));a.equal(A.length,101991);a.equal(B.length,101957);a.equal(t.metadata.start,100251);a.equal(t.metadata.end,100285);a.equal(t.metadata.outputSha256,'846a8c922565486c61236518a1120d8b3a2de14fbd40e13644905686038a7927');a.deepEqual(B,Buffer.concat([A.subarray(0,100251),A.subarray(100285)]));a.equal(B[100251],59);a.equal(v.checkFixture(B.toString()).articles,3);
});
test('wrong source, missing/duplicated call and unknown variant reject',()=>{
 const A=v.fixture(html,'A');a.throws(()=>v.fixture(html+' ','B'));a.throws(()=>v.fixture(html,'C'));
 a.throws(()=>v.transformFocus(A.replace(v.FOCUS,'')),/one exact focus call/);a.throws(()=>v.transformFocus(A+v.FOCUS),/one exact focus call/);a.throws(()=>v.transformFocus(A.replace('<!doctype','<!Doctype')),/archived v4 B hash/);
});
test('classifier preserves existing failure signatures but never accepts absent post-state',()=>{
 const sig="optional:479 _M_get unsigned long this->_M_is_engaged() failed";
 for(const r of [{browserStarted:true,targetReloadStarted:true},{browserStarted:true},{browserStarted:true,pageCrash:true},{browserStarted:true,error:'TimeoutError'},{browserStarted:true,targetReloadStarted:true,error:'TimeoutError'}])for(const stderr of ['',sig])a.deepEqual(v.classify(r,stderr),old.classify(r,stderr));
 const r={browserStarted:true,targetReloadStarted:true,targetReloadCompleted:true,finished:'yes'};a.equal(v.classify(r,'').classification,'INCOMPLETE');a.equal(v.classify({...r,stateAfter:{}},'').classification,'NO_REPRODUCTION');a.equal(v.classify({...r,stateAfter:{},error:'post-state error'},'').classification,'INCOMPLETE');
});
test('build mismatch cannot start any slot',()=>{const ids=Object.fromEntries(Object.entries(v.EXPECTED_WEBKIT).map(([k,sha256])=>[k,{sha256}]));a.equal(v.compareBuild(ids).status,'MATCH');for(const k of Object.keys(ids))a.equal(v.compareBuild({...ids,[k]:{sha256:'bad'}}).status,'BUILD_MISMATCH');});

test('mismatch saves eight NOT_RUN rows and failure identity',()=>{const path=require('node:path'),os=require('node:os'),dir=fs.mkdtempSync(path.join(process.cwd(),'v5-preflight-test-'));try{const rows=v.PLANS.map(x=>({id:x.id,status:'NOT_RUN'})),actual={};a.equal(v.saveBuildPreflight(dir,actual,rows,{status:'BUILD_MISMATCH',mismatches:['renderer']}),false);const saved=JSON.parse(fs.readFileSync(path.join(dir,'summary.json')));a.equal(saved.rows.length,8);a(saved.rows.every(x=>x.status==='NOT_RUN'));a.equal(saved.actual.result,'NOT_RUN');a.equal(saved.actual.stopReason,'BUILD_MISMATCH');}finally{fs.unlinkSync(path.join(dir,'summary.json'));fs.rmdirSync(dir);}});
