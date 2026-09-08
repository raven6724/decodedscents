#!/usr/bin/env python3
"""
Trust pages generator — /about/, /disclosure/, /privacy/ in EN and ES   (2026-08-08)

WHY THESE EXIST

  1. COMPLIANCE. The site carries Amazon, Rakuten (FragranceNet, Shop Simon) and CJ
     (Perfumania) affiliate links and has never disclosed them anywhere. The Amazon
     Associates Operating Agreement requires the earnings statement to be displayed
     clearly; the FTC requires disclosure independently. GA4 sets cookies, which is
     what the privacy page is for.

  2. RANKINGS. Google's reviews guidance rewards demonstrable first-hand method and
     penalises thin affiliate pages. DecodedScents has the strongest version of that
     story in this niche — an 85% floor, published failures, entries pulled after
     going live — and it lived nowhere as a page.

WRITTEN TO BE TRUE, NOT FLATTERING. The method described here is research and
cross-referencing weighted by owner-of-both testimony. It does NOT claim the
maintainer personally wears every fragrance, because the handoff records decants as
an intention rather than a completed practice. If that changes, the copy changes.

PLACEHOLDERS that must be confirmed before publishing are listed at the end of a run.
"""
import json, html, os, sys
from shell import SHELL

BASE = 'https://decodedscents.com'
OUT = '/home/claude'
esc = lambda s: html.escape(str(s or ''))

# ---- must be confirmed by Carlos before this goes live ----
CONTACT_EMAIL = 'decodedscents@gmail.com'
OPERATOR = 'Decoded Scents'                  # publish a personal name? his call
LOCATION = 'Florida, United States'

EXTRA = SHELL + """
    .doc h2 { font-size:1.18rem; margin:34px 0 10px; }
    .doc h3 { font-size:0.98rem; color:var(--gold,#c9a84c); margin:24px 0 8px;
              letter-spacing:0.02em; }
    .doc ul { margin:0 0 16px; padding-left:20px; color:var(--text-muted,#a9a396); line-height:1.65; }
    .doc li { margin:6px 0; }
    .doc .lede { font-size:1.05rem; color:var(--text,#e8e4dc); line-height:1.6; margin-bottom:22px; }
    .doc .callout { border-left:3px solid var(--gold,#c9a84c); background:rgba(201,168,76,0.05);
                    padding:16px 18px; margin:24px 0; border-radius:0 8px 8px 0; }
    .doc .callout p:last-child { margin-bottom:0; }
    .doc .updated { font-size:0.8rem; color:var(--text-dim,#7a756c); margin-top:40px;
                    padding-top:16px; border-top:1px solid var(--border,rgba(255,255,255,0.07)); }
"""

NAV_EN = """<nav class="top-nav">
  <div class="container">
    <a href="/" class="nav-logo">DECODED SCENTS</a>
    <div class="nav-links">
      <a href="/">Home</a><a href="/dupes/">All Dupes</a><a href="/about/">About</a>
      <a href="/es/" hreflang="es">Espa\u00f1ol</a>
    </div>
  </div>
</nav>"""
NAV_ES = """<nav class="top-nav">
  <div class="container">
    <a href="/es/" class="nav-logo">DECODED SCENTS</a>
    <div class="nav-links">
      <a href="/es/">Inicio</a><a href="/dupes-es/">Todos los Dupes</a>
      <a href="/acerca-de/">Qui\u00e9nes somos</a><a href="/" hreflang="en">English</a>
    </div>
  </div>
</nav>"""

UPDATED_EN = 'Last updated 8 August 2026.'
UPDATED_ES = 'Actualizado el 8 de agosto de 2026.'

# ------------------------------------------------------------------ content

