'use strict';
const cp=require('node:child_process'),a=require('node:assert/strict');
const base='0338e39629880eab89602abd33e0f44d697f27df';
const git=(...args)=>cp.execFileSync('git',args,{encoding:'utf8'}).trim();
const names=git('diff','--name-only',base).split('\n').filter(Boolean);
for(const f of names)a(f.startsWith('diagnostics/webkit-isolation/')||f==='.github/workflows/webkit-isolation.yml','out-of-scope change: '+f);
for(const f of ['prototype/eikyouki/index.html','prototype/eikyouki/eikyouki_records.json','prototype/eikyouki/browser_acceptance.cjs','.github/workflows/acceptance.yml','.github/workflows/pages.yml']){
 try{const b=git('rev-parse',base+':'+f);a.equal(git('hash-object',f),b,'protected bytes: '+f)}catch(e){if(f.endsWith('/pages.yml')&&String(e.stderr).includes('does not exist'))continue;throw e;}
}
console.log('Protected product/data/formal contract unchanged; diagnostic scope only');
