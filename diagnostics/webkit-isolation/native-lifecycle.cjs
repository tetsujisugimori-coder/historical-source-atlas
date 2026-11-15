'use strict';
const cp=require('node:child_process');
const mono=()=>Number(process.hrtime.bigint())/1e6;
class Scope {
 constructor({totalMs=60000,evidence}={}) {
  this.started=mono();this.deadline=this.started+totalMs;this.evidence=evidence;this.owned=[];this.error=null;this.commandIndex=0;
  this.aborted=new Promise((_,reject)=>{this.rejectAbort=reject});this.aborted.catch(()=>{});
  // Reserve the final four seconds for TERM, KILL and observed close.
  this.timer=setTimeout(()=>this.abort(Error('OVERALL_TIMEOUT')),Math.max(0,totalMs-4000));
 }
 check(){if(this.error)throw this.error;if(mono()>=this.deadline-4000){this.abort(Error('OVERALL_TIMEOUT'));throw this.error;}}
 abort(error){if(this.error)return;this.error=error instanceof Error?error:Error(String(error));this.rejectAbort(this.error);void this.cleanup();}
 wait(p){return Promise.race([p,this.aborted]);}
 own(child,role){
  const entry={child,role,pid:child.pid,startedMs:mono(),exitObserved:false,closeObserved:false,requests:[],errors:[]};
  entry.done=new Promise(resolve=>{entry.resolve=resolve});
  child.on('exit',(code,signal)=>{entry.exitObserved=true;entry.exit={code,signal,atMs:mono()};});
  child.on('close',(code,signal)=>{entry.closeObserved=true;entry.close={code,signal,atMs:mono()};entry.resolve();});
  child.on('error',e=>{entry.errors.push(e.message);this.abort(Error('PROCESS_ERROR:'+role+':'+e.message));});
  this.owned.push(entry);return entry;
 }
 spawn(command,args,options,role){this.check();return this.own(cp.spawn(command,args,options),role);}
 signal(entry,signal){
  if(!this.owned.includes(entry))throw Error('UNOWNED_PROCESS');
  if(entry.closeObserved||entry.exitObserved)return;
  if(entry.requests.some(r=>r.signal===signal))return;
  const request={signal,atMs:mono()};entry.requests.push(request);
  try{request.accepted=entry.child.kill(signal);if(!request.accepted)entry.errors.push('SIGNAL_NOT_ACCEPTED:'+signal);}catch(e){request.accepted=false;entry.errors.push(e.message);}
 }
 async cleanup(){
  if(this.cleaning)return this.cleaning;
  this.cleaning=(async()=>{
   for(const e of this.owned)this.signal(e,'SIGTERM');
   const all=Promise.all(this.owned.map(e=>e.done));
   let timer;await Promise.race([all,new Promise(r=>timer=setTimeout(r,Math.max(0,Math.min(2000,this.deadline-mono()))))]);clearTimeout(timer);
   for(const e of this.owned)this.signal(e,'SIGKILL');
   await Promise.race([all,new Promise(r=>timer=setTimeout(r,Math.max(0,Math.min(2000,this.deadline-mono()))))]);clearTimeout(timer);
   this.cleanupFinishedMs=mono();
   this.remaining=this.owned.filter(e=>!e.closeObserved).map(e=>({role:e.role,pid:e.pid,status:'EXIT_NOT_CONFIRMED'}));
  })();return this.cleaning;
 }
 summary(){return {startedMonotonicMs:this.started,deadlineMonotonicMs:this.deadline,elapsedMs:mono()-this.started,cleanupFinishedMs:this.cleanupFinishedMs,
  remaining:this.remaining||[],owned:this.owned.map(({child,done,resolve,...e})=>e)};}
 finish(){clearTimeout(this.timer);}
 async environment(command,args,evidence){
  this.check();const id=String(++this.commandIndex).padStart(3,'0'),limit={limit:131072,received:0,retained:0,discarded:0,truncated:false};
  const out=evidence.stream('environment-'+id+'-stdout.bin',131072,limit),err=evidence.stream('environment-'+id+'-stderr.bin',131072,limit);
  const entry=this.spawn(command,args,{stdio:['ignore','pipe','pipe']},'environment:'+id);let text='';
  for(const stream of [entry.child.stdout,entry.child.stderr])stream.on('error',e=>this.abort(e));
  entry.child.stdout.on('data',b=>{const n=evidence.append(out,b);text+=Buffer.from(b).subarray(0,n).toString('utf8');if(limit.truncated)this.abort(Error('ENVIRONMENT_OUTPUT_LIMIT'));});
  entry.child.stderr.on('data',b=>{evidence.append(err,b);if(limit.truncated)this.abort(Error('ENVIRONMENT_OUTPUT_LIMIT'));});
  const timer=setTimeout(()=>this.abort(Error('ENVIRONMENT_TIMEOUT')),5000);
  try{await this.wait(entry.done);this.check();if(entry.close?.code!==0)throw Error('ENVIRONMENT_EXIT:'+command);return text;}
  finally{clearTimeout(timer);evidence.event('environment-command',{command,args,role:entry.role,limit,close:entry.close});}
 }
}
module.exports={Scope,mono};
