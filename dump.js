const fs=require('fs');let src=fs.readFileSync(process.argv[2],'utf8');
const s=src.indexOf('const VERIFIED_DB = {');const b=src.indexOf('{',s);let d=0,e=-1;
for(let i=b;i<src.length;i++){if(src[i]==='{')d++;else if(src[i]==='}'){d--;if(d===0){e=i;break;}}}
process.stdout.write(JSON.stringify(eval('('+src.slice(b,e+1)+')')));
