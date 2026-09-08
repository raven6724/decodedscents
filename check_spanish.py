#!/usr/bin/env python3
"""
Spanish page checker — runs against RENDERED HTML, not source   (2026-08-08)

Built after four separate Spanish re-uploads in one evening. Every one of those was
the same failure: a register checker existed for the dupe pages and was never
pointed at the trust pages, the homepage, or the index. Each fix shipped alone
instead of prompting the question "what else has this same gap?".

This checks EVERY rendered Spanish page in one pass. Run it before packaging
anything. If it prints findings, nothing should be uploaded.

WHAT IT CANNOT DO. It catches patterns it has been taught. It would have caught
"web", "coste", the guillemets and the orphan "both". It would NOT have caught
"coincidencia" — that was a judgement about register across 70 instances, and it
needed a reader. Anything this reports is a floor, not a ceiling.
"""
import os, re, sys, html, json
from collections import defaultdict

ROOT = '/home/claude'
DIRS = ['dupes-es', 'acerca-de', 'divulgacion', 'privacidad', 'es', 'marcas']

# Text inside article cards is English by design (the journal has its own EN/ES
# filter and Spanish articles already exist). Skip that block, don't flag it.
ARTICLE_BLOCK = re.compile(r'<(article-card|div[^>]*class="[^"]*article-card[^"]*")', re.I)

SPAIN = {
    r'\b(esta|nuestra|la|una|las|los|su)\s+webs?\b(?!\s*(est\u00e1n|se\s|,\s*Google))':
        'Spain: "web" for the site \u2192 sitio  (note: "por la web" = the internet is fine)',
    r'\bcoste\b': 'Spain: "coste" \u2192 costo',
    r'\bordenador\b': 'Spain: ordenador \u2192 computadora',
    r'\bm\u00f3vil\b': 'Spain: m\u00f3vil \u2192 celular',
    r'\bzumo\b': 'Spain: zumo \u2192 jugo',
    r'\bcoger\b': 'Spain/vulgar in LatAm: coger',
    r'\bvosotros\b|\b(?!diecis\u00e9is|veintis\u00e9is|seis)\w{3,}[\u00e1\u00e9]is\b': 'Spain: vosotros form',
    r'\bmerece la pena\b': 'Spain: \u2192 vale la pena',
    r'\bordena(r|d)\b(?! por)': 'check usage',
    r'\balbaricoque\b': 'Spain: \u2192 damasco',
    r'\bmelocot\u00f3n\b': 'Spain: \u2192 durazno',
    r'\bpomelo\b': 'Spain: \u2192 toronja',
    r'\bpulverizado\b': 'Spain-leaning: \u2192 aplicaci\u00f3n',
    r'\bun fijo\b': 'Spain: \u2192 un infaltable',
    r'\btira a\b|\btira algo m\u00e1s\b': 'Spain-colloquial: \u2192 se inclina a / resulta',
    r'\bpiso\b': 'Spain: piso \u2192 departamento',
}

CALQUE = {
    r'\bdivulgaci\u00f3n\b': '"divulgaci\u00f3n" = dissemination, not disclosure \u2192 aviso',
    r'\bdescansa en\b': 'calque of "rests on" \u2192 se basa en',
    r'\bcontra sus fuentes\b|\bcontra el que\b|\bcontra la que\b': 'calque of "against" \u2192 cotejar con',
    r'\bde forma consciente\b': 'calque of "knowingly" \u2192 a sabiendas',
    r'\bcomprable\b': 'not a word \u2192 se pueda comprar',
    r'\bprovocar? cumplidos\b': 'calque \u2192 recibir cumplidos',
    r'\bencanto de fiesta\b': 'calque of "party charm"',
    r'\bsin matices\b': 'reads as "unnuanced" \u2192 y punto',
    r'\bmateriales primas\b': '\u2192 materias primas',
    r'\bpuntan\b': '\u2192 punt\u00faan',
    r'\bse vende contra\b': 'calque \u2192 se vende como alternativa a',
    r'\bfuera de blanco\b': 'calque \u2192 fuera del objetivo',
    r'\bcoincidencia\b': 'reads as "coincidence" \u2192 alternativa / parecido',
    r'\bpesar la evidencia\b': '\u2192 sopesar',
}

TYPOG = {
    r'\u00ab|\u00bb': 'guillemets \u2192 curly quotes (LatAm web convention)',
    r'(?<=\d),(?=\d)(?!\d{3}\b)': 'decimal comma \u2192 decimal point',

}

