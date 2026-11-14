/* Diagnostic only. No product or formal acceptance mutation. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto'),os=require('node:os'),http=require('node:http'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../..');
const HEADS={current:'7d7a1bd9614c315287fa34ec4e740bc1965b0da5'};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const git=(...args)=>cp.execFileSync('git',args,{cwd:ROOT,maxBuffer:16*1024*1024,timeout:10000});
const textGit=(...args)=>git(...args).toString().trim();
const read=p=>{try{return fs.readFileSync(p,'utf8')}catch(e){return {status:'NOT_OBTAINED',reason:e.code}}};
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,'unique transformation anchor');return s.replace(a,b)};
const PLANS=[];let n=0;
function add(head,fixture,engine='webkit',extra={}){PLANS.push({id:String(++n).padStart(2,'0')+'-'+head+'-'+fixture+'-'+engine,head,fixture,engine,route:'common',sample:false,...extra});}
// v4: v3 three-record fixture versus removal of its sole style element.
for(let rep=1;rep<=3;rep++)for(const f of ['A','B'])add('current',f,'webkit',{route:'bridge-no-filters',rep});
for(const f of ['A','B'])add('current',f,'chromium',{route:'bridge-no-filters',rep:1});
const DOC={version:4,heads:HEADS,cases:PLANS,viewport:{width:375,height:1000},motion:'no-preference',playwright:'1.56.1',apiTimeoutMs:30000,trialWallMs:150000,trialLimit:PLANS.length,retries:0,minimumFreeBytes:2*1024**3,stdoutLimit:4*1024**2,stderrLimit:8*1024**2,eventLimit:4*1024**2,coreDumps:false,productionAcceptance:false,signature:"optional:479 + _M_get + unsigned long + this->_M_is_engaged() + failed",interpretation:'NO_REPRODUCTION is not fixed or PASS; DOM differences/timeout are distinct; same signature does not prove same cause'};
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
const V3_FIXTURE_SHA='4c88617fdb127306e228ecdee153b209f97c19a4308740444814595fe4603179';
const B_SHA='11dc7201c04c2c4fe271f2a64774a5b3a1512de201cb046f5fb58bd7c428da14';
function fixture(original,name){
 const a=require('./isolate-v3.cjs').fixture(original,'three-record');
 assert.equal(hash(Buffer.from(a)),V3_FIXTURE_SHA,'v3 archived fixture exact bytes');
 assert(['A','B'].includes(name),'registered condition');
 const bytes=Buffer.from(a),matches=[...a.matchAll(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi)];
 assert.equal(matches.length,1,'one style element');
 const start=Buffer.byteLength(a.slice(0,matches[0].index));
 const end=start+Buffer.byteLength(matches[0][0]);
 assert.equal(start,225);assert.equal(end,5246);
 if(name==='A')return a;
 const b=Buffer.concat([bytes.subarray(0,start),bytes.subarray(end)]);
 assert.equal(hash(b),B_SHA,'only style bytes removed');return b.toString('utf8');
}

function checkFixture(s){
 const rows=payload(s,'payload').value, p=payload(s,'provenance').value;
 for(const id of ['EK-0120','EK-0130','EK-0131'])assert.equal(rows.filter(x=>x.id===id).length,1,'required article '+id);
 assert.equal(p.narrative_references.filter(x=>[x.from,x.to].includes('EK-0130')&&[x.from,x.to].includes('EK-0131')).length,1,'unique bridge reference');
 const d=p.document_structures.filter(x=>x.article_id==='EK-0120');assert.equal(d.length,1);assert.deepEqual(d[0].clauses.map(x=>x.clause_id),['EK-0120-C01','EK-0120-C02','EK-0120-C03','EK-0120-C04','EK-0120-C05']);
 return {articles:rows.length,narrativeReferences:p.narrative_references.length,documentStructures:p.document_structures.length,retainedProvenance:true,interpretation:'provenance is intentionally not reduced; counts/references may exceed reduced payload'};
}
const EXPECTED_WEBKIT={launcher:'a85baad3d8c07173ac387a59b41500c382b21ed692afe0964d29aac247ccc63b',mini:'e0d1da0ec4ccb9dd0e6ed9242ee00e16d9341c086f7bdf85499d25d135bd7dc9',renderer:'b46f88603e43eca28083389188944f7f47fd26311c8697a14f910e4f8bfa0d66',webkitLibrary:'daa10258a2161710c7c1d6a3e3f7abe0a100a6f269c00f5843dcd0f7df46ec29'};
function verifyBuild(pw){
 const dir=path.dirname(pw.webkit.executablePath());
 const identities={launcher:executableInfo(pw.webkit.executablePath()),mini:executableInfo(path.join(dir,'minibrowser-wpe/bin/MiniBrowser')),renderer:executableInfo(path.join(dir,'minibrowser-wpe/bin/WPEWebProcess')),webkitLibrary:executableInfo(path.join(dir,'minibrowser-wpe/lib/libWPEWebKit-2.0.so.1.7.0'))};
 return compareBuild(identities);
}
function compareBuild(identities){
 const mismatches=Object.keys(EXPECTED_WEBKIT).filter(k=>identities[k]?.sha256!==EXPECTED_WEBKIT[k]);
 return {expected:EXPECTED_WEBKIT,identities,mismatches,status:mismatches.length?'BUILD_MISMATCH':'MATCH'};
}

function saveBuildPreflight(out,actual,rows,assessment){
 actual.webKitIdentity=assessment;
 if(assessment.status!=='MATCH'){actual.result='NOT_RUN';actual.stopReason=assessment.status;}
 fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify({actual,rows},null,2));
 return assessment.status==='MATCH';
}
function classify(r,stderr){
 const signature=stderr.includes('optional:479')&&stderr.includes('_M_get')&&stderr.includes('unsigned long')&&stderr.includes("this->_M_is_engaged()")&&stderr.includes('failed');
 if(signature)return {classification:r.targetReloadStarted?'MATCHING_NATIVE_ASSERTION':'PRE_TARGET_NATIVE_ASSERTION',signatureMatch:true,targetReached:r.targetReloadStarted===true};
 if(r.pageCrash)return {classification:'OTHER_PAGE_CRASH',signatureMatch:false};
 if(!r.browserStarted)return {classification:'LAUNCH_BLOCKED',signatureMatch:false};
 if(!r.targetReloadStarted)return {classification:r.error?.includes('Timeout')?'PRECONDITION_TIMEOUT':'NOT_COMPARABLE',signatureMatch:false};
 if(r.error&&!r.targetReloadCompleted)return {classification:r.error.includes('Timeout')?'RELOAD_TIMEOUT':'OTHER_ERROR',signatureMatch:false};
 if(r.targetReloadCompleted!==true||!r.finished)return {classification:'INCOMPLETE',signatureMatch:false};
 return {classification:'NO_REPRODUCTION',signatureMatch:false};
}
function evidenceState(row,r){return row.code===0&&!row.stopReason&&row.classification!=='INCOMPLETE'&&!(r.error&&r.targetReloadCompleted)&&!(r.errors?.length)?'COLLECTED':'INCOMPLETE';}
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
  result.webKitIdentity=verifyBuild(pw);assert.equal(result.webKitIdentity.status,'MATCH','worker build preflight');
  result.launcher=executableInfo(pw[spec.engine].executablePath());
  browser=await pw[spec.engine].launch({headless:true,timeout:30000});result.browserStarted=true;result.browserVersion=browser.version();result.playwright=pkg.version;
  const context=await browser.newContext({viewport:DOC.viewport,reducedMotion:DOC.motion});const page=await context.newPage();page.setDefaultTimeout(30000);page.setDefaultNavigationTimeout(30000);
  page.on('crash',()=>{result.pageCrash=true;emit({kind:'page-crash'})});page.on('pageerror',e=>emit({kind:'pageerror',message:e.message}));page.on('console',m=>emit({kind:'console',type:m.type(),text:m.text()}));browser.on('disconnected',()=>emit({kind:'browser-disconnected'}));
  if(spec.sample){sample();timer=setInterval(sample,1000);}
  const state=()=>page.evaluate(()=>({hash:location.hash,focus:document.activeElement?.id,scrollX,scrollY,details:[...document.querySelectorAll('details')].map(x=>({id:x.id,open:x.open}))}));
  await action('goto',[spec.route==='direct'?'#EK-0120-C05':''],()=>page.goto(url+(spec.route==='direct'?'#EK-0120-C05':'')));
  if(spec.route.startsWith('bridge')){
   if(spec.route!=='bridge-no-filters'){
    await action('prefix-year',['1467'],()=>page.locator('#year').selectOption('1467'));
    await action('prefix-year',['all'],()=>page.locator('#year').selectOption('all'));
    await action('prefix-chapter',['kyoto_battle'],()=>page.locator('#chapter').selectOption('kyoto_battle'));
    await action('prefix-chapter',['all'],()=>page.locator('#chapter').selectOption('all'));
    await action('prefix-search',['其由来を伝聞くに'],()=>page.locator('#search').fill('其由来を伝聞くに'));
   }
   await action('prefix-goto',['#EK-0131'],()=>page.goto(url+'#EK-0131'));
   await action('prefix-reference',['.narrative-reference','EK-0130'],()=>page.locator('.narrative-reference').filter({hasText:'EK-0130'}).click());
   if(spec.route!=='bridge-no-prior-reload')await action('prefix-reload',[],()=>page.reload());
   await action('prefix-search',[''],()=>page.locator('#search').fill(''));
   if(spec.route!=='bridge-no-filters'){
    await action('prefix-year',['1461'],()=>page.locator('#year').selectOption('1461'));
    await action('prefix-year',['all'],()=>page.locator('#year').selectOption('all'));
    await action('prefix-chapter',['horikoshi'],()=>page.locator('#chapter').selectOption('horikoshi'));
    await action('prefix-chapter',['all'],()=>page.locator('#chapter').selectOption('all'));
   }
  }
  if(spec.route==='prior-reload'||spec.route==='prior-no-reload'){
   await action('prior-goto',['#EK-0118'],()=>page.goto(url+'#EK-0118'));
   if(spec.route==='prior-reload')await action('prior-reload',[],()=>page.reload());
  }
  if(spec.route==='synthetic-prior-reload'){
   await action('synthetic-prior-goto',['#EK-0120-C01'],()=>page.goto(url+'#EK-0120-C01'));
   await action('synthetic-prior-reload',[],()=>page.reload());
  }
  if(spec.route!=='direct')for(let i=1;i<=5;i++){
   const id='EK-0120-C0'+i;await action('fill',['#search',id],()=>page.locator('#search').fill(id));
   await action('click',['.article summary'],()=>page.locator('.article summary').click());
   await action('click',['#'+id+' a'],()=>page.locator('#'+id+' a').click());assert.equal(new URL(page.url()).hash,'#'+id);
  }
  assert.equal(new URL(page.url()).hash,'#EK-0120-C05');
  if(spec.sample)result.stateBefore=await action('state-before',[],state);
  if(spec.debugger){
   sample();const live=processes();const renderer=[...native.values()].filter(x=>(/^(?:WPEWebProcess|WebKitWebProcess)$/.test(path.basename(x.exe||'')))&&/^\d+$/.test(x.startTicks)&&live.some(y=>y.pid===x.pid&&y.startTicks===x.startTicks&&y.start===x.start));result.debugger={candidates:renderer.map(x=>({pid:x.pid,start:x.start,exe:x.exe})),status:'NOT_OBTAINED',intervention:'attach/stop/continue changes timing; separate case, no core dump'};
   if(renderer.length===1){
    const target=renderer[0];result.debugger.target={pid:target.pid,startTicks:target.startTicks,executable:target.identity};
    const maps=read('/proc/'+target.pid+'/maps');const libraries=typeof maps==='string'?[...new Set(maps.split('\n').map(l=>l.match(/\/.*$/)?.[0]).filter(x=>x&&/lib(?:WPEWebKit|webkit|javascriptcore|stdc\+\+)/i.test(x)))]:[];
    result.debugger.libraries=libraries.slice(0,20).map(executableInfo);result.debugger.symbolValidation='UNKNOWN: only listed executable/shared-library build IDs verified; stack needs independent frame-to-image match';
    const args=['-q','-nx','-batch','-ex','set pagination off','-ex','set debuginfod enabled off','-ex','handle SIGABRT stop print pass','-p',String(target.pid),'-ex','echo ATLAS_GDB_ATTACHED\\n','-ex','continue','-ex','thread apply all bt 24','-ex','info sharedlibrary','-ex','detach'];
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
  if(result.debugger){const g=read(path.join(out,'gdb.log'));if(typeof g==='string'){
   result.debugger.observedSIGABRT=/received signal SIGABRT/.test(g);
   result.nativeStack=/^#0\s/m.test(g)?'PARTIAL_RAW_STACK_OBTAINED':'NOT_OBTAINED';
   result.rendererExit=/Program terminated with signal/.test(g)?g.match(/Program terminated with signal[^\n]*/)?.[0]:'NOT_OBTAINED';
   result.debugger.status=result.nativeStack==='NOT_OBTAINED'?'NOT_OBTAINED':'PARTIAL';
  }}
  result.nativeProcesses=[...native.values()];
  if(browser)try{await browser.close()}catch(e){result.errors.push({kind:'close',error:e.message})}
  await new Promise(r=>server.close(r));result.finalResource=resource();result.finished=new Date().toISOString();save();
 }
}
async function main(out,check){
 assert.equal(process.platform,'linux','Linux diagnosis only');fs.mkdirSync(out,{recursive:false});
 const available=fs.statfsSync(path.dirname(out));assert(available.bavail*available.bsize>=DOC.minimumFreeBytes,'minimum 2GiB required');
 assert(available.ffree>=1024,'minimum 1024 free inodes required');
 const tmp=process.env.TMPDIR;assert(tmp&&path.isAbsolute(tmp)&&!tmp.startsWith('/tmp/'),'dedicated non-shared TMPDIR required');assert.equal(process.env.TMP,tmp);assert.equal(process.env.TEMP,tmp);fs.mkdirSync(tmp,{recursive:true});fs.writeFileSync(path.join(tmp,'write-probe-'+process.pid),'diagnostic');
 const actual={estimatedGeneratedBytes:256*1024**2,availableBefore:{bytes:available.bavail*available.bsize,inodes:available.ffree},head:textGit('rev-parse','HEAD'),tree:textGit('rev-parse','HEAD^{tree}'),status:textGit('status','--porcelain'),node:process.version,os:read('/etc/os-release'),kernel:os.release(),run:process.env.GITHUB_RUN_ID||'LOCAL',attempt:process.env.GITHUB_RUN_ATTEMPT||'LOCAL',image:process.env.ImageVersion||'UNKNOWN',plan:DOC,inputs:{},cgroup:cgroup(),result:'NOT_RUN'};
 for(const [name,head] of Object.entries(HEADS)){const dir=path.join(out,'inputs',name);fs.mkdirSync(dir,{recursive:true});const html=git('show',head+':prototype/eikyouki/index.html');fs.writeFileSync(path.join(dir,'original.html'),html);actual.inputs[name]={head,tree:textGit('rev-parse',head+'^{tree}'),htmlBlob:textGit('rev-parse',head+':prototype/eikyouki/index.html'),htmlSha256:hash(html),htmlBytes:html.length};}
 const original=fs.readFileSync(path.join(out,'inputs/current/original.html'),'utf8');
 const gdb=cp.spawnSync('sh',['-c','command -v gdb'],{encoding:'utf8',timeout:3000,maxBuffer:4096});actual.nativePreflight={gdbAvailable:gdb.status===0,path:gdb.status===0?gdb.stdout.trim():null,status:'NOT_OBTAINED',reason:gdb.status===0?'No debugger intervention registered in this 8-trial style comparison; separate native plan required':'GDB not found; no spawn/attach attempted'};
 for(const spec of PLANS){const dir=path.join(out,spec.id);fs.mkdirSync(dir);const input=fixture(fs.readFileSync(path.join(out,'inputs',spec.head,'original.html'),'utf8'),spec.fixture);const contract=checkFixture(input);fs.writeFileSync(path.join(dir,'input-contract.json'),JSON.stringify(contract,null,2));fs.writeFileSync(path.join(dir,'input.html'),input);}
 fs.writeFileSync(path.join(out,'plan.json'),JSON.stringify(actual,null,2));fs.copyFileSync(__filename,path.join(out,'isolate-executed.cjs'));
 if(check){console.log('CHECK_ONLY: plan/fixtures generated; no browser');return;}
 const rows=PLANS.map(spec=>({id:spec.id,status:'NOT_RUN'}));const save=()=>fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify({actual,rows},null,2));save();
 try{actual.webKitIdentity=verifyBuild(require(process.env.PLAYWRIGHT_MODULE||'playwright'));}catch(e){actual.webKitIdentity={status:'PREFLIGHT_ERROR',error:e.message};}
 if(!saveBuildPreflight(out,actual,rows,actual.webKitIdentity)){process.exitCode=1;return;}
 for(let i=0;i<PLANS.length;i++){
  const spec=PLANS[i],dir=path.join(out,spec.id),row=rows[i],temp=path.join(tmp,spec.id);fs.mkdirSync(temp,{recursive:false});row.status='RUNNING';save();
  await new Promise(resolve=>{const child=cp.spawn(process.execPath,[__filename,'--worker',dir,JSON.stringify(spec),path.join(dir,'input.html')],{cwd:ROOT,detached:true,env:{...process.env,TMPDIR:temp,TMP:temp,TEMP:temp,DEBUG:'pw:browser'},stdio:['ignore','pipe','pipe']});let counts={stdout:0,stderr:0},killTimer;const stop=reason=>{row.stopReason??=reason;try{process.kill(-child.pid,'SIGTERM')}catch{};killTimer=setTimeout(()=>{try{process.kill(-child.pid,'SIGKILL')}catch{}},2000)};const timer=setTimeout(()=>stop('WATCHDOG'),DOC.trialWallMs);
   for(const stream of ['stdout','stderr']){const fd=fs.openSync(path.join(dir,stream+'.log'),'wx'),limit=stream==='stdout'?DOC.stdoutLimit:DOC.stderrLimit;child[stream].on('data',b=>{const room=Math.max(0,limit-counts[stream]);if(room)fs.writeSync(fd,b.subarray(0,room));counts[stream]+=b.length;if(counts[stream]>limit)stop(stream.toUpperCase()+'_LIMIT')});child[stream].on('end',()=>fs.closeSync(fd));}
   child.on('error',e=>row.spawnError=e.message);child.on('close',(code,signal)=>{clearTimeout(timer);clearTimeout(killTimer);Object.assign(row,{code,signal,counts,status:'FINISHED'});let alive=false;try{process.kill(-child.pid,0);alive=true}catch{}row.processGroupRemaining=alive;if(alive){row.stopReason??='DESCENDANTS_REMAIN';try{process.kill(-child.pid,'SIGKILL')}catch{}}resolve();});});
  let r;try{r=JSON.parse(fs.readFileSync(path.join(dir,'result.json')))}catch{row.evidence='MISSING_RESULT';}
  if(r){Object.assign(row,classify(r,fs.readFileSync(path.join(dir,'stderr.log'),'utf8')));row.targetReached=r.targetReloadStarted===true;row.targetCompleted=r.targetReloadCompleted===true;if(r.debugger?.stopReason)row.nativeEvidence='INCOMPLETE: '+r.debugger.stopReason;}row.evidence??=evidenceState(row,r||{});save();
  if(row.stopReason||row.spawnError){actual.stopReason=row.stopReason||row.spawnError;break;}
 }
 actual.result=rows.every(r=>r.evidence==='COLLECTED')?'COLLECTION_COMPLETE':'COLLECTION_PARTIAL';const after=fs.statfsSync(path.dirname(out));actual.availableAfter={bytes:after.bavail*after.bsize,inodes:after.ffree};const inventory=[];const walk=d=>{for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())walk(p);else if(e.isFile())inventory.push(fs.statSync(p).size)}};walk(out);actual.generatedBeforeFinalSummary={files:inventory.length,bytes:inventory.reduce((a,b)=>a+b,0)};save();if(actual.result!=='COLLECTION_COMPLETE')process.exitCode=1;
}
module.exports={V3_FIXTURE_SHA,B_SHA,HEADS,PLANS,DOC,fixture,classify,tiny,evidenceState,checkFixture,EXPECTED_WEBKIT,verifyBuild,compareBuild,saveBuildPreflight};
if(require.main===module){if(process.argv[2]==='--worker')worker(process.argv[3],JSON.parse(process.argv[4]),process.argv[5]).catch(e=>{console.error(e);process.exitCode=1});else main(path.resolve(process.argv[2]||'evidence/isolation'),process.argv.includes('--check')).catch(e=>{console.error(e);process.exitCode=1});}
