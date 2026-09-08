# Build scripts

The generators and checkers that build decodedscents.com. These are **tools**, not
site content — nothing here is deployed.

## Do NOT commit `worker.js` or `worker_live.js` to this repo

The worker carries a live Anthropic key and a live Together AI key in plain text,
around lines 8 and 9. **This repository is public.**

On 2026-09-01 we confirmed the worker had never been committed, so the keys had
never been exposed. On 2026-09-04 a packaged bundle of "repo files" included
`worker_live.js` by mistake and GitHub's secret scanning blocked the push. That
scanner is the only thing that stopped it.

**If a push is ever blocked with "Anthropic API Key detected": cancel it.**
Do not click "Allow Secret". Find the file, remove it, push again.

The scripts read the worker from a local path at build time. It never needs to be
in version control.

## What runs when

Any change to the database:

    prep_es_batch2.py        reshape DB + merge Spanish glossaries — READ ITS OUTPUT
    build_dupe_pages_es.py   /dupes-es/
    build_dupe_pages.py      /dupes/
    run_indexes.py           both directory indexes
    build_brand_pages.py     /brands/ and /marcas/
    build_es_home.py         /es/  (needs the CURRENT Index.html)
    build_sitemap.py         sitemap.xml

Before packaging anything, all three:

    check_links.py     every product has a working buy link
    check_shared.py    sharedNotes verify on both sides, family-aware
    check_spanish.py   register, calque, typography

`prep_es_batch2.py` exits without writing when it fails, and the page builders will
then run on stale data — shipping an English page with four dupes and a Spanish one
with two. Read its output before continuing.

See `WORKER_PROTOCOLS.md` §12.22 for what each checker can and cannot catch.
