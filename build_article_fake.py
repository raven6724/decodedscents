#!/usr/bin/env python3
"""
Article: "Is a Dupe a Fake?"   ->  /Articles/is-a-dupe-a-fake/
                                   /Articles/es-un-dupe-una-falsificacion/   (2026-08-14)

WHY THIS ARTICLE. Search Console shows people arriving on queries like "are afnan
perfumes dupes" and "are there fake rayhaan perfumes". Those are two different
questions that get conflated constantly -- is the HOUSE a knockoff, versus are
there counterfeits OF the house -- and nobody separates them.

Every authenticity guide currently ranking is written by a retailer: OLVIO, Hala
Perfumes, The Perfume Specialist all conclude "buy from a trustworthy seller",
meaning themselves. We sell nothing, which makes this the one piece of content on
the site a competitor structurally cannot write.

NOT A NEW ARTICLE TYPE, EXACTLY. ARTICLE_PROTOCOLS lists two: Brand Deep-Dive and
Roundup/Deals. This is an explainer, which the protocols anticipate ("If a third
type emerges, this section gets revised"). Section 1.3 should be added.

Follows the section 2 direction: the answer sits above the fold, prose stays tight,
and the comparison table carries the load.
"""
import json, os, html, subprocess
from shell import SHELL

BASE = 'https://decodedscents.com'
EN_SLUG = 'is-a-dupe-a-fake'
ES_SLUG = 'es-un-dupe-una-falsificacion'
OUT = '/home/claude/Articles'
esc = lambda s: html.escape(str(s or ''))

EXTRA = SHELL + """
    .lede { font-size:1.12rem; line-height:1.6; color:var(--text,#e8e4dc); margin-bottom:8px; }
    .answer { border-left:3px solid var(--gold,#c9a84c); background:rgba(201,168,76,.06);
              padding:18px 20px; border-radius:0 10px 10px 0; margin:24px 0 30px; }
    .answer p { color:var(--text,#e8e4dc); margin:0 0 10px; }
    .answer p:last-child { margin:0; }
    .vs { width:100%; border-collapse:collapse; margin:24px 0 8px; font-size:.94rem; }
    .vs th { text-align:left; padding:11px 12px; border-bottom:2px solid rgba(201,168,76,.4);
             color:var(--gold,#c9a84c); font-size:.72rem; letter-spacing:.07em; text-transform:uppercase; }
    .vs td { padding:12px; border-bottom:1px solid rgba(255,255,255,.06); vertical-align:top; }
    .vs tr:last-child td { border-bottom:none; }
    .vs td:first-child { color:var(--text-dim,#7a756c); font-size:.82rem; letter-spacing:.03em;
                         text-transform:uppercase; white-space:nowrap; width:1%; }
    .ok { color:#4ade80; } .no { color:#f87171; }
    .flags { list-style:none; padding:0; margin:16px 0 24px; }
    .flags li { padding:11px 0 11px 30px; position:relative; border-bottom:1px solid rgba(255,255,255,.05);
                color:var(--text-muted,#a9a396); line-height:1.6; }
    .flags li:last-child { border-bottom:none; }
    .flags li:before { content:"\\2715"; position:absolute; left:4px; top:11px; color:#f87171; font-size:.9rem; }
    .flags b { color:var(--text,#e8e4dc); }
    .note { font-size:.88rem; color:var(--text-dim,#7a756c); border-top:1px solid var(--border,rgba(255,255,255,.07));
            margin-top:34px; padding-top:16px; line-height:1.6; }
    @media(max-width:640px){ .vs td:first-child{white-space:normal} }
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

EN_BODY = """
<p class="lede">Two questions get asked constantly and they are not the same question:
<em>is Lattafa a fake brand?</em> and <em>are there fake Lattafas?</em> The first
misunderstands what a clone house is. The second is a real problem worth protecting
yourself from.</p>

<div class="answer">
<p><strong>Short answer.</strong> Lattafa, Armaf, Afnan, Rayhaan, Maison Alhambra and
the rest are real, legal companies making their own fragrances. They are not
counterfeits. A counterfeit is something else entirely: a bottle pretending to be a
Lattafa that Lattafa did not make.</p>
<p>And yes, those exist. The clone houses are now popular enough to be counterfeited
themselves.</p>
</div>

<h2>A dupe and a counterfeit are opposites</h2>

<p>A dupe is a fragrance built to smell like an expensive one, sold openly under its
own name. Scent itself cannot be copyrighted, which is why this is legal and why the
industry has existed for decades. Some houses are explicit about it \u2014 Dossier names
the fragrance each of its scents is inspired by, right on the product page.</p>

