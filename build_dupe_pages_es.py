#!/usr/bin/env python3
"""
Spanish dupe-page generator (2026-08-03)

Mirrors build_dupe_pages.py but emits Spanish pages at /dupes-es/{slug}.

SLUGS ARE IDENTICAL to the English set. Fragrance names are proper nouns and do
not translate, so "creed-aventus" is correct in both languages. This makes the
hreflang pairing trivial and avoids inventing Spanish spellings for brand names.
The directory carries the language, not the slug.

SCOPE: 10 pages in this first batch, not all 121. The database holds ~11,000 words
of English prose across 340 fields, and ARTICLE_PROTOCOLS §5.3 requires a full
bilingual proofread with no exceptions. Machine-quality translation at that volume
would breach the standard the site is built on -- the Rayhaan Spanish proofread
caught 12 issues in 1,600 words, including 4 English calques. Ten fully-proofread
pages beat 121 that fail their own standard. Expand once these prove out.

Translations live in /tmp/es_trans.json, written by hand and checked against the
glossary in ARTICLE_PROTOCOLS §6.
"""
import json, re, os, html, unicodedata, urllib.parse
from shell import SHELL

DATA = json.load(open('/tmp/es_data.json'))
TRANS = json.load(open('/tmp/es_trans.json'))
NOTES = json.load(open('/tmp/notes_es.json'))
FAMS = json.load(open('/tmp/fam_es.json'))
STYLE = open('/tmp/style.html', encoding='utf-8').read()
FOOTER = open('/tmp/footer_es.html', encoding='utf-8').read()
BASE = "https://decodedscents.com"
OUT = "/home/claude/dupes-es"
YEAR = "2026"
os.makedirs(OUT, exist_ok=True)

