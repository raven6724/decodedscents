#!/usr/bin/env python3
"""
English dupe-page generator, rebuilt 2026-08-04.

Two changes from the 2026-07-31 version:
  1. Reads the CURRENT worker.js. Static pages go stale the instant the database
     changes -- adding Club de Nuit Untold silently made the BR540 Extrait page
     wrong until this was rerun. **Rerun this after every DB change.**
  2. Emits a Spanish backlink and hreflang pair on any page that has a /dupes-es/
     counterpart, so the language pairing is bidirectional rather than one-way.

Also builds the /dupes/ directory index.
"""
import json, re, os, html, subprocess, urllib.parse, unicodedata
from shell import SHELL

# The working copy, not a stale sibling one directory up.
SRC="/home/claude/work/worker_live.js"
OUT="/home/claude/dupes"; BASE="https://decodedscents.com"; YEAR="2026"
os.makedirs(OUT, exist_ok=True)
STYLE=open('/tmp/style.html',encoding='utf-8').read()
NAV=open('/tmp/nav.html',encoding='utf-8').read()
FOOTER=open('/tmp/footer.html',encoding='utf-8').read()
ES=set(json.load(open('/tmp/es_slugs.json')).values())

open('/tmp/dump.js','w').write("""
const fs=require('fs');let src=fs.readFileSync(process.argv[2],'utf8');
const s=src.indexOf('const VERIFIED_DB = {');const b=src.indexOf('{',s);let d=0,e=-1;
for(let i=b;i<src.length;i++){if(src[i]==='{')d++;else if(src[i]==='}'){d--;if(d===0){e=i;break;}}}
process.stdout.write(JSON.stringify(eval('('+src.slice(b,e+1)+')')));
""")

# Guard: this generator silently produced stale pages twice on 2026-08-08 because it
# read a copy of worker.js one directory up from the one being edited. Fail loudly
# instead of emitting 122 pages built from the wrong database.
import hashlib as _h
_db = json.loads(subprocess.check_output(['node', '/home/claude/work/dump.js', SRC]).decode())
_ref = json.load(open('/home/claude/work/db.json'))
if _h.md5(json.dumps(_db, sort_keys=True).encode()).hexdigest() != \
   _h.md5(json.dumps(_ref, sort_keys=True).encode()).hexdigest():
    raise SystemExit('ABORT: worker.js does not match db.json — one of them is stale')
DB=json.loads(subprocess.check_output(['node','/tmp/dump.js',SRC]).decode())

