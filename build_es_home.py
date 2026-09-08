#!/usr/bin/env python3
"""
Spanish homepage generator  ->  /es/index.html          (2026-08-08)

GENERATED, NEVER HAND-WRITTEN. Same rule as the dupe pages. A hand-made Spanish
homepage would drift the first time Index.html changes -- and it already has this
session, when "ALL DUPES" was added to the nav. This reads the CURRENT Index.html
and applies a translation map, so re-running it after any English change is the
whole maintenance story.

EVERY replacement is asserted. If a string is not found exactly once, the script
prints what is missing and exits without writing. That is deliberate: a silently
skipped replacement ships an English sentence on a Spanish page, which is the
failure mode that is invisible until a reader hits it.

WHAT THIS TRANSLATES
  - all static page copy (hero, the "What Is a Fragrance Dupe?" SEO section,
    journal headers, share block, footer)
  - the JS-rendered search result UI (labels, buttons, empty states, note tiers)
  - note names and scent families, via the glossary already built for /dupes-es/

WHAT IT DOES NOT TRANSLATE, YET
  The `description` and `whySimilar` prose returned by worker.js. That is 6,255
  words still to hand-translate (batches 6-8) plus a `lang` parameter on the
  worker. Until then a Spanish search shows Spanish labels, Spanish notes, correct
  percentages -- and English paragraphs. Known gap, phase 3.

  The article cards are left exactly as they are: the journal already has its own
  EN/ES filter and Spanish articles already live in the grid.
"""
import json, re, sys, os, html

SRC = '/home/claude/edit_index.html'
OUT = '/home/claude/es/index.html'
BASE = 'https://decodedscents.com'