<p>A counterfeit lies about what it is. It carries someone else's name and logo to
make you think you are buying their product. That is fraud, and it is illegal
everywhere.</p>

<table class="vs">
<thead><tr><th></th><th>A dupe</th><th>A counterfeit</th></tr></thead>
<tbody>
<tr><td>Whose name is on it</td><td class="ok">Its own</td><td class="no">Someone else's</td></tr>
<tr><td>Legal</td><td class="ok">Yes</td><td class="no">No</td></tr>
<tr><td>Tells you what it is</td><td class="ok">Yes \u2014 often names its inspiration</td><td class="no">No \u2014 the lie is the point</td></tr>
<tr><td>Who made it</td><td class="ok">The house on the bottle</td><td class="no">Unknown</td></tr>
<tr><td>What is in it</td><td class="ok">Regulated, disclosed</td><td class="no">Unknown and untested</td></tr>
<tr><td>Example</td><td class="ok">Lattafa Khamrah</td><td class="no">A fake bottle of Lattafa Khamrah</td></tr>
</tbody>
</table>

<h2>The clone houses are being counterfeited</h2>

<p>This is the part most people miss. Lattafa runs its own batch-code checker,
because enough fake Lattafa is circulating that the company needed one. Enter a code
from a counterfeit and the response is blunt: the system does not recognise it.</p>

<p>That tells you something useful. A brand does not build anti-counterfeiting
infrastructure against itself. Lattafa fighting fake Lattafa is the clearest evidence
available that Lattafa is a real company with something to protect.</p>

<p>Counterfeits also carry a risk a dupe does not. A legitimate clone house is subject
to the same fragrance regulations as anyone else. A counterfeiter is subject to
nothing, and what is in the bottle is genuinely unknown.</p>

<h2>How to tell you are looking at a fake</h2>

<p>Every guide to this ends the same way: buy from a trusted seller, meaning the shop
that wrote the guide. We sell nothing, so here is the version without the pitch.</p>

<ul class="flags">
<li><b>The batch code does not match.</b> The code on the base of the bottle should
match the one on the box. Missing, smudged, or mismatched is the single strongest
signal. Lattafa will check a code for you directly.</li>
<li><b>The price is impossible.</b> Khamrah is not $12. These houses are already
cheap \u2014 that is the entire proposition \u2014 so a steep discount on something already
inexpensive has nowhere good to come from.</li>
<li><b>The printing is soft.</b> Blurred text, thin cardboard, a misspelling, a logo
slightly off. Counterfeiters copy a photo, not a press file.</li>
<li><b>The cap and sprayer feel wrong.</b> A loose cap, a sputtering atomiser, an
uneven mist. Cheap to notice, expensive to fake.</li>
<li><b>The seller cannot say where it came from.</b> A marketplace listing with no
named supplier and no returns is the common thread in almost every counterfeit story.</li>
</ul>

<h2>Where this site fits</h2>

<p>We do not test for counterfeits and we would not pretend to. What we do is a
narrower job: deciding whether a dupe actually smells like the thing it claims to,
and publishing the ones that do not.</p>

<p>That standard has a number attached. Nothing below <strong>85% similarity</strong>
goes on this site. Twenty-four of our entries sit exactly at that line and say so on
the page. Eight originals have no dupe at all, because we looked and nothing
qualified \u2014 those pages stay empty rather than get filled.</p>

<p>In August 2026 we audited every note pyramid in the database and removed fourteen
records whose listed notes had been shaped to fit the fragrance they were filed under
rather than what was actually in the bottle. The database got smaller. That is the
trade.</p>

<p class="note">The honest summary: a dupe is a legal product being upfront about
what it is, a counterfeit is a lie, and the fact that clone houses are now worth
counterfeiting is a sign of how far they have come. Buy the dupe. Check the batch
code.</p>
"""

ES_BODY = """
<p class="lede">Hay dos preguntas que se hacen todo el tiempo y no son la misma:
<em>\u00bfLattafa es una marca falsa?</em> y <em>\u00bfexisten Lattafas falsos?</em> La primera
parte de un malentendido sobre qu\u00e9 es una casa de clones. La segunda es un problema
real del que conviene protegerse.</p>

<div class="answer">
<p><strong>Respuesta corta.</strong> Lattafa, Armaf, Afnan, Rayhaan, Maison Alhambra y
las dem\u00e1s son empresas reales y legales que fabrican sus propias fragancias. No son
falsificaciones. Una falsificaci\u00f3n es otra cosa: un frasco que finge ser un Lattafa
sin que Lattafa lo haya hecho.</p>
<p>Y s\u00ed, existen. Las casas de clones ya son lo bastante populares como para que las
falsifiquen a ellas.</p>
</div>

