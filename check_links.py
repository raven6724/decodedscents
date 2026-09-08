#!/usr/bin/env python3
"""
check_links.py — every product must give the reader somewhere to buy   (2026-08-20)

Run this BEFORE packaging, alongside check_spanish.py.

WHY IT EXISTS. Delina Exclusif and Bois Imperial both shipped with nothing but a
Fragrantica reference link. A reader who reads a page, believes it, and wants the
fragrance then has nowhere to go -- and the site earns nothing either. That is a
worse failure than a thin entry, because the work of researching it is already done
and simply wasted at the last step.

WHAT COUNTS AS A BUY LINK
  amazonLink        Amazon, must be /dp/ASIN with the affiliate tag
  fragranceNetLink  FragranceNet or Shop Simon via Rakuten, must be wrapped
  shopSimonLink     as above
  directLink        the brand's own shop, or a real retailer. Earns nothing on its
                    own and that is fine: a reader who can buy beats a reader who
                    bounces, and unpaid links are disclosed on /disclosure/.

WHAT DOES NOT COUNT
  fragranticaQuery  a reference, not a shop.

An honest empty is still allowed -- some products genuinely are not sold anywhere
findable. But it has to be a decision, not an oversight, so record it in
SKIP_NO_RETAILER below with the reason. The checker then stops complaining about it
and the exception is visible in the file rather than forgotten.
"""
import json, re, sys, subprocess, os

TAG = 'decodedscents-20'
WORK = os.path.dirname(os.path.abspath(__file__))

# product -> why no buy link exists. Reviewed and accepted, not forgotten.
SKIP_NO_RETAILER = {
    ('Cyrus Parfums', 'Chancellor Ultimate EDP'):
        'No stable US retailer. Not on Amazon or FragranceNet; only intermittent '
        'overseas marketplace listings. Product and target both verified. The entry '
        'warns the reader it is hard to find. Reviewed 2026-08.',
}

BUY_FIELDS = ('amazonLink', 'fragranceNetLink', 'shopSimonLink', 'perfumaniaLink', 'brandLink', 'directLink')


def main():
    db = json.loads(subprocess.check_output(
        ['node', os.path.join(WORK, 'dump.js'), os.path.join(WORK, 'worker_live.js')]).decode())

    missing, malformed = [], []
    for key, v in db.items():
        items = [('original', v['original'])] + [('dupe', d) for d in (v.get('dupes') or [])]
        for kind, p in items:
            ident = (p.get('brand', ''), p.get('name', ''))
            links = {f: p[f] for f in BUY_FIELDS if p.get(f)}

            # an Amazon link that is a search URL, or missing the tag, earns nothing
            a = links.get('amazonLink')
            if a:
                if '/s?k=' in a or '/s/ref=' in a:
                    malformed.append((key, kind, ident, 'Amazon SEARCH url, not /dp/'))
                elif TAG not in a:
                    malformed.append((key, kind, ident, 'Amazon link without the affiliate tag'))
                elif not re.search(r'/dp/[A-Z0-9]{10}', a):
                    malformed.append((key, kind, ident, 'Amazon link is not /dp/ASIN'))

            # Rakuten links must actually be wrapped or they pay nothing
            # perfumaniaLink is wrapped at RENDER time by index.html, so a
            # pre-wrapped value here would be wrapped twice and would not track.
            pf = links.get('perfumaniaLink')
            if pf and 'tkqlhce.com' in pf:
                malformed.append((key, kind, ident, 'perfumaniaLink is pre-wrapped; store the raw product URL'))

            for f in ('fragranceNetLink', 'shopSimonLink'):
                u = links.get(f)
                if u and 'linksynergy.com' not in u:
                    malformed.append((key, kind, ident, f'{f} is not Rakuten-wrapped'))

            if not links and ident not in SKIP_NO_RETAILER:
                missing.append((key, kind, ident, p.get('similarity')))

    if malformed:
        print(f'MALFORMED LINKS: {len(malformed)}\n')
        for key, kind, (b, n), why in malformed:
            print(f'  [{kind}] {b} {n} @ {key}\n      {why}')
        print()

    if missing:
        print(f'NO BUY LINK: {len(missing)} product(s) give the reader nowhere to go\n')
        for key, kind, (b, n), sim in sorted(missing, key=lambda r: (r[1] != 'original', r[0])):
            s = f'  ({sim}%)' if sim else ''
            print(f'  [{kind:8s}] {b} {n}{s}\n      on: {key}')
        print('\nAdd a link, or record the product in SKIP_NO_RETAILER with a reason.')

    if not missing and not malformed:
        print(f'CLEAN — every product in {len(db)} entries has a working buy link.')
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
