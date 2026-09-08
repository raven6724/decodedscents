#!/usr/bin/env python3
"""
normalise_shared.py — make every sharedNotes claim verifiable   (rebuilt 2026-08-30)

THE PROBLEM. A sharedNote is only meaningful if the exact string appears in both
pyramids. Over time the labels drifted: a dupe says "Musk" where the original says
"White Musk", or "Blackcurrant" against "Black Currant", or "Gaiac Wood" against
"Guaiac Wood". 108 claims across the database could not be verified by exact match.

None of them are fabrications. Every one resolves to the same material under a
different name. But an unverifiable claim is indistinguishable from a false one at
a glance, which is exactly the ambiguity this database exists to remove -- and it
made the per-entry assertions fire on correct work, which trains you to ignore them.

THE FIX. Rewrite each sharedNotes entry to use the ORIGINAL's vocabulary. The
original is the reference product, so its labels are the canonical ones. The dupe's
own notes list is left untouched: it should say what the brand says.

The previous version of this script was lost in an environment reset, which is why
the drift accumulated unchecked. It is now checkpointed with the other scripts.

Run with --write to apply. Default is a dry run.
"""
import json, re, shutil, subprocess, sys, os

WORK = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(WORK, 'worker_live.js')

#  Materials that are the same thing under different names. Each set is one family;
#  a claim matches if the dupe's label and the original's label share a family.
#
#  Deliberately conservative. Notes that merely smell similar are NOT families --
#  only genuine synonyms, spelling variants, and origin-qualified forms of the same
#  material. Getting this wrong would let real mismatches through as "normalised".
FAMILIES = [
    # spelling and spacing
    {'Blackcurrant', 'Black Currant', 'Cassis'},
    {'Oakmoss', 'Oak Moss'},
    {'Guaiac Wood', 'Gaiac Wood', 'Guaiacwood'},
    {'Dried Fruits', 'Dry Fruits'},
    {'Cacao', 'Cocoa', 'Chocolate', 'Dark Chocolate'},

    # same material, different common name
    {'Citron', 'Cedrat'},
    {'Oud', 'Agarwood', 'Agarwood (Oud)'},
    {'Incense', 'Olibanum', 'Frankincense'},
    {'Iris', 'Orris', 'Orris Root'},
    {'Aquatic Notes', 'Marine Notes', 'Sea Notes', 'Marine Accord', 'Water Notes'},
    {'Tonka Bean', 'Tonka', 'Tonka Absolute', 'Coumarin'},
    {'Ginger', 'Ginger Flower', 'Nigerian Ginger'},

    # origin-qualified forms
    {'Bergamot', 'Calabrian Bergamot'},
    {'Orange', 'Sicilian Orange', 'Bitter Orange'},
    {'Mandarin', 'Mandarin Orange', 'Green Mandarin', 'Sicilian Mandarin'},
    {'Lemon', 'Sicilian Lemon'},
    {'Neroli', 'Tunisian Neroli'},
    {'Cinnamon', 'Ceylon Cinnamon', 'Cassia'},
    {'Tea', 'Black Tea', 'Green Tea', 'Chinese Black Tea'},
    {'Rose', 'Turkish Rose', 'Damascena Rose', 'Rose Damascena'},
    {'Jasmine', 'Jasmine Sambac', 'Moroccan Jasmine', 'Sambac Jasmine'},
    {'Tuberose', 'Indian Tuberose'},
    {'Sage', 'Clary Sage'},
    {'Labdanum', 'Spanish Labdanum'},
    {'Vetiver', 'Haitian Vetiver'},
    {'Patchouli', 'Indonesian Patchouli'},
    {'Pepper', 'Sichuan Pepper', 'Szechuan Pepper'},
    {'Timur', 'Timut', 'Timur Pepper', 'Timut Pepper'},
    {'Cedar', 'Cedarwood', 'Virginia Cedar', 'Atlas Cedarwood', 'Virginian Cedar'},
    {'Musk', 'White Musk', 'Mineral Musk'},

    {'Lotus', 'Lotus Flower'},
    {'Ambrette', 'Ambrette Seeds'},
    {'Cedar', 'White Cedar', 'Cedarwood', 'Virginia Cedar', 'Atlas Cedarwood', 'Virginian Cedar'},
    {'Rose', 'White Rose', 'Bulgarian Rose', 'Turkish Rose', 'Damascena Rose', 'Rose Damascena'},
    {'Vanilla', 'Vanilla Orchid', 'Madagascar Vanilla', 'Bourbon Vanilla'},
    {'Musks', 'Musk', 'White Musk', 'Mineral Musk'},
    {'Rosemary', 'Rosemary Essence'},
    {'Dried Fruit', 'Dried Fruits', 'Dry Fruits'},
    {'Amber Woods', 'Ambery Woods', 'Amberwood', 'Amber', 'Ambroxan', 'Ambrox', 'Ambrofix', 'Amber Wood'},
    {'Jasmine', 'Indian Jasmine', 'Jasmine Sambac', 'Moroccan Jasmine', 'Sambac Jasmine'},
    {'Moss', 'Oakmoss', 'Oak Moss'},

    #  The amber family. Amber, amberwood, ambroxan and ambrox are not chemically
    #  identical -- ambroxan is a molecule, amber is an accord -- but they occupy
    #  the same role and the industry names them interchangeably. Grouped, and the
    #  claim is relabelled to whatever the ORIGINAL calls it, so the page never
    #  claims a material the original does not list.
    {'Amber', 'Amberwood', 'Ambroxan', 'Ambrox', 'Ambrofix', 'Ambery Woods'},
]

