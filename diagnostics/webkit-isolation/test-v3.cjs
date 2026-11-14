'use strict';
const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs');
const {DOC,PLANS,fixture,checkFixture,classify,evidenceState,EXPECTED_WEBKIT,compareBuild,saveBuildPreflight}=require('./isolate-v3.cjs');
const html=fs.readFileSync('prototype/eikyouki/index.html','utf8');
const payload=s=>JSON.parse(s.match(/<script[^>]*id="payload"[^>]*>([\s\S]*?)<\/script>/)[1]);
const withoutPayload=s=>s.replace(/(<script[^>]*id="payload"[^>]*>)[\s\S]*?(<\/script>)/,'$1REMOVED$2');
test('v3 frozen 8 rows A/B repeat3 WebKit then Chromium control',()=>{
 a.equal(DOC.version,3);a.equal(DOC.retries,0);a.equal(DOC.trialLimit,8);
 a.deepEqual(PLANS.map(x=>[x.fixture,x.engine,x.rep]),[['original','webkit',1],['three-record','webkit',1],['original','webkit',2],['three-record','webkit',2],['original','webkit',3],['three-record','webkit',3],['original','chromium',1],['three-record','chromium',1]]);
 a(PLANS.every(x=>x.route==='bridge-no-filters'&&!x.sample&&!x.debugger));a.equal(DOC.apiTimeoutMs,30000);a.equal(DOC.trialWallMs,150000);
});
test('one input factor only; retained rows exact and all outside payload bytes identical',()=>{
 const b=fixture(html,'three-record');a.equal(fixture(html,'original'),html);a.equal(withoutPayload(b),withoutPayload(html));
 a.deepEqual(payload(b),payload(html).filter(x=>['EK-0120','EK-0130','EK-0131'].includes(x.id)));a.equal(checkFixture(html).articles,131);a.equal(checkFixture(b).articles,3);
});
test('fault controls: missing bridge article/reference or clause rejected before launch',()=>{
 const b=fixture(html,'three-record');for(const bad of [b.replace('"id":"EK-0131"','"id":"BAD"'),b.replace(/"from":\s*"EK-0131"/,'"from":"BAD"'),b.replace(/"clause_id":\s*"EK-0120-C05"/,'"clause_id":"BAD"')]){a.notEqual(bad,b,'fault mutation actually applied');a.throws(()=>checkFixture(bad));}
 a.throws(()=>fixture(html,'unregistered'));
});
test('historical signature before target is not overridden by route failure',()=>{
 const r={browserStarted:true,targetReloadStarted:false,error:'TimeoutError',finished:'done'};
 a.equal(classify(r,"optional:479 _M_get<unsigned long> this->_M_is_engaged() failed").classification,'PRE_TARGET_NATIVE_ASSERTION');a.equal(classify({...r,pageCrash:true},'').classification,'OTHER_PAGE_CRASH');a.equal(classify(r,'').classification,'PRECONDITION_TIMEOUT');
});
test('missing and truncated collection stays incomplete despite absence of assertion',()=>{
 const r={browserStarted:true,targetReloadStarted:true,targetReloadCompleted:true,finished:'done'};a.equal(classify(r,'').classification,'NO_REPRODUCTION');
 for(const stopReason of ['WATCHDOG','STDERR_LIMIT','DESCENDANTS_REMAIN'])a.equal(evidenceState({code:0,classification:'NO_REPRODUCTION',stopReason},r),'INCOMPLETE');
 a.equal(evidenceState({code:0,classification:'NO_REPRODUCTION'},{...r,errors:[{error:'EVENT_LIMIT'}]}),'INCOMPLETE');
});
test('v3 pins historical launcher and native executable hashes, not only revision',()=>{a.equal(Object.keys(EXPECTED_WEBKIT).length,4);for(const v of Object.values(EXPECTED_WEBKIT))a.match(v,/^[a-f0-9]{64}$/);a.equal(EXPECTED_WEBKIT.renderer,'b46f88603e43eca28083389188944f7f47fd26311c8697a14f910e4f8bfa0d66')});

test('build mismatch retains expected/actual identities and cannot pass',()=>{const good=Object.fromEntries(Object.entries(EXPECTED_WEBKIT).map(([k,v])=>[k,{sha256:v,buildId:'recorded'}]));a.equal(compareBuild(good).status,'MATCH');const bad={...good,renderer:{sha256:'bad',buildId:'different'}};const r=compareBuild(bad);a.equal(r.status,'BUILD_MISMATCH');a.deepEqual(r.mismatches,['renderer']);a.equal(r.identities.renderer.sha256,'bad');a.equal(r.expected.renderer,EXPECTED_WEBKIT.renderer);a.equal(compareBuild({}).status,'BUILD_MISMATCH');});

test('build mismatch writes eight NOT_RUN rows before any browser launch',()=>{const path=require('node:path');const parent=process.env.TMPDIR||path.resolve('diagnostics/webkit-isolation');const out=fs.mkdtempSync(path.join(parent,'build-fault-'));const actual={result:'NOT_RUN'},rows=PLANS.map(p=>({id:p.id,status:'NOT_RUN'})),assessment=compareBuild({renderer:{sha256:'bad',buildId:'wrong'}});a.equal(saveBuildPreflight(out,actual,rows,assessment),false);const saved=JSON.parse(fs.readFileSync(path.join(out,'summary.json')));a.equal(saved.actual.stopReason,'BUILD_MISMATCH');a.equal(saved.actual.webKitIdentity.identities.renderer.sha256,'bad');a.equal(saved.rows.length,8);a(saved.rows.every(r=>r.status==='NOT_RUN'));a.equal(saved.actual.result,'NOT_RUN');});