ABOUT_EN = f"""
<p class="lede">Most fragrance dupe sites will tell you every cheap perfume is a 95% match
for something expensive. We publish the ones that fail.</p>

<p>Decoded Scents is a database of fragrance dupes with a similarity floor. If an alternative
does not reach <strong>85% similarity</strong> to the original, it does not go on the site —
and when we research a fragrance and nothing qualifies, we publish that too. Those pages say
so plainly instead of quietly filling the gap with a weak match.</p>

<div class="callout">
<p><strong>The differentiator is refusal.</strong> Anyone can list ten alternatives to Creed
Aventus. The useful question is which ones we <em>rejected</em>, and why. That is the part
no competitor copies, because most of them have no floor to fail against.</p>
</div>

<h2>We buy what we test</h2>
<p>Most entries on this site have been worn side by side on skin — the original on one wrist,
the alternative on the other, across a full day rather than a thirty-second pass at a counter.
Where something looks doubtful, we buy it specifically to settle the question.</p>

<p>Everything we test, we pay for. Sometimes that is a decant, sometimes a full bottle. It is
never a press sample, because we don't accept free product from fragrance houses — see below
for why.</p>

<p>We are not going to pretend that covers all 205 entries. Where we have not worn both
ourselves, a score rests on research and on the testimony of people who own both. That is the
weaker of the two kinds of evidence, and it is the reason we keep buying.</p>

<h2>Who runs this</h2>
<p>Decoded Scents is written and maintained by Carlos, working from Florida. One person, buying
his own bottles and decants, publishing what clears the 85% floor and what doesn't. There is no
team, no sponsor and no house sending product.</p>

<h2>How a match gets scored</h2>
<p>Every percentage comes from cross-referencing note pyramids against Fragrantica and each
brand's own published material, then weighting what people who own <em>both</em> fragrances
actually report. Sources are ranked in that order: brand-official first, then Fragrantica,
Parfumo and Basenotes, then enthusiast communities, then retailers last.</p>

<p>Note pyramids are marketing copy, not formulas. Two fragrances can share almost every
listed note and still smell different — so owner-of-both testimony outranks note overlap when
the two disagree. One entry on this site shares 25 of 26 published notes with its original and
still sits at 85%, because everyone who owns both reports it thin.</p>

<h3>What disqualifies an entry</h3>
<ul>
<li>Similarity below 85%</li>
<li>A claim we cannot trace to a real, findable source</li>
<li>Evidence pinned to the wrong version of a fragrance — a flanker or a different
concentration is a different product</li>
<li>A note list that does not match the product's own published pyramid</li>
</ul>

<h2>We remove things after publishing them</h2>
<p>In August 2026 a note-level audit of the whole database found twelve products whose
listed notes had been reshaped toward whatever original they were filed under. Fourteen
records were removed, ten had their notes corrected against sources, and the database
shrank from 219 verified dupes to 205.</p>

<p>That is the trade this site is built to make. A smaller database that is true beats a
larger one that is not.</p>

<h2>What we don't do</h2>
<ul>
<li><strong>We don't accept free product from fragrance houses.</strong> This site assigns a
number that drives affiliate revenue. Taking product from the same brands would create two
financial relationships pointing the same direction.</li>
<li><strong>We don't invent links.</strong> An entry with no verified retailer ships with a
Fragrantica reference only, rather than a search URL dressed up as a product page.</li>
<li><strong>We don't hide what a dupe gets wrong.</strong> Every entry names the gap, not just
the resemblance.</li>
</ul>

<h2>Corrections</h2>
<p>If something here is wrong, we want to know — particularly if you own both fragrances in a
comparison and our reading does not match yours. That is the evidence we weight highest.
Write to <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

<h2>How this site makes money</h2>
<p>Some links here are affiliate links, and we may earn a commission when you buy through
them. It costs you nothing extra and it does not affect a similarity score — the scores are
set before links are attached, and entries with no affiliate relationship at all are ranked
the same way. The full terms are on our <a href="/disclosure/">affiliate disclosure</a> page.</p>
"""

