'use strict';
const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),v=require('./isolate-v6.cjs'),old=require('./isolate-v5.cjs');
const html=fs.readFileSync('prototype/eikyouki/index.html','utf8');
test('v6 fixed eight exact order, no retries, same worker and build/budgets',()=>{
 a.deepEqual(v.PLANS,old.PLANS);a.equal(v.DOC.trialLimit,8);a.equal(v.DOC.retries,0);a.equal(v.DOC.apiTimeoutMs,30000);a.equal(v.DOC.trialWallMs,150000);a.deepEqual(v.EXPECTED_WEBKIT,old.EXPECTED_WEBKIT);
 const worker=p=>fs.readFileSync(require.resolve(p),'utf8').split('async function worker(')[1].split('async function main(')[0];a.equal(worker('./isolate-v6.cjs'),worker('./isolate-v5.cjs'));
 const order=['A','B','A','B','A','B','A','B'];a.deepEqual(v.PLANS.map(x=>x.fixture),order);a.deepEqual(v.PLANS.map(x=>x.engine),[...Array(6).fill('webkit'),'chromium','chromium']);
});
test('v6 archived A and exact 57 expression bytes deleted; inverse full-byte restoration',()=>{
 const A=Buffer.from(v.fixture(html,'A')),B=Buffer.from(v.fixture(html,'B')),t=v.transformScroll(A);
 a.deepEqual(A,Buffer.from(old.fixture(html,'B')));a.equal(A.length,101957);a.equal(B.length,101900);a.equal(t.metadata.start,100145);a.equal(t.metadata.end,100202);a.equal(t.metadata.outputSha256,'d2989329db626bf06f26f3db5bedd951d9cd2edbfeb1da1867c481311508c1d1');a.deepEqual(B,Buffer.concat([A.subarray(0,100145),A.subarray(100202)]));a.equal(B[100145],59);a.equal(v.checkFixture(B.toString()).articles,3);
 a.deepEqual(Buffer.concat([B.subarray(0,100145),Buffer.from(v.SCROLL),B.subarray(100145)]),A);
 a.equal(B.includes(Buffer.from(v.SCROLL)),false);a.equal(B.toString().split('document.getElementById(target).scrollIntoView()').length,2);
 for(const bytes of [A,B])for(const m of bytes.toString().matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g))if(!m[1].includes('application/json'))new vm.Script(m[2]);
});
test('v6 rejects missing/duplicate/wrong input and unknown variant',()=>{
 const A=v.fixture(html,'A');a.throws(()=>v.fixture(html+' ','B'));a.throws(()=>v.fixture(html,'C'));
 a.throws(()=>v.transformScroll(A.replace(v.SCROLL,'')),/one exact scroll call/);a.throws(()=>v.transformScroll(A+v.SCROLL),/one exact scroll call/);a.throws(()=>v.transformScroll(A.replace('<!doctype','<!Doctype')),/archived v5 B hash/);
});
test('v6 classifier failure compatibility and strict non-reproduction',()=>{
 const sig="optional:479 _M_get unsigned long this->_M_is_engaged() failed";
 for(const r of [{browserStarted:true,targetReloadStarted:true},{browserStarted:true},{browserStarted:true,pageCrash:true},{browserStarted:true,error:'TimeoutError'},{browserStarted:true,targetReloadStarted:true,error:'TimeoutError'}])for(const stderr of ['',sig])a.deepEqual(v.classify(r,stderr),old.classify(r,stderr));
 const r={browserStarted:true,targetReloadStarted:true,targetReloadCompleted:true,finished:'yes',stateAfter:{}};a.equal(v.classify(r,'').classification,'NO_REPRODUCTION');
 for(const change of [{stateAfter:null},{finished:null},{targetReloadCompleted:false},{error:'post-state error'},{errors:['close error']},{observedPageErrors:[{message:'JS error'}]}])a.notEqual(v.classify({...r,...change},'').classification,'NO_REPRODUCTION');
 a.equal(v.classify({...r,targetReloadStarted:false},'').classification,'NOT_COMPARABLE');
});
test('v6 mismatch stops before any slot, records all eight NOT_RUN',()=>{const path=require('node:path'),dir=fs.mkdtempSync(path.join(process.cwd(),'v6-preflight-test-'));try{const ids=Object.fromEntries(Object.entries(v.EXPECTED_WEBKIT).map(([k,sha256])=>[k,{sha256}]));a.equal(v.compareBuild(ids).status,'MATCH');for(const k of Object.keys(ids))a.equal(v.compareBuild({...ids,[k]:{sha256:'bad'}}).status,'BUILD_MISMATCH');const rows=v.PLANS.map(x=>({id:x.id,status:'NOT_RUN'})),actual={};a.equal(v.saveBuildPreflight(dir,actual,rows,{status:'BUILD_MISMATCH',mismatches:['renderer']}),false);const saved=JSON.parse(fs.readFileSync(path.join(dir,'summary.json')));a.equal(saved.rows.length,8);a(saved.rows.every(x=>x.status==='NOT_RUN'));a.equal(saved.actual.result,'NOT_RUN');}finally{fs.unlinkSync(path.join(dir,'summary.json'));fs.rmdirSync(dir);}});

test('v6 event loss/corruption is incomplete, not a fatal collector exception',()=>{const path=require('node:path'),dir=fs.mkdtempSync(path.join(process.cwd(),'v6-events-test-')),f=path.join(dir,'events.jsonl');try{
 a.equal(v.readEvents(f).status,'INCOMPLETE');fs.writeFileSync(f,'bad JSON\n');a.equal(v.readEvents(f).status,'INCOMPLETE');fs.writeFileSync(f,'{}\n');a.equal(v.readEvents(f).status,'INCOMPLETE');fs.writeFileSync(f,JSON.stringify({kind:'action-start'})+'\n'+JSON.stringify({kind:'pageerror',message:'bad'})+'\n');a.equal(v.readEvents(f).status,'COLLECTED');a.equal(v.readEvents(f).pageErrors.length,1);
 a.equal(v.classify({browserStarted:false},'').classification,'LAUNCH_BLOCKED');
 }finally{if(fs.existsSync(f))fs.unlinkSync(f);fs.rmdirSync(dir);}});
