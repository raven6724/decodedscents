const fs=require('fs');let src=fs.readFileSync('worker_live.js','utf8');
function grab(n){const s=src.indexOf('const '+n+' = {');const b=src.indexOf('{',s);let d=0,e=-1;
for(let i=b;i<src.length;i++){if(src[i]==='{')d++;else if(src[i]==='}'){d--;if(d===0){e=i;break;}}}
return eval('('+src.slice(b,e+1)+')');}
const DB=grab('VERIFIED_DB'),AL=grab('ALIASES'),D2O=grab('DUPE_TO_ORIGINAL');
const norm=s=>s.toLowerCase().replace(/\b(edp|edt|extrait|parfum|cologne|eau de parfum|eau de toilette)\b/g,'').replace(/[^a-z0-9]+/g,' ').trim();
const out=[];
for (const [tbl,name] of [[AL,'ALIASES'],[D2O,'DUPE_TO_ORIGINAL']]) {
  for (const [k,v] of Object.entries(tbl)) {
    if (!DB[v]) { out.push([name,k,v,'TARGET MISSING']); continue; }
    const nk=norm(k);
    // if the key names a dupe, that dupe must still live under the target
    const holds=(DB[v].dupes||[]).some(d=>{const n=norm(d.brand+' '+d.name);return n.includes(nk)||nk.includes(norm(d.name));});
    const isOrig=norm(DB[v].original.brand+' '+DB[v].original.name).includes(nk)||nk.includes(norm(DB[v].original.name));
    if(!holds && !isOrig) out.push([name,k,v,'DUPE NOT UNDER TARGET']);
  }
}
console.log('suspect lookups:',out.length);
const seen={};
for(const [t,k,v,why] of out){ (seen[why]=seen[why]||[]).push(`${t}  "${k}" -> ${v}`); }
for(const w in seen){ console.log('\n== '+w+' ('+seen[w].length+') =='); seen[w].slice(0,80).forEach(x=>console.log('   '+x)); }
