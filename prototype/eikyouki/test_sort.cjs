const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(`${__dirname}/index.html`,'utf8');
const records=JSON.parse(html.match(/<script id="payload" type="application\/json">(.*?)<\/script>/s)[1]);
const code=html.match(/function compareSource[^\n]+/)[0]+'\n'+html.match(/function compareChronology[^\n]+/)[0];
const context=vm.createContext({});vm.runInContext(code,context);
const expected=records.slice(0,12).map(r=>r.id).concat('EK-0015','EK-0016','EK-0019','EK-0017','EK-0018','EK-0013','EK-0014','EK-0025','EK-0026','EK-0027','EK-0030','EK-0031','EK-0032','EK-0040','EK-0042','EK-0046','EK-0049','EK-0050','EK-0051','EK-0052','EK-0054','EK-0060','EK-0062','EK-0067','EK-0063','EK-0066','EK-0064','EK-0065','EK-0068','EK-0069','EK-0070','EK-0071','EK-0074','EK-0073','EK-0082','EK-0075','EK-0091','EK-0092','EK-0097','EK-0098','EK-0099','EK-0100','EK-0105','EK-0111','EK-0120','EK-0020','EK-0021','EK-0022','EK-0023','EK-0024','EK-0028','EK-0029','EK-0033','EK-0034','EK-0035','EK-0036','EK-0037','EK-0038','EK-0039','EK-0041','EK-0043','EK-0044','EK-0045','EK-0047','EK-0048','EK-0053','EK-0055','EK-0056','EK-0057','EK-0058','EK-0059','EK-0061','EK-0072','EK-0076','EK-0077','EK-0078','EK-0079','EK-0080','EK-0081','EK-0083','EK-0084','EK-0085','EK-0086','EK-0087','EK-0088','EK-0089','EK-0090','EK-0093','EK-0094','EK-0095','EK-0096','EK-0101','EK-0102','EK-0103','EK-0104','EK-0106','EK-0107','EK-0108','EK-0109','EK-0110','EK-0112','EK-0113','EK-0114','EK-0115','EK-0116','EK-0117','EK-0118','EK-0119','EK-0121','EK-0122','EK-0123','EK-0124','EK-0125','EK-0126','EK-0127','EK-0128','EK-0129');
for(const input of [records,[...records].reverse(),[...records.slice(8),...records.slice(0,8)]]) {
 assert.deepEqual([...input].sort(context.compareChronology).map(r=>r.id),expected);
 assert.deepEqual([...input].sort(context.compareSource).map(r=>r.id),records.map(r=>r.id));
}
const same=[{id:'b',source_order:2,gregorian_start:'1438-01-01'},{id:'a',source_order:1,gregorian_start:'1438-01-01'},{id:'z',source_order:0,gregorian_start:null}];
assert.deepEqual(same.sort(context.compareChronology).map(r=>r.id),['a','b','z']);
assert(context.compareChronology({id:'a',source_order:1,gregorian_start:null},{id:'b',source_order:1,gregorian_start:null})<0);
console.log('PASS: actual HTML comparator / 3 input orders / chronological and source order / same-day and unknown ties');
