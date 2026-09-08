#!/usr/bin/env python3
"""
Brand directory pages  ->  /brands/{slug}/  and  /marcas/{slug}/     (2026-08-14)

WHY THIS EXISTS. Search Console shows the site ranks at position 5-8 for
"rayhaan dupe list", "rayhaan dupes list", "rayhaan list of dupes" and "all
rayhaan dupes" -- six of the seven queries that convert at all. Meanwhile
"aventus dupe" sits at position 47 with 60 impressions and zero clicks.

The pattern: people search "[clone house] dupe list", wanting a complete
enumeration for a brand. And almost nobody publishes those, because every
competitor organises by the expensive original instead. The Rayhaan article
ranks by accident of that gap.

This turns the gap into 15 pages of data the database already holds.

THRESHOLD. A brand needs 2+ verified dupes. Thirteen brands have exactly one;
a page for those would be a thin duplicate of the entry page it links to.
They are named on the index instead, so nothing is hidden.

Sorted by similarity descending -- a reader scanning a brand wants the best
match first, and the floor is the story: the last row is the weakest thing we
were willing to publish.
"""
import json, os, re, html, unicodedata, subprocess
from collections import defaultdict
from shell import SHELL

BASE = 'https://decodedscents.com'
OUT_EN = '/home/claude/brands'
OUT_ES = '/home/claude/marcas'
YEAR = '2026'
MIN_DUPES = 2

esc = lambda s: html.escape(str(s or ''))

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.lower().replace('&', 'and').replace("'", '').replace('\u2019', '')
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s).strip('-'))

def full(o):
    b, n = o['brand'], o['name']
    return n if n.lower().startswith(b.lower()) else f'{b} {n}'

def dupe_label(d):
    b, n = d.get('brand', ''), d.get('name', '')
    return n if n.lower().startswith(b.lower()) else f'{b} {n}'

EXTRA = SHELL + """
    .bt { width:100%; border-collapse:collapse; margin:22px 0 8px; font-size:.95rem; }
    .bt th { text-align:left; padding:10px 12px; border-bottom:2px solid rgba(201,168,76,.4);
             color:var(--gold,#c9a84c); font-size:.72rem; letter-spacing:.07em; text-transform:uppercase; }
    .bt td { padding:11px 12px; border-bottom:1px solid rgba(255,255,255,.06); vertical-align:top; }
    .bt tr:last-child td { border-bottom:none; }
    .bt .pct { font-weight:700; font-variant-numeric:tabular-nums; white-space:nowrap; }
    .bt .t3 { color:#4ade80; } .bt .t2 { color:var(--gold,#c9a84c); } .bt .t1 { color:#facc15; }
    .bt .dn { color:var(--text,#e8e4dc); }
    .bt .pr { color:var(--text-dim,#7a756c); white-space:nowrap; }
    .bt a { border-bottom:1px solid rgba(201,168,76,.25); }
    .bstat { display:flex; flex-wrap:wrap; gap:26px; margin:20px 0 4px;
             padding:16px 18px; background:var(--bg2,#111118); border-radius:10px;
             border:1px solid var(--border,rgba(255,255,255,.07)); }
    .bstat div { min-width:90px; }
    .bstat b { display:block; font-size:1.5rem; color:var(--gold,#c9a84c); line-height:1.2; }
    .bstat span { font-size:.72rem; letter-spacing:.08em; text-transform:uppercase;
                  color:var(--text-dim,#7a756c); }
    .bgrid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
             gap:12px; margin:22px 0 28px; }
    .bcard { display:block; padding:16px 18px; border-radius:10px; text-decoration:none;
             background:var(--bg2,#111118); border:1px solid var(--border,rgba(255,255,255,.07));
             border-left:3px solid rgba(201,168,76,.3); transition:border-color .15s, transform .15s; }
    .bcard:hover { border-color:var(--gold,#c9a84c); border-left-color:var(--gold,#c9a84c);
                   transform:translateY(-1px); }
    article a.bcard { border-bottom:1px solid var(--border,rgba(255,255,255,.07)); }
    article a.bcard:hover { border-bottom-color:var(--gold,#c9a84c); }
    .bcard .bn { display:block; font-size:1.02rem; color:var(--text,#e8e4dc); margin-bottom:7px; }
    .bcard .bm { font-size:.79rem; color:var(--text-dim,#7a756c); letter-spacing:.02em; }
    .bcard .bm b { color:var(--gold,#c9a84c); font-weight:700; font-variant-numeric:tabular-nums; }
    .bthin { font-size:.85rem; color:var(--text-dim,#7a756c); line-height:1.6;
             padding:14px 16px; border-left:2px solid var(--border,rgba(255,255,255,.09));
             margin:6px 0 22px; }
    @media(max-width:640px){ .bt th,.bt td{padding:8px 6px;font-size:.86rem} .bstat{gap:16px} }
"""