# ---------------------------------------------------------------- string map
# (english, spanish, required)  required=1 -> abort if absent; 0 -> optional
# All occurrences are replaced. Sorted longest-first at apply time so that a
# shorter string never eats the prefix of a longer one.
COPY = [
    # --- nav / brand ---
    ('Luxury Perfume Dupes &amp; Alternatives', 'Dupes y Alternativas de Perfumes de Lujo', 1),
    ('The Scent Journal', 'The Scent Journal', 0),          # brand name, kept
    ('>Dupe Finder<', '>Buscador de Dupes<', 0),
    ('>All Dupes<', '>Todos los Dupes<', 0),                 # may not exist in older copies

    # --- hero ---
    ('✦ Community-Verified Fragrance Research',
     '✦ Investigación de Fragancias Verificada por la Comunidad', 1),
    ('Every Scent,', 'Cada Aroma,', 1),
    ('Decoded.', 'Descifrado.', 1),
    ('Search any luxury or niche fragrance and instantly discover its top affordable dupes — backed by real community research.',
     'Busca cualquier fragancia de lujo o de nicho y descubre al instante sus mejores dupes asequibles, respaldados por investigación real de la comunidad.', 1),
    ('>Find Dupes<', '>Buscar Dupes<', 1),
    ("Try 'Creed Aventus' or ", "Prueba con 'Creed Aventus' o ", 1),
    ('✦ Decoding your fragrance...', '✦ Descifrando tu fragancia...', 1),

    # --- SEO section ---
    ('What Is a Fragrance Dupe?', '¿Qué es un dupe de fragancia?', 1),
    ('Read More ↓', 'Leer más ↓', 1),
    ('Read Less ↑', 'Leer menos ↑', 1),
    ('>fragrance dupe<', '>dupe de fragancia<', 1),
    ('— also known as an', '—también llamado', 1),
    ('affordable perfume clone', 'clon de perfume asequible', 1),
    ('luxury fragrance alternative', 'alternativa a una fragancia de lujo', 2),
    ('— is a perfume that smells nearly identical to a',
     '— es un perfume que huele casi idéntico a una', 1),
    ('high-end designer or niche fragrance, but costs a fraction of the price. At Decoded Scents,',
     'fragancia de diseñador o de nicho, pero cuesta una fracción del precio. En Decoded Scents', 1),
    ('we define a true dupe as any fragrance that scores',
     'definimos un dupe real como cualquier fragancia que alcance', 1),
    ('85% or higher in community similarity testing',
     'un 85% o más en las pruebas de similitud de la comunidad', 1),
    ('against its luxury counterpart. Anything below that threshold is simply "inspired by" — and we don\'t include those in our results.',
     'frente a su contraparte de lujo. Todo lo que quede por debajo de ese umbral es simplemente "inspirado en", y eso no entra en nuestros resultados.', 1),
    ('In our testing, we cross-reference thousands of fragrance community reviews from',
     'En nuestras pruebas contrastamos miles de reseñas de la comunidad de fragancias de', 1),
    (', and verified purchase reviews on Amazon and Walmart. We noticed that',
     ', además de reseñas de compra verificada en Amazon y Walmart. Notamos que', 1),
    ('the most reliable similarity scores come from reviewers who own',
     'las puntuaciones de similitud más fiables vienen de quienes tienen', 1),
    ('the original and', 'el original y', 1),
    ('the alternative — not just people who have smelled one in a store. That is the standard we hold',
     'la alternativa, no de quien solo ha olido una en una tienda. Ese es el estándar al que sometemos', 1),
    ('every entry in our database to.', 'cada entrada de nuestra base de datos.', 1),
    ('Our database currently covers', 'Nuestra base de datos cubre actualmente', 1),
    ('luxury perfume dupes', 'dupes de perfumes de lujo', 1),
    ('for fragrances from Creed,', 'de fragancias de Creed,', 1),
    ("Penhaligon's, Maison Margiela, and more. In our testing, brands like",
     "Penhaligon's, Maison Margiela y muchas más. En nuestras pruebas, marcas como", 1),
    ('consistently produce the most accurate',
     'producen de forma constante los', 1),
    ('affordable perfume clones', 'clones de perfume asequibles más fieles', 1),
    ('— often achieving 88-95% similarity to originals',
     '— y a menudo alcanzan entre un 88% y un 95% de similitud con originales', 1),
    ('that cost 10 times more.', 'que cuestan diez veces más.', 1),
    ('Every result you see on Decoded Scents is backed by real community research. We noticed that',
     'Cada resultado que ves en Decoded Scents está respaldado por investigación real de la comunidad. Notamos que', 1),
    ('generic "inspired by" lists published across the web are filled with invented product names',
     'las listas genéricas de "inspirado en" que circulan por la web están llenas de nombres de productos inventados', 1),
    ('and unverified claims. Our rule is simple:',
     'y afirmaciones sin verificar. Nuestra regla es simple:', 1),
    ('if we cannot find verified community',
     'si no encontramos confirmación verificada de la comunidad', 1),
    ('confirmation of the similarity, it does not appear in our results.',
     'sobre la similitud, no aparece en nuestros resultados.', 1),
    ('One honest result', 'Un resultado honesto', 1),
    ('is worth more than ten invented ones. Search any luxury or niche fragrance above and',
     'vale más que diez inventados. Busca arriba cualquier fragancia de lujo o de nicho y', 1),
    ('instantly discover its best', 'descubre al instante su mejor', 1),
    ('— verified,', '— verificada,', 1),
    ('affordable, and real.', 'asequible y real.', 1),


    # --- journal ---
    ('Expert guides &amp; comparisons', 'Guías y comparativas de expertos', 1),
    ('Search articles...', 'Buscar artículos...', 1),
    ('No articles found. Try a different search.',
     'No se encontraron artículos. Prueba con otra búsqueda.', 1),

    # --- share block ---
    ('✦ SHARE DECODED SCENTS ✦', '✦ COMPARTE DECODED SCENTS ✦', 1),
    ('Know someone who loves fragrance? Send them here.',
     '¿Conoces a alguien que ame los perfumes? Mándale este enlace.', 1),
    ('📋 Copy Link', '📋 Copiar enlace', 2),

    # --- footer ---
    ('Every Scent, Decoded.', 'Cada Aroma, Descifrado.', 1),

    # --- JS-rendered results UI ---
    ('SHARE THIS DUPE', 'COMPARTE ESTE DUPE', 2),
    ('>Shared Notes<', '>Notas compartidas<', 1),
    ('Shared Notes', 'Notas compartidas', 0),
    ('No verified dupe found', 'Sin dupes verificados', 1),
    ('✦ Show All ${dupes.length} Results', '✦ Ver los ${dupes.length} resultados', 1),
    ('← New Search', '← Nueva búsqueda', 1),
    ('Community verified', 'Verificado por la comunidad', 1),
    ('Dupes</span>', 'Dupes</span>', 0),
]

