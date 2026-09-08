import json, subprocess, os, sys
sys.path.insert(0,'.')
from build_index import build_index, slugify
DB=json.loads(subprocess.check_output(['node','dump.js','worker_live.js']).decode())
def full(o):
    b,n=o['brand'],o['name']
    return n if n.lower().startswith(b.lower()) else f"{b} {n}"
EN={k:slugify(full(v['original'])) for k,v in DB.items()}
ES=json.load(open('/tmp/es_slugs.json'))
style=open('style.html',encoding='utf-8').read()
footer=open('footer.html',encoding='utf-8').read()
footer_es=open('footer_es.html',encoding='utf-8').read()
nav_en=open('nav.html',encoding='utf-8').read()
nav_es="""<nav class="top-nav">
  <div class="container">
    <a href="/es/" class="nav-logo">DECODED SCENTS</a>
    <div class="nav-links">
      <a href="/es/">Inicio</a>
      <a href="/dupes-es/">Todos los Dupes</a>\n      <a href="/marcas/">Marcas</a>
      <a href="/acerca-de/">Qui\u00e9nes somos</a>
      <a href="/Articles/">Art\u00edculos</a>
      <a href="/" hreflang="en">English</a>
    </div>
  </div>
</nav>"""
BASE="https://decodedscents.com"
open('/home/claude/dupes/index.html','w',encoding='utf-8').write(
    build_index(DB,EN,'en',style,footer,nav_en,BASE))
open('/home/claude/dupes-es/index.html','w',encoding='utf-8').write(
    build_index(DB,{k:ES[k] for k in ES},'es',style,footer_es,nav_es,BASE))
print('EN index:',len(EN),'originals |','ES index:',len(ES),'originals')