def nav(es):
    if es:
        return ('<nav class="top-nav"><div class="container">'
                '<a href="/es/" class="nav-logo">DECODED SCENTS</a><div class="nav-links">'
                '<a href="/es/">Inicio</a><a href="/dupes-es/">Todos los Dupes</a>'
                '<a href="/marcas/">Marcas</a><a href="/acerca-de/">Qui\u00e9nes somos</a>'
                '<a href="/" hreflang="en">English</a></div></div></nav>')
    return ('<nav class="top-nav"><div class="container">'
            '<a href="/" class="nav-logo">DECODED SCENTS</a><div class="nav-links">'
            '<a href="/">Home</a><a href="/dupes/">All Dupes</a><a href="/brands/">Brands</a>'
            '<a href="/about/">About</a><a href="/es/" hreflang="es">Espa\u00f1ol</a></div></div></nav>')

def page(title, desc, url, alt, ld, body, style, footer, es, h1, eyebrow, byline):
    return f"""<!DOCTYPE html>
<html lang="{'es' if es else 'en'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | Decoded Scents</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{alt[0]}">
<link rel="alternate" hreflang="es" href="{alt[1]}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Decoded Scents">
{'<meta property="og:locale" content="es_MX">' if es else ''}
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
{style.replace('  </style>', EXTRA + '  </style>')}
</head>
<body>
{nav(es)}
<header class="article-hero"><div class="container">
  <div class="hero-meta">{esc(eyebrow)}</div>
  <h1>{esc(h1)}</h1>
  <div class="hero-byline">{byline}</div>
</div></header>
<main class="container"><article>
{body}
</article></main>
{footer}
</body>
</html>"""

def tier(p):
    return 't3' if p >= 90 else ('t2' if p >= 87 else 't1')

