/* Diagnostic counterfactuals only. The unchanged full acceptance follows this probe. */
const {webkit}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),cp=require('node:child_process');
const out=path.resolve(process.argv[2]||'evidence/reload-diagnostics');fs.mkdirSync(out,{recursive:true});
const original=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const variants={
 current:original,
 no_initial_render:original.replace('});render();\n// Restore fragment','});\n// Restore fragment').replace("if(document.readyState==='complete')applyFragment();else window.addEventListener('load',applyFragment,{once:true});","function initialView(){if(location.hash)applyFragment();else render()}if(document.readyState==='complete')initialView();else window.addEventListener('load',initialView,{once:true});"),
 no_programmatic_focus:original.replace("target.focus({preventScroll:true})","void 0"),
 no_prevent_scroll:original.replace("target.focus({preventScroll:true})","target.focus()"),
 no_scroll:original.replace("target.scrollIntoView({behavior:'instant',block:'start'});",''),
 frame_after_load:original.replace("window.addEventListener('load',applyFragment,{once:true})","window.addEventListener('load',()=>requestAnimationFrame(applyFragment),{once:true})"),
 no_instrumentation:original,
 blur_before_reload:original,
};
const result={classification:'diagnostic counterfactuals, not acceptance PASS',head:cp.execFileSync('git',['rev-parse','HEAD'],{cwd:__dirname,encoding:'utf8'}).trim(),started:new Date().toISOString(),platform:process.platform,cases:[]};
const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(variants[req.url.split('/')[1].split('?')[0]]||original)});
async function main(){await new Promise(r=>server.listen(0,'127.0.0.1',r));const browser=await webkit.launch({headless:true});
 try{for(const [name,html] of Object.entries(variants)){
  const c={variant:name,modified:html!==original,events:[],stages:[],crashed:false};result.cases.push(c);const context=await browser.newContext({viewport:{width:375,height:1000}});const p=await context.newPage();
  p.on('crash',()=>c.crashed=true);p.on('pageerror',e=>c.events.push({pageerror:e.message}));
  try{
   if(name!=='no_instrumentation'){await p.exposeFunction('recordInput',e=>c.events.push(e));await p.addInitScript(()=>{for(const type of ['keydown','keyup','click','input','change','focusin'])document.addEventListener(type,e=>window.recordInput({type,key:e.key||null,target:e.target.id||e.target.tagName,time:performance.now()}),true)});}
   const stage=s=>c.stages.push({stage:s,time:new Date().toISOString()});const url=`http://127.0.0.1:${server.address().port}/${name}`;
   stage('initial');await p.goto(url);await p.locator('#search').fill('其由来を伝聞くに');await p.goto(url+'#EK-0131');await p.locator('.narrative-reference').filter({hasText:'EK-0130'}).click();stage('article-reload');await p.reload();
   await p.locator('#search').fill('');await p.locator('#year').selectOption('1461');await p.locator('#year').selectOption('all');await p.locator('#chapter').selectOption('horikoshi');await p.locator('#chapter').selectOption('all');
   for(let n=1;n<=5;n++){const id=`EK-0120-C0${n}`;await p.locator('#search').fill(id);await p.locator('.article summary').click();await p.locator('#'+id+' a').click();stage(id);}
   c.beforeReload=await p.evaluate(()=>({hash:location.hash,active:document.activeElement.id,ready:document.readyState}));await p.screenshot({path:path.join(out,name+'-before.png')});
   if(name==='blur_before_reload')await p.evaluate(()=>document.activeElement.blur());stage('clause-reload');await p.reload();c.afterReload=await p.evaluate(()=>({hash:location.hash,active:document.activeElement.id,ready:document.readyState,open:document.querySelector('#EK-0120')?.open}));stage('finished');c.outcome='COMPLETED';
  }catch(e){c.outcome='ERROR';c.error=e.stack;}finally{await context.close();fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));}
 }}finally{await browser.close();server.close();result.finished=new Date().toISOString();fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));}
 console.log(JSON.stringify(result.cases.map(c=>({variant:c.variant,outcome:c.outcome,crashed:c.crashed,last:c.stages.at(-1),error:c.error})),null,2));
}
main().catch(e=>{result.fatal=e.stack;fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));server.close();process.exitCode=1});