<h2>Un dupe y una falsificaci\u00f3n son lo contrario</h2>

<p>Un dupe es una fragancia hecha para oler como una cara, y se vende abiertamente con
su propio nombre. Un aroma no se puede registrar como propiedad intelectual, por eso
esto es legal y por eso el negocio lleva d\u00e9cadas existiendo. Algunas casas lo dicen
sin rodeos: Dossier nombra en su propia ficha de producto la fragancia en la que se
inspira cada uno de sus perfumes.</p>

<p>Una falsificaci\u00f3n miente sobre lo que es. Lleva el nombre y el logo de otro para
que creas que compras su producto. Eso es fraude, y es ilegal en todas partes.</p>

<table class="vs">
<thead><tr><th></th><th>Un dupe</th><th>Una falsificaci\u00f3n</th></tr></thead>
<tbody>
<tr><td>De qui\u00e9n es el nombre</td><td class="ok">Suyo propio</td><td class="no">De otra marca</td></tr>
<tr><td>Legal</td><td class="ok">S\u00ed</td><td class="no">No</td></tr>
<tr><td>Dice lo que es</td><td class="ok">S\u00ed, y a menudo nombra su inspiraci\u00f3n</td><td class="no">No, la mentira es el punto</td></tr>
<tr><td>Qui\u00e9n lo fabric\u00f3</td><td class="ok">La casa que aparece en el frasco</td><td class="no">Se desconoce</td></tr>
<tr><td>Qu\u00e9 lleva dentro</td><td class="ok">Regulado y declarado</td><td class="no">Desconocido y sin analizar</td></tr>
<tr><td>Ejemplo</td><td class="ok">Lattafa Khamrah</td><td class="no">Un frasco falso de Lattafa Khamrah</td></tr>
</tbody>
</table>

<h2>A las casas de clones tambi\u00e9n las falsifican</h2>

<p>Esta es la parte que casi nadie tiene clara. Lattafa mantiene su propio verificador
de c\u00f3digos de lote, porque circula suficiente Lattafa falso como para que a la empresa
le hiciera falta uno. Si introduces el c\u00f3digo de una falsificaci\u00f3n, la respuesta es
tajante: el sistema no lo reconoce.</p>

<p>Eso dice algo \u00fatil. Una marca no monta un sistema antifalsificaci\u00f3n contra s\u00ed
misma. Que Lattafa combata los Lattafa falsos es la mejor prueba disponible de que
Lattafa es una empresa real con algo que proteger.</p>

<p>Adem\u00e1s, una falsificaci\u00f3n implica un riesgo que un dupe no tiene. Una casa de
clones legal cumple la misma normativa de perfumer\u00eda que cualquier otra. Un
falsificador no cumple ninguna, y lo que lleva el frasco es sencillamente
desconocido.</p>

<h2>C\u00f3mo saber que tienes delante una falsificaci\u00f3n</h2>

<p>Todas las gu\u00edas sobre esto terminan igual: compra en una tienda de confianza, es
decir, en la tienda que escribi\u00f3 la gu\u00eda. Nosotros no vendemos nada, as\u00ed que aqu\u00ed va
la versi\u00f3n sin el anuncio.</p>

<ul class="flags">
<li><b>El c\u00f3digo de lote no coincide.</b> El c\u00f3digo de la base del frasco debe
coincidir con el de la caja. Que falte, est\u00e9 borroso o no cuadre es la se\u00f1al m\u00e1s
fiable de todas. Lattafa te comprueba un c\u00f3digo directamente.</li>
<li><b>El precio es imposible.</b> Khamrah no cuesta 12 d\u00f3lares. Estas casas ya son
baratas \u2014esa es toda su propuesta\u2014 as\u00ed que un descuento enorme sobre algo que ya vale
poco no puede venir de ning\u00fan sitio bueno.</li>
<li><b>La impresi\u00f3n se ve floja.</b> Texto borroso, cart\u00f3n fino, una falta de
ortograf\u00eda, un logo ligeramente desplazado. Los falsificadores copian una foto, no un
archivo de imprenta.</li>
<li><b>La tapa y el vaporizador se sienten mal.</b> Una tapa suelta, un atomizador que
escupe, una nube irregular. Barato de notar, caro de imitar.</li>
<li><b>El vendedor no sabe decir de d\u00f3nde sali\u00f3.</b> Un anuncio de marketplace sin
proveedor identificado y sin devoluciones es el hilo com\u00fan de casi todas las historias
de falsificaciones.</li>
</ul>