NAV = """<nav class="top-nav">
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

esc = lambda s: html.escape(str(s or ''))


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
    b, n = d.get('brand',''), d.get('name','')
    href = brand_href(b, es=True)
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


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.lower().replace('&', 'and').replace("'", '').replace('\u2019', '')
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s).strip('-'))

def full_name(brand, name):
    return name if name.lower().startswith(brand.lower()) else f"{brand} {name}"


# Brands with 2+ verified dupes get a directory page. Linking each dupe's brand
# name to it turns every row into a path onward: a reader who likes one Lattafa
# can see all 39 without going back to the index. Only brands that actually have
# a page are linked -- a dead link is worse than plain text.
_BRAND_PAGES = None
def brand_href(brand, es=False):
    global _BRAND_PAGES
    if _BRAND_PAGES is None:
        from collections import Counter
        c = Counter(d['brand'] for v in DATA.values() for d in (v.get('dupes') or []))
        _BRAND_PAGES = {b for b, n in c.items() if n >= 2}
    if brand not in _BRAND_PAGES:
        return None
    return ('/marcas/' if es else '/brands/') + slug(brand) + '/'

SLUGS = {k: slug(full_name(v['brand'], v['name'])) for k, v in DATA.items()}

def buttons(links, brand, fq):
    b = []
    #  'br' is the brand's own shop, 'd' a third-party retailer. Both labelled
    #  from the URL host so a button never names a shop it does not go to.
    for _k in ('br', 'd'):
        if links.get(_k):
            nm = direct_label(links[_k], brand)
            b.append(f'<a href="{esc(links[_k])}" target="_blank" rel="noopener nofollow" class="cta-btn">\U0001f310 Comprar en {esc(nm)}</a>')
    if links.get('a'):
        b.append(f'<a href="{esc(links["a"])}" target="_blank" rel="noopener nofollow sponsored" class="cta-btn">\U0001f6d2 Amazon</a>')
    if links.get('f'):
        b.append(f'<a href="{esc(links["f"])}" target="_blank" rel="noopener nofollow sponsored" class="cta-btn">\U0001f3ea FragranceNet</a>')
    if links.get('s'):
        b.append(f'<a href="{esc(links["s"])}" target="_blank" rel="noopener nofollow sponsored" class="cta-btn">\U0001f6cd\ufe0f Shop Simon</a>')
    q = urllib.parse.quote_plus(fq or '')
    b.append(f'<a href="https://www.fragrantica.es/search/?query={q}" target="_blank" rel="noopener" class="cta-btn">\U0001f4d6 Fragrantica</a>')
    return '<div class="buying-options">\n    ' + '\n    '.join(b) + '\n  </div>'

def tr_fam(x):
    return FAMS.get(x, x)

def tr_note(x):
    """Translate a note name. Unknown notes pass through untouched rather than
    guessing -- a wrong note name is worse than an English one."""
    return NOTES.get(x, x)

def notes(n):
    if not n: return ''
    rows = []
    for label, key in (('Salida', 'top'), ('Coraz\u00f3n', 'middle'), ('Fondo', 'base')):
        v = n.get(key) or []
        if v: rows.append(f'<div class="note-row"><span class="note-label">{label}</span> {esc(", ".join(tr_note(x) for x in v))}</div>')
    return '<div class="notes">' + ''.join(rows) + '</div>'

EXTRA = SHELL + """
    .dupe-rank { display:inline-block; min-width:2.6rem; font-weight:700; color:#c9a84c; }
    .pct-big { font-size:1.35rem; font-weight:700; color:#4ade80; }
    .pct-big.floor { color:#facc15; }
    .notes { margin:10px 0; font-size:0.92rem; }
    .note-row { margin:3px 0; }
    .note-label { display:inline-block; min-width:4.4rem; color:#c9a84c; font-size:0.72rem;
                  letter-spacing:0.08em; text-transform:uppercase; }
    .cmp-table { width:100%; border-collapse:collapse; margin:22px 0 6px; font-size:0.95rem; }
    .cmp-table th { text-align:left; padding:10px 12px; border-bottom:2px solid rgba(201,168,76,0.4);
                    color:#c9a84c; font-size:0.76rem; letter-spacing:0.06em; text-transform:uppercase; }
    .cmp-table td { padding:10px 12px; border-bottom:1px solid rgba(255,255,255,0.07); vertical-align:top; }
    .cmp-table tr:last-child td { border-bottom:none; }
    .related-links { display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
    .related-links a { background:rgba(255,255,255,0.04); border:1px solid rgba(201,168,76,0.25);
                       border-radius:20px; padding:6px 14px; font-size:0.85rem; text-decoration:none; }
    .related-links a:hover { border-color:#c9a84c; }
    .method { border-left:3px solid rgba(201,168,76,0.5); padding:12px 16px; margin:26px 0;
              background:rgba(255,255,255,0.02); font-size:0.9rem; }
    @media (max-width:640px){ .cmp-table{font-size:0.85rem} .cmp-table th,.cmp-table td{padding:8px 6px} }
"""

def build(key):
    v = DATA[key]; t = TRANS[key]
    sl = SLUGS[key]
    url = f"{BASE}/dupes-es/{sl}"
    en_url = f"{BASE}/dupes/{sl}"
    fn = full_name(v['brand'], v['name'])
    dupes = sorted(zip(v['dupes'], t['why']), key=lambda z: -(z[0]['sim'] or 0))
    n = len(dupes)
    best = dupes[0][0] if dupes else None

    if best is None:
        #  Nothing cleared the 85% floor. The page still ships, and says so --
        #  an honest empty is the whole point of having a floor.
        title = f"Dupes de {fn}: sin alternativas verificadas todav\u00eda ({YEAR})"
        desc = (f"Buscamos dupes de {v['name']} y ninguno super\u00f3 nuestro m\u00ednimo del 85% de "
                f"similitud. Esta p\u00e1gina se queda vac\u00eda a prop\u00f3sito hasta que aparezca uno que lo logre.")
    else:
        title = f"Dupes de {fn}: {n} Alternativa{'s' if n != 1 else ''} Verificada{'s' if n != 1 else ''} ({YEAR})"
        desc = (f"Todos los dupes verificados de {v['name']}. {dupe_label(best)} coincide al "
                f"{best['sim']}% por {best.get('price','menos')} frente a {v.get('price','su precio de venta')}. "
                f"No publicamos nada por debajo del 85%.")

    rows = ''.join(
        f'<tr><td><strong>{esc(dupe_label(d))}</strong></td>'
        f'<td class="pct-big{" floor" if d["sim"]==85 else ""}">{d["sim"]}%</td>'
        f'<td>{esc(d.get("price",""))}</td></tr>' for d, _ in dupes)
    table = ('' if not dupes else
             f'<table class="cmp-table"><thead><tr><th>Dupe</th><th>Similitud</th><th>Precio</th></tr></thead>'
             f'<tbody>{rows}</tbody></table>'
             f'<p style="font-size:0.85rem;opacity:0.7">{esc(v["name"])} se vende en torno a {esc(v.get("price","\u2014"))}.</p>')

    if not dupes:
        table = ('<div class="dupe-entry"><h3>Todav\u00eda no hay alternativas verificadas</h3>'
                 f'<p>Buscamos dupes de {esc(v["name"])} y ninguno super\u00f3 nuestro m\u00ednimo del 85% de '
                 'similitud. Preferimos dejar esta p\u00e1gina vac\u00eda antes que recomendar algo que no se '
                 'parece lo suficiente. Volveremos a revisarlo.</p>'
                 f'<p style="font-size:0.85rem;opacity:0.7">{esc(v["name"])} se vende en torno a '
                 f'{esc(v.get("price","\u2014"))}.</p></div>')

    cards = []
    for i, (d, why) in enumerate(dupes, 1):
        sh = d.get('shared') or []
        cards.append(f"""<div class="dupe-entry tier-{'real' if d['sim']>=88 else 'inspired'}">
  <h3><span class="dupe-rank">#{i}</span>{_dl(d)}</h3>
  <div class="dupe-meta"><span class="pct-big{' floor' if d['sim']==85 else ''}">{d['sim']}% de similitud</span>
    &nbsp;\u00b7&nbsp; {esc(d.get('price',''))} &nbsp;\u00b7&nbsp; {esc(tr_fam(d.get('fam','')))}</div>
  {notes(d.get('notes'))}
  {'<p><strong>Comparte con el original:</strong> ' + esc(', '.join(tr_note(x) for x in sh)) + '</p>' if sh else ''}
  <p>{esc(why)}</p>
  {buttons(d.get('links') or {}, d['brand'], (d.get('links') or {}).get('fq'))}
</div>""")

    sibs = [k for k in TRANS if k != key and DATA[k]['brand'] == v['brand']][:6]
    related = ''
    if sibs:
        links = ''.join(f'<a href="/dupes-es/{SLUGS[s]}">{esc(DATA[s]["name"])}</a>' for s in sibs)
        related = f'<h2>M\u00e1s de {esc(v["brand"])}</h2><div class="related-links">{links}</div>'

    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": title,
          "description": desc, "url": url, "inLanguage": "es", "numberOfItems": n,
          "itemListElement": [{"@type": "ListItem", "position": i,
                               "name": dupe_label(d),
                               "description": f"{d['sim']}% de similitud con {fn}"}
                              for i, (d, _) in enumerate(dupes, 1)]}

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | Decoded Scents</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="es" href="{url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Decoded Scents">
<meta property="og:locale" content="es_MX">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/assets/brand/favicon.png">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3KS1C0WH40"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-3KS1C0WH40');
</script>
{STYLE.replace('  </style>', EXTRA + '  </style>')}
</head>
<body>
{NAV}
<header class="article-hero">
  <div class="container">
    <div class="hero-meta">\u2726 Dupes Verificados \u00b7 {esc(v['brand'])}</div>
    <h1>Dupes de {esc(fn)}</h1>
    <div class="hero-byline">{n} alternativa{'s' if n != 1 else ''} verificada{'s' if n != 1 else ''} \u00b7 nada por debajo del 85% \u00b7 actualizado en {YEAR}</div>
  </div>
</header>
<main class="container">
<article>
<div class="dupe-entry tier-callout">
  <h2 style="margin-top:0">El original: {esc(fn)}</h2>
  <div class="dupe-meta">{esc(v.get('price',''))} &nbsp;\u00b7&nbsp; {esc(tr_fam(v.get('fam','')))}</div>
  {notes(v.get('notes'))}
  <p>{esc(t['desc'])}</p>
  {buttons(v.get('links') or {}, v['brand'], (v.get('links') or {}).get('fq'))}
</div>
{table}
<div class="method">
  <p><strong>C\u00f3mo puntuamos.</strong> Cada porcentaje sale de contrastar las pir\u00e1mides olfativas con Fragrantica
  y con las fuentes oficiales de cada marca, y despu\u00e9s sopesar lo que realmente reportan quienes tienen ambas
  fragancias. No publicamos nada por debajo del 85%, y cuando algo apenas supera el umbral, lo decimos.</p>
</div>
{''.join(cards)}
{related}
<h2>Versi\u00f3n en ingl\u00e9s</h2>
<p>Esta p\u00e1gina tambi\u00e9n existe <a href="{en_url}">en ingl\u00e9s</a>, con la base de datos completa de
{len(DATA)}+ originales. <a href="/">Busca cualquier fragancia aqu\u00ed</a>.</p>
</article>
</main>
{FOOTER}
</body>
</html>"""

count = 0
for k in TRANS:
    open(os.path.join(OUT, SLUGS[k] + '.html'), 'w', encoding='utf-8').write(build(k))
    count += 1
print(f"generated {count} Spanish pages in {OUT}/")
json.dump({k: SLUGS[k] for k in TRANS}, open('/tmp/es_slugs.json', 'w'), indent=1)