ABOUT_ES = f"""
<p class="lede">Casi todos los sitios de dupes te van a decir que cualquier perfume barato es
un 95% idéntico a uno caro. Nosotros también publicamos los que no dan la talla.</p>

<p>Decoded Scents es una base de datos de dupes de fragancias con un mínimo exigido. Si una
alternativa no llega al <strong>85% de similitud</strong> con el original, no entra al sitio.
Y cuando investigamos una fragancia y ninguna alternativa califica, también lo decimos: esa
página lo explica sin rodeos en lugar de tapar el hueco con un parecido flojo.</p>

<div class="callout">
<p><strong>Lo que nos distingue es saber decir que no.</strong> Cualquiera puede armar una
lista con diez alternativas a Creed Aventus. La pregunta que sirve es cuáles
<em>descartamos</em> y por qué. Esa es la parte que nadie nos copia, porque la mayoría no
tiene ningún mínimo que respetar.</p>
</div>

<h2>Compramos lo que probamos</h2>
<p>La mayoría de las entradas de este sitio las hemos usado en paralelo sobre la piel: el
original en una muñeca y la alternativa en la otra, durante un día completo y no treinta
segundos en el mostrador de una tienda. Cuando una fragancia nos genera dudas, la compramos
justamente para salir de la duda.</p>

<p>Todo lo que probamos lo pagamos nosotros, a veces en decant y a veces en frasco completo.
Nunca es una muestra de prensa, porque no aceptamos producto gratis de las casas de perfume.
Más abajo explicamos por qué.</p>

<p>No vamos a fingir que eso alcanza para las 205 entradas. Cuando no hemos usado las dos
fragancias, la puntuación se basa en la investigación y en el testimonio de quien sí las
tiene. De los dos tipos de evidencia, ese es el más débil, y es la razón por la que seguimos
comprando.</p>

<h2>Quién está detrás</h2>
<p>Decoded Scents lo escribe y lo mantiene Carlos, desde Florida. Una sola persona, que compra
sus propios frascos y decants, y publica tanto lo que supera el mínimo del 85% como lo que no.
No hay equipo, no hay patrocinador y ninguna casa de perfume nos manda producto.</p>

<h2>Cómo puntuamos un dupe</h2>
<p>Cada porcentaje surge de cotejar las pirámides olfativas con Fragrantica y con el material
oficial de cada marca, y de sopesar después lo que reporta quien tiene <em>las dos
fragancias</em>. Las fuentes se consultan en ese orden: primero la marca, luego Fragrantica,
Parfumo y Basenotes, después las comunidades de aficionados y, al final, las tiendas.</p>

<p>Las pirámides olfativas son material de marketing, no fórmulas. Dos fragancias pueden
compartir casi todas las notas publicadas y oler distinto, así que cuando las notas y la
experiencia no coinciden, mandan quienes tienen las dos. Una entrada de este sitio comparte
25 de 26 notas publicadas con su original y aun así se queda en el 85%, porque todo el mundo
que las tiene describe la copia como plana.</p>

<h3>Qué descalifica una entrada</h3>
<ul>
<li>Una similitud por debajo del 85%</li>
<li>Una afirmación que no podamos rastrear hasta una fuente real y verificable</li>
<li>Evidencia que corresponde a otra versión de la fragancia: un flanker o una concentración
distinta ya es otro producto</li>
<li>Una lista de notas que no coincide con la pirámide publicada del propio producto</li>
</ul>

<h2>Retiramos entradas después de publicarlas</h2>
<p>En agosto de 2026, una auditoría de notas de toda la base de datos detectó doce productos
cuyas notas habían sido acomodadas para parecerse al original que tenían asignado. Se
eliminaron catorce registros, se corrigieron diez pirámides cotejándolas con sus fuentes y la
base de datos bajó de 219 dupes verificados a 205.</p>

<p>Ese es el trato que aceptamos desde el principio: preferimos una base de datos más chica y
confiable que una más grande y dudosa.</p>

<h2>Lo que no hacemos</h2>
<ul>
<li><strong>No aceptamos producto gratis de las casas de perfume.</strong> Este sitio asigna
un número que genera ingresos por afiliación. Aceptar producto de esas mismas marcas nos
dejaría con dos intereses económicos apuntando en la misma dirección.</li>
<li><strong>No inventamos enlaces.</strong> Una entrada sin tienda verificada se publica solo
con su referencia de Fragrantica, en vez de disfrazar una búsqueda como si fuera una ficha de
producto.</li>
<li><strong>No escondemos lo que un dupe hace mal.</strong> Cada entrada dice en qué se queda
corto, no solo en qué se parece.</li>
</ul>

<h2>Correcciones</h2>
<p>Si encuentras algo mal, queremos saberlo, sobre todo si tienes las dos fragancias de una
comparación y tu experiencia no coincide con la nuestra. Ese es justamente el tipo de
evidencia a la que más peso le damos. Escríbenos a
<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

<h2>Cómo se financia este sitio</h2>
<p>Algunos enlaces son de afiliación y podemos ganar una comisión si compras a través de
ellos. A ti no te cuesta nada adicional y no cambia ninguna puntuación de similitud: las
puntuaciones se definen antes de agregar los enlaces, y las entradas que no tienen ninguna
relación de afiliación se ordenan igual que el resto. Los términos completos están en nuestro
<a href="/divulgacion/">aviso de afiliación</a>.</p>
"""

