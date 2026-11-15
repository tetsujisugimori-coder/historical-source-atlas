'use strict';
// Diagnostic-only sibling attach. No privilege escalation, ptrace policy change, core or memory capture.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function executable(file){const real=fs.realpathSync(file),bytes=fs.readFileSync(real);let buildId='NOT_OBTAINED';try{buildId=cp.execFileSync('readelf',['-n',real],{encoding:'utf8',timeout:5000,maxBuffer:131072,stdio:['ignore','pipe','pipe']}).match(/Build ID: (\S+)/)?.[1]||'NOT_OBTAINED';}catch{}return {path:real,sha256:sha(bytes),size:bytes.length,buildId};}
function parseStat(s,pid){const end=s.lastIndexOf(')');assert(end>0,'invalid process stat');assert.equal(Number(s.slice(0,s.indexOf(' '))),pid,'stat PID mismatch');const a=s.slice(end+2).trim().split(/\s+/),ppid=Number(a[1]);assert(Number.isSafeInteger(pid)&&pid>1,'valid PID');assert(Number.isSafeInteger(ppid)&&ppid>=0,'valid PPID');assert(typeof a[19]==='string'&&/^\d+$/.test(a[19]),'startTicks missing or invalid');return {pid,ppid,startTicks:a[19]};}
function stat(pid){return parseStat(fs.readFileSync(`/proc/${pid}/stat`,'utf8'),pid);}
function captureIdentity(pid,options={}){
 assert(Number.isSafeInteger(pid)&&pid>1,'valid PID');const first=stat(pid),ancestorPid=options.ancestorPid||process.pid,ancestors=[];let at=first;
 for(let i=0;i<64&&at.pid!==ancestorPid;i++){assert(at.ppid>1,'target not descendant');at=stat(at.ppid);ancestors.push(at);}
 assert.equal(at.pid,ancestorPid,'target ancestry');const exe=executable(`/proc/${pid}/exe`);if(options.expectedExeSha)assert.equal(exe.sha256,options.expectedExeSha,'target executable mismatch');
 const maps=fs.readFileSync(`/proc/${pid}/maps`,'utf8');const paths=[...new Set(maps.split('\n').map(l=>l.match(/\/(.*)$/)?.[0]).filter(Boolean))];
 const libraries=paths.filter(p=>/\/libWPEWebKit[^/]*\.so/.test(p)).map(executable);
 if(options.expectedLibrarySha){assert.equal(libraries.length,1,'unique WebKit library');assert.equal(libraries[0].sha256,options.expectedLibrarySha,'target library mismatch');}
 const last=stat(pid);assert.deepEqual(last,first,'PID changed during identity capture');return {...first,ancestorPid,ancestors,exe,libraries,options};
}
function sameIdentity(a,b){for(const x of [a,b]){assert(Number.isSafeInteger(x.pid)&&x.pid>1,'valid PID');assert(Number.isSafeInteger(x.ppid)&&x.ppid>=0,'valid PPID');assert(typeof x.startTicks==='string'&&/^\d+$/.test(x.startTicks),'startTicks missing or invalid');assert(typeof x.exe?.sha256==='string'&&x.exe.sha256.length>0,'executable hash missing');}assert.equal(b.pid,a.pid,'PID mismatch');assert.equal(b.ppid,a.ppid,'parent mismatch');assert.equal(b.startTicks,a.startTicks,'PID reused');assert.equal(b.exe.path,a.exe.path,'executable path changed');assert.equal(b.exe.size,a.exe.size,'executable size changed');assert.equal(b.exe.sha256,a.exe.sha256,'executable changed');assert.equal(b.exe.buildId,a.exe.buildId,'build changed');assert.deepEqual(b.libraries,a.libraries,'libraries changed');return true;}
function parseRecord(line){const m=line.match(/^(\d+)?([\^*=])(\w[\w-]*)(?:,(.*))?$/);return m?{token:m[1]?Number(m[1]):null,kind:m[2],class:m[3],payload:m[4]||'',raw:line}:null;}
function field(r,name){return r.payload.match(new RegExp('(?:^|,)'+name+'="((?:[^"\\\\]|\\\\.)*)"'))?.[1];}
function hasRawStack(text){return text.split('\n').filter(l=>l.startsWith('~')).some(l=>/#0(?:\s|\\t|\\n)/.test(l));}
function outcome(r){return {attachment:r.attached?'CONFIRMED':'NOT_OBTAINED',resume:r.resumed?'CONFIRMED':'NOT_OBTAINED',signalStop:r.signalStop||'NOT_OBTAINED',signalDelivery:r.signalDelivery||'NOT_OBTAINED',rendererTermination:r.rendererTermination||'NOT_OBTAINED',stack:r.stack||'NOT_OBTAINED',status:r.error||r.stopReason?'BLOCKED':r.attached&&r.resumed&&r.signalStop?.signal==='SIGABRT'&&r.rendererTermination?.reason==='exited-signalled'&&r.rendererTermination?.signal==='SIGABRT'&&r.stack==='RAW_STACK_OBTAINED'&&r.signalDelivery?.continueConfirmed?'COLLECTED':'INCOMPLETE'};}
const {Evidence}=require('./native-evidence.cjs');
const {Scope,mono}=require('./native-lifecycle.cjs');
const LIMITS=Object.freeze({overallMs:60000,gdbMs:45000,gdbBytes:2097152,childBytes:65536,eventBytes:1048576,resultBytes:1048576,environmentMs:5000,environmentBytes:131072});

async function identityAsync(pid,options,scope,evidence){
 scope.check();assert(Number.isSafeInteger(pid)&&pid>1,'valid PID');
 const readStat=async p=>{const s=await scope.wait(fs.promises.readFile(`/proc/${p}/stat`,'utf8'));scope.check();return parseStat(s,p);};
 const first=await readStat(pid),ancestorPid=options.ancestorPid||process.pid,ancestors=[];let at=first;
 for(let i=0;i<64&&at.pid!==ancestorPid;i++){assert(at.ppid>1,'target not descendant');at=await readStat(at.ppid);ancestors.push(at);}
 assert.equal(at.pid,ancestorPid,'target ancestry');
 const image=async file=>{const real=await scope.wait(fs.promises.realpath(file));const bytes=await scope.wait(fs.promises.readFile(real));scope.check();
  const notes=await scope.environment('readelf',['-n',real],evidence);return {path:real,sha256:sha(bytes),size:bytes.length,buildId:notes.match(/Build ID: (\S+)/)?.[1]||'NOT_OBTAINED'};};
 const exe=await image(`/proc/${pid}/exe`);if(options.expectedExeSha)assert.equal(exe.sha256,options.expectedExeSha,'target executable mismatch');
 if(options.requireBuildId||options.expectedExeSha)assert.notEqual(exe.buildId,'NOT_OBTAINED','required executable build ID');
 if(options.expectedBuildId)assert.equal(exe.buildId,options.expectedBuildId,'executable build ID mismatch');
 const maps=await scope.wait(fs.promises.readFile(`/proc/${pid}/maps`,'utf8'));
 const paths=[...new Set(maps.split('\n').map(l=>l.match(/\/(.*)$/)?.[0]).filter(Boolean))],libraries=[];
 for(const p of paths.filter(p=>/\/libWPEWebKit[^/]*\.so/.test(p)))libraries.push(await image(p));
 if(options.expectedLibrarySha){assert.equal(libraries.length,1,'unique WebKit library');assert.equal(libraries[0].sha256,options.expectedLibrarySha,'target library mismatch');assert.notEqual(libraries[0].buildId,'NOT_OBTAINED','required library build ID');}
 assert.deepEqual(await readStat(pid),first,'PID changed during identity capture');
 return {...first,ancestorPid,ancestors,exe,libraries,options,checkedAt:new Date().toISOString(),checkedMonotonicMs:mono()};
}

function startCapture({pid,identity,outDir,gdb='gdb',timeoutMs=LIMITS.gdbMs,maxBytes=LIMITS.gdbBytes,scope:externalScope,identityReader}){
 let failure;const scope=externalScope||new Scope();let evidence;
 try{evidence=new Evidence(outDir,{deadline:scope.deadline,clock:mono,eventBudget:externalScope?.evidence?.eventBudget,resultBudget:externalScope?.evidence?.resultBudget,onFailure:e=>failure?.(e)});}catch(e){if(!externalScope)scope.finish();throw e;}
 const readIdentity=identityReader||((p,o)=>identityAsync(p,o,scope,evidence));
 const result={pid,identity,started:new Date().toISOString(),startedMonotonicMs:mono(),commands:[],attached:false,resumed:false,
  symbols:'UNKNOWN: image build IDs do not prove matching debug symbols',signalStop:null,signalDelivery:null,rendererTermination:null,stack:'NOT_OBTAINED',rawReferences:['gdb-stdout.bin','gdb-stderr.bin','gdb-mi.log','events.jsonl'],identityChecks:[]};
 let child,entry,closed=false,finalized=false,buffer='',token=0,stackSeen=false,signalTask=null,timer,stopTask;
 const records=[],pending=new Map(),waiters=[];let resolveReady,rejectReady,resolveFinished;
 const ready=new Promise((a,b)=>{resolveReady=a;rejectReady=b});ready.catch(()=>{});
 const finished=new Promise(r=>resolveFinished=r);
 const rejectPending=e=>{for(const p of pending.values())p.reject(e);pending.clear();for(const w of waiters)w.reject(e);waiters.length=0;};
 function finalize(){
  if(finalized)return;finalized=true;clearTimeout(timer);rejectPending(Error('GDB_CLOSED'));
  if(!result.resumed){result.error??='EARLY_GDB_EXIT';rejectReady(Error(result.error));}
  result.finished=new Date().toISOString();result.elapsedMs=mono()-result.startedMonotonicMs;result.classification=outcome(result);
  result.terminationObservation=entry?{exitObserved:entry.exitObserved,closeObserved:entry.closeObserved,remaining:!entry.closeObserved,requests:entry.requests,errors:entry.errors}:null;
  const saved=evidence.finish('native-result.json',result);saved.classification=outcome(saved);
  if(!externalScope)scope.finish();resolveFinished(saved);
 }
 function stop(reason='STOP_REQUESTED'){
  if(finalized||closed)return stopTask||Promise.resolve();result.stopReason??=reason;
  rejectReady(Error(reason));rejectPending(Error(reason));
  if(stopTask)return stopTask;
  stopTask=(async()=>{
   if(entry){scope.signal(entry,'SIGTERM');let t;await Promise.race([entry.done,new Promise(r=>t=setTimeout(r,Math.max(0,Math.min(2000,scope.deadline-mono()))))]);clearTimeout(t);
    if(!entry.closeObserved)scope.signal(entry,'SIGKILL');await Promise.race([entry.done,new Promise(r=>t=setTimeout(r,Math.max(0,Math.min(2000,scope.deadline-mono()))))]);clearTimeout(t);
    if(!entry.closeObserved)result.error??='GDB_EXIT_NOT_CONFIRMED';}
   finalize();
  })();return stopTask;
 }
 function fail(error){if(finalized)return;result.error??=String(error.message||error).slice(0,1024);void stop(result.error);}
 failure=fail;
 function waitFor(predicate,from=0){if(finalized||result.error)return Promise.reject(Error(result.error||'GDB_CLOSED'));const found=records.slice(from).find(predicate);if(found)return Promise.resolve(found);return scope.wait(new Promise((resolve,reject)=>waiters.push({predicate,resolve,reject})));}
 function command(text,allowed=['done']){
  scope.check();if(closed||finalized||result.error)return Promise.reject(Error(result.error||'GDB_CLOSED'));if(result.commands.length>=32)return Promise.reject(Error('COMMAND_LIMIT'));
  const t=++token;result.commands.push({token:t,text,at:new Date().toISOString(),monotonicMs:mono()});evidence.event('command',{token:t,text});
  return scope.wait(new Promise((resolve,reject)=>{pending.set(t,{resolve:r=>allowed.includes(r.class)?resolve(r):reject(Error('GDB_COMMAND_'+r.class+':'+r.payload)),reject});child.stdin.write(t+text+'\n',e=>{if(e)fail(e)});}));
 }
 async function checkIdentity(phase){scope.check();const current=await readIdentity(pid,identity.options||{});scope.check();sameIdentity(identity,current);result.identityChecks.push({phase,identity:current});evidence.event('identity',{phase,identity:current});}
 async function onSignal(r){
  result.signalStop={signal:field(r,'signal-name'),record:r.raw,at:new Date().toISOString(),monotonicMs:mono()};
  try{await checkIdentity('signal-stop');await command('-interpreter-exec console "thread apply all bt 24"');await command('-interpreter-exec console "info sharedlibrary"');
   result.stack=stackSeen?'RAW_STACK_OBTAINED':'NOT_OBTAINED';
   const from=records.length;await command('-exec-continue',['running']);await waitFor(x=>x.kind==='*'&&x.class==='running',from);
   result.signalDelivery={requested:'SIGABRT',policy:'handle SIGABRT stop print pass',continueConfirmed:true,at:new Date().toISOString(),monotonicMs:mono()};
  }catch(e){fail(e);}
 }
 function ingest(line){
  if(hasRawStack(line))stackSeen=true;const r=parseRecord(line);if(!r)return;records.push(r);evidence.event('mi-record',{record:r.raw});
  if(r.kind==='^'&&pending.has(r.token)){const p=pending.get(r.token);pending.delete(r.token);p.resolve(r);}
  for(let i=waiters.length-1;i>=0;i--)if(waiters[i].predicate(r)){const [w]=waiters.splice(i,1);w.resolve(r);}
  if(r.kind==='*'&&r.class==='stopped'&&field(r,'reason')==='signal-received'&&field(r,'signal-name')==='SIGABRT'&&result.resumed&&!signalTask)signalTask=onSignal(r);
  if(r.kind==='*'&&r.class==='stopped'&&['exited-signalled','exited-normally','exited'].includes(field(r,'reason'))){
   result.rendererTermination={reason:field(r,'reason'),signal:field(r,'signal-name')||'NOT_OBTAINED',record:r.raw};
   child.stdin.write(++token+'-gdb-exit\n',e=>{if(e)fail(e)});
  }
  if(r.kind==='='&&r.class==='thread-group-exited')result.threadGroupExit=r.raw;
 }
 try{
  const combined={limit:Math.min(maxBytes,LIMITS.gdbBytes),received:0,retained:0,discarded:0,truncated:false};
  const streams={stdout:evidence.stream('gdb-stdout.bin',combined.limit,combined),stderr:evidence.stream('gdb-stderr.bin',combined.limit,combined)},merged=evidence.stream('gdb-mi.log',combined.limit);
  entry=scope.spawn(gdb,['--quiet','--nx','--interpreter=mi2'],{stdio:['pipe','pipe','pipe']},'gdb');child=entry.child;
  for(const name of ['stdout','stderr']){child[name].on('error',fail);child[name].on('data',value=>{
   if(finalized)return;const b=Buffer.from(value),offset=streams[name].retained,n=evidence.append(streams[name],b);evidence.append(merged,b.subarray(0,n));
   evidence.event('raw-chunk',{stream:streams[name].name,offset,received:b.length,retained:n,discarded:b.length-n});
   if(result.error)return;if(name==='stdout'){buffer+=b.subarray(0,n).toString('utf8');let i;while((i=buffer.indexOf('\n'))>=0){ingest(buffer.slice(0,i).replace(/\r$/,''));buffer=buffer.slice(i+1);}}
  });}
  child.on('error',fail);child.stdin.on('error',fail);child.on('close',(code,signal)=>{
   closed=true;result.gdbExit={code,signal};if(buffer)ingest(buffer);buffer='';
   // Drain already-resolved MI promises before freezing the one final summary.
   Promise.resolve().then(()=>Promise.resolve()).then(()=>{if(signalTask&&!result.error){
    let t;Promise.race([signalTask,new Promise(r=>t=setTimeout(()=>{result.error??='INCOMPLETE_SIGNAL_HANDLER';r();},Math.max(0,Math.min(100,scope.deadline-mono()))))]).then(()=>{clearTimeout(t);finalize();});
   }else finalize();});
  });
  timer=setTimeout(()=>fail(Error('DEBUGGER_TIMEOUT')),Math.min(timeoutMs,LIMITS.gdbMs));
  scope.aborted.catch(fail);
  (async()=>{try{
   await command('-gdb-set pagination off');await command('-gdb-set confirm off');await command('-interpreter-exec console "set debuginfod enabled off"');await command('-interpreter-exec console "handle SIGABRT stop print pass"');
   await checkIdentity('attach-before');const from=records.length;await command('-target-attach '+pid);await waitFor(r=>r.kind==='*'&&r.class==='stopped',from);await checkIdentity('attach-stopped');result.attached=true;
   const resumedFrom=records.length;await command('-exec-continue',['running']);await waitFor(r=>r.kind==='*'&&r.class==='running',resumedFrom);result.resumed=true;evidence.event('ready',{pid});resolveReady({pid,attached:true,resumed:true});
  }catch(e){fail(e);}})();
 }catch(e){fail(e);}
 return {ready,finished,stop};
}

function validatePreflightCapture(capture,childExit){assert(!capture.error,'capture error');assert(!capture.stopReason,'capture stop');assert.equal(capture.classification?.status,'COLLECTED','capture incomplete');assert.equal(capture.rendererTermination?.reason,'exited-signalled','renderer termination missing');assert.equal(capture.rendererTermination?.signal,'SIGABRT','renderer signal missing');assert.equal(capture.signalStop?.signal,'SIGABRT','signal stop missing');assert(capture.signalDelivery?.continueConfirmed,'signal pass missing');assert.equal(childExit?.signal,'SIGABRT','actual child signal mismatch');assert.equal(capture.stack,'RAW_STACK_OBTAINED','stack missing');return true;}

async function preflight(outDir,options={}){
 const scope=new Scope({totalMs:LIMITS.overallMs});let evidence;
 try{evidence=new Evidence(outDir,{deadline:scope.deadline,clock:mono,onFailure:e=>scope.abort(e)});}catch(e){scope.finish();throw e;}
 scope.evidence=evidence;
 const result={kind:'NON_BROWSER_SIBLING_ATTACH',started:new Date().toISOString(),status:'BLOCKED',limits:LIMITS,identityChecks:[],
  stack:'NOT_OBTAINED',rendererTermination:'NOT_OBTAINED',captureReference:'gdb/native-result.json',captureCompletionReference:'gdb/native-result-completion.json'};
 let target,capture,readyText='';
 const saveIdentity=async phase=>{const id=await identityAsync(target.pid,{ancestorPid:process.pid,requireBuildId:true},scope,evidence);if(result.identity)sameIdentity(result.identity,id);else result.identity=id;result.identityChecks.push({phase,identity:id});evidence.event('identity',{phase,identity:id});return id;};
 try{
  assert.equal(process.platform,'linux','Linux preflight only');
  assert(/^Max core file size\s+0\s/m.test(await scope.wait(fs.promises.readFile('/proc/self/limits','utf8'))),'core limit must be zero');
  result.gdbVersion=await scope.environment('gdb',['--version'],evidence);
  const stdout=evidence.stream('child-stdout.bin',LIMITS.childBytes),stderr=evidence.stream('child-stderr.bin',LIMITS.childBytes);
  target=scope.spawn(process.execPath,['-e','process.stdout.write("READY\\n");setInterval(()=>{},1000)'],{stdio:['ignore','pipe','pipe']},'preflight-target');
  let readyResolve,readyReject;const childReady=new Promise((a,b)=>{readyResolve=a;readyReject=b});childReady.catch(()=>{});
  target.child.stdout.on('data',b=>{const n=evidence.append(stdout,b);readyText+=Buffer.from(b).subarray(0,n).toString('utf8');if(readyText.includes('READY\n'))readyResolve();});
  target.child.stderr.on('data',b=>evidence.append(stderr,b));
  for(const stream of [target.child.stdout,target.child.stderr])stream.on('error',e=>scope.abort(e));
  target.child.once('close',()=>readyReject(Error('CHILD_EARLY_EXIT')));
  let readyTimer;try{await scope.wait(Promise.race([childReady,new Promise((_,reject)=>readyTimer=setTimeout(()=>reject(Error('CHILD_START_TIMEOUT')),5000))]));}finally{clearTimeout(readyTimer);}
  const identity=await saveIdentity('target-initial');
  capture=startCapture({pid:target.pid,identity,outDir:path.join(outDir,'gdb'),scope,identityReader:(p,o)=>identityAsync(p,o,scope,evidence)});
  await scope.wait(capture.ready);await saveIdentity('signal-before');scope.check();
  // Owned ChildProcess only, after the identity check. No arbitrary PID kill.
  if(target.exitObserved||target.closeObserved)throw Error('CHILD_EARLY_EXIT');
  scope.signal(target,'SIGABRT');result.signalRequest={signal:'SIGABRT',at:new Date().toISOString(),monotonicMs:mono()};
  result.capture=await scope.wait(capture.finished);
  let exitTimer;try{await scope.wait(Promise.race([target.done,new Promise((_,reject)=>exitTimer=setTimeout(()=>reject(Error('CHILD_EXIT_TIMEOUT')),3000))]));}finally{clearTimeout(exitTimer);}
  result.childExit=target.close;validatePreflightCapture(result.capture,result.childExit);result.status='PASS';
 }catch(e){result.reason=e.message;scope.abort(e);}
 finally{
  if(capture){await capture.stop(result.reason||'PREFLIGHT_FINALIZE');result.capture=await capture.finished;}
  await scope.cleanup();result.lifecycle=scope.summary();
  if(target)result.childExit=target.close||{code:null,signal:'NOT_OBTAINED',observed:false};
  result.cleanupSignals=result.lifecycle.owned.flatMap(p=>p.requests.filter(r=>r.signal!=='SIGABRT').map(r=>({role:p.role,pid:p.pid,...r})));
  if(scope.error||result.lifecycle.remaining.length||result.lifecycle.elapsedMs>LIMITS.overallMs||result.lifecycle.owned.some(p=>p.errors.length)){result.status='BLOCKED';result.reason??=scope.error?.message||'CLEANUP_NOT_CONFIRMED';}
  result.finished=new Date().toISOString();result.cleanupComplete=result.lifecycle.remaining.length===0;
  if(!result.cleanupComplete)result.evidenceComplete=false;
 }
 const saved=evidence.finish('preflight.json',result);scope.finish();saved.lifecycle.finalElapsedIncludingSaveMs=mono()-scope.started;if(saved.error)saved.status='BLOCKED';return saved;
}
module.exports={sha,stat,executable,captureIdentity,sameIdentity,parseRecord,field,hasRawStack,outcome,startCapture,validatePreflightCapture,preflight,identityAsync,LIMITS};
if(require.main===module)preflight(path.resolve(process.argv[2]||'native-preflight')).then(r=>{console.log(JSON.stringify(r));process.exitCode=r.status==='PASS'?0:1}).catch(e=>{console.error(e.message);process.exitCode=1});
