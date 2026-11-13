/* Diagnostic only. No product or formal acceptance mutation. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto'),os=require('node:os'),http=require('node:http'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../..');
const HEADS={main:'3e56d13d77048d056e79c6971e6e7d24ad92b4ff',pre:'542751d9ac327a3d869d383fe75de373e8aec9d1',current:'0338e39629880eab89602abd33e0f44d697f27df'};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const git=(...args)=>cp.execFileSync('git',args,{cwd:ROOT,maxBuffer:16*1024*1024,timeout:10000});
const textGit=(...args)=>git(...args).toString().trim();
const read=p=>{try{return fs.readFileSync(p,'utf8')}catch(e){return {status:'NOT_OBTAINED',reason:e.code}}};
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,'unique transformation anchor');return s.replace(a,b)};
const PLANS=[];let n=0;
function add(head,fixture,engine='webkit',extra={}){PLANS.push({id:String(++n).padStart(2,'0')+'-'+head+'-'+fixture+'-'+engine,head,fixture,engine,route:'common',sample:false,...extra});}
for(let rep=1;rep<=2;rep++)for(const h of Object.keys(HEADS))add(h,'original','webkit',{rep});
for(const h of Object.keys(HEADS))add(h,'original','chromium');
add('current','original','webkit',{route:'bridge'});
add('current','original','webkit',{sample:true});
for(const f of ['one-record','no-css','tiny','no-restore','native-only','tiny-direct'])for(let rep=1;rep<=2;rep++)add('current',f,'webkit',{rep,route:f==='tiny-direct'?'direct':'common'});
for(const f of ['tiny','native-only'])add('current',f,'chromium');
add('current','no-focus');add('current','no-scroll');
add('current','original','webkit',{sample:true,debugger:true});
const DOC={version:1,heads:HEADS,cases:PLANS,viewport:{width:375,height:1000},motion:'no-preference',playwright:'1.56.1',apiTimeoutMs:30000,trialWallMs:150000,trialLimit:PLANS.length,retries:0,minimumFreeBytes:2*1024**3,stdoutLimit:4*1024**2,stderrLimit:8*1024**2,eventLimit:4*1024**2,coreDumps:false,productionAcceptance:false,signature:"optional:479 + _M_get + unsigned long + this->_M_is_engaged() + failed",interpretation:'NO_REPRODUCTION is not fixed or PASS; DOM differences/timeout are distinct; same signature does not prove same cause'};
function payload(s,id){const re=new RegExp('(<script[^>]*id="'+id+'"[^>]*>)([\\s\\S]*?)(</script>)');const m=s.match(re);assert(m,'payload '+id);return {value:JSON.parse(m[2]),replace:v=>s.replace(re,(_,a,b,c)=>a+JSON.stringify(v)+c)};}
function tiny({restore=true,focus=true,scroll=true,native=false}={}){
 return `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>diagnostic, not Atlas data</title><input id="search"><main id="timeline"></main><script>
const root=document.getElementById('timeline');function render(){root.innerHTML='<details class="article" id="EK-0120"><summary>Diagnostic document</summary>'+Array.from({length:5},(_,i)=>'<section tabindex="-1" class="document-clause" id="EK-0120-C0'+(i+1)+'"><a href="#EK-0120-C0'+(i+1)+'">clause '+(i+1)+'</a><p>Fixed synthetic diagnostic text.</p></section>').join('')+'</details>';}
function openReference(id){${native?'':"render();"}document.getElementById('EK-0120').open=true;const t=document.getElementById(id);if(t){${scroll?"t.scrollIntoView({behavior:'instant',block:'start'});":''}${focus?'t.focus({preventScroll:true});':''}}}
${native?'':"root.addEventListener('click',e=>{if(e.target.tagName==='A'){e.preventDefault();const id=e.target.hash.slice(1);openReference(id);history.pushState(null,'','#'+id)}});"}
document.getElementById('search').addEventListener('input',render);render();
${restore&&!native?"window.addEventListener('load',()=>{if(location.hash)openReference(location.hash.slice(1))},{once:true});":''}
<\/script>`;
}
function fixture(original,name){
 if(name==='original')return original;
 if(['tiny','tiny-direct','no-restore','native-only','no-focus','no-scroll'].includes(name))return tiny({restore:name!=='no-restore',focus:name!=='no-focus',scroll:name!=='no-scroll',native:name==='native-only'});
 let s=payload(original,'payload').replace(payload(original,'payload').value.filter(x=>x.id==='EK-0120'));
 const p=payload(s,'provenance').value;p.article_relationships=[];p.narrative_references=[];p.publication.articles=Object.fromEntries(Object.entries(p.publication.articles).filter(([k])=>k==='EK-0120'));p.document_structures=p.document_structures.filter(x=>x.article_id==='EK-0120');s=payload(s,'provenance').replace(p);
 if(name==='no-css')s=s.replace(/<style>[\s\S]*?<\/style>/,'');
 return s;
}
function classify(r,stderr){
 const signature=stderr.includes('optional:479')&&stderr.includes('_M_get')&&stderr.includes('unsigned long')&&stderr.includes("this->_M_is_engaged()")&&stderr.includes('failed');
 if(signature)return {classification:r.targetReloadStarted?'MATCHING_NATIVE_ASSERTION':'PRE_TARGET_NATIVE_ASSERTION',signatureMatch:true,targetReached:r.targetReloadStarted===true};
 if(r.pageCrash)return {classification:'OTHER_PAGE_CRASH',signatureMatch:false};
 if(!r.browserStarted)return {classification:'LAUNCH_BLOCKED',signatureMatch:false};
 if(!r.targetReloadStarted)return {classification:r.error?.includes('Timeout')?'PRECONDITION_TIMEOUT':'NOT_COMPARABLE',signatureMatch:false};
 if(r.error)return {classification:r.error.includes('Timeout')?'RELOAD_TIMEOUT':'OTHER_ERROR',signatureMatch:false};
 if(r.targetReloadCompleted!==true||!r.finished)return {classification:'INCOMPLETE',signatureMatch:false};
 return {classification:'NO_REPRODUCTION',signatureMatch:false};
}
function processes(){
 const rows=cp.execFileSync('ps',['-eo','pid=,ppid=,lstart=,rss=,comm='],{encoding:'utf8',timeout:3000,maxBuffer:2*1024**2}).trim().split('\n').map(l=>{const a=l.trim().split(/\s+/);return {pid:+a[0],ppid:+a[1],start:a.slice(2,7).join(' '),rssKiB:+a[7],name:a.slice(8).join(' ')}});
 const set=new Set([process.pid]);let changed=true;while(changed){changed=false;for(const p of rows)if(set.has(p.ppid)&&!set.has(p.pid)){set.add(p.pid);changed=true}}
 return rows.filter(x=>set.has(x.pid)).map(x=>{const st=read('/proc/'+x.pid+'/stat');return {...x,startTicks:typeof st==='string'?st.slice(st.lastIndexOf(')')+2).split(' ')[19]:'NOT_OBTAINED'}});
}
function cgroup(){const membership=read('/proc/self/cgroup'), mount=read('/proc/self/mountinfo');let rel=typeof membership==='string'?membership.split('\n').find(x=>x.startsWith('0::'))?.slice(3):null;let base='/sys/fs/cgroup';if(rel&&fs.existsSync(path.join(base,rel)))base=path.join(base,rel);return {membership,mounts:typeof mount==='string'?mount.split('\n').filter(x=>x.includes(' - cgroup')):mount,path:base,events:read(path.join(base,'memory.events')),max:read(path.join(base,'memory.max')),current:read(path.join(base,'memory.current')),peak:read(path.join(base,'memory.peak'))};}
function resource(){return {at:new Date().toISOString(),freeMemory:os.freemem(),self:process.memoryUsage(),cgroup:cgroup(),processes:processes()};}
function executableInfo(p){try{const real=fs.realpathSync(p),b=fs.readFileSync(real);let elf;try{elf=cp.execFileSync('readelf',['-n',real],{encoding:'utf8',timeout:5000,maxBuffer:128*1024})}catch(e){elf={status:'NOT_OBTAINED',reason:e.message.slice(0,1000)}}return {path:real,size:b.length,sha256:hash(b),buildId:typeof elf==='string'?elf.match(/Build ID: (\S+)/)?.[1]||'NOT_OBTAINED':'NOT_OBTAINED',readelf:elf};}catch(e){return {path:p,status:'NOT_OBTAINED',reason:e.message}}}
async function worker(out,spec,input){
 const pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');const pkg=require((process.env.PLAYWRIGHT_MODULE||'playwright')+'/package.json');assert.equal(pkg.version,DOC.playwright);const pwRoot=path.dirname(require.resolve('playwright-core/package.json'));const browserBuilds=JSON.parse(fs.readFileSync(path.join(pwRoot,'browsers.json')));
 const result={spec,started:new Date().toISOString(),browserStarted:false,targetReloadStarted:false,pageCrash:false,errors:[],actions:[],stateBefore:null,stateAfter:null,nativeStack:'NOT_OBTAINED',rendererExit:'NOT_OBTAINED',formalAcceptance:'NOT_APPLICABLE',temp:os.tmpdir(),initialResource:resource(),playwrightCore:require('playwright-core/package.json').version,browserBuilds};
 const emit=x=>{const line=JSON.stringify({at:new Date().toISOString(),...x})+'\n';if((fs.existsSync(path.join(out,'events.jsonl'))?fs.statSync(path.join(out,'events.jsonl')).size:0)+Buffer.byteLength(line)>DOC.eventLimit)throw Error('EVENT_LIMIT');fs.appendFileSync(path.join(out,'events.jsonl'),line)};
 const save=()=>fs.writeFileSync(path.join(out,'result.json'),JSON.stringify(result,null,2));save();
 const bytes=fs.readFileSync(input);result.htmlSha256=hash(bytes);
 const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(bytes)});await new Promise(r=>server.listen(0,'127.0.0.1',r));const url=`http://127.0.0.1:${server.address().port}`;
 let browser,timer,gdb,gdbTimer,gdbKillTimer,gdbDone;const native=new Map();
 const sample=()=>{try{const res=resource();for(const p of res.processes){if(!native.has(p.pid)){let ex;try{ex=fs.readlinkSync('/proc/'+p.pid+'/exe')}catch{};native.set(p.pid,{...p,exe:ex,identity:ex?executableInfo(ex):null});}}emit({kind:'resource',value:res})}catch(e){result.errors.push({kind:'sampling',error:e.message});}};
 const action=async(name,args,fn)=>{const a={name,args,start:new Date().toISOString()};result.actions.push(a);emit({kind:'action-start',name,args});try{const r=await fn();a.end=new Date().toISOString();emit({kind:'action-end',name});return r}catch(e){a.error=e.message;throw e}};
 try{
  result.launcher=executableInfo(pw[spec.engine].executablePath());
  browser=await pw[spec.engine].launch({headless:true,timeout:30000});result.browserStarted=true;result.browserVersion=browser.version();result.playwright=pkg.version;
  const context=await browser.newContext({viewport:DOC.viewport,reducedMotion:DOC.motion});const page=await context.newPage();page.setDefaultTimeout(30000);page.setDefaultNavigationTimeout(30000);
  page.on('crash',()=>{result.pageCrash=true;emit({kind:'page-crash'})});page.on('pageerror',e=>emit({kind:'pageerror',message:e.message}));page.on('console',m=>emit({kind:'console',type:m.type(),text:m.text()}));browser.on('disconnected',()=>emit({kind:'browser-disconnected'}));
  if(spec.sample){sample();timer=setInterval(sample,1000);}
  const state=()=>page.evaluate(()=>({hash:location.hash,focus:document.activeElement?.id,scrollX,scrollY,details:[...document.querySelectorAll('details')].map(x=>({id:x.id,open:x.open}))}));
  await action('goto',[spec.route==='direct'?'#EK-0120-C05':''],()=>page.goto(url+(spec.route==='direct'?'#EK-0120-C05':'')));
  if(spec.route==='bridge'){
   await action('year',['1467'],()=>page.locator('#year').selectOption('1467'));await page.locator('#year').selectOption('all');await page.locator('#chapter').selectOption('kyoto_battle');await page.locator('#chapter').selectOption('all');await page.locator('#search').fill('其由来を伝聞くに');await page.goto(url+'#EK-0131');await page.locator('.narrative-reference').filter({hasText:'EK-0130'}).click();await page.reload();await page.locator('#search').fill('');await page.locator('#year').selectOption('1461');await page.locator('#year').selectOption('all');await page.locator('#chapter').selectOption('horikoshi');await page.locator('#chapter').selectOption('all');
  }
  if(spec.route!=='direct')for(let i=1;i<=5;i++){
   const id='EK-0120-C0'+i;await action('fill',['#search',id],()=>page.locator('#search').fill(id));
   await action('click',['.article summary'],()=>page.locator('.article summary').click());
   await action('click',['#'+id+' a'],()=>page.locator('#'+id+' a').click());assert.equal(new URL(page.url()).hash,'#'+id);
  }
  assert.equal(new URL(page.url()).hash,'#EK-0120-C05');
  if(spec.sample)result.stateBefore=await action('state-before',[],state);
  if(spec.debugger){
   sample();const live=processes();const renderer=[...native.values()].filter(x=>(/WebKitWebProcess/.test(x.name)||/WebKitWebProcess/.test(x.exe||''))&&/^\d+$/.test(x.startTicks)&&live.some(y=>y.pid===x.pid&&y.startTicks===x.startTicks&&y.start===x.start));result.debugger={candidates:renderer.map(x=>({pid:x.pid,start:x.start,exe:x.exe})),status:'NOT_OBTAINED',intervention:'attach/stop/continue changes timing; separate case, no core dump'};
   if(renderer.length===1){
    const target=renderer[0];result.debugger.target={pid:target.pid,startTicks:target.startTicks,executable:target.identity};
    const maps=read('/proc/'+target.pid+'/maps');const libraries=typeof maps==='string'?[...new Set(maps.split('\n').map(l=>l.match(/\/.*$/)?.[0]).filter(x=>x&&/lib(?:WPEWebKit|webkit|javascriptcore|stdc\+\+)/i.test(x)))]:[];
    result.debugger.libraries=libraries.slice(0,20).map(executableInfo);result.debugger.symbolValidation='UNKNOWN: only listed executable/shared-library build IDs verified; stack needs independent frame-to-image match';
    const args=['-q','-nx','-batch','-ex','set pagination off','-ex','set debuginfod enabled off','-ex','handle SIGABRT stop print nopass','-p',String(target.pid),'-ex','echo ATLAS_GDB_ATTACHED\\n','-ex','continue','-ex','thread apply all bt 24','-ex','info sharedlibrary','-ex','detach'];
    const log=fs.openSync(path.join(out,'gdb.log'),'wx');let size=0;
    gdb=cp.spawn('gdb',args,{stdio:['ignore','pipe','pipe']});
    const stopGdb=reason=>{result.debugger.stopReason??=reason;gdb.kill('SIGTERM');gdbKillTimer=setTimeout(()=>gdb.kill('SIGKILL'),2000)};
    for(const stream of ['stdout','stderr'])gdb[stream].on('data',b=>{const room=Math.max(0,2*1024**2-size);if(room)fs.writeSync(log,b.subarray(0,room));size+=b.length;if(size>2*1024**2&&!result.debugger.stopReason)stopGdb('OUTPUT_LIMIT')});
    gdbDone=new Promise(resolve=>{gdb.on('error',e=>{result.debugger.error=e.message});gdb.on('close',(code,signal)=>{clearTimeout(gdbTimer);clearTimeout(gdbKillTimer);result.debugger.exit={code,signal};result.debugger.outputBytes=size;fs.closeSync(log);resolve()})});
    gdbTimer=setTimeout(()=>stopGdb('TIME_LIMIT'),45000);
    for(let k=0;k<50;k++){await new Promise(r=>setTimeout(r,100));const t=read(path.join(out,'gdb.log'));if(typeof t==='string'&&(t.includes('ATLAS_GDB_ATTACHED')||t.includes('ptrace:')||t.includes('No such process')))break;}
   }
  }
  result.targetReloadStarted=true;save();await action('target-reload',[],()=>page.reload());result.targetReloadCompleted=true;
  // Post-result observations cannot reclassify a failed primary reload as success.
  result.stateAfter=await action('state-after',[],state);
 }catch(e){result.error=e.stack;}
 finally{
  clearInterval(timer);if(gdb){for(let k=0;k<50&&!result.debugger.exit;k++)await new Promise(r=>setTimeout(r,100));if(!result.debugger.exit){result.debugger.stopReason??='FINALIZATION_LIMIT';gdb.kill('SIGTERM');gdbKillTimer=setTimeout(()=>gdb.kill('SIGKILL'),2000);}await gdbDone;clearTimeout(gdbTimer);clearTimeout(gdbKillTimer);}if(spec.sample)sample();
  result.nativeProcesses=[...native.values()];
  if(browser)try{await browser.close()}catch(e){result.errors.push({kind:'close',error:e.message})}
  await new Promise(r=>server.close(r));result.finalResource=resource();result.finished=new Date().toISOString();save();
 }
}
async function main(out,check){
 assert.equal(process.platform,'linux','Linux diagnosis only');fs.mkdirSync(out,{recursive:false});
 const available=fs.statfsSync(path.dirname(out));assert(available.bavail*available.bsize>=DOC.minimumFreeBytes,'minimum 2GiB required');
 const tmp=process.env.TMPDIR;assert(tmp&&path.isAbsolute(tmp)&&!tmp.startsWith('/tmp/'),'dedicated non-shared TMPDIR required');assert.equal(process.env.TMP,tmp);assert.equal(process.env.TEMP,tmp);fs.mkdirSync(tmp,{recursive:true});fs.writeFileSync(path.join(tmp,'write-probe-'+process.pid),'diagnostic');
 const actual={head:textGit('rev-parse','HEAD'),tree:textGit('rev-parse','HEAD^{tree}'),status:textGit('status','--porcelain'),node:process.version,os:read('/etc/os-release'),kernel:os.release(),run:process.env.GITHUB_RUN_ID||'LOCAL',attempt:process.env.GITHUB_RUN_ATTEMPT||'LOCAL',image:process.env.ImageVersion||'UNKNOWN',plan:DOC,inputs:{},cgroup:cgroup(),result:'NOT_RUN'};
 for(const [name,head] of Object.entries(HEADS)){const dir=path.join(out,'inputs',name);fs.mkdirSync(dir,{recursive:true});const html=git('show',head+':prototype/eikyouki/index.html');fs.writeFileSync(path.join(dir,'original.html'),html);actual.inputs[name]={head,tree:textGit('rev-parse',head+'^{tree}'),htmlBlob:textGit('rev-parse',head+':prototype/eikyouki/index.html'),htmlSha256:hash(html),htmlBytes:html.length};}
 const original=fs.readFileSync(path.join(out,'inputs/current/original.html'),'utf8');
 for(const spec of PLANS){const dir=path.join(out,spec.id);fs.mkdirSync(dir);const input=fixture(fs.readFileSync(path.join(out,'inputs',spec.head,'original.html'),'utf8'),spec.fixture);fs.writeFileSync(path.join(dir,'input.html'),input);}
 fs.writeFileSync(path.join(out,'plan.json'),JSON.stringify(actual,null,2));fs.copyFileSync(__filename,path.join(out,'isolate-executed.cjs'));
 if(check){console.log('CHECK_ONLY: plan/fixtures generated; no browser');return;}
 const rows=PLANS.map(spec=>({id:spec.id,status:'NOT_RUN'}));const save=()=>fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify({actual,rows},null,2));save();
 for(let i=0;i<PLANS.length;i++){
  const spec=PLANS[i],dir=path.join(out,spec.id),row=rows[i],temp=path.join(tmp,spec.id);fs.mkdirSync(temp,{recursive:false});row.status='RUNNING';save();
  await new Promise(resolve=>{const child=cp.spawn(process.execPath,[__filename,'--worker',dir,JSON.stringify(spec),path.join(dir,'input.html')],{cwd:ROOT,detached:true,env:{...process.env,TMPDIR:temp,TMP:temp,TEMP:temp,DEBUG:'pw:browser'},stdio:['ignore','pipe','pipe']});let counts={stdout:0,stderr:0},killTimer;const stop=reason=>{row.stopReason??=reason;try{process.kill(-child.pid,'SIGTERM')}catch{};killTimer=setTimeout(()=>{try{process.kill(-child.pid,'SIGKILL')}catch{}},2000)};const timer=setTimeout(()=>stop('WATCHDOG'),DOC.trialWallMs);
   for(const stream of ['stdout','stderr']){const fd=fs.openSync(path.join(dir,stream+'.log'),'wx'),limit=stream==='stdout'?DOC.stdoutLimit:DOC.stderrLimit;child[stream].on('data',b=>{const room=Math.max(0,limit-counts[stream]);if(room)fs.writeSync(fd,b.subarray(0,room));counts[stream]+=b.length;if(counts[stream]>limit)stop(stream.toUpperCase()+'_LIMIT')});child[stream].on('end',()=>fs.closeSync(fd));}
   child.on('error',e=>row.spawnError=e.message);child.on('close',(code,signal)=>{clearTimeout(timer);clearTimeout(killTimer);Object.assign(row,{code,signal,counts,status:'FINISHED'});let alive=false;try{process.kill(-child.pid,0);alive=true}catch{}row.processGroupRemaining=alive;if(alive){row.stopReason??='DESCENDANTS_REMAIN';try{process.kill(-child.pid,'SIGKILL')}catch{}}resolve();});});
  let r;try{r=JSON.parse(fs.readFileSync(path.join(dir,'result.json')))}catch{row.evidence='MISSING_RESULT';}
  if(r){Object.assign(row,classify(r,fs.readFileSync(path.join(dir,'stderr.log'),'utf8')));row.targetReached=r.targetReloadStarted===true;row.targetCompleted=r.targetReloadCompleted===true;if(r.debugger?.stopReason)row.nativeEvidence='INCOMPLETE: '+r.debugger.stopReason;}row.evidence??=(row.code===0&&!row.stopReason&&row.classification!=='INCOMPLETE'?'COLLECTED':'INCOMPLETE');save();
  if(row.stopReason||row.spawnError){actual.stopReason=row.stopReason||row.spawnError;break;}
 }
 actual.result=rows.every(r=>r.evidence==='COLLECTED')?'COLLECTION_COMPLETE':'COLLECTION_PARTIAL';save();if(actual.result!=='COLLECTION_COMPLETE')process.exitCode=1;
}
module.exports={HEADS,PLANS,DOC,fixture,classify,tiny};
if(require.main===module){if(process.argv[2]==='--worker')worker(process.argv[3],JSON.parse(process.argv[4]),process.argv[5]).catch(e=>{console.error(e);process.exitCode=1});else main(path.resolve(process.argv[2]||'evidence/isolation'),process.argv.includes('--check')).catch(e=>{console.error(e);process.exitCode=1});}