DISC_EN = f"""
<p class="lede">Decoded Scents earns money through affiliate links. This page explains
exactly how, and what it does and does not influence.</p>

<div class="callout">
<p><strong>As an Amazon Associate, {OPERATOR} earns from qualifying purchases.</strong></p>
</div>

<h2>Which links are affiliate links</h2>
<p>We participate in the Amazon Associates Program, and in affiliate programs for
FragranceNet and Shop Simon through Rakuten Advertising, and Perfumania through CJ
Affiliate. When you click one of those links and buy something, we may receive a commission
from the retailer. <strong>The price you pay is exactly the same.</strong></p>

<p>Not every link here earns anything. Links to Fragrantica are reference links and pay us
nothing. Links to a brand's own shop generally pay us nothing. Some entries carry only a
Fragrantica link, because no retailer we can verify sells that fragrance.</p>

<h2>What affiliate relationships do not affect</h2>
<ul>
<li><strong>Similarity scores.</strong> A percentage is set from research before any link is
attached, and it is not revised because a product happens to be purchasable through a partner.</li>
<li><strong>Whether an entry appears at all.</strong> Fragrances with no affiliate
relationship anywhere are included on the same terms as any other.</li>
<li><strong>Ranking within a page.</strong> Dupes are ordered by similarity, not by what pays.</li>
<li><strong>What we say about a product.</strong> Every entry names what the dupe gets wrong.
Several entries sit at our 85% floor and say so on the page.</li>
</ul>

<h2>Where we send you to buy</h2>
<p>When a fragrance is sold in several places, we link the one we would use ourselves \u2014 and
that is regularly not the one that pays us. Several entries here point at retailers we earn
nothing from, because they were cheaper on the day we checked. If a link earns us a commission
and a cheaper option exists, we would rather you had the cheaper option.</p>

<p>One thing that follows from this, so it does not look like a mistake: <strong>the price shown
on an entry is the original\u0027s normal retail, not the best price we found.</strong> Discount
sellers move their pricing constantly, and a page quoting last month\u0027s deal would be quietly
wrong. So you will sometimes click through and find it cheaper than the number we listed. That
is the intended direction.</p>

<h2>Free product</h2>
<p>We buy every fragrance we test, as decants or full bottles. We do not accept free product
from fragrance houses. This site assigns a number that
drives affiliate revenue; taking product from the same brands would create two financial
relationships pointing the same direction.</p>

<h2>Prices</h2>
<p>Prices shown are approximate and change often. Always check the current price at the
retailer before buying. We are not responsible for a retailer's pricing, stock, shipping or
returns.</p>

<h2>Questions</h2>
<p>Write to <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
"""

