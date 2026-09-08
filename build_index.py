#!/usr/bin/env python3
"""
Directory index builder — /dupes/ and /dupes-es/   (2026-08-07)

Replaces the two-column alphabetical brand wall. That layout put 121 originals
across 50 brand blocks with no way in: a reader who wanted "Bleu de Chanel dupes"
had to scan for Chanel, and half the rows were entries with zero or one match
competing for attention with the strong ones.

Three changes, in order of how much they matter:

1. INSTANT FILTER. 121 items is exactly the size where typing beats browsing.
   Matches brand and fragrance name together, so "aventus", "creed" and "dior s"
   all work. No dependencies, no build step.

2. MATCH COUNT AS HIERARCHY. The count was a grey number at the end of a row.
   It is the site's entire proposition, so it now carries visual weight: entries
   with 3+ verified matches read strongest, single matches read normally, and
   zero-match entries are quiet but present. They stay visible deliberately —
   publishing what failed is the brand, and hiding the zeros would be the one
   change that actually damages the site.

3. TWO VIEWS. By brand (finding something specific) or by match count (browsing
   for the best-served originals). The second view did not exist before and is
   the one that answers "what's actually worth reading".

Everything is derived from VERIFIED_DB. Colours and type come from the existing
site stylesheet; this adds layout, not a new identity.
"""
import json, html, re, unicodedata
from shell import SHELL

esc = lambda s: html.escape(str(s or ''))

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.lower().replace('&', 'and').replace("'", '').replace('\u2019', '')
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s).strip('-'))

EXTRA = SHELL + """
    .dx-tools { position:sticky; top:0; z-index:20; padding:14px 0 12px;
                background:linear-gradient(180deg, rgba(12,12,14,0.98) 70%, rgba(12,12,14,0)); }
    .dx-search { position:relative; }
    .dx-search input { width:100%; padding:13px 15px 13px 42px; font-size:1rem; font-family:inherit;
        color:#f3efe6; background:rgba(255,255,255,0.045); border:1px solid rgba(201,168,76,0.28);
        border-radius:10px; outline:none; transition:border-color .15s, background .15s; }
    .dx-search input::placeholder { color:#7a756c; }
    .dx-search input:focus { border-color:#c9a84c; background:rgba(255,255,255,0.07); }
    .dx-search svg { position:absolute; left:14px; top:50%; transform:translateY(-50%);
                     width:16px; height:16px; stroke:#8a8479; fill:none; stroke-width:2; }
    .dx-bar { display:flex; flex-wrap:wrap; gap:10px; align-items:center;
              justify-content:space-between; margin-top:11px; }
    .dx-views { display:flex; gap:2px; background:rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:2px; }
    .dx-views button { font:inherit; font-size:0.79rem; letter-spacing:0.03em; padding:6px 13px;
        border:0; border-radius:6px; background:transparent; color:#948d80; cursor:pointer; }
    .dx-views button[aria-pressed="true"] { background:rgba(201,168,76,0.16); color:#e8c97a; }
    .dx-views button:focus-visible { outline:2px solid #c9a84c; outline-offset:1px; }
    .dx-count { font-size:0.79rem; color:#7a756c; letter-spacing:0.03em; }

    .dx-cols { margin-top:22px; }
    @media (min-width:880px) { .dx-cols { columns:2; column-gap:44px; } }
    .dx-group { margin:0 0 26px; break-inside:avoid; -webkit-column-break-inside:avoid; }
    .dx-group > h2 { font-size:0.8rem; letter-spacing:0.11em; text-transform:uppercase;
        color:#c9a84c; margin:0 0 9px; padding-bottom:7px;
        border-bottom:1px solid rgba(201,168,76,0.18); }
    .dx-list { list-style:none; padding:0; margin:0; }
    .dx-row { display:flex; align-items:baseline; gap:12px; padding:7px 0;
              border-bottom:1px solid rgba(255,255,255,0.045); }
    .dx-row:last-child { border-bottom:none; }
    .dx-row a { text-decoration:none; color:#e6e1d6; flex:1; font-size:0.97rem; line-height:1.35; }
    .dx-row a:hover, .dx-row a:focus-visible { color:#e8c97a; }
    .dx-row .brand { color:#8a8479; font-size:0.84rem; }
    .dx-n { flex-shrink:0; min-width:2.4rem; text-align:right; font-size:0.83rem;
            font-variant-numeric:tabular-nums; letter-spacing:0.02em; }
    .dx-n b { font-size:1rem; font-weight:700; }
    .dx-n.t3 { color:#4ade80; }
    .dx-n.t2 { color:#c9a84c; }
    .dx-n.t1 { color:#9c968a; }
    .dx-n.t0 { color:#615c54; }
    .dx-empty { padding:34px 4px; color:#8a8479; font-size:0.95rem; }
    .dx-empty b { color:#e6e1d6; }
    [hidden] { display:none !important; }
    @media (max-width:640px) {
      .dx-row { gap:9px; } .dx-row a { font-size:0.93rem; }
      .dx-bar { gap:8px; }
    }
"""

