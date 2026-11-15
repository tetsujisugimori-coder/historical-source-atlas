'use strict';
// No native execution: child processes, MI, /proc, signals and clocks are VM mocks.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),{EventEmitter}=require('node:events');
const {run,mockEnvironment}=require('./stage-a-compare.cjs');
const {Evidence}=require('./native-evidence.cjs');
const base=process.env.ATLAS_STAGE_A_TEST_ROOT;
if(!base||!path.isAbsolute(base))throw Error('ATLAS_STAGE_A_TEST_ROOT must be a dedicated absolute directory');
fs.mkdirSync(base,{recursive:true});const root=fs.mkdtempSync(path.join(base,'negative-'));
const source=path.join(__dirname,'native-gdb.cjs'),normal=JSON.parse(fs.readFileSync(path.join(__dirname,'stage-a-fixtures/01-normal.json'),'utf8'));
let sequence=0;
function variant(overrides){const f={...normal,...overrides},p=path.join(root,'input-'+(++sequence)+'.json');fs.writeFileSync(p,JSON.stringify(f),{flag:'wx'});return p;}
function load(mock,name='native-gdb.cjs'){
 const cache=new Map();function loadFile(file){if(cache.has(file))return cache.get(file).exports;const m={exports:{}};cache.set(file,m);
  const context=vm.createContext({...mock.context,module:m,exports:m.exports,__filename:file,__dirname:path.dirname(file),require:n=>n.startsWith('./')?loadFile(path.resolve(path.dirname(file),n)):mock.require(n)});
  new vm.Script(fs.readFileSync(file,'utf8'),{filename:file}).runInContext(context,{timeout:5000});return m.exports;
 }return loadFile(path.join(__dirname,name));
}
function setup(name){const dir=path.join(root,name),mock=mockEnvironment(normal,dir);return {dir,mock};}

for(const file of fs.readdirSync(path.join(__dirname,'stage-a-fixtures')).filter(f=>/^\d.*\.json$/.test(f)).sort())test('fixed input '+file,async()=>{
 const r=await run(source,path.join(__dirname,'stage-a-fixtures',file),path.join(root,'fixed-'+file));
 assert.equal(r.status,r.expectedStatus);assert.equal(r.overwriteAttempts.length,0);assert(r.result.capture,'capture always included after creation');
 assert(r.virtualElapsedMs<=60000);assert.equal(r.result.cleanupComplete,true);
 if(file.startsWith('01')){assert.equal(r.result.capture.classification.status,'COLLECTED');assert.equal(r.result.evidenceComplete,true);assert.equal(r.result.identityChecks.at(-1).phase,'signal-before');
  assert.equal(r.result.capture.identityChecks.map(x=>x.phase).join(','),'attach-before,attach-stopped,signal-stop');
 }else if(file.startsWith('06')){assert.equal(r.result.evidenceComplete,false);assert(r.result.capture.evidence.streams.some(s=>s.truncated&&s.discarded>0));}
});

test('partial native result write retains partial original and separate failure receipt',async()=>{
 const r=await run(source,variant({fsFault:{suffix:'native-result.json',firstBytes:7}}),path.join(root,'partial-result'));
 assert.equal(r.status,'BLOCKED');assert.equal(r.result.capture.evidenceComplete,false);
 const original=path.join(root,'partial-result/runner/gdb/native-result.json');assert.equal(fs.statSync(original).size,7);
 assert(fs.existsSync(path.join(path.dirname(original),'save-failure.json')));assert.equal(r.overwriteAttempts.length,0);
});

