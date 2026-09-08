#!/usr/bin/env python3
"""
sitemap.xml regenerator (2026-08-04)

The uploaded sitemap carries 29 article URLs and ZERO /dupes/ URLs, so none of the
122 static pages built on 2026-07-31 are being declared to Google. This rebuilds it.

Existing <url> blocks are carried through BYTE-FOR-BYTE -- their lastmod values and
article hreflang pairs are real information this script has no way to re-derive, and
ARTICLE_PROTOCOLS 3.3 is explicit that lastmod is set only where the real date is
known. Nothing gets a stamped date it did not earn.

Dupe URLs are read off the generated directories rather than from the DB, so the
sitemap can only ever declare files that actually exist. hreflang pairs are emitted
only where BOTH files are present on disk.
"""
import os, re, sys

SRC = '/mnt/user-data/uploads/sitemap.xml'
EN = '/home/claude/dupes'
ES = '/home/claude/dupes-es'
OUT = '/home/claude/sitemap.xml'
BASE = 'https://decodedscents.com'

raw = open(SRC, encoding='utf-8').read()
existing = re.findall(r'  <url>.*?</url>\n', raw.replace('\r\n', '\n'), re.S)
if not existing:
    sys.exit('could not parse existing sitemap')

locs = set(re.findall(r'<loc>([^<]+)</loc>', raw))
en_files = {f[:-5] for f in os.listdir(EN) if f.endswith('.html') and f != 'index.html'}
es_files = {f[:-5] for f in os.listdir(ES) if f.endswith('.html') and f != 'index.html'}
assert es_files <= en_files, f'ES pages with no EN counterpart: {es_files - en_files}'

def block(loc, freq, pri, alts=None):
    s = f'  <url>\n    <loc>{loc}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n'
    for lang, href in (alts or []):
        s += f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{href}"/>\n'
    return s + '  </url>\n'

new = []
# directories
new.append(block(f'{BASE}/dupes/', 'weekly', '0.9',
                 [('en', f'{BASE}/dupes/'), ('es', f'{BASE}/dupes-es/')]))
new.append(block(f'{BASE}/dupes-es/', 'weekly', '0.8',
                 [('en', f'{BASE}/dupes/'), ('es', f'{BASE}/dupes-es/')]))
# entry pages
for sl in sorted(en_files):
    alts = None
    if sl in es_files:
        alts = [('en', f'{BASE}/dupes/{sl}'), ('es', f'{BASE}/dupes-es/{sl}')]
    new.append(block(f'{BASE}/dupes/{sl}', 'monthly', '0.8', alts))
for sl in sorted(es_files):
    new.append(block(f'{BASE}/dupes-es/{sl}', 'monthly', '0.7',
                     [('en', f'{BASE}/dupes/{sl}'), ('es', f'{BASE}/dupes-es/{sl}')]))

# trust pages, EN/ES paired
for en, es in (('about', 'acerca-de'), ('disclosure', 'divulgacion'), ('privacy', 'privacidad')):
    for slug in (en, es):
        new.append(block(f'{BASE}/{slug}/', 'yearly', '0.4',
                         [('en', f'{BASE}/{en}/'), ('es', f'{BASE}/{es}/')]))

# brand directory pages, EN/ES paired
import os as _os
_bd = '/home/claude/brands'
if _os.path.isdir(_bd):
    new.append(block(f'{BASE}/brands/', 'weekly', '0.8',
                     [('en', f'{BASE}/brands/'), ('es', f'{BASE}/marcas/')]))
    new.append(block(f'{BASE}/marcas/', 'weekly', '0.7',
                     [('en', f'{BASE}/brands/'), ('es', f'{BASE}/marcas/')]))
    for b in sorted(d for d in _os.listdir(_bd) if _os.path.isdir(_os.path.join(_bd, d))):
        alts = [('en', f'{BASE}/brands/{b}/'), ('es', f'{BASE}/marcas/{b}/')]
        new.append(block(f'{BASE}/brands/{b}/', 'weekly', '0.8', alts))
        new.append(block(f'{BASE}/marcas/{b}/', 'weekly', '0.7', alts))

dupe_locs = set(re.findall(r'<loc>([^<]+)</loc>', ''.join(new)))
clash = dupe_locs & locs
assert not clash, f'would duplicate existing URLs: {clash}'

out = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
       '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
       + ''.join(existing) + ''.join(new) + '</urlset>\n')
open(OUT, 'w', encoding='utf-8').write(out)

n = out.count('<url>')
assert n == len(existing) + len(new), 'url count mismatch'
print(f'sitemap: {len(existing)} existing (unchanged) + {len(new)} dupe URLs = {n} total')
print(f'  /dupes/ pages: {len(en_files)} + index')
print(f'  /dupes-es/ pages: {len(es_files)} + index')
print(f'  hreflang pairs: {len(es_files) + 1}')