SCRIPT = """
(function () {
  var q = document.getElementById('dxq'),
      tally = document.getElementById('dxTally'),
      rows = Array.prototype.slice.call(document.querySelectorAll('.dx-row')),
      groups = Array.prototype.slice.call(document.querySelectorAll('.dx-group')),
      empty = document.getElementById('dxEmpty'),
      views = Array.prototype.slice.call(document.querySelectorAll('.dx-views button'));

  function fold(s) {
    return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
  }
  rows.forEach(function (r) { r.dataset.k = fold(r.textContent); });

  function apply() {
    var term = fold(q.value.trim()), shown = 0;
    rows.forEach(function (r) {
      var hit = !term || r.dataset.k.indexOf(term) > -1;
      r.hidden = !hit;
      if (hit) shown++;
    });
    groups.forEach(function (g) {
      if (g.hidden && g.dataset.view !== current) return;
      var any = g.querySelector('.dx-row:not([hidden])');
      g.hidden = g.dataset.view !== current || !any;
    });
    empty.hidden = shown > 0;
    tally.textContent = term ? shown + TALLY_MATCH : TALLY_ALL;
  }

  var current = 'brand';
  function setView(v) {
    current = v;
    views.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.view === v)); });
    apply();
  }
  views.forEach(function (b) {
    b.addEventListener('click', function () { setView(b.dataset.view); });
  });
  q.addEventListener('input', apply);
  q.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { q.value = ''; apply(); }
  });
  setView('brand');
})();
"""

def tier(n):
    return 't3' if n >= 3 else 't2' if n == 2 else 't1' if n == 1 else 't0'

