const fs=require('fs');let src=fs.readFileSync('worker_live.js','utf8');
function grab(n){const s=src.indexOf('const '+n+' = {');const b=src.indexOf('{',s);let d=0,e=-1;
for(let i=b;i<src.length;i++){if(src[i]==='{')d++;else if(src[i]==='}'){d--;if(d===0){e=i;break;}}}
return eval('('+src.slice(b,e+1)+')');}
const DB=grab('VERIFIED_DB'),AL=grab('ALIASES'),D2O=grab('DUPE_TO_ORIGINAL');
const t=["baccarat rouge 540","creed aventus","dior sauvage","bianco latte","vibrato","hacivat",
"sumou platinum","maahir black edition","yara moi","perseus","jean lowe immortel","zahi","ajwad"];
for(const q of t){let k=DB[q]?q:(AL[q]||D2O[q]||null); if(k&&!DB[k])k=AL[k]||D2O[k]||k;
const e=k&&DB[k]; console.log(`"${q}" -> ${k||'NO MATCH'}${e?`  (${e.dupes.length} dupes)`:''}`);}