# Bare English words stranded between tags — the "A ... or ... both" failure.
ORPHAN = re.compile(
    r'^(a|an|the|or|and|both|of|in|for|with|to|is|are|that|this|but|not|also|more|'
    r'every|from|your|our|we|they|what|which|who|when|it|by|as|at|on)$', re.I)


def visible_text(p):
    """Strip head, scripts and styles; return the body a reader actually sees."""
    b = p[p.index('</head>'):] if '</head>' in p else p
    b = re.sub(r'<(script|style|noscript).*?</\1>', ' ', b, flags=re.S)
    return b


def check(path):
    raw = open(path, encoding='utf-8').read()
    body = visible_text(raw)
    # Tag stripping fabricates whitespace: "<a>x</a>, y" becomes "x , y", and HTML
    # indentation becomes runs of spaces. Neither is visible to a reader, so collapse
    # before checking or the report drowns in noise.
    text = html.unescape(re.sub(r'<[^>]+>', ' ', body))
    text = re.sub(r'\s+', ' ', text)
    found = []

    for group, table in (('REGISTER', SPAIN), ('CALQUE', CALQUE), ('TYPOGRAPHY', TYPOG)):
        for pat, note in table.items():
            for m in re.finditer(pat, text, re.I):
                frag = re.sub(r'\s+', ' ', text[max(0, m.start()-45):m.end()+45]).strip()
                found.append((group, note, frag))

    # Repeated words are checked PER TEXT NODE. Across nodes a heading and the link
    # under it ("M\u00e1s de Dior" + "Dior Sauvage") look like a repeat and are not.
    for node in re.split(r'<[^>]+>', body):
        n = re.sub(r'\s+', ' ', html.unescape(node)).strip()
        # "Bade'e Al Oud Oud for Glory" is the real product name: a line called
        # "Bade'e Al Oud" and a variant called "Oud for Glory". Not a typo.
        for m in re.finditer(r'\b(?!ylang|oud)(\w{3,})\s+\1\b', n, re.I):
            found.append(('TYPOGRAPHY', 'repeated word', m.group(0)))

    # orphan English words sitting between tags
    for node in re.split(r'<[^>]+>', body):
        n = html.unescape(node).strip()
        if n and ORPHAN.fullmatch(n):
            found.append(('ORPHAN EN', f'bare "{n}" between tags', n))

    # untranslated note names actually rendered
    try:
        notes = json.load(open('/tmp/notes_es.json'))
        for chunk in re.findall(r'<span class="note-label">.*?</span>(.*?)</div>', body) + \
                     re.findall(r'<strong>Comparte con el original:</strong>(.*?)</p>', body):
            for t in [x.strip() for x in html.unescape(re.sub(r'<[^>]+>', '', chunk)).split(',')]:
                if t in notes and notes[t] != t:
                    found.append(('UNTRANSLATED NOTE', f'"{t}" \u2192 {notes[t]}', t))
    except Exception:
        pass

    # head hygiene
    head = raw[:raw.index('</head>')] if '</head>' in raw else ''
    if '<html lang="es"' not in raw:
        found.append(('HEAD', 'lang attribute is not es', ''))
    if 'hreflang="en"' not in head or 'hreflang="es"' not in head:
        found.append(('HEAD', 'missing hreflang pair', ''))
    if 'es_MX' not in head:
        found.append(('HEAD', 'og:locale is not es_MX', ''))
    return found


def main():
    files = []
    for d in DIRS:
        p = os.path.join(ROOT, d)
        if not os.path.isdir(p):
            print(f'  (skipped, not built: {d})'); continue
        for root_dir, _, fnames in os.walk(p):
            files += [os.path.join(root_dir, f) for f in sorted(fnames) if f.endswith('.html')]

    total, by_issue = 0, defaultdict(list)
    for f in files:
        for group, note, frag in check(f):
            total += 1
            by_issue[(group, note)].append((os.path.relpath(f, ROOT), frag))

    print(f'checked {len(files)} rendered Spanish pages\n')
    if not total:
        print('CLEAN \u2014 no register, calque, typography, orphan-English or head issues found.')
        print('\nNote: this checks patterns it knows about. Register judgements like')
        print('"coincidencia" still need a native read.')
        return 0

    print(f'{total} findings across {len(by_issue)} distinct issues:\n')
    for (group, note), hits in sorted(by_issue.items(), key=lambda x: -len(x[1])):
        print(f'[{group}] {note}  \u2014 {len(hits)} page(s)')
        for path, frag in hits[:3]:
            print(f'     {path}: ...{frag[:95]}...')
        if len(hits) > 3:
            print(f'     ... and {len(hits)-3} more')
        print()
    return 1


if __name__ == '__main__':
    sys.exit(main())
