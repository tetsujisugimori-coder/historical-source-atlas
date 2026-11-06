const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
process.env.PLAYWRIGHT_BROWSERS_PATH='C:/Users/tetsu/AppData/Local/ms-playwright';
const pw=require('C:/Users/tetsu/Documents/Codex/2026-11-01/task/calculator-memo/e2e/node_modules/playwright-core');
const source=path.resolve(process.argv[2],'prototype/eikyouki/index.html');
const out=path.resolve(process.argv[3]);fs.mkdirSync(out,{recursive:true});
const bytes=fs.readFileSync(source), results={source,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),playwright:require('C:/Users/tetsu/Documents/Codex/2026-11-01/task/calculator-memo/e2e/node_modules/playwright-core/package.json').version,cases:[]};
const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(bytes)});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));
 for(const engine of ['chromium','webkit']){
  let browser;try{browser=await pw[engine].launch({headless:true});results[engine]=browser.version();}catch(e){results.cases.push({engine,status:'NOT_TESTED',error:String(e)});continue;}
  for(const width of [390,1280]){
   const ctx=await browser.newContext({viewport:{width,height:1000},acceptDownloads:true});const page=await ctx.newPage();const errors=[];
   page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
   const r={engine,width,errors};results.cases.push(r);
   try{
    await page.goto(`http://127.0.0.1:${server.address().port}/`);await page.bringToFront();
    r.document=await page.evaluate(()=>({focus:document.hasFocus(),visibility:document.visibilityState}));
    r.chronological=await page.locator('.article .topline span:nth-child(2)').allTextContents();
    await page.screenshot({path:path.join(out,`${engine}-${width}-chronology.png`),fullPage:true});
    await page.locator('#sort').click();r.sourceOrder=await page.locator('.article .topline span:nth-child(2)').allTextContents();
    await page.locator('#search').fill('EK-0015');r.search=await page.locator('.article .topline span:nth-child(2)').allTextContents();
    await page.locator('.article summary').focus();await page.keyboard.press('Enter');r.detailOpen=await page.locator('.article').evaluate(n=>n.open);
    r.sourceLink=await page.locator('.article .details a').first().getAttribute('href');
    r.keyboardFocus=await page.evaluate(()=>({tag:document.activeElement.tagName,outline:getComputedStyle(document.activeElement).outlineStyle}));
    await page.keyboard.press('Tab');r.tabForward=await page.evaluate(()=>({tag:document.activeElement.tagName,href:document.activeElement.getAttribute('href'),focus:document.hasFocus()}));
    await page.keyboard.press('Shift+Tab');r.tabBack=await page.evaluate(()=>({tag:document.activeElement.tagName,focus:document.hasFocus()}));
    await page.screenshot({path:path.join(out,`${engine}-${width}-focus.png`),fullPage:true});
    const downloadPromise=page.waitForEvent('download');await page.locator('#export').click();const download=await downloadPromise;const target=path.join(out,`${engine}-${width}-download.json`);await download.saveAs(target);r.download=JSON.parse(fs.readFileSync(target,'utf8'));
    await page.locator('#search').fill('unmatched-independent-probe');r.emptyCount=await page.locator('.article').count();r.emptyVisible=await page.locator('.empty').isVisible();
    await page.locator('#search').fill('');await page.locator('#year').selectOption('1437');r.yearIds=await page.locator('.article .topline span:nth-child(2)').allTextContents();
    await page.locator('#year').selectOption('all');await page.locator('#chapter').selectOption('hakone');r.chapterIds=await page.locator('.article .topline span:nth-child(2)').allTextContents();
    await page.locator('.article summary').focus();await page.keyboard.press('Space');r.spaceOpen=await page.locator('.article').evaluate(n=>n.open);
    r.overflow=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,viewport:innerWidth}));
    await page.screenshot({path:path.join(out,`${engine}-${width}-filtered.png`),fullPage:true});r.status='EXECUTED';
   }catch(e){r.status='FAIL';r.error=String(e)}finally{await ctx.close()}
  }await browser.close();
 }
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results.cases.map(({download,...r})=>r),null,2));
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>server.close());
