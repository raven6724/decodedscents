#!/usr/bin/env python3
"""Reshape VERIFIED_DB into /tmp/es_data.json and merge Spanish translations,
with the positional-alignment assertion that keeps why[i] tied to dupes[i]."""
import json, sys, os, glob, subprocess
WORK=os.path.dirname(os.path.abspath(__file__)); p=lambda f: os.path.join(WORK,f)
DB=json.loads(subprocess.check_output(['node',p('dump.js'),p('worker_live.js')]).decode())
B1=json.load(open(p('es_trans.json')))
B2={}
for f in sorted(glob.glob(p('es_trans_batch*_src.json'))): B2.update(json.load(open(f)))
def links(o):
    d={}
    for s,t in (('brandLink','br'),('directLink','d'),('amazonLink','a'),('fragranceNetLink','f'),('shopSimonLink','s')):
        if o.get(s): d[t]=o[s]
    b,n=o.get('brand',''),o.get('name','')
    d['fq']=o.get('fragranticaQuery') or (n if n.lower().startswith(b.lower()) else f'{b} {n}').strip()
    return d
def flat(o): return {'brand':o['brand'],'name':o['name'],'price':o.get('price'),
                     'fam':o.get('scentFamily'),'notes':o.get('notes') or {},'links':links(o)}
data={}
for k,e in DB.items():
    o=flat(e['original']); o['dupes']=[]
    for d in e.get('dupes') or []:
        f=flat(d); f['sim']=d.get('similarity'); f['shared']=d.get('sharedNotes') or []
        o['dupes'].append(f)
    data[k]=o
trans={}; errors=[]
for k,t in B1.items():
    if k not in DB: errors.append(f'batch1 key not in DB: {k}'); continue
    n=len(DB[k].get('dupes') or [])
    if len(t['why'])!=n: errors.append(f'batch1 {k}: {len(t["why"])} why vs {n} dupes')
    trans[k]={'desc':t['desc'],'why':list(t['why'])}
for k,t in B2.items():
    if k in trans: errors.append(f'{k}: already in batch 1'); continue
    if k not in DB: errors.append(f'key not in DB: {k}'); continue
    keyed=dict(t['why']); why=[]
    for d in DB[k].get('dupes') or []:
        lbl=f"{d['brand']} {d['name']}"
        if lbl not in keyed: errors.append(f'{k}: no translation for {lbl!r}'); why.append('')
        else: why.append(keyed.pop(lbl))
    for left in keyed: errors.append(f'{k}: translation {left!r} matches no dupe')
    trans[k]={'desc':t['desc'],'why':why}
notes=json.load(open(p('notes_es.json'))); fams=json.load(open(p('fam_es.json')))
for f in sorted(glob.glob(p('notes_es_batch*.json'))): notes.update(json.load(open(f)))
for f in sorted(glob.glob(p('fam_es_batch*.json'))): fams.update(json.load(open(f)))
if errors:
    print('FAILED — nothing written:'); [print('  ',e) for e in errors]; sys.exit(1)
miss_n={x for k in trans for o in [DB[k]['original']]+(DB[k].get('dupes') or [])
        for x in sum((o.get('notes') or {}).values(),[])+(o.get('sharedNotes') or []) if x not in notes}
miss_f={o['scentFamily'] for k in trans for o in [DB[k]['original']]+(DB[k].get('dupes') or [])
        if o.get('scentFamily') and o['scentFamily'] not in fams}
if miss_n or miss_f:
    print('WARNING — untranslated terms will render in English:')
    for x in sorted(miss_n): print('   note:',x)
    for x in sorted(miss_f): print('   family:',x)
for name,obj in (('es_data.json',data),('es_trans.json',trans),('notes_es.json',notes),('fam_es.json',fams)):
    json.dump(obj,open('/tmp/'+name,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
for f in ('style.html','footer.html','footer_es.html','nav.html'):
    open('/tmp/'+f,'w',encoding='utf-8').write(open(p(f),encoding='utf-8').read())
print(f'ok: {len(data)} originals, {len(trans)} translated, '
      f'{sum(len(t["why"]) for t in trans.values())} dupe paragraphs, '
      f'{len(notes)} notes / {len(fams)} families')
