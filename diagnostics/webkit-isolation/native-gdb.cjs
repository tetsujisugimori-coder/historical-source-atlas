'use strict';
// Diagnostic-only sibling attach. No privilege escalation, ptrace policy change, core or memory capture.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function executable(file){const real=fs.realpathSync(file),bytes=fs.readFileSync(real);let buildId='NOT_OBTAINED';try{buildId=cp.execFileSync('readelf',['-n',real],{encoding:'utf8',timeout:5000,maxBuffer:131072,stdio:['ignore','pipe','pipe']}).match(/Build ID: (\S+)/)?.[1]||'NOT_OBTAINED';}catch{}return {path:real,sha256:sha(bytes),size:bytes.length,buildId};}
function stat(pid){const s=fs.readFileSync(`/proc/${pid}/stat`,'utf8'),a=s.slice(s.lastIndexOf(')')+2).trim().split(/\s+/);return {pid,ppid:Number(a[1]),startTicks:a[19]};}
function captureIdentity(pid,options={}){
 assert(Number.isSafeInteger(pid)&&pid>1,'valid PID');const first=stat(pid),ancestorPid=options.ancestorPid||process.pid,ancestors=[];let at=first;
 for(let i=0;i<64&&at.pid!==ancestorPid;i++){assert(at.ppid>1,'target not descendant');at=stat(at.ppid);ancestors.push(at);}
 assert.equal(at.pid,ancestorPid,'target ancestry');const exe=executable(`/proc/${pid}/exe`);if(options.expectedExeSha)assert.equal(exe.sha256,options.expectedExeSha,'target executable mismatch');
 const maps=fs.readFileSync(`/proc/${pid}/maps`,'utf8');const paths=[...new Set(maps.split('\n').map(l=>l.match(/\/(.*)$/)?.[0]).filter(Boolean))];
 const libraries=paths.filter(p=>/\/libWPEWebKit[^/]*\.so/.test(p)).map(executable);
 if(options.expectedLibrarySha){assert.equal(libraries.length,1,'unique WebKit library');assert.equal(libraries[0].sha256,options.expectedLibrarySha,'target library mismatch');}
 const last=stat(pid);assert.deepEqual(last,first,'PID changed during identity capture');return {...first,ancestorPid,ancestors,exe,libraries,options};
}
function sameIdentity(a,b){assert.equal(b.pid,a.pid,'PID mismatch');assert.equal(b.ppid,a.ppid,'parent mismatch');assert.equal(b.startTicks,a.startTicks,'PID reused');assert.equal(b.exe.sha256,a.exe.sha256,'executable changed');assert.equal(b.exe.buildId,a.exe.buildId,'build changed');assert.deepEqual(b.libraries,a.libraries,'libraries changed');return true;}
function parseRecord(line){const m=line.match(/^(\d+)?([\^*=])(\w[\w-]*)(?:,(.*))?$/);return m?{token:m[1]?Number(m[1]):null,kind:m[2],class:m[3],payload:m[4]||'',raw:line}:null;}
function field(r,name){return r.payload.match(new RegExp('(?:^|,)'+name+'="((?:[^"\\\\]|\\\\.)*)"'))?.[1];}
function hasRawStack(text){return text.split('\n').filter(l=>l.startsWith('~')).some(l=>/#0(?:\s|\\t|\\n)/.test(l));}
function outcome(r){return {attachment:r.attached?'CONFIRMED':'NOT_OBTAINED',resume:r.resumed?'CONFIRMED':'NOT_OBTAINED',signalStop:r.signalStop||'NOT_OBTAINED',signalDelivery:r.signalDelivery||'NOT_OBTAINED',rendererTermination:r.rendererTermination||'NOT_OBTAINED',stack:r.stack||'NOT_OBTAINED',status:r.error?'BLOCKED':r.rendererTermination&&r.stack==='RAW_STACK_OBTAINED'&&r.signalDelivery?.continueConfirmed?'COLLECTED':'INCOMPLETE'};}
function startCapture({pid,identity,outDir,gdb='gdb',timeoutMs=45000,maxBytes=2097152}){
 assert(!fs.existsSync(outDir),'evidence directory already exists');fs.mkdirSync(outDir,{recursive:true});const result={pid,identity,started:new Date().toISOString(),commands:[],attached:false,resumed:false,symbols:'UNKNOWN: build IDs identify images, not matching debug symbols',signalStop:null,signalDelivery:null,rendererTermination:null,stack:null};
 let count=0,buffer='',token=0,closed=false,killTimer,timer,signalHandling=false;const records=[],pending=new Map(),waiters=[];
 const fd=fs.openSync(path.join(outDir,'gdb-mi.log'),'wx');const child=cp.spawn(gdb,['--quiet','--nx','--interpreter=mi2'],{stdio:['pipe','pipe','pipe']});
 let resolveReady,rejectReady,resolveFinished;const ready=new Promise((a,b)=>{resolveReady=a;rejectReady=b});ready.catch(()=>{});const finished=new Promise(a=>resolveFinished=a);
 function persist(){fs.writeFileSync(path.join(outDir,'native-result.json'),JSON.stringify({...result,classification:outcome(result)},null,2));}
 function fail(error){result.error??=String(error?.message||error);rejectReady(Error(result.error));stop(result.error);}
 function stop(reason='STOP_REQUESTED'){result.stopReason??=reason;if(closed)return;child.kill('SIGTERM');if(!killTimer)killTimer=setTimeout(()=>{if(!closed)child.kill('SIGKILL')},2000);}
 function waitFor(predicate,from=0){const found=records.slice(from).find(predicate);if(found)return Promise.resolve(found);return new Promise((resolve,reject)=>waiters.push({predicate,resolve,reject}));}
 function command(text,allowed=['done']){if(closed)return Promise.reject(Error('GDB_CLOSED'));const t=++token;result.commands.push({token:t,text,at:new Date().toISOString()});assert(result.commands.length<=32,'COMMAND_LIMIT');return new Promise((resolve,reject)=>{pending.set(t,{resolve:r=>allowed.includes(r.class)?resolve(r):reject(Error('GDB_COMMAND_'+r.class+':'+r.payload)),reject});child.stdin.write(t+text+'\n',e=>{if(e)fail(e)});});}
 async function onSignal(r){if(signalHandling)return;signalHandling=true;result.signalStop={signal:field(r,'signal-name'),record:r.raw,at:new Date().toISOString()};
  try{sameIdentity(identity,captureIdentity(pid,identity.options));await command('-interpreter-exec console "thread apply all bt 24"');await command('-interpreter-exec console "info sharedlibrary"');
   const text=fs.readFileSync(path.join(outDir,'gdb-mi.log'),'utf8');result.stack=hasRawStack(text)?'RAW_STACK_OBTAINED':'NOT_OBTAINED';
   const from=records.length;await command('-exec-continue',['running']);await waitFor(x=>x.kind==='*'&&x.class==='running',from);result.signalDelivery={requested:'SIGABRT',policy:'handle SIGABRT stop print pass',continueConfirmed:true,at:new Date().toISOString()};
  }catch(e){fail(e);}persist();}
 function ingest(line){const r=parseRecord(line);if(!r)return;records.push(r);if(r.kind==='^'&&pending.has(r.token)){const p=pending.get(r.token);pending.delete(r.token);p.resolve(r);}
  for(let i=waiters.length-1;i>=0;i--)if(waiters[i].predicate(r)){const [w]=waiters.splice(i,1);w.resolve(r);}
  if(r.kind==='*'&&r.class==='stopped'&&field(r,'reason')==='signal-received'&&field(r,'signal-name')==='SIGABRT'&&result.resumed)void onSignal(r);
  if(r.kind==='*'&&r.class==='stopped'&&['exited-signalled','exited-normally','exited'].includes(field(r,'reason'))){result.rendererTermination={reason:field(r,'reason'),signal:field(r,'signal-name')||'NOT_OBTAINED',record:r.raw};child.stdin.write(++token+'-gdb-exit\n');}
  if(r.kind==='='&&r.class==='thread-group-exited'){result.threadGroupExit=r.raw;/* This notification alone does not identify renderer termination signal. */}
 }
 for(const name of ['stdout','stderr'])child[name].on('data',b=>{const room=Math.max(0,maxBytes-count);if(room)fs.writeSync(fd,b.subarray(0,room));count+=b.length;if(count>maxBytes){fail('OUTPUT_LIMIT');return;}if(name==='stdout'){buffer+=b.toString();let i;while((i=buffer.indexOf('\n'))>=0){ingest(buffer.slice(0,i).replace(/\r$/,''));buffer=buffer.slice(i+1);}}});
 child.on('error',fail);child.on('close',(code,signal)=>{closed=true;clearTimeout(timer);clearTimeout(killTimer);result.gdbExit={code,signal};result.outputBytes=count;result.finished=new Date().toISOString();if(!result.resumed){result.error??='EARLY_GDB_EXIT';rejectReady(Error(result.error));}for(const p of pending.values())p.reject(Error('GDB_CLOSED'));for(const w of waiters)w.reject(Error('GDB_CLOSED'));fs.closeSync(fd);persist();resolveFinished({...result,classification:outcome(result)});});
 timer=setTimeout(()=>fail('DEBUGGER_TIMEOUT'),timeoutMs);
 (async()=>{try{sameIdentity(identity,captureIdentity(pid,identity.options));await command('-gdb-set pagination off');await command('-gdb-set confirm off');await command('-interpreter-exec console "set debuginfod enabled off"');await command('-interpreter-exec console "handle SIGABRT stop print pass"');
  const attachFrom=records.length;await command('-target-attach '+pid);await waitFor(r=>r.kind==='*'&&r.class==='stopped',attachFrom);sameIdentity(identity,captureIdentity(pid,identity.options));result.attached=true;const from=records.length;await command('-exec-continue',['running']);await waitFor(r=>r.kind==='*'&&r.class==='running',from);result.resumed=true;persist();resolveReady({pid,attached:true,resumed:true});
 }catch(e){fail(e);}})();return {ready,finished,stop};
}
function validatePreflightCapture(capture,childExit){assert(!capture.error,'capture error');assert(!capture.stopReason,'capture stop');assert.equal(capture.classification?.status,'COLLECTED','capture incomplete');assert.equal(capture.rendererTermination?.reason,'exited-signalled','renderer termination missing');assert.equal(capture.rendererTermination?.signal,'SIGABRT','renderer signal missing');assert.equal(capture.signalStop?.signal,'SIGABRT','signal stop missing');assert(capture.signalDelivery?.continueConfirmed,'signal pass missing');assert.equal(childExit?.signal,'SIGABRT','actual child signal mismatch');assert.equal(capture.stack,'RAW_STACK_OBTAINED','stack missing');return true;}
async function preflight(outDir){
 assert(!fs.existsSync(outDir),'evidence directory already exists');fs.mkdirSync(outDir,{recursive:true});const result={kind:'NON_BROWSER_SIBLING_ATTACH',started:new Date().toISOString(),status:'BLOCKED'};let child,capture,childDone;try{
  assert(/^Max core file size\s+0\s/m.test(fs.readFileSync('/proc/self/limits','utf8')),'core limit must be zero');
  result.gdbVersion=cp.execFileSync('gdb',['--version'],{encoding:'utf8',timeout:5000,maxBuffer:8192});
  child=cp.spawn(process.execPath,['-e','process.stdout.write("READY\\n");setInterval(()=>{},1000)'],{stdio:['ignore','pipe','pipe']});
  childDone=new Promise(resolve=>child.once('close',(code,signal)=>{result.childExit={code,signal};resolve()}));
  await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('CHILD_START_TIMEOUT')),5000);child.stdout.once('data',b=>{clearTimeout(t);b.toString().includes('READY')?resolve():reject(Error('CHILD_NOT_READY'))});child.once('error',e=>{clearTimeout(t);reject(e)})});
  const identity=captureIdentity(child.pid,{ancestorPid:process.pid});capture=startCapture({pid:child.pid,identity,outDir:path.join(outDir,'gdb')});await capture.ready;process.kill(child.pid,'SIGABRT');result.capture=await capture.finished;
  await Promise.race([childDone,new Promise((_,reject)=>setTimeout(()=>reject(Error('CHILD_EXIT_TIMEOUT')),3000))]);
  validatePreflightCapture(result.capture,result.childExit);result.status='PASS';
 }catch(e){result.reason=e.message;}finally{capture?.stop('PREFLIGHT_FINALIZE');if(capture)await capture.finished;if(child&&!result.childExit){child.kill('SIGKILL');await Promise.race([childDone,new Promise(r=>setTimeout(r,2000))]);if(!result.childExit){result.cleanup='CHILD_EXIT_NOT_OBSERVED';result.status='BLOCKED';}}result.finished=new Date().toISOString();fs.writeFileSync(path.join(outDir,'preflight.json'),JSON.stringify(result,null,2));}return result;
}
module.exports={sha,stat,executable,captureIdentity,sameIdentity,parseRecord,field,hasRawStack,outcome,startCapture,validatePreflightCapture,preflight};
if(require.main===module)preflight(path.resolve(process.argv[2]||'native-preflight')).then(r=>{console.log(JSON.stringify(r));process.exitCode=r.status==='PASS'?0:1});