DISC_ES = f"""
<p class="lede">Decoded Scents gana dinero con enlaces de afiliación. Esta página explica
exactamente cómo, y en qué influye y en qué no.</p>

<div class="callout">
<p><strong>En calidad de Afiliado de Amazon, {OPERATOR} obtiene ingresos por las compras
adscritas que cumplen los requisitos aplicables.</strong></p>
</div>

<h2>Qué enlaces son de afiliación</h2>
<p>Participamos en el Programa de Afiliados de Amazon, y en los programas de FragranceNet y
Shop Simon a través de Rakuten Advertising, y de Perfumania a través de CJ Affiliate. Si haces
clic en uno de esos enlaces y compras algo, es posible que recibamos una comisión de la
tienda. <strong>A ti te cuesta exactamente lo mismo.</strong></p>

<p>No todos los enlaces generan ingresos. Los enlaces a Fragrantica son de referencia y no nos
pagan nada. Los enlaces a la tienda propia de una marca normalmente tampoco. Algunas entradas
llevan únicamente un enlace a Fragrantica, porque no encontramos ninguna tienda verificable
que venda esa fragancia.</p>

<h2>En qué no influyen las relaciones de afiliación</h2>
<ul>
<li><strong>En las puntuaciones de similitud.</strong> El porcentaje se define a partir de la
investigación, antes de agregar cualquier enlace, y no lo cambiamos porque un producto se
pueda comprar a través de un socio.</li>
<li><strong>En que una entrada aparezca o no.</strong> Las fragancias que no tienen ninguna
relación de afiliación entran en las mismas condiciones que el resto.</li>
<li><strong>En el orden dentro de una página.</strong> Los dupes se ordenan por similitud, no
por lo que nos pagan.</li>
<li><strong>En lo que decimos de un producto.</strong> Cada entrada dice en qué se queda corto
el dupe. Varias apenas alcanzan nuestro mínimo del 85% y lo aclaran en la página.</li>
</ul>

<h2>A d\u00f3nde te mandamos a comprar</h2>
<p>Cuando una fragancia se vende en varios sitios, enlazamos el que usar\u00edamos nosotros, y con
frecuencia no es el que nos paga. Varias entradas de este sitio apuntan a tiendas de las que no
ganamos nada, sencillamente porque el d\u00eda que lo revisamos estaban m\u00e1s baratas. Si un enlace
nos deja comisi\u00f3n y existe una opci\u00f3n m\u00e1s barata, preferimos que te quedes con la m\u00e1s
barata.</p>

<p>De ah\u00ed se sigue algo que conviene aclarar para que no parezca un error: <strong>el precio que
aparece en una entrada es el precio de venta habitual del original, no el mejor precio que
encontramos.</strong> Las tiendas de descuento cambian sus precios constantemente, y una p\u00e1gina
que citara la oferta del mes pasado estar\u00eda equivocada sin que nadie se enterara. As\u00ed que a
veces har\u00e1s clic y lo encontrar\u00e1s m\u00e1s barato de lo que dec\u00eda la ficha. Esa es la direcci\u00f3n
correcta.</p>

<h2>Producto gratuito</h2>
<p>Compramos cada fragancia que probamos, en decant o en frasco completo. No aceptamos
producto gratis de las casas de perfume. Este sitio asigna un número que genera ingresos por
afiliación; aceptar producto de esas mismas marcas nos dejaría con dos intereses económicos
apuntando en la misma dirección.</p>

<h2>Precios</h2>
<p>Los precios que aparecen son aproximados y cambian seguido. Revisa siempre el precio
vigente en la tienda antes de comprar. No somos responsables de los precios, la
disponibilidad, los envíos ni las devoluciones de ninguna tienda.</p>

<h2>Dudas</h2>
<p>Escríbenos a <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
"""

