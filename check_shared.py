#!/usr/bin/env python3
"""check_shared.py — verify every sharedNotes claim, family-aware.

A shared note is valid when the original AND the dupe each list that material,
under whatever name their own source uses. Requiring the identical string on both
sides is too strict: Arabiyat Aristo publishes "Ginger Flower" where Sospiro
Vibrato publishes "Ginger". Same material, two vocabularies.

We do NOT rewrite a dupe's pyramid to match its original -- the dupe should say
what its own brand says.
"""
import json, re, subprocess, sys, os
WORK = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(WORK, 'normalise_shared.py'), encoding='utf-8').read()
ns = {'re': re}
exec(src[src.index('FAMILIES = ['):src.index('def same_material')], ns)
INDEX = {}
for fam in ns['FAMILIES']:
    for n in fam:
        INDEX.setdefault(n, set()).update(fam)

def same(a, b):
    return a == b or b in INDEX.get(a, set())

def main():
    db = json.loads(subprocess.check_output(
        ['node', os.path.join(WORK, 'dump.js'), os.path.join(WORK, 'worker_live.js')]).decode())
    exact = family = 0
    bad = []
    for key, entry in db.items():
        orig = sum(entry['original']['notes'].values(), [])
        for dupe in entry.get('dupes') or []:
            dn = sum((dupe.get('notes') or {}).values(), [])
            for claim in dupe.get('sharedNotes') or []:
                if claim in orig and claim in dn:
                    exact += 1
                elif any(same(claim, x) for x in orig) and any(same(claim, y) for y in dn):
                    family += 1
                else:
                    side = 'original' if not any(same(claim, x) for x in orig) else 'dupe'
                    bad.append((key, dupe['brand'], dupe['name'], claim, side))
    print(f'exact on both sides : {exact}')
    print(f'family-equivalent   : {family}')
    if bad:
        print(f'\nBROKEN: {len(bad)}\n')
        for k, b, n, c, s in bad:
            print(f'  [{k}] {b} {n}: "{c}" missing from the {s}')
        return 1
    print('\nCLEAN — every sharedNotes claim verifies on both sides.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