test('exclusive result and directory creation never destroy earlier bytes',()=>{
 const dir=path.join(root,'exclusive'),e=new Evidence(dir);const raw=e.stream('raw.bin',100);e.append(raw,Buffer.from([0,255,10]));
 fs.writeFileSync(path.join(dir,'summary.json'),'OLD',{flag:'wx'});const r=e.finish('summary.json',{status:'PASS'});
 assert.equal(r.status,'BLOCKED');assert.equal(fs.readFileSync(path.join(dir,'summary.json'),'utf8'),'OLD');assert.deepEqual(fs.readFileSync(path.join(dir,'raw.bin')),Buffer.from([0,255,10]));
 assert.throws(()=>e.finish('summary.json',{status:'PASS'}),/FINALIZED/);assert.throws(()=>new Evidence(dir),/DIRECTORY_EXISTS/);
});

test('event and result caps preserve originals and classify truncation',()=>{
 const e=new Evidence(path.join(root,'limits'),{eventLimit:200,resultLimit:1024});e.event('large',{text:'x'.repeat(300)});
 const r=e.finish('summary.json',{status:'PASS',large:'x'.repeat(2000)});assert.equal(r.status,'BLOCKED');assert.equal(r.evidenceComplete,false);
 assert(r.evidence.streams.some(s=>s.truncated&&s.discarded>0));assert(r.resultLimit.truncated);assert(fs.statSync(path.join(e.dir,'summary.json')).size<1024);
});

test('stream exact limit and overflow count bytes, including binary/multibyte data',()=>{
 for(const size of [8,11]){const e=new Evidence(path.join(root,'raw-limit-'+size)),s=e.stream('raw.bin',8);const b=Buffer.from('あいうえ');e.append(s,b.subarray(0,size));const r=e.finish('summary.json',{status:'PASS'});
  assert.equal(r.status,'BLOCKED');assert.equal(s.retained,8);assert.equal(s.discarded,size-8);assert(s.truncated);assert.deepEqual(fs.readFileSync(path.join(e.dir,'raw.bin')),b.subarray(0,8));}
});

test('normal immutable summary needs completion plus caller final verdict',async()=>{
 const r=await run(source,variant({}),path.join(root,'completion'));assert.equal(r.status,'PASS');
 const dir=path.join(root,'completion/runner'),summary=JSON.parse(fs.readFileSync(path.join(dir,'preflight.json'),'utf8')),receipt=JSON.parse(fs.readFileSync(path.join(dir,'preflight-completion.json'),'utf8'));
 assert.equal(summary.status,'PENDING_FINALIZATION');assert.equal(receipt.status,'PASS');assert.equal(receipt.requiresCallerFinalVerdict,true);
 assert.equal(receipt.summarySha256,require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(dir,'preflight.json'))).digest('hex'));
});

test('overall monotonic watchdog includes hanging startup and TERM/KILL/remaining check',async()=>{
 const {mock}=setup('watchdog');const {Scope}=load(mock,'native-lifecycle.cjs'),scope=new Scope();
 const child=new EventEmitter();child.pid=999;const requests=[];child.kill=s=>{requests.push({signal:s,at:mock.clock.now});if(s==='SIGKILL')mock.clock.set(()=>{child.emit('exit',null,s);child.emit('close',null,s)},1);return true;};
 scope.own(child,'owned-synthetic');let failed=false;const task=(async()=>{try{await scope.wait(new Promise(()=>{}));}catch(e){failed=/OVERALL_TIMEOUT/.test(e.message);}await scope.cleanup();scope.finish();return scope.summary();})();
 const result=await mock.clock.until(task);assert(failed);assert.equal(requests[0].signal,'SIGTERM');assert.equal(requests[1].signal,'SIGKILL');assert.equal(requests[1].at-requests[0].at,2000);assert(result.elapsedMs<=60000);assert.equal(result.remaining.length,0);
 assert.throws(()=>scope.signal({child},'SIGKILL'),/UNOWNED/);
});

test('unconfirmed stop remains BLOCKED at absolute deadline without more signals',async()=>{
 const {mock}=setup('remaining');const {Scope}=load(mock,'native-lifecycle.cjs'),scope=new Scope();const child=new EventEmitter();child.pid=1001;child.kill=()=>false;scope.own(child,'owned-unresponsive');
 const result=await mock.clock.until((async()=>{try{await scope.wait(new Promise(()=>{}));}catch{}await scope.cleanup();scope.finish();return scope.summary();})());
 assert.equal(result.elapsedMs,60000);assert.equal(result.remaining.length,1);assert.equal(result.owned[0].requests.length,2);assert(result.owned[0].errors.length>0);
});

