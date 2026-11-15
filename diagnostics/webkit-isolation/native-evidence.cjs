'use strict';
// Bounded, exclusive evidence files. Original streams are never reopened/truncated.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const now=()=>Number(process.hrtime.bigint())/1e6;
class Evidence {
 constructor(dir,{eventLimit=1048576,resultLimit=1048576,eventBudget,resultBudget,onFailure=()=>{},deadline=Infinity,clock=now}={}) {
  if(fs.existsSync(dir))throw Error('EVIDENCE_DIRECTORY_EXISTS');
  fs.mkdirSync(dir,{recursive:true});this.dir=dir;this.eventLimit=eventLimit;this.resultLimit=resultLimit;this.onFailure=onFailure;
  this.files=new Map();this.errors=[];this.closed=false;this.sequence=0;this.deadline=deadline;this.clock=clock;
  this.eventBudget=eventBudget||{limit:eventLimit,received:0,retained:0,discarded:0,truncated:false};
  this.resultBudget=resultBudget||{limit:resultLimit,received:0,retained:0,discarded:0,truncated:false};
 }
 failure(error){this.failureCount=(this.failureCount||0)+1;if(this.errors.length<32)this.errors.push(String(error.message||error).slice(0,1024));this.onFailure(error);}
 stream(name,limit,shared){
  if(this.closed)throw Error('EVIDENCE_CLOSED');
  if(path.basename(name)!==name||Buffer.byteLength(name)>128)throw Error('INVALID_EVIDENCE_NAME');
  if(this.files.has(name))throw Error('DUPLICATE_STREAM');
  const s={name,limit,received:0,retained:0,discarded:0,truncated:false,shared,fd:fs.openSync(path.join(this.dir,name),'wx')};
  this.files.set(name,s);return s;
 }
 append(s,value){
  const b=Buffer.from(value);s.received+=b.length;
  const counter=s.shared||s,room=Math.max(0,counter.limit-counter.retained),n=Math.min(room,b.length);
  let written=0;
  try {
   if(this.closed)throw Error('EVIDENCE_CLOSED');
   while(written<n){const k=fs.writeSync(s.fd,b,written,n-written);if(!k)throw Error('ZERO_BYTE_WRITE');written+=k;s.retained+=k;if(s.shared)counter.retained+=k;}
  }catch(e){this.failure(Error('SAVE_FAILED:'+e.message));}
  s.discarded+=b.length-written;
  if(s.shared){counter.received+=b.length;counter.discarded+=b.length-written;}
  if(counter.received>=counter.limit){s.truncated=true;counter.truncated=true;this.failure(Error('OUTPUT_LIMIT:'+s.name));}
  return written;
 }
 event(kind,value={}){
  if(this.closed)return;
  try {
   let s=this.files.get('events.jsonl');if(!s)s=this.stream('events.jsonl',this.eventLimit,this.eventBudget);
   const b=Buffer.from(JSON.stringify({sequence:++this.sequence,at:new Date().toISOString(),monotonicMs:now(),kind,...value})+'\n');
   // Keep complete JSONL records only. Rejected bytes are accounted for in summary.
   if(this.eventBudget.received+b.length>=this.eventBudget.limit){s.received+=b.length;s.discarded+=b.length;s.truncated=true;this.eventBudget.received+=b.length;this.eventBudget.discarded+=b.length;this.eventBudget.truncated=true;this.failure(Error('OUTPUT_LIMIT:events.jsonl'));return;}
   this.append(s,b);
  }catch(e){this.failure(Error('SAVE_FAILED:'+e.message));}
 }
 counters(){return [...this.files.values()].map(({fd,shared,...s})=>({...s,sharedLimit:shared?{...shared}:undefined}));}
 finish(name,result){
  if(this.closed)throw Error('EVIDENCE_ALREADY_FINALIZED');
  this.closed=true;
  for(const s of this.files.values()){try{fs.fsyncSync(s.fd);}catch(e){this.errors.push('SAVE_FAILED:'+e.message);}finally{try{fs.closeSync(s.fd);}catch(e){this.errors.push('SAVE_FAILED:'+e.message);}}}
  const payload={...result,evidence:{events:'events.jsonl',streams:this.counters(),saveErrors:[...this.errors],failureCount:this.failureCount||0}};
  payload.evidenceComplete=result.evidenceComplete!==false&&!this.errors.length&&!this.eventBudget.truncated&&!this.resultBudget.truncated&&payload.evidence.streams.every(s=>!s.truncated&&!s.discarded)&&result.capture?.evidenceComplete!==false;
  if(this.errors.length){payload.error??=this.errors[0];payload.status='BLOCKED';if(payload.classification)payload.classification={...payload.classification,status:'BLOCKED'};}
  const completionName=name.replace(/\.json$/,'-completion.json');
  const resultOutput=this.resultBudget;
  const writeResult=(file,value)=>{
   const bytes=Buffer.isBuffer(value)?value:Buffer.from(JSON.stringify(value,null,2));resultOutput.received+=bytes.length;
   if(resultOutput.retained+bytes.length>=resultOutput.limit){resultOutput.discarded+=bytes.length;resultOutput.truncated=true;throw Error('OUTPUT_LIMIT:result-records');}
   let fd,at=0;try{fd=fs.openSync(path.join(this.dir,file),'wx');while(at<bytes.length){const n=fs.writeSync(fd,bytes,at,bytes.length-at);if(!n)throw Error('ZERO_BYTE_WRITE');at+=n;resultOutput.retained+=n;}fs.fsyncSync(fd);}
   finally{resultOutput.discarded+=bytes.length-at;if(fd!==undefined)fs.closeSync(fd);}
  };
  if(this.clock()>=this.deadline){payload.status='BLOCKED';payload.error??='OVERALL_TIMEOUT_DURING_SAVE';}
  let b=Buffer.from(JSON.stringify({...payload,status:'PENDING_FINALIZATION',proposedStatus:payload.status||payload.classification?.status,completionReference:completionName},null,2));
  // Reserve space inside the same 1MiB result budget for completion/failure receipts.
  const summaryBudget=this.resultLimit-Math.min(32768,Math.floor(this.resultLimit/2));
  if(b.length>=summaryBudget){
   const received=b.length;
   Object.assign(payload,{status:'BLOCKED',error:'OUTPUT_LIMIT:'+name});
   b=Buffer.from(JSON.stringify({status:'PENDING_FINALIZATION',proposedStatus:'BLOCKED',completionReference:completionName,error:'OUTPUT_LIMIT:'+name,summaryTruncated:true,receivedBytes:received,retainedBytes:0,discardedBytes:received,rawReferences:payload.evidence.streams.map(s=>s.name)},null,2));
   payload.resultLimit={truncated:true,receivedBytes:received,retainedBytes:0,discardedBytes:received};
  }
  try{writeResult(name,b);}
  catch(e){payload.status='BLOCKED';payload.error='SAVE_FAILED:'+e.message;payload.summaryIncomplete=true;
   // A partial original is retained. A new failure receipt never replaces it.
   try{writeResult('save-failure.json',{status:'BLOCKED',error:payload.error.slice(0,1024),partialOriginal:name});}catch{}
  }
  if(this.clock()>=this.deadline){payload.status='BLOCKED';payload.error??='OVERALL_TIMEOUT_DURING_SAVE';}
  payload.completionReference=completionName;
  if(payload.error||payload.summaryIncomplete||payload.resultLimit?.truncated)payload.evidenceComplete=false;
  const receipt={status:payload.status||payload.classification?.status,requiresCallerFinalVerdict:true,summary:name,summarySha256:crypto.createHash('sha256').update(b).digest('hex'),summaryIncomplete:!!payload.summaryIncomplete,evidenceComplete:payload.evidenceComplete,
   error:payload.error?.slice(0,1024)||null,monotonicMs:this.clock(),deadlineMonotonicMs:Number.isFinite(this.deadline)?this.deadline:null};
  // Success requires the separate receipt; the immutable summary is provisional.
  try{writeResult(completionName,receipt);}
  catch(e){payload.status='BLOCKED';payload.error='SAVE_FAILED:completion:'+e.message;}
  if(this.clock()>=this.deadline){payload.status='BLOCKED';payload.error??='OVERALL_TIMEOUT_DURING_SAVE';
   try{writeResult('deadline-exceeded.json',{status:'BLOCKED',error:payload.error.slice(0,1024),completionReference:completionName,monotonicMs:this.clock()});}catch{}
  }
  if(payload.error){payload.status='BLOCKED';payload.stopReason??=payload.error;payload.evidenceComplete=false;if(payload.classification)payload.classification={...payload.classification,status:'BLOCKED'};}
  payload.resultOutput=resultOutput;
  return payload;
 }
}
module.exports={Evidence,now};