# Applied AFTER the main map, because these anchors contain text the main map
# produces. Same assertion: absent anchor -> abort.
POST_FIX = [
# These slipped through the first build: the string map anchored on text
    # inside <strong>/<em>, so the loose words joining those tags stayed English
    # and produced "A dupe de fragancia ... clon de perfume asequible or ...".
    # Anchored on the surrounding markup so they cannot match anywhere else.
    (' A <strong style="color:var(--text);">dupe de fragancia</strong>',
     ' Un <strong style="color:var(--text);">dupe de fragancia</strong>', 1),
    ('clon de perfume asequible</strong> or', 'clon de perfume asequible</strong> o', 1),
    ('</strong>, and <strong style="color:var(--text);">Afnan</strong>',
     '</strong> y <strong style="color:var(--text);">Afnan</strong>', 1),

    # The "both" sentence needs restructuring, not word-swapping: Spanish does not
    # carry the emphatic bare "both" the way English does. The emphasis moves onto
    # "las dos fragancias", which is where it belongs.
    ('vienen de quienes tienen <em style="color:var(--gold);">both</em> el original y',
     'vienen de quienes tienen <em style="color:var(--gold);">las dos fragancias</em>, el original y',
     1),
    ('la alternativa, no de quien solo ha olido una en una tienda.',
     'la alternativa, no de quien solo ha olido una fragancia en tienda.', 1),
]

# note tier labels rendered by the results JS
TIERS = [('"Top"', '"Salida"'), ("'Top'", "'Salida'"),
         ('"Heart"', '"Corazón"'), ("'Heart'", "'Corazón'"),
         ('"Middle"', '"Corazón"'), ("'Middle'", "'Corazón'"),
         ('"Base"', '"Fondo"'), ("'Base'", "'Fondo'")]