test('identity rejects reuse, target/parent/path/hash/build changes without treating timestamp change as mismatch',()=>{
 const n=require('./native-gdb.cjs'),a={pid:5,ppid:2,startTicks:'1',exe:{path:'/a',size:2,sha256:'a',buildId:'b'},libraries:[]};
 assert(n.sameIdentity(a,{...a,checkedAt:'later'}));for(const b of [{pid:6},{ppid:3},{startTicks:'2'},{exe:{...a.exe,path:'/b'}},{exe:{...a.exe,sha256:'x'}},{exe:{...a.exe,buildId:'x'}}])assert.throws(()=>n.sameIdentity(a,{...a,...b}));
 assert.equal(n.outcome({gdbExit:{code:0},cleanupSignals:['SIGKILL']}).rendererTermination,'NOT_OBTAINED');
});

test('GDB stdin error is caught, retained and BLOCKED',async()=>{
 const {dir,mock}=setup('stdin-error'),cp=mock.require('node:child_process'),spawn=cp.spawn;
 cp.spawn=(...args)=>{const c=spawn(...args);if(c.role==='gdb')mock.clock.set(()=>c.stdin.emit('error',Error('SYNTHETIC_EPIPE')),0);return c;};
 const n=load(mock),r=await mock.clock.until(n.preflight(dir));assert.equal(r.status,'BLOCKED');assert.match(r.capture.error,/EPIPE/);assert(fs.existsSync(path.join(dir,'preflight.json')));
});

test('slow final save and slow completion cannot return PASS outside overall deadline',async()=>{
 for(const suffix of ['preflight.json','preflight-completion.json']){
  const {dir,mock}=setup('slow-'+suffix),get=mock.require.bind(mock),io=get('node:fs'),fdPaths=new Map();
  const proxy=new Proxy(io,{get(t,k){if(k==='openSync')return (p,...args)=>{const fd=t.openSync(p,...args);fdPaths.set(fd,String(p));return fd;};if(k==='writeSync')return (fd,...args)=>{if(fdPaths.get(fd)?.endsWith(suffix))mock.clock.now+=70000;return t.writeSync(fd,...args);};if(k==='writeFileSync')return (p,...args)=>{if(String(p).endsWith(suffix))mock.clock.now+=70000;return t.writeFileSync(p,...args);};return Reflect.get(t,k);}});
  mock.require=n=>n==='node:fs'?proxy:get(n);const n=load(mock),r=await mock.clock.until(n.preflight(dir));assert.equal(r.status,'BLOCKED');assert.equal(r.evidenceComplete,false);assert(r.lifecycle.finalElapsedIncludingSaveMs>60000);
  assert.equal(JSON.parse(fs.readFileSync(path.join(dir,'preflight.json'),'utf8')).status,'PENDING_FINALIZATION');
 }
});

test('small child streams each have an independent 64KiB cap',async()=>{
 for(const stream of ['stdout','stderr']){const {dir,mock}=setup('child-'+stream),cp=mock.require('node:child_process'),spawn=cp.spawn;
  cp.spawn=(...args)=>{const child=spawn(...args);if(child.role==='node')mock.clock.set(()=>child.emitData(stream,Buffer.alloc(65536,122)),2);return child;};
  const r=await mock.clock.until(load(mock).preflight(dir));assert.equal(r.status,'BLOCKED');assert.equal(r.evidenceComplete,false);const s=r.evidence.streams.find(x=>x.name==='child-'+stream+'.bin');assert(s.truncated);assert(s.retained<=65536);
 }
});

