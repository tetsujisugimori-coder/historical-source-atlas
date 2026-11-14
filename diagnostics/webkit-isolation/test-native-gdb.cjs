'use strict';
const test=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),cp=require('node:child_process');
const n=require('./native-gdb.cjs');
const tmp=fs.mkdtempSync(path.join(process.env.TMPDIR||os.tmpdir(),'atlas-native-unit-'));
function fake(mode){const p=path.join(tmp,'fake-'+mode);fs.writeFileSync(p,`#!/usr/bin/env node
const readline=require('node:readline');let continues=0;
function out(s){process.stdout.write(s+'\\n')}
readline.createInterface({input:process.stdin}).on('line',s=>{const m=s.match(/^(\\d+)(.*)$/);if(!m)return;const t=m[1],c=m[2];
 if(${JSON.stringify(mode)}==='early'){process.exit(1)}
 if(${JSON.stringify(mode)}==='timeout')return;
 if(${JSON.stringify(mode)}==='limit'){out('x'.repeat(20000));return;}
 if(c.startsWith('-target-attach')){if(${JSON.stringify(mode)}==='attachfail'){out(t+'^error,msg="ptrace: Operation not permitted"');return;}out(t+'^done');out('*stopped,reason="signal-received",signal-name="SIGSTOP"');return;}
 if(c==='-exec-continue'){continues++;out(t+'^running');if(${JSON.stringify(mode)}==='no-running')return;out('*running,thread-id="all"');
 if(continues===1)setTimeout(()=>out('*stopped,reason="signal-received",signal-name="SIGABRT"'),20);
 else setTimeout(()=>{out('*stopped,reason="exited-signalled",signal-name="SIGABRT"');},20);return;}
 if(c.includes('thread apply all')&&${JSON.stringify(mode)}!=='nostack')out('~"#0  0x1234 in abort ()\\\\n"');
 if(c==='-gdb-exit'){out(t+'^exit');process.exit(0);}
 out(t+'^done');
});
`,{mode:0o700});return p;}
async function run(mode){const child=cp.spawn('/bin/sleep',['60']);await new Promise((r,j)=>{child.once('spawn',r);child.once('error',j)});try{const identity=n.captureIdentity(child.pid,{ancestorPid:process.pid}),c=n.startCapture({pid:child.pid,identity,gdb:fake(mode),outDir:path.join(tmp,mode),timeoutMs:1000,maxBytes:10000});let ready=false;try{await c.ready;ready=true}catch{}const result=await c.finished;return {ready,result};}finally{child.kill('SIGKILL');}}
test('MI parsing preserves token, state and signal fields',()=>{const r=n.parseRecord('12^done');a.equal(r.token,12);a.equal(r.class,'done');a.equal(n.field(n.parseRecord('*stopped,reason="exited-signalled",signal-name="SIGABRT"'),'signal-name'),'SIGABRT');a.equal(n.parseRecord('bad-json'),null)});
test('identity rejects PID reuse, wrong PID/build/parent',()=>{const x={pid:10,ppid:2,startTicks:'4',exe:{sha256:'a',buildId:'b'},libraries:[]};a(n.sameIdentity(x,x));for(const patch of [{pid:11},{ppid:3},{startTicks:'5'},{exe:{sha256:'x',buildId:'b'}},{exe:{sha256:'a',buildId:'x'}}])a.throws(()=>n.sameIdentity(x,{...x,...patch}));});
test('non-descendant identity is rejected',()=>a.throws(()=>n.captureIdentity(process.pid,{ancestorPid:process.pid+1000000})));
test('normal MI attach-stop-resume-signal-stack-pass-exit',async()=>{const {ready,result:r}=await run('normal');a(ready);a.equal(r.stack,'RAW_STACK_OBTAINED');a.equal(r.signalStop.signal,'SIGABRT');a(r.signalDelivery.continueConfirmed);a.equal(r.rendererTermination.signal,'SIGABRT');a.equal(r.classification.status,'COLLECTED');});
for(const [mode,reason] of [['attachfail','GDB_COMMAND_error'],['early','EARLY_GDB_EXIT'],['no-running','DEBUGGER_TIMEOUT'],['timeout','DEBUGGER_TIMEOUT'],['limit','OUTPUT_LIMIT']])test('fault '+mode+' refuses attach/readiness',async()=>{const r=await run(mode);a.equal(r.ready,false);a.match(r.result.error||r.result.stopReason||'',new RegExp(reason));a.notEqual(r.result.classification.status,'COLLECTED');});
test('missing stack is not collection success',async()=>{const {result:r}=await run('nostack');a.equal(r.stack,'NOT_OBTAINED');a.equal(r.classification.status,'INCOMPLETE');});
test('absence of signal exit cannot infer it from launcher exit',()=>{a.equal(n.outcome({gdbExit:{code:0}}).rendererTermination,'NOT_OBTAINED');a.equal(n.outcome({resumed:true,stack:'RAW_STACK_OBTAINED'}).status,'INCOMPLETE');});

test('preflight rejects capture failure despite partial native fields',()=>{const c={classification:{status:'COLLECTED'},rendererTermination:{reason:'exited-signalled',signal:'SIGABRT'},signalStop:{signal:'SIGABRT'},signalDelivery:{continueConfirmed:true},stack:'RAW_STACK_OBTAINED'};a(n.validatePreflightCapture(c,{signal:'SIGABRT'}));for(const patch of [{error:'OUTPUT_LIMIT'},{stopReason:'DEBUGGER_TIMEOUT'},{classification:{status:'INCOMPLETE'}},{rendererTermination:null},{rendererTermination:{reason:'exited-signalled',signal:'NOT_OBTAINED'}},{stack:'NOT_OBTAINED'}])a.throws(()=>n.validatePreflightCapture({...c,...patch},{signal:'SIGABRT'}));});

test('GDB escaped console tab frames are recognized without accepting arbitrary streams',()=>{a(n.hasRawStack('~"#0\\t0x1234 in abort()\\n"'));a(n.hasRawStack('~"#0  0x1234 in abort()\\n"'));a.equal(n.hasRawStack('&"#0 fake"'),false);a.equal(n.hasRawStack('~"no stack"'),false);});
