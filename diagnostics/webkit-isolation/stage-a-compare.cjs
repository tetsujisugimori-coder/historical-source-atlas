'use strict';
// All process, /proc, signals and clocks in the runner VM are synthetic.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),cp=require('node:child_process'),{EventEmitter}=require('node:events');
const FIXTURES=path.join(__dirname,'stage-a-fixtures');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function writeNew(file,bytes){fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,bytes,{flag:'wx'});}
class Clock{
 constructor(){this.now=0;this.id=0;this.tasks=new Map();}
 set(fn,ms=0,...args){const id=++this.id;this.tasks.set(id,{id,at:this.now+Number(ms),fn:()=>fn(...args)});return id;}
 clear(id){this.tasks.delete(id);}
 async until(promise){let done=false,value,error;promise.then(v=>{value=v;done=true},e=>{error=e;done=true});for(let steps=0;steps<20000&&!done;steps++){for(let i=0;i<1000;i++)await Promise.resolve();if(done)break;const task=[...this.tasks.values()].sort((a,b)=>a.at-b.at||a.id-b.id)[0];if(!task)throw Error('HARNESS_PENDING_WITHOUT_TIMER');if(task.at>90000)throw Error('HARNESS_VIRTUAL_DEADLINE');this.now=task.at;this.tasks.delete(task.id);task.fn();}if(!done)throw Error('HARNESS_STEP_LIMIT');if(error)throw error;return value;}
}
function mockEnvironment(fixture,outDir){
 const clock=new Clock(),trace=[],writes=[],processes=new Map(),fdPaths=new Map(),faultCounts=new Map();let nextPid=4200,statReads=0,continues=0,gdb;
 const record=(kind,data={})=>trace.push({atMs:clock.now,kind,...data});
 const schedule=(fn,ms=1)=>clock.set(fn,ms);
 class Child extends EventEmitter{
  constructor(role){super();this.role=role;this.pid=++nextPid;this.stdout=new EventEmitter();this.stderr=new EventEmitter();this.stdin=new EventEmitter();this.stdin.write=(b,cb)=>{record('stdin',{pid:this.pid,bytes:Buffer.byteLength(b),text:String(b)});schedule(()=>this.command(String(b)));if(cb)schedule(()=>cb());return true;};this.stdin.end=()=>{};this.exitCode=null;this.signalCode=null;this.killed=false;processes.set(this.pid,this);schedule(()=>this.emit('spawn'));}
  emitData(stream,b){if(this.exitCode!==null||this.signalCode!==null)return;this[stream].emit('data',Buffer.from(b));}
  close(code,signal){if(this.exitCode!==null||this.signalCode!==null)return;this.exitCode=code;this.signalCode=signal;record('exit',{pid:this.pid,role:this.role,code,signal});this.emit('exit',code,signal);this.stdout.emit('end');this.stderr.emit('end');this.emit('close',code,signal);}
  kill(signal='SIGTERM'){record('kill',{pid:this.pid,role:this.role,signal});if(signal==='SIGABRT'){schedule(()=>gdb?.emitData('stdout',fixture.protocol.signalStop+'\n'));return true;}this.killed=true;schedule(()=>this.close(null,signal));return true;}
  command(line){if(this.role!=='gdb')return;const m=line.match(/^(\d+)(.*)\n?$/);if(!m)return;const token=m[1],cmd=m[2].trim();const out=s=>this.emitData('stdout',s+'\n');
   if(fixture.mode==='timeout')return;
   if(fixture.mode==='output-limit'){this.emitData('stdout',Buffer.alloc(fixture.outputBytes,120));return;}
   if(fixture.mode==='early-exit'){this.close(7,null);return;}
   if(cmd.startsWith('-target-attach')){out(fixture.protocol.attach.replaceAll('token',token).replaceAll('\\n','\n'));return;}
   if(cmd==='-exec-continue'){continues++;out(fixture.protocol.resume.replaceAll('token',token).replaceAll('\\n','\n'));if(fixture.mode==='missing-notification')return;if(continues>1)schedule(()=>{out(fixture.protocol.termination);const node=[...processes.values()].find(x=>x.role==='node');node?.close(null,'SIGABRT');});return;}
   if(cmd.includes('thread apply all'))out(fixture.protocol.stack);
   if(cmd==='-gdb-exit'){out(token+'^exit');this.close(0,null);return;}
   out(fixture.protocol.configuration.replaceAll('token',token));
  }
 }
 const mockCp={spawn(exe,args,options){record('spawn',{exe,args,options});const role=exe==='/mock/node'?'node':(args?.includes('--version')||exe==='readelf')?'environment':'gdb';const child=new Child(role);if(role==='node')schedule(()=>child.emitData('stdout','READY\n'));else if(role==='environment')schedule(()=>{child.emitData('stdout',exe==='readelf'?'Build ID: synthetic-build-id\n':'GNU gdb (synthetic) 15.1\n');child.close(0,null);});else gdb=child;return child;},
  execFileSync(exe,args,options){record('environment-command',{exe,args,options});if(exe==='readelf')return 'Build ID: synthetic-build-id\n';if(exe==='gdb')return 'GNU gdb (synthetic) 15.1\n';throw Error('HARNESS_UNEXPECTED_EXEC:'+exe);},
  execFile(exe,args,options,cb){if(typeof options==='function'){cb=options;options={};}const child=new Child('environment');schedule(()=>{let stdout='';try{stdout=mockCp.execFileSync(exe,args,options);cb?.(null,stdout,'');child.emitData('stdout',stdout);child.close(0,null);}catch(e){cb?.(e,'','');child.close(1,null);}});return child;}};
 const realFile=p=>{const a=path.resolve(String(p));if(a!==path.resolve(outDir)&&!a.startsWith(path.resolve(outDir)+path.sep))throw Error('HARNESS_FS_OUTSIDE_CASE:'+p);return a;};
 const stat=pid=>{const arr=Array(25).fill('0');arr[0]='S';arr[1]=String(pid===4000?1:4000);arr[19]=String(fixture.mode==='identity-mismatch'&&++statReads>=5?101:100);return `${pid} (synthetic) ${arr.join(' ')}\n`;};
 let mockFs;mockFs=new Proxy(fs,{get(target,key){
  if(key==='promises')return new Proxy(fs.promises,{get(p,k){if(['readFile','realpath','readlink','stat','access'].includes(k)){return async (file,...args)=>{if(k==='access'){realFile(file);return;}return mockFs[k+'Sync'](file,...args);};}return Reflect.get(p,k);}});
  if(key==='readFileSync')return (p,...args)=>{const s=String(p);if(s==='/proc/self/limits')return 'Max core file size        0        0        bytes\n';if(/^\/proc\/\d+\/stat$/.test(s))return stat(Number(s.split('/')[2]));if(/^\/proc\/\d+\/maps$/.test(s))return '';if(/^\/proc\/\d+\/exe$/.test(s))return Buffer.from('synthetic-node-executable');if(s==='/mock/node')return Buffer.from('synthetic-node-executable');if(s==='/etc/os-release')return 'NAME=SyntheticLinux\n';return fs.readFileSync(realFile(p),...args);};
  if(key==='realpathSync')return p=>String(p).startsWith('/proc/')?'/mock/node':fs.realpathSync(realFile(p));
  if(key==='readlinkSync')return p=>String(p).startsWith('/proc/')?'/mock/node':fs.readlinkSync(realFile(p));
  if(key==='writeFileSync')return (p,b,...args)=>{const file=realFile(p);writes.push({path:path.relative(outDir,file),existed:fs.existsSync(file),bytes:Buffer.byteLength(b)});return fs.writeFileSync(file,b,...args);};
  if(key==='openSync')return (p,...args)=>{const file=realFile(p),fd=target.openSync(file,...args);fdPaths.set(fd,file);return fd;};
  if(key==='writeSync')return (fd,b,offset,length,...args)=>{const file=fdPaths.get(fd),fault=fixture.fsFault;if(fault&&file&&file.endsWith(fault.suffix)){const count=faultCounts.get(fd)||0;faultCounts.set(fd,count+1);if(count===0)return fs.writeSync(fd,b,offset,Math.min(length,fault.firstBytes||7),...args);const e=Error('SYNTHETIC_WRITE_INTERRUPTION');e.code='EIO';throw e;}return fs.writeSync(fd,b,offset,length,...args);};
  if(['mkdirSync','existsSync','statSync','readdirSync','renameSync','unlinkSync','appendFileSync'].includes(key))return (p,...args)=>target[key](realFile(p),...args);
  return Reflect.get(target,key);
 }});
 const mockProcess={pid:4000,execPath:'/mock/node',platform:'linux',env:{},getuid:()=>1000,geteuid:()=>1000,hrtime:Object.assign(()=>[Math.floor(clock.now/1000),(clock.now%1000)*1e6],{bigint:()=>BigInt(Math.round(clock.now*1e6))}),kill(pid,signal){record('process.kill',{pid,signal});const child=processes.get(pid);if(!child)throw Error('HARNESS_UNOWNED_PID');if(signal===0){if(child.exitCode!==null||child.signalCode!==null){const e=Error('ESRCH');e.code='ESRCH';throw e;}return true;}if(signal==='SIGABRT'){schedule(()=>gdb?.emitData('stdout',fixture.protocol.signalStop+'\n'));return true;}return child.kill(signal);}};
 const NativeDate=Date;class MockDate extends NativeDate{constructor(...args){super(...(args.length?args:[Date.UTC(2026,10,15,11,31,0)+clock.now]));}static now(){return Date.UTC(2026,10,15,11,31,0)+clock.now;}}
 return {clock,trace,writes,processes,require(name){if(name==='node:fs')return mockFs;if(name==='node:child_process')return mockCp;return require(name);},context:{process:mockProcess,Date:MockDate,setTimeout:clock.set.bind(clock),clearTimeout:clock.clear.bind(clock),setImmediate:fn=>schedule(fn,0),clearImmediate:clock.clear.bind(clock),Buffer,console,performance:{now:()=>clock.now}}};
}
function inventory(dir){const rows=[];function walk(d){for(const item of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,item.name);if(item.isDirectory())walk(p);else{const b=fs.readFileSync(p);rows.push({path:path.relative(dir,p).split(path.sep).join('/'),bytes:b.length,sha256:sha(b)});}}}walk(dir);return rows.sort((a,b)=>a.path.localeCompare(b.path));}
async function run(sourceFile,fixtureFile,outDir){
 const bytes=fs.readFileSync(fixtureFile),fixture=JSON.parse(bytes),source=fs.readFileSync(sourceFile,'utf8');
 if(fs.existsSync(outDir))throw Error('HARNESS_CASE_ALREADY_EXISTS');fs.mkdirSync(outDir,{recursive:true});const runnerOut=path.join(outDir,'runner'),mock=mockEnvironment(fixture,runnerOut),module={exports:{}};
 const modules=new Map();
 function load(file){if(modules.has(file))return modules.get(file).exports;const m=file===sourceFile?module:{exports:{}};modules.set(file,m);const localRequire=name=>name.startsWith('.')?load(path.resolve(path.dirname(file),name)):mock.require(name);const context=vm.createContext({...mock.context,module:m,exports:m.exports,require:localRequire,__filename:file,__dirname:path.dirname(file)});new vm.Script(file===sourceFile?source:fs.readFileSync(file,'utf8'),{filename:file}).runInContext(context,{timeout:5000});return m.exports;}
 load(sourceFile);let result,error;
 try{result=await mock.clock.until(module.exports.preflight(runnerOut));}catch(e){error={name:e.name,message:e.message};}
 const status=result?.status||'HARNESS_ERROR',observedExitCode=status==='PASS'?0:1;
 const record={fixture:fixture.id,fixtureBytes:bytes.length,fixtureSha256:sha(bytes),sourceBytes:Buffer.byteLength(source),sourceSha256:sha(Buffer.from(source)),harnessSha256:sha(fs.readFileSync(__filename)),expectedStatus:fixture.expectedStatus,status,expectedClassificationMatched:status===fixture.expectedStatus,observedExitCode,exitCodeMeaning:'Requested by the isolated mock-case CLI from the returned runner status; parent comparison records the actual OS process exit separately.',virtualElapsedMs:mock.clock.now,result,error,overwriteAttempts:mock.writes.filter(x=>x.existed),processTrace:mock.trace,ownedProcesses:[...mock.processes.values()].map(x=>({pid:x.pid,role:x.role,exitCode:x.exitCode,signalCode:x.signalCode})),rawFileInventory:inventory(runnerOut)};
 writeNew(path.join(outDir,'comparison-result.json'),JSON.stringify(record,null,2)+'\n');return record;
}
async function main(){
 if(process.argv[2]==='--case'){const [,sourceFile,fixtureFile,outDir]=process.argv.slice(2);const result=await run(path.resolve(sourceFile),path.resolve(fixtureFile),path.resolve(outDir));console.log(JSON.stringify({fixture:result.fixture,status:result.status,requestedExitCode:result.observedExitCode}));process.exitCode=result.observedExitCode;return;}
 const [sourceFile,outRoot]=process.argv.slice(2);if(!sourceFile||!outRoot)throw Error('usage: node stage-a-compare.cjs <source.cjs> <new-out-root>');if(fs.existsSync(outRoot))throw Error('HARNESS_OUTPUT_EXISTS');fs.mkdirSync(outRoot,{recursive:true});const rows=[];
 for(const file of fs.readdirSync(FIXTURES).filter(x=>/^\d.*\.json$/.test(x)).sort()){
  const dir=path.join(outRoot,path.basename(file,'.json')),args=[__filename,'--case',path.resolve(sourceFile),path.join(FIXTURES,file),path.resolve(dir)];
  // These are ordinary isolated Node test processes, never GDB or a browser.
  // Their runner's process/kill interface remains fully synthetic inside VM.
  const child=cp.spawnSync(process.execPath,args,{encoding:null,maxBuffer:1048576,timeout:60000});
  writeNew(path.join(dir,'case-cli.stdout.raw'),child.stdout||Buffer.alloc(0));writeNew(path.join(dir,'case-cli.stderr.raw'),child.stderr||Buffer.alloc(0));
  const r=JSON.parse(fs.readFileSync(path.join(dir,'comparison-result.json'),'utf8'));
  rows.push({fixture:r.fixture,fixtureBytes:r.fixtureBytes,fixtureSha256:r.fixtureSha256,sourceSha256:r.sourceSha256,harnessSha256:r.harnessSha256,status:r.status,expectedStatus:r.expectedStatus,requestedExitCode:r.observedExitCode,actualOsProcessExitCode:child.status,actualOsProcessSignal:child.signal,actualOsProcessError:child.error?.message,expectedClassificationMatched:r.expectedClassificationMatched,virtualElapsedMs:r.virtualElapsedMs,captureInOverview:!!r.result?.capture,overwriteAttempts:r.overwriteAttempts.length,error:r.error,resultFileSha256:sha(fs.readFileSync(path.join(dir,'comparison-result.json')))});
 }
 writeNew(path.join(outRoot,'comparison-summary.json'),JSON.stringify(rows,null,2)+'\n');console.log(JSON.stringify(rows));if(rows.some(r=>!r.expectedClassificationMatched||r.actualOsProcessExitCode!==r.requestedExitCode||r.actualOsProcessSignal))process.exitCode=1;
}
module.exports={run,mockEnvironment,inventory};if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
