/* Separate diagnostic experiment. Never a replacement for formal acceptance. */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),Module=require('node:module');
const root=path.resolve(__dirname,'../..');
const out=path.resolve(process.argv[2]||'evidence/reload-diagnostics');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const git=(...args)=>cp.execFileSync('git',args,{cwd:root,encoding:'utf8'}).trim();
const formal=fs.readFileSync(path.join(__dirname,'browser_acceptance.cjs'),'utf8');
const original=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const formalHash='9882aeace2a822d838dafc5a0172c2f090d727d08f32cbdbdabbe979c00a77e4';
if(sha(formal)!==formalHash)throw Error('Formal acceptance changed; stop diagnosis and review plan');
const plan=[
 {id:'01-minimal',route:'minimal',png:false,engine:'webkit',contexts:1},
 {id:'02-minimal-repeat',route:'minimal',png:false,engine:'webkit',contexts:1},
 {id:'03-minimal-screenshot',route:'minimal',png:true,engine:'webkit',contexts:1},
 {id:'04a-minimal-route-control',route:'minimal',png:false,engine:'webkit',contexts:1,routeControl:true},
 {id:'04-minimal-no-initial-fragment',route:'minimal',png:false,engine:'webkit',contexts:1,noInitial:true},
 {id:'05-full-no-screenshots',route:'full',png:false,engine:'webkit',contexts:1},
 {id:'06-full-original-screenshots',route:'full',png:true,engine:'webkit',contexts:1},
 {id:'07-full-reused-browser',route:'full',png:true,engine:'webkit',contexts:2},
 {id:'08-full-chromium-control',route:'full',png:true,engine:'chromium',contexts:1},
];
function replaceOnce(s,a,b){if(s.split(a).length!==2)throw Error('Diagnostic extraction anchor changed: '+a);return s.replace(a,b)}
function derived(spec){
 let code=replaceOnce(formal,'Object.entries({chromium,webkit})',`Object.entries({${spec.engine}})`);
 code=replaceOnce(code,'const width of [375,390,765,1280]',`const width of [${Array(spec.contexts).fill(375).join(',')}]`);
 code=replaceOnce(code,"const motion of ['no-preference','reduce']","const motion of ['no-preference']");
 code=replaceOnce(code,'result.cases.length===16',`result.cases.length===${spec.contexts}`);
 code=replaceOnce(code,'PASS: 16 real-engine conditions','DIAGNOSTIC ONLY: restricted conditions');
 code=replaceOnce(code,"classification:'new execution'","classification:'diagnostic restricted matrix / counterfactual; NOT formal acceptance'");
 code=replaceOnce(code,'result.cases.push(c);','c.diagnosticSequence=result.cases.length;result.cases.push(c);');
 code=code.replaceAll('${name}-${width}-${motion}','${name}-${width}-${motion}-${c.diagnosticSequence}');
 if(spec.route==='minimal'){
  const start=code.indexOf("    await p.goto(url);check('131 articles'");
  const end=code.indexOf("    await p.locator('#search').fill('');await p.locator('#year').selectOption('1467')");
  if(start<0||end<=start)throw Error('Minimal route extraction changed');
  code=code.slice(0,start)+'    await p.goto(url);\n'+code.slice(end);
  const tail=code.indexOf('    await p.goBack();');const stop=code.indexOf("c.status='PASS';",tail);
  if(tail<0||stop<0)throw Error('Minimal route endpoint changed');
  code=code.slice(0,tail)+"    c.status='PASS';"+code.slice(stop+"c.status='PASS';".length);
 }
 return code;
}
function optionalRead(p){try{return fs.readFileSync(p,'utf8')}catch(e){return {status:'NOT_OBTAINED',reason:e.code}}}
function resources(){
 const r={time:new Date().toISOString(),node:process.memoryUsage(),freeMemory:os.freemem(),totalMemory:os.totalmem()};
 try{const s=fs.statfsSync(out);r.disk={availableBytes:s.bavail*s.bsize,freeBytes:s.bfree*s.bsize}}catch(e){r.disk={status:'NOT_OBTAINED',reason:e.code}}
 if(process.platform==='linux'){
  r.cgroupMemoryEvents=optionalRead('/sys/fs/cgroup/memory.events');
  try{const lines=cp.execFileSync('ps',['-eo','pid=,ppid=,rss=,vsz=,comm='],{encoding:'utf8'}).trim().split('\n').map(l=>{const [pid,ppid,rss,vsz,...comm]=l.trim().split(/\s+/);return {pid:+pid,ppid:+ppid,rssKiB:+rss,vszKiB:+vsz,comm:comm.join(' ')}});const keep=new Set([process.pid]);let changed=true;while(changed){changed=false;for(const p of lines)if(keep.has(p.ppid)&&!keep.has(p.pid)){keep.add(p.pid);changed=true}}r.descendantProcesses=lines.filter(p=>keep.has(p.pid));}catch(e){r.descendantProcesses={status:'NOT_OBTAINED',reason:e.message}}
 }else r.descendantProcesses={status:'NOT_OBTAINED',reason:'Linux /proc process collection only'};
 return r;
}
fs.mkdirSync(out,{recursive:true});
if(process.argv[3]==='--worker'){
 const spec=plan.find(p=>p.id===process.argv[4]);if(!spec)throw Error('Unknown fixed diagnostic case');
 const pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');
 const eventsFile=path.join(out,'events.jsonl');const emit=x=>fs.appendFileSync(eventsFile,JSON.stringify({time:new Date().toISOString(),...x})+'\n');
 const pkgPath=require.resolve((process.env.PLAYWRIGHT_MODULE||'playwright')+'/package.json');
 const observations={spec,head:git('rev-parse','HEAD'),tree:git('rev-parse','HEAD^{tree}'),run:process.env.GITHUB_RUN_ID||'LOCAL',attempt:process.env.GITHUB_RUN_ATTEMPT||'LOCAL',platform:os.platform(),release:os.release(),arch:os.arch(),cpu:os.cpus()[0]?.model,cpuCount:os.cpus().length,node:process.version,playwright:JSON.parse(fs.readFileSync(pkgPath)).version,webkitVersion:'NOT_OBTAINED',browserVersion:'NOT_OBTAINED',nativeStack:'NOT_OBTAINED',rendererExit:'NOT_OBTAINED; inspect browser-stderr.log for available process signals',browserExit:'NOT_OBTAINED; lifecycle events and DEBUG stderr recorded',osRelease:process.platform==='linux'?optionalRead('/etc/os-release'):'NOT_APPLICABLE',temp:os.tmpdir(),initialResources:resources(),formalSourceSha256:sha(formal),productHtmlSha256:sha(original)};
 const save=()=>fs.writeFileSync(path.join(out,'environment.json'),JSON.stringify(observations,null,2));save();
 const timer=setInterval(()=>emit({kind:'resources',value:resources()}),5000);timer.unref();
 const wrapped={};let contextIndex=0;
 for(const name of ['chromium','webkit'])wrapped[name]={launch:async options=>{
  emit({kind:'browser-launch-request',engine:name,executable:pw[name].executablePath()});
  const browser=await pw[name].launch(options);observations.browserVersion=browser.version();if(name==='webkit')observations.webkitVersion=browser.version();save();emit({kind:'browser-launched',engine:name,version:browser.version()});
  browser.on('disconnected',()=>emit({kind:'browser-disconnected',resources:resources()}));
  const newContext=browser.newContext.bind(browser);browser.newContext=async options=>{
   const context=await newContext(options),index=++contextIndex;emit({kind:'context-open',index,resources:resources()});
   const newPage=context.newPage.bind(context);context.newPage=async()=>{
    const p=await newPage();let reload=0,shots=0;
    p.on('crash',()=>emit({kind:'page-crash',index,reload,resources:resources()}));p.on('close',()=>emit({kind:'page-close',index}));
    p.on('console',m=>emit({kind:'console',index,type:m.type(),text:m.text()}));p.on('pageerror',e=>emit({kind:'pageerror',index,message:e.message,stack:e.stack}));
    const state=async()=>{try{return await p.evaluate(()=>({fragment:location.hash,focus:document.activeElement?.id,scrollX,scrollY,ready:document.readyState,details:[...document.querySelectorAll('details[open]')].map(x=>x.id)}))}catch(e){return {status:'NOT_OBTAINED',reason:e.message}}};
    const load=p.reload.bind(p);p.reload=async(...args)=>{reload++;emit({kind:'before-reload',index,reload,state:await state(),resources:resources()});if(spec.route==='minimal'&&spec.png&&reload===2)await p.screenshot({path:path.join(out,'minimal-before-reload.png')});try{const r=await load(...args);emit({kind:'after-reload',index,reload,state:await state(),resources:resources()});return r}catch(e){emit({kind:'reload-error',index,reload,error:e.stack,resources:resources()});throw e}};
    const screenshot=p.screenshot.bind(p);p.screenshot=async options=>{shots++;emit({kind:'screenshot',index,shots,suppressed:!spec.png});if(!spec.png)return Buffer.alloc(0);const adjusted={...options,path:options.path?path.join(out,`context-${index}-`+path.basename(options.path)):undefined};return screenshot(adjusted)};
    // Existing recordInput calls are observed without installing additional DOM listeners.
    const expose=p.exposeFunction.bind(p);p.exposeFunction=(name,fn)=>expose(name,(...args)=>{if(name==='recordInput')emit({kind:'input',index,event:args[0]});return fn(...args)});
    if(spec.noInitial||spec.routeControl){const needle="if(document.readyState==='complete')applyFragment();else window.addEventListener('load',applyFragment,{once:true});";const html=spec.noInitial?replaceOnce(original,needle,'/* diagnostic only: initial fragment restoration omitted */'):original;observations.variantHtmlSha256=sha(html);observations.counterfactual=spec.noInitial?'Only the clause reload omits initial restoration; open/focus assertion failure differs from crash':'Matched route control: original HTML fulfilled at clause reload; routing disables HTTP cache';save();await p.route('http://127.0.0.1:**/*',async route=>{if(reload===2&&route.request().resourceType()==='document'){emit({kind:'variant-response-attempt',index,reload,htmlSha256:sha(html)});try{await route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:html});emit({kind:'variant-response-fulfilled',index,reload,htmlSha256:sha(html)})}catch(e){emit({kind:'variant-response-error',index,reload,error:e.stack});throw e}return}return route.continue()});}
    return p;
   };context.on('close',()=>emit({kind:'context-close',index,resources:resources()}));return context;
  };return browser;
 }};
 const code=derived(spec);fs.writeFileSync(path.join(out,'diagnostic-derived.cjs'),code);observations.derivedSha256=sha(code);observations.variantHtmlSha256??=sha(original);save();
 const m=new Module(path.join(__dirname,'diagnostic-derived.cjs'),module);m.filename=path.join(__dirname,'diagnostic-derived.cjs');m.paths=module.paths;const requireOriginal=m.require.bind(m);m.require=id=>id===(process.env.PLAYWRIGHT_MODULE||'playwright')?wrapped:requireOriginal(id);
 process.on('exit',code=>{clearInterval(timer);observations.finalResources=resources();observations.workerExitCode=code;save();emit({kind:'worker-exit',code})});m._compile(code,m.filename);
}else{
 const checkOnly=process.argv[3]==='--check';
 const summary={classification:'diagnostic only; never formal acceptance',started:new Date().toISOString(),head:git('rev-parse','HEAD'),tree:git('rev-parse','HEAD^{tree}'),run:process.env.GITHUB_RUN_ID||'LOCAL',attempt:process.env.GITHUB_RUN_ATTEMPT||'LOCAL',formalSourceSha256:sha(formal),plan,policy:'one execution per case in listed order; only case02 repeats case01; no adaptive retries; fresh process/browser except two contexts in case07; stop entire experiment on insufficient disk/write permission; 240s child watchdog bounds diagnosis only; normal Playwright timeouts unchanged',interventions:'DEBUG logging, event listeners, synchronous JSONL/resource sampling and pre/post reload state evaluation may change timing. Minimal screenshot only case03. Full variants execute exact formal prefix and suffix with restricted matrix; screenshot suppression only case05. No successful diagnostic implies crash fixed.',cases:[]};
 const temp=process.env.TEMP||process.env.TMP||os.tmpdir();fs.mkdirSync(temp,{recursive:true});const probe=fs.mkdtempSync(path.join(temp,'atlas13-diagnostic-'));fs.writeFileSync(path.join(probe,'write-probe.txt'),'atlas13');summary.tempProbe=probe;
 summary.preflight=resources();if(!Number.isFinite(summary.preflight.disk.availableBytes)||summary.preflight.disk.availableBytes<2*1024**3)throw Error('Disk capacity unknown or less than 2 GiB; stop before diagnosis');
 for(const spec of plan){const code=derived(spec);new Function('require','module','__filename','__dirname',code);}
 fs.writeFileSync(path.join(out,'plan.json'),JSON.stringify(summary,null,2));
 if(checkOnly){console.log('PASS: fixed diagnostic plan/extraction/syntax/preflight; no browser executed');process.exit(0)}
 (async()=>{for(const spec of plan){
  const dir=path.join(out,spec.id);fs.mkdirSync(dir,{recursive:true});const stdout=fs.openSync(path.join(dir,'stdout.log'),'wx'),stderr=fs.openSync(path.join(dir,'browser-stderr.log'),'wx');
  const entry={id:spec.id,started:new Date().toISOString()};summary.cases.push(entry);
  await new Promise(resolve=>{const child=cp.spawn(process.execPath,[__filename,dir,'--worker',spec.id],{cwd:root,env:{...process.env,DEBUG:'pw:browser'},stdio:['ignore',stdout,stderr]});let timed=false;const watchdog=setTimeout(()=>{timed=true;child.kill();},240000);child.on('error',e=>{entry.spawnError=e.message});child.on('close',(code,signal)=>{clearTimeout(watchdog);Object.assign(entry,{code,signal,timedOut:timed,finished:new Date().toISOString()});fs.closeSync(stdout);fs.closeSync(stderr);resolve()})});
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(summary,null,2));console.log(JSON.stringify(entry));
  if(entry.timedOut){summary.stopReason='Diagnostic watchdog; subsequent cases NOT_RUN to avoid orphan resource contamination';break;}
 }summary.finished=new Date().toISOString();summary.collectionStatus=summary.cases.length===plan.length?'COMPLETED':'PARTIAL';fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(summary,null,2));})().catch(e=>{summary.fatal=e.stack;fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(summary,null,2));console.error(e);process.exitCode=1});
}