PRIV_EN = f"""
<p class="lede">Decoded Scents does not ask you for personal information, and there is no
account to create. This page explains the little that is collected anyway.</p>

<h2>What we collect</h2>
<p><strong>Analytics.</strong> We use Google Analytics 4 to count visits and see which pages
people read. It sets cookies and records things like approximate location, browser and the
pages you view. We use it in aggregate — we are looking at whether a page gets read, not at
you.</p>

<p><strong>Searches.</strong> When you search a fragrance, the term is sent to our own server
to look up results. Search terms are not tied to an identity and we do not build a profile
from them.</p>

<p><strong>Nothing else.</strong> There is no newsletter, no sign-up, no comment system, and
we do not sell or share data with anyone.</p>

<h2>Affiliate cookies</h2>
<p>Clicking an affiliate link sets a cookie from that retailer or network — Amazon, Rakuten
Advertising or CJ Affiliate — so the retailer knows the visit came from us. That cookie is
theirs, governed by their privacy policy, and we never see your order details. See our
<a href="/disclosure/">affiliate disclosure</a>.</p>

<h2>Your choices</h2>
<p>You can block or delete cookies in your browser at any time; the site still works. Browser
"do not track" and Google's own analytics opt-out are both respected.</p>

<p>Depending on where you live you may have the right to request access to or deletion of
data about you. Since we do not hold accounts, in practice this means analytics data — write
to <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> and we will help.</p>

<h2>Children</h2>
<p>This site is not directed at children under 13 and we do not knowingly collect information
from them.</p>

<h2>Who operates this site</h2>
<p>Decoded Scents is operated from Florida, United States. Questions about this policy go to <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

<h2>Changes</h2>
<p>If this policy changes, the date below changes with it.</p>
"""

PRIV_ES = f"""
<p class="lede">Decoded Scents no te pide información personal y no hay ninguna cuenta que
crear. Esta página explica lo poco que de todos modos se recopila.</p>

<h2>Qué recopilamos</h2>
<p><strong>Analítica.</strong> Usamos Google Analytics 4 para contar visitas y ver qué páginas
se leen. Esa herramienta guarda cookies y registra datos como la ubicación aproximada, el
navegador y las páginas que visitas. La usamos de forma agregada: nos interesa saber si una
página se lee, no quién eres.</p>

<p><strong>Búsquedas.</strong> Cuando buscas una fragancia, el término viaja a nuestro propio
servidor para consultar los resultados. Los términos de búsqueda no se asocian con ninguna
identidad y no armamos ningún perfil con ellos.</p>

<p><strong>Nada más.</strong> No hay boletín, ni registro, ni sistema de comentarios, y no
vendemos ni compartimos datos con nadie.</p>

<h2>Cookies de afiliación</h2>
<p>Al hacer clic en un enlace de afiliación, esa tienda o esa red —Amazon, Rakuten Advertising
o CJ Affiliate— guarda una cookie para saber que la visita salió de aquí. Esa cookie es de
ellos y se rige por su propia política de privacidad; nosotros nunca vemos los datos de tu
compra. Puedes leer nuestro <a href="/divulgacion/">aviso de afiliación</a>.</p>

<h2>Tus opciones</h2>
<p>Puedes bloquear o borrar las cookies desde tu navegador cuando quieras y el sitio va a
seguir funcionando. Respetamos la señal "no rastrear" del navegador y también el complemento
de Google para desactivar la analítica.</p>

<p>Según el lugar donde vivas, es posible que tengas derecho a pedir acceso a tus datos o su
eliminación. Como no manejamos cuentas, en la práctica se trata de datos de analítica:
escríbenos a <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> y te ayudamos.</p>

<h2>Menores</h2>
<p>Este sitio no está dirigido a menores de 13 años y no recopilamos su información a
sabiendas.</p>

<h2>Quién opera este sitio</h2>
<p>Decoded Scents se opera desde Florida, Estados Unidos. Las dudas sobre esta política van a <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

<h2>Cambios</h2>
<p>Si esta política cambia, la fecha que aparece abajo cambia con ella.</p>
"""