test('environment command exact/overflow caps are byte-counted at 128KiB',async()=>{
 for(const size of [131072,131089]){const {dir,mock}=setup('env-cap-'+size),cp=mock.require('node:child_process'),spawn=cp.spawn;
  cp.spawn=(...args)=>{const c=spawn(...args);if(c.role==='environment')mock.clock.set(()=>c.emitData('stdout',Buffer.alloc(size,65)),0);return c;};
  const r=await mock.clock.until(load(mock).preflight(dir));assert.equal(r.status,'BLOCKED');assert.equal(r.evidenceComplete,false);
  const s=r.evidence.streams.find(x=>x.name==='environment-001-stdout.bin');assert.equal(s.sharedLimit.limit,131072);assert.equal(s.sharedLimit.retained,131072);assert(s.sharedLimit.truncated);
 }
});

test('environment command timeout is 5 seconds with bounded owned cleanup',async()=>{
 const {dir,mock}=setup('env-timeout'),cp=mock.require('node:child_process'),spawn=cp.spawn;
 cp.spawn=(...args)=>{const c=spawn(...args);if(c.role==='environment'){c.emitData=()=>{};c.close=()=>{};}return c;};
 const r=await mock.clock.until(load(mock).preflight(dir));assert.equal(r.status,'BLOCKED');assert.match(r.reason,/ENVIRONMENT_TIMEOUT/);assert(r.lifecycle.elapsedMs<=9000);assert.equal(r.lifecycle.owned[0].requests[0].atMs,5000);
});

test('environment spawn error is retained and cannot become PASS',async()=>{
 const {dir,mock}=setup('env-error'),cp=mock.require('node:child_process'),spawn=cp.spawn;
 cp.spawn=(...args)=>{const c=spawn(...args);if(c.role==='environment')mock.clock.set(()=>c.emit('error',Error('SYNTHETIC_SPAWN_ERROR')),0);return c;};
 const r=await mock.clock.until(load(mock).preflight(dir));assert.equal(r.status,'BLOCKED');assert.match(r.reason,/SPAWN_ERROR/);assert(fs.existsSync(path.join(dir,'preflight.json')));
});

test('reuse immediately before SIGABRT prevents the request',async()=>{
 const {dir,mock}=setup('signal-reuse'),get=mock.require.bind(mock),io=get('node:fs');let reads=0;
 const read=(p,...args)=>{let s=io.readFileSync(p,...args);if(/^\/proc\/\d+\/stat$/.test(String(p))&&++reads>=10){const at=s.lastIndexOf(')')+2,a=s.slice(at).trim().split(/\s+/);a[19]='101';s=s.slice(0,at)+a.join(' ');}return s;};
 const proxy=new Proxy(io,{get(t,k){if(k==='readFileSync')return read;if(k==='promises')return new Proxy(t.promises,{get(p,n){return n==='readFile'?async(...args)=>read(...args):Reflect.get(p,n)}});return Reflect.get(t,k);}});
 mock.require=n=>n==='node:fs'?proxy:get(n);const r=await mock.clock.until(load(mock).preflight(dir));assert.equal(r.status,'BLOCKED');assert.match(r.reason,/PID reused/);assert.equal(mock.trace.filter(x=>x.kind==='kill'&&x.signal==='SIGABRT').length,0);
});

for(const field of ['attach','termination'])test('missing required '+field+' notification is BLOCKED',async()=>{
 const protocol={...normal.protocol,[field]:field==='attach'?'token^done':''};
 const r=await run(source,variant({protocol}),path.join(root,'missing-'+field));assert.equal(r.status,'BLOCKED');assert(r.virtualElapsedMs<=60000);
});