<h2>D\u00f3nde encaja este sitio</h2>

<p>Nosotros no detectamos falsificaciones y no vamos a fingir que s\u00ed. Lo que hacemos
es m\u00e1s estrecho: decidir si un dupe huele de verdad a lo que dice, y publicar tambi\u00e9n
los que no.</p>

<p>Ese est\u00e1ndar tiene un n\u00famero. Nada por debajo del <strong>85% de similitud</strong>
entra en este sitio. Veinticuatro de nuestras entradas se quedan justo en esa l\u00ednea y
lo dicen en su p\u00e1gina. Ocho originales no tienen ning\u00fan dupe, porque buscamos y no
calific\u00f3 ninguno: esas p\u00e1ginas se quedan vac\u00edas en lugar de rellenarse.</p>

<p>En agosto de 2026 auditamos todas las pir\u00e1mides olfativas de la base de datos y
eliminamos catorce registros cuyas notas hab\u00edan sido acomodadas para encajar con la
fragancia bajo la que estaban archivadas, en vez de reflejar lo que llevaba el frasco.
La base de datos se hizo m\u00e1s peque\u00f1a. Ese es el intercambio que aceptamos.</p>

<p class="note">El resumen honesto: un dupe es un producto legal que dice claramente
lo que es, una falsificaci\u00f3n es una mentira, y que ya valga la pena falsificar a las
casas de clones dice mucho de lo lejos que han llegado. Compra el dupe. Comprueba el
c\u00f3digo de lote.</p>
"""

def build(es):
    slug = ES_SLUG if es else EN_SLUG
    url = f'{BASE}/Articles/{slug}'
    if es:
        title = '\u00bfUn dupe es una falsificaci\u00f3n? La diferencia que casi nadie explica'
        desc = ('Lattafa, Armaf y Rayhaan son marcas reales y legales, no falsificaciones. '
                'Pero s\u00ed existen falsificaciones de ellas. Explicamos la diferencia y c\u00f3mo detectarlas, '
                'sin venderte nada.')
        h1 = '\u00bfUn dupe es una falsificaci\u00f3n?'
        eyebrow = '\u2726 Explicaci\u00f3n'
        byline = 'La diferencia entre una casa de clones y una falsificaci\u00f3n \u00b7 lectura de 5 minutos'
        body = ES_BODY
        foot = open('/home/claude/work/footer_es.html', encoding='utf-8').read()
    else:
        title = 'Is a Dupe a Fake? The Difference Almost Nobody Explains'
        desc = ('Lattafa, Armaf and Rayhaan are real, legal brands \u2014 not counterfeits. '
                'But counterfeits of them do exist. Here is the difference, and how to spot one, '
                'from a site that sells nothing.')
        h1 = 'Is a Dupe a Fake?'
        eyebrow = '\u2726 Explainer'
        byline = 'The difference between a clone house and a counterfeit \u00b7 5 minute read'
        body = EN_BODY
        foot = open('/home/claude/work/footer.html', encoding='utf-8').read()

    ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': title,
          'description': desc, 'url': url, 'datePublished': '2026-08-14',
          'author': {'@type': 'Organization', 'name': 'Decoded Scents', 'url': BASE},
          'publisher': {'@type': 'Organization', 'name': 'Decoded Scents', 'url': BASE}}
    if es: ld['inLanguage'] = 'es'

    style = open('/home/claude/work/style.html', encoding='utf-8').read()
    return f"""<!DOCTYPE html>
<html lang="{'es' if es else 'en'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | Decoded Scents</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{BASE}/Articles/{EN_SLUG}">
<link rel="alternate" hreflang="es" href="{BASE}/Articles/{ES_SLUG}">
<meta property="og:type" content="article">
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
  <div class="hero-meta">{eyebrow}</div>
  <h1>{esc(h1)}</h1>
  <div class="hero-byline">{byline}</div>
</div></header>
<main class="container"><article>
{body}
</article></main>
{foot}
</body>
</html>"""

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for es, slug in ((False, EN_SLUG), (True, ES_SLUG)):
        p = os.path.join(OUT, slug + '.html')
        open(p, 'w', encoding='utf-8').write(build(es))
        print('wrote', p)
    print('\nremaining per ARTICLE_PROTOCOLS section 3:')
    print('  [ ] index.html article card (EN + ES)')
    print('  [ ] OG image 1200x630, one per language')
    print('  [ ] sitemap entry')
    print('  [ ] native Spanish proofread (section 5.3)')
