const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(`${__dirname}/index.html`,'utf8');
const records=JSON.parse(html.match(/<script id="payload" type="application\/json">(.*?)<\/script>/s)[1]);
const code=html.match(/function compareSource[^\n]+/)[0]+'\n'+html.match(/function compareChronology[^\n]+/)[0];
const context=vm.createContext({});vm.runInContext(code,context);
const expected=records.slice(0,12).map(r=>r.id).concat('EK-0015','EK-0016','EK-0019','EK-0017','EK-0018','EK-0013','EK-0014','EK-0025','EK-0026','EK-0020','EK-0021','EK-0022','EK-0023','EK-0024');
for(const input of [records,[...records].reverse(),[...records.slice(8),...records.slice(0,8)]]) {
 assert.deepEqual([...input].sort(context.compareChronology).map(r=>r.id),expected);
 assert.deepEqual([...input].sort(context.compareSource).map(r=>r.id),records.map(r=>r.id));
}
const same=[{id:'b',source_order:2,gregorian_start:'1438-01-01'},{id:'a',source_order:1,gregorian_start:'1438-01-01'},{id:'z',source_order:0,gregorian_start:null}];
assert.deepEqual(same.sort(context.compareChronology).map(r=>r.id),['a','b','z']);
assert(context.compareChronology({id:'a',source_order:1,gregorian_start:null},{id:'b',source_order:1,gregorian_start:null})<0);
console.log('PASS: actual HTML comparator / 3 input orders / chronological and source order / same-day and unknown ties');