def slug(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode('ascii')
    s=s.lower().replace('&','and').replace("'",'').replace('\u2019','')
    return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',s).strip('-'))
esc=lambda s: html.escape(str(s or ''))


# "Buy at {brand}" is correct only when directLink actually points at the brand's
# own shop. Batch 1 added Jomashop and BeautyHouse links, where that label tells the
# reader they are going somewhere they are not. Label from the URL's host instead,
# falling back to the brand for genuine brand-direct links.
RETAILERS = {'jomashop.com': 'Jomashop', 'beautyhouse.com': 'BeautyHouse',
             'microperfumes.com': 'MicroPerfumes', 'fragrancex.com': 'FragranceX',
             'perfumania.com': 'Perfumania', 'notino.com': 'Notino',
             'venbafragrance.com': 'Venba', 'macys.com': "Macy's",
             'bluechateau25.net': 'Blue Chateau 25', 'shopfrenchavenue.com': 'French Avenue',
             'theduabrand.com': 'Dua', 'luckyscent.com': 'Luckyscent', 'scentsplit.com': 'Scent Split'}

def host_label(host):
    """Readable name from a domain we have not mapped. Plain, but never wrong."""
    core = host.split(':')[0]
    for suf in ('.com.au', '.co.uk', '.com', '.net', '.org', '.co', '.fr', '.ae'):
        if core.endswith(suf):
            core = core[: -len(suf)]
            break
    core = core.split('.')[-1]
    return core.replace('-', ' ').title()


def direct_label(url, brand):
    """Name the shop the link actually goes to.

    The brand name is used ONLY when the host looks like that brand's own store.
    Assuming an unknown host belongs to the brand is how "Buy at French Avenue"
    ended up pointing at Blue Chateau 25.
    """
    import urllib.parse as _u
    host = _u.urlparse(url).netloc.lower().removeprefix('www.').removeprefix('us.')
    for dom, nm in RETAILERS.items():
        if host.endswith(dom):
            return nm
    key = re.sub(r'[^a-z0-9]', '', brand.lower())
    hostkey = re.sub(r'[^a-z0-9]', '', host)
    if key and (key in hostkey or hostkey.startswith(key[:6])):
        return brand.replace(' Fragrances', '').replace('Maison Alhambra', 'Alhambra')
    return host_label(host)

def _dl(d):
    """Card heading with the brand linked to its directory page, when one exists."""
    b, n = d.get('brand',''), d.get('name','')
    href = brand_href(b)
    if n.lower().startswith(b.lower()) or not href:
        return esc(dupe_label(d))
    return f'<a href="{href}">{esc(b)}</a> {esc(n)}'

def dupe_label(d):
    """Brand + name, minus the duplication when the name already starts with the brand.
    'Verset' + 'Verset Andrea EDP' should read 'Verset Andrea EDP', not 'Verset Verset
    Andrea EDP'. The originals already had this via full_name(); the dupe cards and the
    comparison table never did."""
    b, n = d.get('brand', ''), d.get('name', '')
    return n if n.lower().startswith(b.lower()) else f"{b} {n}"

def full(o):
    b,n=o['brand'],o['name']
    return n if n.lower().startswith(b.lower()) else f"{b} {n}"

SLUGS={k:slug(full(v['original'])) for k,v in DB.items()}

# Brands with 2+ verified dupes get a directory page. Linking each dupe's brand
# name to it turns every row into a path onward: a reader who likes one Lattafa
# can see all 39 without going back to the index. Only brands that actually have
# a page are linked -- a dead link is worse than plain text.
_BRAND_PAGES = None
def brand_href(brand, es=False):
    global _BRAND_PAGES
    if _BRAND_PAGES is None:
        from collections import Counter
        c = Counter(d['brand'] for v in DB.values() for d in (v.get('dupes') or []))
        _BRAND_PAGES = {b for b, n in c.items() if n >= 2}
    if brand not in _BRAND_PAGES:
        return None
    return ('/marcas/' if es else '/brands/') + slug(brand) + '/'

BRANDS={}
for k,v in DB.items(): BRANDS.setdefault(v['original']['brand'],[]).append(k)

def btns(p,brand):
    b=[]
    #  brandLink is the brand's own shop; directLink is a third-party
    #  retailer. Both are labelled from the URL host, so a button never
    #  names a shop the link does not go to.
    for _f in ('brandLink','directLink'):
        if p.get(_f):
            _nm=direct_label(p[_f], brand)
            b.append(f'<a href="{esc(p[_f])}" target="_blank" rel="noopener nofollow" class="cta-btn">\U0001f310 Buy at {esc(_nm)}</a>')
    for f,lab,spon in (('amazonLink','\U0001f6d2 Amazon',1),('fragranceNetLink','\U0001f3ea FragranceNet',1),('shopSimonLink','\U0001f6cd\ufe0f Shop Simon',1)):
        if p.get(f):
            b.append(f'<a href="{esc(p[f])}" target="_blank" rel="noopener nofollow sponsored" class="cta-btn">{lab}</a>')
    q=urllib.parse.quote_plus(p.get('fragranticaQuery') or f"{brand} {p.get('name','')}")
    b.append(f'<a href="https://www.fragrantica.com/search/?query={q}" target="_blank" rel="noopener" class="cta-btn">\U0001f4d6 Fragrantica</a>')
    return '<div class="buying-options">\n    '+'\n    '.join(b)+'\n  </div>'

def notes(n):
    if not n: return ''
    r=[]
    for lab,key in (('Top','top'),('Heart','middle'),('Base','base')):
        v=n.get(key) or []
        if v: r.append(f'<div class="note-row"><span class="note-label">{lab}</span> {esc(", ".join(v))}</div>')
    return '<div class="notes">'+''.join(r)+'</div>'

EXTRA = SHELL + """
    .dupe-rank{display:inline-block;min-width:2.6rem;font-weight:700;color:#c9a84c}
    .pct-big{font-size:1.35rem;font-weight:700;color:#4ade80}
    .pct-big.floor{color:#facc15}
    .notes{margin:10px 0;font-size:.92rem}.note-row{margin:3px 0}
    .note-label{display:inline-block;min-width:3.6rem;color:#c9a84c;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase}
    .cmp-table{width:100%;border-collapse:collapse;margin:22px 0 6px;font-size:.95rem}
    .cmp-table th{text-align:left;padding:10px 12px;border-bottom:2px solid rgba(201,168,76,.4);color:#c9a84c;font-size:.76rem;letter-spacing:.06em;text-transform:uppercase}
    .cmp-table td{padding:10px 12px;border-bottom:1px solid rgba(255,255,255,.07);vertical-align:top}
    .cmp-table tr:last-child td{border-bottom:none}
    .related-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
    .related-links a{background:rgba(255,255,255,.04);border:1px solid rgba(201,168,76,.25);border-radius:20px;padding:6px 14px;font-size:.85rem;text-decoration:none}
    .related-links a:hover{border-color:#c9a84c}
    .method{border-left:3px solid rgba(201,168,76,.5);padding:12px 16px;margin:26px 0;background:rgba(255,255,255,.02);font-size:.9rem}
    .idx-grid{columns:2;column-gap:34px}@media(max-width:760px){.idx-grid{columns:1}}
    .brand-block{break-inside:avoid;margin-bottom:26px}
    .brand-block h2{font-size:1.05rem;color:#c9a84c;margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid rgba(201,168,76,.2)}
    .dupe-index{list-style:none;padding:0;margin:0}
    .dupe-index li{display:flex;justify-content:space-between;align-items:baseline;padding:4px 0;font-size:.93rem}
    .dupe-index a{text-decoration:none}.dupe-index a:hover{color:#e8c97a}
    .dcount{color:#6b6760;font-size:.78rem}
    @media(max-width:640px){.cmp-table{font-size:.86rem}.cmp-table th,.cmp-table td{padding:8px 7px}}
"""

def head(title,desc,url,ld,alt_es=None):
    hre=''
    if alt_es:
        hre=(f'<link rel="alternate" hreflang="en" href="{url}">\n'
             f'<link rel="alternate" hreflang="es" href="{alt_es}">\n')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | Decoded Scents</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{hre}<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Decoded Scents">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/assets/brand/favicon.png">
<script type="application/ld+json">
{json.dumps(ld,ensure_ascii=False,indent=1)}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3KS1C0WH40"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-3KS1C0WH40');
</script>
{STYLE.replace('  </style>', EXTRA+'  </style>')}
</head>
<body>
{NAV}"""

def build(key,entry):
    o=entry['original']; sl=SLUGS[key]
    dupes=sorted(entry.get('dupes') or [], key=lambda d:-(d.get('similarity') or 0))
    url=f"{BASE}/dupes/{sl}"; n=len(dupes); fn=full(o)
    es=f"{BASE}/dupes-es/{sl}" if sl in ES else None
    if n:
        best=dupes[0]
        title=f"{fn} Dupes: {n} Verified Match{'es' if n!=1 else ''} ({YEAR})"
        desc=(f"Every verified {o['name']} dupe we've tested. {dupe_label(best)} matches at "
              f"{best['similarity']}% for {best.get('price','less')} versus {o.get('price','retail')}. "
              f"Nothing below 85% is published.")
    else:
        title=f"{fn} Dupes: What We Found ({YEAR})"
        desc=(f"We researched {o['name']} alternatives and none cleared our 85% similarity floor. "
              f"Here's what we checked and why nothing made the cut.")
    table=''
    if n:
        rows=''.join(f'<tr><td><strong>{esc(dupe_label(d))}</strong></td>'
                     f'<td class="pct-big{" floor" if d["similarity"]==85 else ""}">{d["similarity"]}%</td>'
                     f'<td>{esc(d.get("price",""))}</td></tr>' for d in dupes)
        table=(f'<table class="cmp-table"><thead><tr><th>Dupe</th><th>Match</th><th>Price</th></tr></thead>'
               f'<tbody>{rows}</tbody></table>'
               f'<p style="font-size:0.85rem;opacity:0.7">{esc(o["name"])} retails around {esc(o.get("price","\u2014"))}.</p>')
    cards=[]
    for i,d in enumerate(dupes,1):
        sh=d.get('sharedNotes') or []
        cards.append(f"""<div class="dupe-entry tier-{'real' if d['similarity']>=88 else 'inspired'}">
  <h3><span class="dupe-rank">#{i}</span>{_dl(d)}</h3>
  <div class="dupe-meta"><span class="pct-big{' floor' if d['similarity']==85 else ''}">{d['similarity']}% match</span>
    &nbsp;\u00b7&nbsp; {esc(d.get('price',''))} &nbsp;\u00b7&nbsp; {esc(d.get('scentFamily',''))}</div>
  {notes(d.get('notes'))}
  {'<p><strong>Shares with the original:</strong> '+esc(', '.join(sh))+'</p>' if sh else ''}
  <p>{esc(d.get('whySimilar',''))}</p>
  {'<p style="font-size:0.85rem;opacity:0.65"><em>Sources: '+esc(d.get('communitySource',''))+'</em></p>' if d.get('communitySource') else ''}
  {btns(d,d['brand'])}
</div>""")
    sibs=[k for k in BRANDS.get(o['brand'],[]) if k!=key][:8]
    related=''
    if sibs:
        links=''.join(f'<a href="/dupes/{SLUGS[s]}">{esc(DB[s]["original"]["name"])}</a>' for s in sibs)
        related=f'<h2>More from {esc(o["brand"])}</h2><div class="related-links">{links}</div>'
    es_block=''
    if es:
        es_block=(f'<h2>En espa\u00f1ol</h2><p>Esta p\u00e1gina tambi\u00e9n est\u00e1 disponible '
                  f'<a href="/dupes-es/{sl}" hreflang="es">en espa\u00f1ol</a>.</p>')
    empty='' if n else (f'<div class="method"><p><strong>No verified dupes yet.</strong> We researched alternatives to '
        f'{esc(o["name"])} and nothing cleared our 85% similarity floor. Rather than publish a weak match, we leave this '
        f'empty until something earns a place. If you know of one, we want to hear about it.</p></div>')
    ld={"@context":"https://schema.org","@type":"ItemList","name":title,"description":desc,"url":url,
        "numberOfItems":n,"itemListElement":[{"@type":"ListItem","position":i,"name":dupe_label(d),
        "description":f"{d['similarity']}% match to {fn}"} for i,d in enumerate(dupes,1)]}
    return head(title,desc,url,ld,es)+f"""
<header class="article-hero">
  <div class="container">
    <div class="hero-meta">\u2726 Verified Dupes \u00b7 {esc(o['brand'])}</div>
    <h1>{esc(fn)} Dupes</h1>
    <div class="hero-byline">{n} verified match{'es' if n!=1 else ''} \u00b7 nothing below 85% \u00b7 updated {YEAR}</div>
  </div>
</header>
<main class="container">
<article>
<div class="dupe-entry tier-callout">
  <h2 style="margin-top:0">The original: {esc(fn)}</h2>
  <div class="dupe-meta">{esc(o.get('price',''))} &nbsp;\u00b7&nbsp; {esc(o.get('scentFamily',''))}</div>
  {notes(o.get('notes'))}
  {'<p>'+esc(o.get('description',''))+'</p>' if o.get('description') else ''}
  {btns(o,o['brand'])}
</div>
{table}
{empty}
<div class="method">
  <p><strong>How we score.</strong> Every percentage comes from cross-referencing note pyramids against
  Fragrantica and brand-official sources, then weighting what people who own both fragrances actually
  report. We don't publish anything below 85%, and we say when something barely clears.</p>
</div>
{''.join(cards)}
{related}
{es_block}
<h2>Search anything else</h2>
<p>Our full database covers {len(DB)} originals and {sum(len(v.get('dupes') or []) for v in DB.values())} verified dupes.
<a href="/">Search it here</a>.</p>
</article>
</main>
{FOOTER}
</body>
</html>"""

for k,x in DB.items():
    open(os.path.join(OUT,SLUGS[k]+'.html'),'w',encoding='utf-8').write(build(k,x))

# ---- directory ----
total=sum(len(v.get('dupes') or []) for v in DB.values())
rows=[]
for brand in sorted(BRANDS,key=lambda b:b.lower()):
    keys=sorted(BRANDS[brand],key=lambda k:DB[k]['original']['name'].lower())
    items=''.join(f'<li><a href="/dupes/{SLUGS[k]}">{esc(DB[k]["original"]["name"])}</a>'
                  f'<span class="dcount">{len(DB[k].get("dupes") or [])}</span></li>' for k in keys)
    rows.append(f'<div class="brand-block"><h2>{esc(brand)}</h2><ul class="dupe-index">{items}</ul></div>')
ld={"@context":"https://schema.org","@type":"CollectionPage","name":"Every Fragrance Dupe We've Verified",
    "description":f"{len(DB)} originals, {total} verified dupes, nothing below 85%.","url":f"{BASE}/dupes/"}
idx=head(f"Every Fragrance Dupe We've Verified \u2014 {len(DB)} Originals, {total} Matches",
   f"Browse every verified fragrance dupe in our database. {len(DB)} originals across {len(BRANDS)} brands, {total} verified matches, nothing published below 85% similarity.",
   f"{BASE}/dupes/",ld)+f"""
<header class="article-hero">
  <div class="container">
    <div class="hero-meta">\u2726 The Database</div>
    <h1>Every Dupe We've Verified</h1>
    <div class="hero-byline">{len(DB)} originals \u00b7 {total} verified matches \u00b7 {len(BRANDS)} brands \u00b7 nothing below 85%</div>
  </div>
</header>
<main class="container"><article>
<p>Every fragrance below has been researched against Fragrantica and brand-official sources, then weighted by
what people who own both actually report. <strong>We don't publish anything under 85% similarity</strong> \u2014 and where
something barely clears, we say so on the page.</p>
<p>The number beside each name is how many verified dupes we found. A zero means we looked and nothing qualified.</p>
<p><a href="/dupes-es/">Ver en espa\u00f1ol \u2192</a></p>
<div class="idx-grid">{''.join(rows)}</div>
</article></main>
{FOOTER}
</body>
</html>"""
open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write(idx)
json.dump(SLUGS,open('/tmp/slugs.json','w'),indent=1)
print(f"generated {len(DB)} pages + index. dupes={total}. Spanish backlinks on {len(ES)} pages.")