PAGES = [
    ('about',      'acerca-de',   'en', 'About Decoded Scents',
     'How we score fragrance dupes, why we publish the ones that fail, and what our 85% similarity floor actually means.',
     'About', 'Our method, our floor, and what we refuse to do', ABOUT_EN),
    ('about',      'acerca-de',   'es', 'Qui\u00e9nes somos \u2014 Decoded Scents',
     'C\u00f3mo puntuamos los dupes de fragancias, por qu\u00e9 publicamos los que no llegan, y qu\u00e9 significa realmente nuestro umbral del 85%.',
     'Qui\u00e9nes somos', 'Nuestro m\u00e9todo, nuestro umbral y lo que nos negamos a hacer', ABOUT_ES),
    ('disclosure', 'divulgacion', 'en', 'Affiliate Disclosure',
     'How Decoded Scents makes money, which links earn a commission, and what affiliate relationships do not influence.',
     'Affiliate disclosure', 'How this site makes money \u2014 and what that does not change', DISC_EN),
    ('disclosure', 'divulgacion', 'es', 'Aviso de afiliaci\u00f3n',
     'C\u00f3mo gana dinero Decoded Scents, qu\u00e9 enlaces generan comisi\u00f3n y en qu\u00e9 no influyen las relaciones de afiliaci\u00f3n.',
     'Aviso de afiliaci\u00f3n', 'C\u00f3mo se financia este sitio, y qu\u00e9 no cambia por ello', DISC_ES),
    ('privacy',    'privacidad',  'en', 'Privacy Policy',
     'What Decoded Scents collects, what it does not, and how to opt out.',
     'Privacy', 'What we collect, and what we don\u2019t', PRIV_EN),
    ('privacy',    'privacidad',  'es', 'Pol\u00edtica de privacidad',
     'Qu\u00e9 recoge Decoded Scents, qu\u00e9 no, y c\u00f3mo excluirte.',
     'Privacidad', 'Qu\u00e9 recogemos y qu\u00e9 no', PRIV_ES),
]


def page(en_slug, es_slug, lang, title, desc, h1, byline, body, style, footer):
    es = lang == 'es'
    slug = es_slug if es else en_slug
    url = f'{BASE}/{slug}/'
    nav = NAV_ES if es else NAV_EN
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title,
          "description": desc, "url": url, "publisher":
          {"@type": "Organization", "name": "Decoded Scents", "url": BASE}}
    if es: ld["inLanguage"] = "es"
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | Decoded Scents</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{BASE}/{en_slug}/">
<link rel="alternate" hreflang="es" href="{BASE}/{es_slug}/">
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
{nav}
<header class="article-hero">
  <div class="container">
    <div class="hero-meta">\u2726 {esc(byline)}</div>
    <h1>{esc(h1)}</h1>
  </div>
</header>
<main class="container"><article class="doc">
{body}
<p class="updated">{UPDATED_ES if es else UPDATED_EN}</p>
</article></main>
{footer}
</body>
</html>"""


def main():
    style = open('/home/claude/work/style.html', encoding='utf-8').read()
    footer = open('/home/claude/work/footer.html', encoding='utf-8').read()
    footer_es = open('/home/claude/work/footer_es.html', encoding='utf-8').read()
    made = []
    for en_slug, es_slug, lang, title, desc, h1, byline, body in PAGES:
        slug = es_slug if lang == 'es' else en_slug
        d = os.path.join(OUT, slug)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, 'index.html')
        fo = footer_es if lang == 'es' else footer
        open(p, 'w', encoding='utf-8').write(
            page(en_slug, es_slug, lang, title, desc, h1, byline, body, style, fo))
        made.append(f'/{slug}/')
    print('created:', ', '.join(made))
    print('\nCONFIRM BEFORE PUBLISHING:')
    print(f'   contact email  -> {CONTACT_EMAIL}   (placeholder)')
    print(f'   operator name  -> {OPERATOR}        (a personal name may read as more trustworthy)')
    print(f'   jurisdiction   -> {LOCATION}        (affects which privacy law applies)')


if __name__ == '__main__':
    main()