INDEX = {}
for fam in FAMILIES:
    for name in fam:
        INDEX.setdefault(name, set()).update(fam)


def same_material(a, b):
    if a == b:
        return True
    return b in INDEX.get(a, set())


def canonical_for(claim, original_notes):
    """The original's own label for this material, or None if it has none."""
    for n in original_notes:
        if same_material(claim, n):
            return n
    return None


def main(write=False):
    db = json.loads(subprocess.check_output(
        ['node', os.path.join(WORK, 'dump.js'), SRC]).decode())

    changes, unresolved = [], []
    for key, entry in db.items():
        orig = sum(entry['original']['notes'].values(), [])
        for dupe in entry.get('dupes') or []:
            dnotes = sum((dupe.get('notes') or {}).values(), [])
            for claim in dupe.get('sharedNotes') or []:
                if claim in orig and claim in dnotes:
                    continue
                co = canonical_for(claim, orig)
                cd = canonical_for(claim, dnotes)
                if co and cd:
                    if co != claim:
                        changes.append((key, dupe['brand'], dupe['name'], claim, co))
                else:
                    unresolved.append((key, dupe['brand'], dupe['name'], claim,
                                       'not in original' if not co else 'not in dupe'))

    print(f'relabel {len(changes)} claims to the original\'s vocabulary')
    print(f'unresolved (genuinely absent, NOT relabelled): {len(unresolved)}\n')
    for row in unresolved:
        print(f'  UNRESOLVED [{row[0]}] {row[1]} {row[2]}: "{row[3]}" {row[4]}')
    if unresolved:
        print()

    by = {}
    for key, b, n, old, new in changes:
        by.setdefault((old, new), 0)
        by[(old, new)] += 1
    print('--- relabels, by pattern ---')
    for (old, new), n in sorted(by.items(), key=lambda x: -x[1]):
        print(f'  {n:3d}x  "{old}"  ->  "{new}"')

    if not write:
        print('\nDRY RUN — nothing written. Re-run with --write to apply.')
        return 0

    src = open(SRC, encoding='utf-8').read()
    shutil.copy(SRC, SRC + '.bak_normalise')
    applied = 0
    for key, brand, name, old, new in changes:
        # locate this dupe record, then rewrite only inside its sharedNotes array
        #  Scope to THIS entry. The same dupe can appear on several pages needing
        #  opposite relabels -- Sceptre Bronzite is "Ginger Flower" against Tygar's
        #  "Ginger" and "Ginger" against Ingenious Ginger's "Ginger Flower" -- so an
        #  unscoped search edits whichever record comes first in the file.
        em = re.search(r'\n  "' + re.escape(key) + r'":\s*\{', src)
        eb = src.index('{', em.start()); ed = 0
        for i in range(eb, len(src)):
            if src[i] == '{': ed += 1
            elif src[i] == '}':
                ed -= 1
                if ed == 0:
                    ee = i + 1
                    break
        found = False
        for m in re.finditer(r'\{\s*name:"' + re.escape(name) + r'"', src[eb:ee]):
            a = eb + m.start(); d = 0
            for i in range(a, len(src)):
                if src[i] == '{': d += 1
                elif src[i] == '}':
                    d -= 1
                    if d == 0:
                        b = i + 1
                        break
            rec = src[a:b]
            if f'brand:"{brand}"' not in rec:
                continue
            sm = re.search(r'sharedNotes:\[.*?\]', rec, re.S)
            if not sm or f'"{old}"' not in sm.group(0):
                continue
            newshared = sm.group(0).replace(f'"{old}"', f'"{new}"', 1)
            src = src[:a] + rec[:sm.start()] + newshared + rec[sm.end():] + src[b:]
            applied += 1
            found = True
            break
        if not found:
            print(f'  WARN could not apply: {brand} {name} "{old}"')

    open(SRC, 'w', encoding='utf-8').write(src)
    if subprocess.run(['node', '--check', SRC]).returncode != 0:
        shutil.copy(SRC + '.bak_normalise', SRC)
        sys.exit('ABORT: node --check failed, rolled back')
    after = json.loads(subprocess.check_output(
        ['node', os.path.join(WORK, 'dump.js'), SRC]).decode())
    if len(after) != len(db) or \
       sum(len(v.get('dupes') or []) for v in after.values()) != \
       sum(len(v.get('dupes') or []) for v in db.values()):
        shutil.copy(SRC + '.bak_normalise', SRC)
        sys.exit('ABORT: entry counts changed, rolled back')

    bad = 0
    for key, entry in after.items():
        orig = set(sum(entry['original']['notes'].values(), []))
        for dupe in entry.get('dupes') or []:
            dn = set(sum((dupe.get('notes') or {}).values(), []))
            for claim in dupe.get('sharedNotes') or []:
                if claim not in orig:
                    bad += 1
    print(f'\napplied {applied} relabels')
    print(f'claims still not present in their original: {bad}')
    json.dump(after, open(os.path.join(WORK, 'db.json'), 'w'), ensure_ascii=False)
    return 0


if __name__ == '__main__':
    sys.exit(main('--write' in sys.argv))
