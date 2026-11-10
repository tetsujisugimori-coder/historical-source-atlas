/* Real engines against local HTTP; no external hosting or source-site navigation. */
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto'),cp=require('node:child_process'),assert=require('node:assert/strict');
const out=path.resolve(process.argv[2]||'evidence/browser');fs.mkdirSync(out,{recursive:true});
const html=fs.readFileSync(path.join(__dirname,'index.html'));
const records=JSON.parse(fs.readFileSync(path.join(__dirname,'eikyouki_records.json'),'utf8')).records;
const expected=records.slice(0,12).map(r=>r.id).concat('EK-0015','EK-0016','EK-0019','EK-0017','EK-0018','EK-0013','EK-0014','EK-0025','EK-0026','EK-0027','EK-0030','EK-0031','EK-0032','EK-0040','EK-0042','EK-0046','EK-0049','EK-0050','EK-0051','EK-0052','EK-0054','EK-0060','EK-0062','EK-0067','EK-0063','EK-0066','EK-0064','EK-0065','EK-0068','EK-0069','EK-0070','EK-0071','EK-0074','EK-0073','EK-0082','EK-0075','EK-0091','EK-0092','EK-0097','EK-0098','EK-0099','EK-0100','EK-0020','EK-0021','EK-0022','EK-0023','EK-0024','EK-0028','EK-0029','EK-0033','EK-0034','EK-0035','EK-0036','EK-0037','EK-0038','EK-0039','EK-0041','EK-0043','EK-0044','EK-0045','EK-0047','EK-0048','EK-0053','EK-0055','EK-0056','EK-0057','EK-0058','EK-0059','EK-0061','EK-0072','EK-0076','EK-0077','EK-0078','EK-0079','EK-0080','EK-0081','EK-0083','EK-0084','EK-0085','EK-0086','EK-0087','EK-0088','EK-0089','EK-0090','EK-0093','EK-0094','EK-0095','EK-0096','EK-0101','EK-0102');
const ids=p=>p.locator('.article .topline').evaluateAll(xs=>xs.map(x=>x.textContent.match(/EK-\d{4}/)[0]));
const result={classification:'new execution',started:new Date().toISOString(),head:cp.execFileSync('git',['rev-parse','HEAD'],{cwd:__dirname,encoding:'utf8'}).trim(),tree:cp.execFileSync('git',['rev-parse','HEAD^{tree}'],{cwd:__dirname,encoding:'utf8'}).trim(),inputMethod:'Playwright delivered keyboard/click/selectOption and fill; no physical device claim',dirty:cp.execFileSync('git',['status','--porcelain'],{cwd:__dirname,encoding:'utf8'}).trim(),sourceSha256:crypto.createHash('sha256').update(html).digest('hex'),node:process.version,os:process.platform,cases:[]};
const server=http.createServer((req,res)=>{if(req.url==='/favicon.ico'){res.writeHead(204);return res.end()}res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(html)});
async function main(){
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const url=`http://127.0.0.1:${server.address().port}`;
 try{for(const [name,engine] of Object.entries({chromium,webkit})){
  const browser=await engine.launch({headless:true});
  try{for(const width of [375,390,765,1280]){for(const motion of ['no-preference','reduce']){
   const c={browser:name,width,motion,height:1000,version:browser.version(),checks:[],inputEvents:[],consoleErrors:[],pageerrors:[]};result.cases.push(c);
   const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:motion,acceptDownloads:true});const p=await context.newPage();
   p.on('pageerror',e=>c.pageerrors.push({time:new Date().toISOString(),message:e.message}));p.on('console',m=>{if(m.type()==='error')c.consoleErrors.push(m.text())});
   const check=(name,actual,expectedValue)=>{assert.deepEqual(actual,expectedValue,name);c.checks.push({name,actual,expected:expectedValue})};
   try{
    await p.exposeFunction('recordInput',e=>c.inputEvents.push(e));await p.addInitScript(()=>{for(const type of ['keydown','keyup','click','input','change','focusin'])document.addEventListener(type,e=>window.recordInput({type,key:e.key||null,trusted:e.isTrusted,target:e.target.id||e.target.tagName,time:performance.now()}),true)});
    await p.goto(url);check('102 articles',await p.locator('.article').count(),102);check('total KPI',await p.locator('#total').innerText(),'102');check('chapter KPI',await p.locator('.stat b').nth(1).innerText(),'11');check('target year KPI',await p.locator('.stat b').nth(2).innerText(),'1436–1441');check('intro count', (await p.locator('.intro').innerText()).includes('この102件'),true);
    check('chronological order actual display',await ids(p),expected);
    await p.screenshot({path:path.join(out,`${name}-${width}-${motion}-date.png`),fullPage:false});
    await p.locator('#chapter').selectOption('kamakura_return');check('new chapter chronological display',await ids(p),['EK-0019','EK-0018','EK-0025','EK-0026','EK-0027','EK-0020','EK-0021','EK-0022','EK-0023','EK-0024','EK-0028','EK-0029']);
    await p.locator('#chapter').selectOption('all');
    await p.locator('#chapter').selectOption('mochiuji_tonsure');check('batch06 chapter chronological display',await ids(p),['EK-0030','EK-0031','EK-0032','EK-0040','EK-0033','EK-0034','EK-0035','EK-0036','EK-0037','EK-0038','EK-0039']);await p.locator('#chapter').selectOption('all');
    await p.locator('#chapter').selectOption('mochiuji_death');check('batch07 chapter chronology',await ids(p),['EK-0042','EK-0046','EK-0041','EK-0043','EK-0044','EK-0045']);await p.locator('#chapter').selectOption('all');
    await p.locator('#chapter').selectOption('norizane_tonsure');check('batch08 chapter chronology',await ids(p),['EK-0049','EK-0050','EK-0051','EK-0047','EK-0048']);await p.locator('#chapter').selectOption('all');
    await p.locator('#chapter').selectOption('yuki_siege');check('batch09 chronology',await ids(p),['EK-0052','EK-0054','EK-0060','EK-0062','EK-0067','EK-0063','EK-0066','EK-0064','EK-0065','EK-0068','EK-0053','EK-0055','EK-0056','EK-0057','EK-0058','EK-0059','EK-0061']);await p.locator('#chapter').selectOption('all');
    await p.locator('#chapter').selectOption('muraoka_battle');check('muraoka chronology',await ids(p),['EK-0069','EK-0070','EK-0071','EK-0074','EK-0073','EK-0082','EK-0075','EK-0072','EK-0076','EK-0077','EK-0078','EK-0079','EK-0080','EK-0081']);await p.locator('#chapter').selectOption('all');
    await p.locator('#chapter').selectOption('yuki_fall');check('batch10 chronology',await ids(p),['EK-0091','EK-0092','EK-0097','EK-0098','EK-0099','EK-0100','EK-0083','EK-0084','EK-0085','EK-0086','EK-0087','EK-0088','EK-0089','EK-0090','EK-0093','EK-0094','EK-0095','EK-0096','EK-0101','EK-0102']);await p.locator('#chapter').selectOption('all');
    await p.locator('#year').selectOption('1441');check('batch10 year filter',await ids(p),['EK-0091','EK-0092','EK-0097','EK-0098','EK-0099','EK-0100']);await p.locator('#year').selectOption('all');
    await p.locator('#year').selectOption('1439');check('batch07 year filter',await ids(p),['EK-0042','EK-0046','EK-0049','EK-0050','EK-0051']);await p.locator('#year').selectOption('all');
    const allDownloadEvent=p.waitForEvent('download');await p.locator('#export').click();const allDownload=await allDownloadEvent;const allFile=path.join(out,`${name}-${width}-${motion}-all-download.json`);await allDownload.saveAs(allFile);check('all 102 full records exported',JSON.parse(fs.readFileSync(allFile,'utf8')).records,expected.map(id=>records.find(r=>r.id===id)));
    await p.locator('#sort').click();check('source order',await ids(p),records.map(r=>r.id));check('source aria',await p.locator('#sort').getAttribute('aria-pressed'),'false');
    await p.locator('#sort').click();check('date order toggle',await ids(p),expected);
    await p.locator('#year').selectOption('null');check('unknown-date filter',await ids(p),['EK-0020','EK-0021','EK-0022','EK-0023','EK-0024','EK-0028','EK-0029','EK-0033','EK-0034','EK-0035','EK-0036','EK-0037','EK-0038','EK-0039','EK-0041','EK-0043','EK-0044','EK-0045','EK-0047','EK-0048','EK-0053','EK-0055','EK-0056','EK-0057','EK-0058','EK-0059','EK-0061','EK-0072','EK-0076','EK-0077','EK-0078','EK-0079','EK-0080','EK-0081','EK-0083','EK-0084','EK-0085','EK-0086','EK-0087','EK-0088','EK-0089','EK-0090','EK-0093','EK-0094','EK-0095','EK-0096','EK-0101','EK-0102']);
    check('unknown date captions',await p.locator('.date').allTextContents(),Array(48).fill('日付不明'));
    check('unknown converted captions',await p.locator('.cal-modern').allTextContents(),Array(48).fill('未換算'));
    await p.screenshot({path:path.join(out,`${name}-${width}-${motion}-unknown.png`),fullPage:false});
    await p.locator('#year').selectOption('all');
    for(const id of ['EK-0027','EK-0028','EK-0029',...Array.from({length:73},(_,i)=>`EK-${String(i+30).padStart(4,'0')}`)]){
     await p.locator('#search').fill(id);check(id+' unique search',await ids(p),[id]);
     await p.locator('.article summary').click();
     const r=records.find(r=>r.id===id),text=await p.locator('.article').innerText();
     check(id+' original date visible',text.includes(r.original_date),true);
     check(id+' provisional source status visible',text.includes('底本未照合'),true);
     check(id+' fixed source',await p.locator('.details a').first().getAttribute('href'),r.source_url);
     check(id+' explicit calendar distinction',await p.locator('.cal-modern').innerText(),r.gregorian_start?r.gregorian_start.replace(/^(\d{4})-(\d{2})-(\d{2})$/,'$1年$2月$3日'):'未換算');
     check(id+' interpretation visible',text.includes(r.date_interpretation),true);
     if(r.source_order>=52){check(id+' exact original visible',(await p.locator('.source-text').innerText()),r.full_original_text);check(id+' historical unassessed',text.includes('史実認定：未認定'),true);check(id+' geography unplaced',text.includes('現代所在地：未比定'),true);}
     if(r.source_order>=83){const provenance=JSON.parse(fs.readFileSync(path.join(__dirname,'eikyouki_records.json'),'utf8')).publication.articles[id];check(id+' separated narrative',await p.locator('.narrative-text').innerText(),provenance.narrative_text);check(id+' annotations separate',await p.locator('.editorial-annotations').count(),1);check(id+' source reuse',text.includes('再取得は403'),true);}
     await p.screenshot({path:path.join(out,`${name}-${width}-${motion}-${id}.png`),fullPage:false});
    }
    await p.locator('#search').fill('EK-0057');await p.locator('.article summary').click();await p.locator('.related-link').filter({hasText:'EK-0058'}).click();check('related separate Koga article',await ids(p),['EK-0058']);check('related detail opens',await p.locator('.article').getAttribute('open'),'');
    await p.locator('#search').fill('');
    await p.locator('#year').selectOption('1437');check('year filter',await ids(p),records.filter(r=>r.western_year===1437).map(r=>r.id));
    await p.locator('#year').selectOption('all');await p.locator('#chapter').selectOption('hakone');check('chapter filter',await ids(p),['EK-0015','EK-0016','EK-0017']);
    await p.locator('#chapter').selectOption('all');await p.locator('#search').fill('EK-0015');check('search',await ids(p),['EK-0015']);
    const summary=p.locator('.article summary');await summary.focus();await p.keyboard.press('Enter');check('keyboard detail open',await p.locator('.article').getAttribute('open'),'');
    check('focus after Enter',await p.evaluate(()=>document.activeElement.tagName),'SUMMARY');
    c.focus=await summary.evaluate(e=>({outline:getComputedStyle(e).outline,rect:e.getBoundingClientRect().toJSON(),focusVisible:e.matches(':focus-visible')}));
    check('keyboard focus indicator',c.focus.focusVisible&& !c.focus.outline.startsWith('0px') && !c.focus.outline.includes('none'),true);
    check('provisional notice',(await p.locator('.article').innerText()).includes('仮登録'),true);
    check('source href',await p.locator('.details a').first().getAttribute('href'),records[14].source_url);
    check('source safety rel',await p.locator('.details a').first().getAttribute('rel'),'noopener noreferrer');
    await p.keyboard.press('Tab');check('Tab to source link',await p.evaluate(()=>document.activeElement.tagName),'A');
    await p.keyboard.press('Shift+Tab');check('Shift Tab to opener',await p.evaluate(()=>document.activeElement.tagName),'SUMMARY');
    await p.screenshot({path:path.join(out,`${name}-${width}-${motion}-detail-focus.png`),fullPage:false});
    const downloadEvent=p.waitForEvent('download');await p.locator('#export').click();const download=await downloadEvent;const file=path.join(out,`${name}-${width}-${motion}-download.json`);await download.saveAs(file);
    const exported=JSON.parse(fs.readFileSync(file,'utf8'));check('download full record',exported.records,[records[14]]);
    await p.locator('#search').fill('NO_MATCH_987654321');check('no result count',await p.locator('#count').innerText(),'0');check('empty visible',await p.locator('.empty').isVisible(),true);
    await p.locator('#search').fill('');await p.locator('.article summary').first().focus();await p.keyboard.press('Space');check('Space detail toggle',await p.locator('.article').first().getAttribute('open'),'');
    c.geometry=await p.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('.article,.toolbar,button,input,select')].filter(e=>{const r=e.getBoundingClientRect();return r.left<0||r.right>innerWidth+1}).map(e=>e.tagName)}));
    check('no horizontal overflow',c.geometry.scrollWidth<=width&&c.geometry.overflow.length===0,true);
    check('pageerror',c.pageerrors,[]);check('console errors',c.consoleErrors,[]);c.status='PASS';
   }catch(e){c.status='FAIL';c.error=e.stack;await p.screenshot({path:path.join(out,`${name}-${width}-${motion}-failure.png`),fullPage:false}).catch(()=>{});}
   finally{await context.close()}
  }}}finally{await browser.close()}
 }}finally{server.close();result.finished=new Date().toISOString();result.status=result.cases.length===16&&result.cases.every(c=>c.status==='PASS')?'PASS':'FAIL';fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));}
 assert.equal(result.status,'PASS');console.log(`PASS: 16 real-engine conditions; ${result.cases.reduce((n,c)=>n+c.checks.length,0)} operation checks`);
}
main().catch(e=>{result.status='FAIL';result.fatal=e.stack;fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));console.error(e);process.exitCode=1;server.close()});