def build_index(DB, SLUGS, lang, style, footer, nav, base):
    es = lang == 'es'
    keys = sorted(SLUGS, key=lambda k: (DB[k]['original']['brand'].lower(),
                                        DB[k]['original']['name'].lower()))
    total = sum(len(DB[k].get('dupes') or []) for k in keys)
    brands = {}
    for k in keys:
        brands.setdefault(DB[k]['original']['brand'], []).append(k)
    path = '/dupes-es/' if es else '/dupes/'

    T = dict(
        one=('alternativa' if es else 'match'),
        many=('alternativas' if es else 'matches'),
        ph=('Busca una marca o fragancia\u2026' if es else 'Search a brand or fragrance\u2026'),
        by_brand=('Por marca' if es else 'By brand'),
        by_count=('Por n\u00famero de dupes' if es else 'By matches'),
        none=('Sin dupes verificados' if es else 'No matches'),
        nores=('Nada coincide con esa b\u00fasqueda.' if es else 'Nothing matches that search.'),
        nores2=('Prueba con el nombre de la marca, o con menos letras.'
                if es else 'Try the brand name, or fewer letters.'),
    )
    tally_all = f"{len(keys)} " + ('originales' if es else 'originals')
    tally_match = ' ' + ('de ' + str(len(keys)) if es else 'of ' + str(len(keys)))

    def row(k):
        o = DB[k]['original']; n = len(DB[k].get('dupes') or [])
        label = T['none'] if n == 0 else f"{n} {T['one'] if n == 1 else T['many']}"
        num = '\u2014' if n == 0 else f'<b>{n}</b>'
        return (f'<li class="dx-row"><a href="{path}{SLUGS[k]}">{esc(o["name"])}'
                f' <span class="brand">{esc(o["brand"])}</span></a>'
                f'<span class="dx-n {tier(n)}" title="{esc(label)}">{num}</span></li>')

    by_brand = ''.join(
        f'<section class="dx-group" data-view="brand"><h2>{esc(b)}</h2>'
        f'<ul class="dx-list">{"".join(row(k) for k in brands[b])}</ul></section>'
        for b in sorted(brands, key=lambda x: x.lower()))

    buckets = [(3, None), (2, 2), (1, 1), (0, 0)]
    by_count = ''
    for lo, exact in buckets:
        sel = [k for k in keys if (len(DB[k].get('dupes') or []) >= 3 if exact is None
                                   else len(DB[k].get('dupes') or []) == exact)]
        if not sel: continue
        sel.sort(key=lambda k: (-len(DB[k].get('dupes') or []),
                                DB[k]['original']['brand'].lower()))
        if exact is None:
            h = ('3 o m\u00e1s dupes' if es else '3 or more matches')
        elif exact == 0:
            h = ('Sin dupes verificados' if es else 'No verified matches')
        else:
            h = (f'{exact} ' + (T['one'] if exact == 1 else T['many']))
        by_count += (f'<section class="dx-group" data-view="count" hidden><h2>{esc(h)}</h2>'
                     f'<ul class="dx-list">{"".join(row(k) for k in sel)}</ul></section>')

    if es:
        title = f"Todos los dupes verificados \u2014 {len(keys)} originales, {total} alternativas verificadas"
        desc = (f"Explora los {total} dupes de fragancias verificados de nuestra base de datos. "
                f"{len(keys)} originales de {len(brands)} marcas, nada por debajo del 85% de similitud.")
        h1 = "Dupes verificados en espa\u00f1ol"
        eyebrow = "\u2726 La base de datos"
        byline = (f"{len(keys)} originales \u00b7 {total} alternativas verificadas \u00b7 "
                  f"{len(brands)} marcas \u00b7 nada por debajo del 85%")
        intro = ("Cada fragancia se contrast\u00f3 con Fragrantica y con las fuentes oficiales de cada marca, "
                 "y despu\u00e9s se sopes\u00f3 lo que reportan quienes tienen ambas. "
                 "<strong>No publicamos nada por debajo del 85% de similitud.</strong> "
                 "El n\u00famero es cu\u00e1ntos dupes verificados encontramos; un gui\u00f3n significa que buscamos y no calific\u00f3 ninguno.")
    else:
        title = f"Every Fragrance Dupe We've Verified \u2014 {len(keys)} Originals, {total} Matches"
        desc = (f"Browse {total} verified fragrance dupes across {len(keys)} originals and "
                f"{len(brands)} brands. Nothing published below 85% similarity.")
        h1 = "Every Dupe We've Verified"
        eyebrow = "\u2726 The Database"
        byline = (f"{len(keys)} originals \u00b7 {total} verified matches \u00b7 "
                  f"{len(brands)} brands \u00b7 nothing below 85%")
        intro = ("Every fragrance here was researched against Fragrantica and brand-official sources, "
                 "then weighted by what people who own both actually report. "
                 "<strong>We don't publish anything under 85% similarity.</strong> "
                 "The number is how many verified dupes we found; a dash means we looked and nothing qualified.")

    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title,
          "description": desc, "url": base + path}
    if es: ld["inLanguage"] = "es"

    script = (SCRIPT.replace('TALLY_MATCH', json.dumps(tally_match))
                    .replace('TALLY_ALL', json.dumps(tally_all)))

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | Decoded Scents</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{base}{path}">
<link rel="alternate" hreflang="en" href="{base}/dupes/">
<link rel="alternate" hreflang="es" href="{base}/dupes-es/">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{base}{path}">
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
{nav}
<header class="article-hero">
  <div class="container">
    <div class="hero-meta">{eyebrow}</div>
    <h1>{esc(h1)}</h1>
    <div class="hero-byline">{byline}</div>
  </div>
</header>
<main class="container"><article>
<p>{intro}</p>
<p><a href="{'/dupes/' if es else '/dupes-es/'}">{'View in English \u2192' if es else 'Ver en espa\u00f1ol \u2192'}</a></p>

<div class="dx-tools">
  <div class="dx-search">
    <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
    <label for="dxq" class="visually-hidden" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">{esc(T['ph'])}</label>
    <input id="dxq" type="search" autocomplete="off" placeholder="{esc(T['ph'])}">
  </div>
  <div class="dx-bar">
    <div class="dx-views">
      <button type="button" data-view="brand" aria-pressed="true">{esc(T['by_brand'])}</button>
      <button type="button" data-view="count" aria-pressed="false">{esc(T['by_count'])}</button>
    </div>
    <span class="dx-count" id="dxTally">{esc(tally_all)}</span>
  </div>
</div>

<div class="dx-cols">{by_brand}</div>
<div class="dx-cols">{by_count}</div>
<p class="dx-empty" id="dxEmpty" hidden><b>{esc(T['nores'])}</b><br>{esc(T['nores2'])}</p>
</article></main>
{footer}
<script>{script}</script>
</body>
</html>"""