def main():
    if not os.path.exists(SRC):
        sys.exit(f'ABORT: {SRC} not found — upload the CURRENT Index.html')
    src = open(SRC, encoding='utf-8').read()
    out, missing, applied = src, [], 0

    # Longest first: "affordable perfume clone" is a prefix of "...clones", and
    # replacing the short one first would corrupt the plural into Spanglish.
    counts = {}
    for en, es, required in sorted(COPY, key=lambda t: -len(t[0])):
        n = out.count(en)
        counts[en] = n
        if required and n == 0:
            missing.append(f'NOT FOUND: {en[:70]}')
            continue
        if n == 0:
            continue
        out = out.replace(en, es)
        applied += 1

    if missing:
        print('ABORT — Index.html has changed; these anchors did not match:\n')
        for m in missing:
            print('   ', m)
        print('\nNothing written. Update the string map, then rerun.')
        sys.exit(1)

    for en, es, required in POST_FIX:
        if en not in out:
            print('ABORT — post-fix anchor not found:\n   ', en[:90])
            sys.exit(1)
        out = out.replace(en, es)
        applied += 1

    # note tier labels
    for a, b in TIERS:
        out = out.replace(a, b)

    # The journal filter defaults to "all" (labelled English) on the English page.
    # On a Spanish page it should open already filtered to Spanish articles.
    j = [('lang-btn active" data-lang="all">\U0001f1fa\U0001f1f8 English',
          'lang-btn" data-lang="all">\U0001f30e Todos'),
         ('lang-btn" data-lang="es">\U0001f1ea\U0001f1f8 Espa\u00f1ol',
          'lang-btn active" data-lang="es">\U0001f1ea\U0001f1f8 Espa\u00f1ol')]
    for a, b in j:
        if a not in out:
            sys.exit(f'ABORT: journal filter markup changed, not found: {a[:50]}')
        out = out.replace(a, b, 1)
    if 'activeLang = "all"' not in out:
        sys.exit('ABORT: activeLang default not found')
    out = out.replace('activeLang = "all"', 'activeLang = "es"', 1)

    # filterArticles() is only ever called from a click handler — there is no
    # initial call. Without one, changing the default hides nothing and every
    # English card renders until the reader touches a tab. Fire it once on load.
    if 'function filterArticles(' not in out:
        sys.exit('ABORT: filterArticles not found — journal JS changed')
    out = out.replace('</body>',
        '<script>document.addEventListener("DOMContentLoaded",function(){'
        'if(typeof filterArticles==="function"){filterArticles();}});</script>\n</body>', 1)

    # client-side note/family glossary, reused from the /dupes-es/ work
    notes = json.load(open('/tmp/notes_es.json'))
    fams = json.load(open('/tmp/fam_es.json'))
    glossary = ('<script>window.ES_NOTES=' + json.dumps(notes, ensure_ascii=False)
                + ';window.ES_FAMS=' + json.dumps(fams, ensure_ascii=False)
                + ';window.esNote=function(n){return (window.ES_NOTES[n]||n);};'
                + 'window.esFam=function(f){return (window.ES_FAMS[f]||f);};</script>\n')

    # head: language, canonical, hreflang pair
    out = out.replace('<html lang="en">', '<html lang="es">', 1)
    head_add = (f'<link rel="canonical" href="{BASE}/es/">\n'
                f'<link rel="alternate" hreflang="en" href="{BASE}/">\n'
                f'<link rel="alternate" hreflang="es" href="{BASE}/es/">\n'
                f'<meta property="og:locale" content="es_MX">\n')
    out = re.sub(r'<link rel="canonical"[^>]*>\n?', '', out)
    out = out.replace('</head>', glossary + head_add + '</head>', 1)

    # RELATIVE LINKS BREAK ONE DIRECTORY DOWN. The article cards use
    # href="Articles/foo" with no leading slash. From / that resolves to
    # /Articles/foo and works; from /es/ it resolves to /es/Articles/foo and 404s.
    # All 27 article links were dead on the Spanish homepage because of this.
    # Make them absolute.
    before = out.count('href="Articles/')
    out = out.replace('href="Articles/', 'href="/Articles/')
    if before and 'href="/Articles/' not in out:
        sys.exit('ABORT: article links were not made absolute')

    # Any other root-relative asset referenced without a leading slash would have
    # the same problem, so fail loudly rather than ship a broken page.
    import re as _re
    # Only real static paths matter here. `${...}` are JS template literals filled
    # in at runtime by the results renderer, not paths in the document.
    stragglers = _re.findall(r'href="(?!https?:|/|#|mailto:|\$\{)([^"]+)"', out)
    stragglers = [x for x in stragglers if not x.startswith('?') and '${' not in x]
    if stragglers:
        sys.exit(f'ABORT: relative links would break under /es/: {sorted(set(stragglers))[:6]}')

    # Links that mean "this site's homepage" must stay inside /es/ on the Spanish
    # page, and every dupe link must point at the Spanish directory.
    out = out.replace(f'href="{BASE}"', f'href="{BASE}/es/"')
    out = out.replace('href="/dupes/"', 'href="/dupes-es/"')
    out = out.replace('href="/dupes"', 'href="/dupes-es/"')

    # NAV. Index.html's nav is inherited wholesale, so English items must be
    # REPLACED, not supplemented. Injecting alongside them produced a Spanish page
    # showing "Quienes somos" next to "About", and "Espanol" next to "English".
    #
    #   /about/  -> /acerca-de/   (translate in place)
    #   /es/     -> removed        (we are already on the Spanish page)
    #   English  -> appended       (the way back)
    nav_m = re.search(r'(<div class="nav-links">)(.*?)(</div>)', out, re.S)
    if not nav_m:
        sys.exit('ABORT: nav-links block not found')
    nav = nav_m.group(2)

    b = re.search(r'<a href="/brands/"[^>]*>[^<]*</a>', nav)
    if b:
        nav = nav.replace(b.group(0), '<a href="/marcas/">Marcas</a>', 1)

    a = re.search(r'<a href="/about/"[^>]*>[^<]*</a>', nav)
    if a:
        nav = nav.replace(a.group(0), '<a href="/acerca-de/">Qui\u00e9nes somos</a>', 1)
    elif '/acerca-de/' not in nav:
        d = re.search(r'\n(\s*)<a href="/dupes-es/">[^<]*</a>', nav)
        if not d:
            sys.exit('ABORT: no /about/ link and no /dupes-es/ anchor to insert after')
        nav = nav.replace(d.group(0), d.group(0) + f'\n{d.group(1)}<a href="/acerca-de/">Qui\u00e9nes somos</a>', 1)

    # drop any self-referential Spanish switch
    for sw in re.findall(r'\n?\s*<a href="/es/"[^>]*>[^<]*</a>', nav):
        nav = nav.replace(sw, '', 1)

    if '/acerca-de/' not in nav:
        sys.exit('ABORT: Spanish About link missing after rewrite')
    if re.search(r'<a href="/about/"', nav):
        sys.exit('ABORT: English About link survived')
    if re.search(r'<a href="/es/"', nav):
        sys.exit('ABORT: self-referential Espanol link survived')
    if re.search(r'<a href="/brands/"', nav):
        sys.exit('ABORT: English Brands link survived on the Spanish page')

    out = out[:nav_m.start(2)] + nav + out[nav_m.end(2):]

    # A Spanish reader needs a way back. Inject an English switch as the last nav
    # item, whatever the English nav happens to contain when this is re-run.
    m = re.search(r'(<div class="nav-links">)(.*?)(</div>)', out, re.S)
    if not m:
        sys.exit('ABORT: nav-links block not found — nav markup changed')
    if 'hreflang="en"' not in m.group(2):
        out = out[:m.end(2)] + f'\n      <a href="{BASE}/" hreflang="en">English</a>' + out[m.end(2):]


    # The homepage carries affiliate links like every other page, so it needs the
    # same disclosure. Index.html's footer predates it.
    disc = open('/home/claude/work/footer_es.html', encoding='utf-8').read()
    m = re.search(r'<p class="footer-disclosure">.*?</p>', disc, re.S)
    if not m:
        sys.exit('ABORT: disclosure line not found in footer_es.html')
    if 'footer-disclosure' not in out:
        if '</footer>' not in out:
            sys.exit('ABORT: no </footer> on the homepage')
        out = out.replace('</footer>', '  ' + m.group(0) + '\n  </footer>', 1)


    # The Spanish homepage inherits analytics from Index.html. If the English page
    # loses its tag again, the Spanish one silently loses it too — so fail loudly
    # rather than ship an untracked page.
    if 'G-3KS1C0WH40' not in out:
        sys.exit('ABORT: no GA4 tag in Index.html — the Spanish homepage would be untracked')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(out)
    print(f'wrote {OUT}  ({len(out):,} bytes, {applied} strings translated)')

    left = [en for en, es, req in COPY if req and en in out]
    print('untranslated anchors remaining:', left or 'none')
    multi = {k: v for k, v in counts.items() if v > 1}
    if multi:
        print(f'\nstrings that appeared more than once (all replaced): {len(multi)}')
        for k, v in sorted(multi.items(), key=lambda x: -x[1])[:8]:
            print(f'   {v}x  {k[:60]}')


if __name__ == '__main__':
    main()
