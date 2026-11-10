const {chromium,webkit}=require('/workspace/scratch/e622c1e9421e/wasm-focus-repair/node_modules/playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../../../..'), data=JSON.parse(fs.readFileSync(root+'/prototype/eikyouki/eikyouki_records.json')), html=fs.readFileSync(root+'/prototype/eikyouki/index.html');
const result={cases:[],scope:'Independent focused source layers/filter/navigation; not full suite'};
const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html)});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));
try{for(const [name,engine] of [['chromium',chromium],['webkit',webkit]]){
const run={engine:name,checks:[],pageerrors:[]};result.cases.push(run);let browser;
try{browser=await engine.launch({headless:true,...(name==='webkit'?{executablePath:path.join(__dirname,'webkit.sh')}:{})});
const page=await browser.newPage({viewport:{width:390,height:844}});page.setDefaultTimeout(15000);page.on('pageerror',e=>run.pageerrors.push(e.message));
const check=(label,a,b)=>{assert.deepEqual(a,b,label);run.checks.push(label)};
await page.goto(`http://127.0.0.1:${server.address().port}`);check('initial article count',await page.locator('.article').count(),102);
await page.locator('#chapter').selectOption('yuki_fall');check('chapter filter count',await page.locator('.article').count(),20);
for(const id of ['EK-0086','EK-0093','EK-0098']){
 await page.locator('#search').fill(id);check(id+' unique filter',await page.locator('.article').count(),1);await page.locator('.article summary').click();
 const r=data.records.find(r=>r.id===id), pub=data.publication.articles[id];
 check(id+' raw source exact',await page.locator('.source-text').textContent(),r.full_original_text);
 check(id+' narrative exact',await page.locator('.narrative-text').textContent(),pub.narrative_text);
 if(id==='EK-0098'){check('editorial note excluded from narrative',(await page.locator('.narrative-text').textContent()).includes('大草紙'),false);check('editorial note visible',(await page.locator('.editorial-annotations').innerText()).includes('大草紙'),true)}
 await page.screenshot({path:path.join(__dirname,`${name}-${id}.png`)});
}
await page.locator('#chapter').selectOption('all');await page.locator('#search').fill('EK-0057');await page.locator('.article summary').click();await page.locator('.related-link').filter({hasText:'EK-0058'}).click();
check('related target search',await page.locator('#search').inputValue(),'EK-0058');check('related target open',await page.locator('#EK-0058').getAttribute('open'),'');
await page.locator('#search').fill('EK-0098');check('input works after related navigation',await page.locator('.article').count(),1);
await page.locator('#search').fill('');await page.locator('#chapter').selectOption('yuki_fall');await page.locator('#year').selectOption('1441');check('dated year and chapter filter',await page.locator('.article').count(),6);
check('pageerrors',run.pageerrors,[]);run.status='PASS';
}catch(e){run.status='FAIL';run.error=e.stack}finally{if(browser)await browser.close();fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify(result,null,2))}
}}finally{server.close()}})().catch(e=>{console.error(e);server.close();process.exitCode=1});