def build(DB, es_slugs, style, footer, footer_es):
    brands = defaultdict(list)
    for k, v in DB.items():
        for d in v.get('dupes') or []:
            brands[d['brand']].append((k, v['original'], d))
    keep = {b: r for b, r in brands.items() if len(r) >= MIN_DUPES}
    thin = {b: r for b, r in brands.items() if len(r) < MIN_DUPES}
    en_slugs = {k: slugify(full(v['original'])) for k, v in DB.items()}
    made = []

    for es in (False, True):
        root = OUT_ES if es else OUT_EN
        os.makedirs(root, exist_ok=True)
        for brand, rows in sorted(keep.items(), key=lambda x: -len(x[1])):
            bs = slugify(brand)
            rows = sorted(rows, key=lambda r: -r[2]['similarity'])
            n = len(rows)
            origs = len({r[0] for r in rows})
            best = rows[0][2]['similarity']
            url = f'{BASE}/{"marcas" if es else "brands"}/{bs}/'
            alt = (f'{BASE}/brands/{bs}/', f'{BASE}/marcas/{bs}/')

            trs = []
            for k, o, d in rows:
                dupes_dir = '/dupes-es/' if es else '/dupes/'
                # only link into the Spanish tree when that page actually exists
                href = (dupes_dir + en_slugs[k]) if (not es or k in es_slugs) else ('/dupes/' + en_slugs[k])
                trs.append(
                    f'<tr><td class="dn">{esc(dupe_label(d))}</td>'
                    f'<td><a href="{href}">{esc(full(o))}</a></td>'
                    f'<td class="pct {tier(d["similarity"])}">{d["similarity"]}%</td>'
                    f'<td class="pr">{esc(d.get("price",""))}</td></tr>')
            if es:
                head = ['Dupe', 'Alternativa a', 'Similitud', 'Precio']
                title = f'Todos los dupes de {brand} verificados \u2014 {n} alternativas ({YEAR})'
                h1 = f'Todos los dupes de {brand}'
                eyebrow = '\u2726 Por marca'
                byline = (f'{n} alternativas verificadas \u00b7 {origs} originales \u00b7 '
                          f'la mejor al {best}% \u00b7 nada por debajo del 85%')
                desc = (f'Lista completa de los dupes de {brand} que hemos verificado: {n} alternativas '
                        f'con {origs} fragancias originales, la mejor al {best}%. Nada por debajo del 85%.')
                intro = (f'<p>Esta es la lista completa de lo que hemos verificado de <strong>{esc(brand)}</strong>, '
                         f'no una selecci\u00f3n. Cada porcentaje sale de cotejar las pir\u00e1mides olfativas con '
                         f'Fragrantica y con el material oficial de cada marca, y de sopesar despu\u00e9s lo que '
                         f'reporta quien tiene las dos fragancias. <strong>No publicamos nada por debajo del '
                         f'85% de similitud</strong>, as\u00ed que la \u00faltima fila de esta tabla es lo m\u00e1s flojo que '
                         f'estuvimos dispuestos a publicar.</p>')
                stats = (f'<div class="bstat"><div><b>{n}</b><span>Dupes verificados</span></div>'
                         f'<div><b>{origs}</b><span>Originales</span></div>'
                         f'<div><b>{best}%</b><span>Mejor parecido</span></div>'
                         f'<div><b>85%</b><span>M\u00ednimo exigido</span></div></div>')
                foot = (f'<h2>Otras marcas</h2><p>Consulta el <a href="/marcas/">\u00edndice de marcas</a> '
                        f'o la <a href="/dupes-es/">base de datos completa</a>.</p>')
                fo = footer_es
            else:
                head = ['Dupe', 'Alternative to', 'Match', 'Price']
                title = f"Every {brand} Dupe We've Verified \u2014 {n} Matches ({YEAR})"
                h1 = f'Every {brand} Dupe'
                eyebrow = '\u2726 By brand'
                byline = (f'{n} verified matches \u00b7 {origs} originals \u00b7 '
                          f'best at {best}% \u00b7 nothing below 85%')
                desc = (f"The complete list of {brand} dupes we've verified: {n} matches against {origs} "
                        f'original fragrances, the best at {best}%. Nothing below 85% is published.')
                intro = (f'<p>This is the complete list of what we have verified from '
                         f'<strong>{esc(brand)}</strong> \u2014 not a selection. Every percentage comes from '
                         f'cross-referencing note pyramids against Fragrantica and brand-official sources, '
                         f'then weighting what people who own both fragrances actually report. '
                         f'<strong>We don\u2019t publish anything under 85% similarity</strong>, so the last '
                         f'row of this table is the weakest thing we were willing to publish.</p>')
                stats = (f'<div class="bstat"><div><b>{n}</b><span>Verified dupes</span></div>'
                         f'<div><b>{origs}</b><span>Originals</span></div>'
                         f'<div><b>{best}%</b><span>Best match</span></div>'
                         f'<div><b>85%</b><span>Floor</span></div></div>')
                foot = (f'<h2>Other brands</h2><p>See the <a href="/brands/">brand index</a> '
                        f'or the <a href="/dupes/">full database</a>.</p>')
                fo = footer

            ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': title,
                  'description': desc, 'url': url, 'numberOfItems': n,
                  'itemListElement': [{'@type': 'ListItem', 'position': i,
                                       'name': dupe_label(d),
                                       'description': f'{d["similarity"]}% match to {full(o)}'}
                                      for i, (k, o, d) in enumerate(rows, 1)]}
            if es: ld['inLanguage'] = 'es'
            body = (intro + stats +
                    '<table class="bt"><thead><tr>' +
                    ''.join(f'<th>{esc(h)}</th>' for h in head) +
                    '</tr></thead><tbody>' + ''.join(trs) + '</tbody></table>' + foot)
            d = os.path.join(root, bs)
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(
                page(title, desc, url, alt, ld, body, style, fo, es, h1, eyebrow, byline))
            made.append(url)

        # ---- index ----
        tot = sum(len(r) for r in keep.values())
        def card(b, r):
            best = max(x[2]['similarity'] for x in r)
            origs = len({x[0] for x in r})
            meta = (f'<b>{len(r)}</b> dupes \u00b7 <b>{origs}</b> originales \u00b7 mejor <b>{best}%</b>'
                    if es else
                    f'<b>{len(r)}</b> dupes \u00b7 <b>{origs}</b> originals \u00b7 best <b>{best}%</b>')
            return (f'<a class="bcard" href="/{"marcas" if es else "brands"}/{slugify(b)}/">'
                    f'<span class="bn">{esc(b)}</span><span class="bm">{meta}</span></a>')
        chips = ('<div class="bgrid">'
                 + ''.join(card(b, r) for b, r in sorted(keep.items(), key=lambda x: -len(x[1])))
                 + '</div>')
        others = ', '.join(sorted(thin))
        url = f'{BASE}/{"marcas" if es else "brands"}/'
        alt = (f'{BASE}/brands/', f'{BASE}/marcas/')
        if es:
            title = f'Dupes por marca \u2014 {len(keep)} casas, {tot} alternativas verificadas'
            h1 = 'Dupes por marca'
            desc = (f'Explora los dupes verificados por casa: {len(keep)} marcas y {tot} alternativas, '
                    f'nada por debajo del 85% de similitud.')
            body = (f'<p>La mayor\u00eda de la gente busca por la fragancia cara. A veces se busca al rev\u00e9s: '
                    f'qu\u00e9 ha hecho realmente una casa de clones y cu\u00e1nto de ello aguanta. Estas p\u00e1ginas '
                    f'responden a eso.</p>{chips}'
                    f'<p class="bthin">Con un solo dupe verificado, y por eso sin p\u00e1gina propia: '
                    f'{esc(others)}.</p>'
                    f'<p><a href="/dupes-es/">Ver la base de datos completa \u2192</a></p>')
            byline = f'{len(keep)} casas \u00b7 {tot} alternativas verificadas \u00b7 nada por debajo del 85%'
            eyebrow = '\u2726 Por marca'; fo = footer_es
        else:
            title = f"Fragrance Dupes by Brand \u2014 {len(keep)} Houses, {tot} Verified Matches"
            h1 = 'Dupes by Brand'
            desc = (f'Browse verified fragrance dupes by the house that makes them: {len(keep)} brands, '
                    f'{tot} matches, nothing below 85% similarity.')
            body = (f'<p>Most people search the expensive fragrance. Sometimes the question runs the other '
                    f'way \u2014 what has a clone house actually made, and how much of it holds up. These pages '
                    f'answer that.</p>{chips}'
                    f'<p class="bthin">One verified dupe each, so no page of their own yet: {esc(others)}.</p>'
                    f'<p><a href="/dupes/">See the full database \u2192</a></p>')
            byline = f'{len(keep)} houses \u00b7 {tot} verified matches \u00b7 nothing below 85%'
            eyebrow = '\u2726 By brand'; fo = footer
        ld = {'@context': 'https://schema.org', '@type': 'CollectionPage',
              'name': title, 'description': desc, 'url': url}
        if es: ld['inLanguage'] = 'es'
        open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(
            page(title, desc, url, alt, ld, body, style, fo, es, h1, eyebrow, byline))
        made.append(url)
    return made, keep, thin


if __name__ == '__main__':
    DB = json.loads(subprocess.check_output(['node', 'dump.js', 'worker_live.js']).decode())
    es_slugs = json.load(open('/tmp/es_slugs.json'))
    style = open('style.html', encoding='utf-8').read()
    footer = open('footer.html', encoding='utf-8').read()
    footer_es = open('footer_es.html', encoding='utf-8').read()
    made, keep, thin = build(DB, es_slugs, style, footer, footer_es)
    print(f'{len(made)} pages written ({len(keep)} brands x 2 languages + 2 indexes)')
    for b, r in sorted(keep.items(), key=lambda x: -len(x[1])):
        print(f'   {b:24s} {len(r):3d} dupes')
    print(f'\nsingle-dupe brands listed on the index only: {len(thin)}')