test('native saving failure or incomplete native record cannot be promoted by a completed reload',()=>{
 const n=require('./native-stack.cjs');for(const native of [{error:'SAVE_FAILED:completion:EIO',classification:{status:'BLOCKED'},evidenceComplete:false},{classification:{status:'COLLECTED'},evidenceComplete:false},null]){
  const dir=path.join(root,'integration-'+(++sequence));fs.mkdirSync(dir);fs.writeFileSync(path.join(dir,'result.json'),JSON.stringify({browserStarted:true,targetReloadStarted:true,targetReloadCompleted:true,finished:true,stateAfter:{},actions:[],debugger:{status:'ATTACHED_AND_RUNNING'},native}));fs.writeFileSync(path.join(dir,'stderr.log'),'');fs.writeFileSync(path.join(dir,'events.jsonl'),JSON.stringify({kind:'x'}));
  const row=n.collectRow(dir,{code:0},{debugger:true});assert.equal(row.evidence,'INCOMPLETE');assert(row.stopReason);
 }
});

test('summary plus all result receipts stay within the shared result budget',()=>{
 const dir=path.join(root,'combined-result-cap'),e=new Evidence(dir);const r=e.finish('summary.json',{status:'PASS',body:'x'.repeat(1040000)});
 const bytes=fs.readdirSync(dir).filter(n=>n.endsWith('.json')).reduce((n,p)=>n+fs.statSync(path.join(dir,p)).size,0);
 assert.equal(r.status,'BLOCKED');assert(bytes<1048576);assert(r.resultOutput.retained<1048576);
});

for(const suffix of ['gdb-stdout.bin','native-result-completion.json'])test('partial '+suffix+' write blocks and retains original prefix',async()=>{
 const out=path.join(root,'partial-'+suffix),r=await run(source,variant({fsFault:{suffix,firstBytes:7}}),out);
 assert.equal(r.status,'BLOCKED');assert.equal(r.result.capture.evidenceComplete,false);assert.equal(fs.statSync(path.join(out,'runner/gdb',suffix)).size,7);assert.equal(r.overwriteAttempts.length,0);
 const top=JSON.parse(fs.readFileSync(path.join(out,'runner/preflight-completion.json'),'utf8'));assert.equal(top.status,'BLOCKED');assert.equal(top.evidenceComplete,false);
});

test('missing startTicks is BLOCKED before attach instead of equating two missing values',async()=>{
 const {dir,mock}=setup('missing-stat'),get=mock.require.bind(mock),io=get('node:fs');
 const read=(p,...args)=>{const data=io.readFileSync(p,...args);return /^\/proc\/\d+\/stat$/.test(String(p))?data.trim().split(/\s+/).slice(0,4).join(' '):data;};
 const proxy=new Proxy(io,{get(t,k){if(k==='readFileSync')return read;if(k==='promises')return new Proxy(t.promises,{get(p,n){return n==='readFile'?async(...args)=>read(...args):Reflect.get(p,n)}});return Reflect.get(t,k);}});
 mock.require=n=>n==='node:fs'?proxy:get(n);const r=await mock.clock.until(load(mock).preflight(dir));assert.equal(r.status,'BLOCKED');assert.match(r.reason,/startTicks missing or invalid/);assert.equal(mock.trace.filter(x=>x.kind==='stdin'&&x.text.includes('-target-attach')).length,0);
});

test('root and GDB evidence share one event and one result budget',()=>{
 const a=new Evidence(path.join(root,'shared-parent'),{eventLimit:500,resultLimit:2048}),b=new Evidence(path.join(root,'shared-gdb'),{eventBudget:a.eventBudget,resultBudget:a.resultBudget,resultLimit:2048});
 a.event('first',{text:'x'.repeat(100)});b.event('second',{text:'y'.repeat(300)});
 const rb=b.finish('native-result.json',{status:'PASS',body:'z'.repeat(2000)}),ra=a.finish('preflight.json',{status:'PASS'});
 assert.equal(rb.status,'BLOCKED');assert.equal(ra.evidenceComplete,false);assert.equal(a.eventBudget,b.eventBudget);assert.equal(ra.resultOutput,rb.resultOutput);assert(a.eventBudget.retained<500);assert(ra.resultOutput.retained<2048);
});
