# Article Maintenance Protocols

**Location:** `github.com/raven6724/decodedscents/ARTICLE_PROTOCOLS.md`
**Site:** `decodedscents.com`
**Created:** 2026-07-07

---

## Why These Protocols Exist

Articles are DecodedScents' long-form editorial content — curator deep-dives and roundup/deals pieces — published bilingually (English/Spanish) and cross-linked with the `worker.js` dupe database. Getting them wrong costs more than a typo: a wrong fact ships to readers in two languages, and a DB/article mismatch breaks the site's core promise of curator honesty.

**Failure modes we have already experienced:**

1. **Wrong target fragrance used in research** — the Afnan 9PM piece initially used "Le Male" instead of the correct "Ultra Male" as the target. Caught before publish. Carlos required a reshoot of the research, not a reframe of the existing draft.

This list starts short and grows honestly — see Section 7 (Incident Log). We do not backfill incidents we didn't record at the time; we only log what actually gets caught going forward.

---

## 1. Article Types

Two confirmed article types exist. If a third type emerges, this section gets revised.

### 1.1 Brand Deep-Dive (Tiered)

Used for curator deep-dives on a single brand or fragrance family (e.g., the Afnan article).

**Structure:**
- Opening essay / brand introduction
- Tiered sections:
  - 🟢 **Real Dupes** — meets the 85% rule, goes in VERIFIED_DB
  - 🟡 **Inspired-By Interpretations** — lacks a clean single target, article-only
  - 🔴 **Cautionary Tales** — doesn't actually match its claimed target, article-only
- Closing section
- Cross-reference callouts to related articles/DB entries

### 1.2 Roundup / Deals

Used for time-sensitive or comparison-driven pieces (e.g., "Best Prime Day Fragrance Dupe Deals 2026").

**Structure:**
- Quick Comparison table (up top, before any prose — this is the scannable answer for readers who won't read further)
- Numbered Deep Dive cards, one per fragrance (original + dupe)
- FAQ section
- "Keep Exploring" section
- Final CTA

---

## 2. Length & Scannability (Standing Concern)

**Reader behavior signal:** people are not finishing long articles. This is an active, ongoing concern — not yet a fixed rule, but a direction to keep pushing on with every new article and revision pass:

- Lead with the comparison table / answer, always — never make a skimmer scroll past prose to get the one fact they came for
- Keep per-fragrance deep-dive prose tight — 1-2 sentences per side (original / dupe) as a target, not the 3-4 sentence norm from earlier articles
- Consider moving performance caveats and sourcing detail into a collapsible/toggle element so skimmers aren't forced past it, while readers who want the substance can still get it
- This is a direction, not a locked spec — revisit and tighten further as we ship more articles and see what actually keeps readers on the page

### 2.1 Reference Point — The Compressed Deep-Dive (2026-07-27)

The Rayhaan article is the first deliberately compressed Brand Deep-Dive and is the current benchmark. **~1,588 words, ~5 minute read, against the Afnan piece's ~16 minutes** — roughly a third the length covering more fragrances (twelve versus seven).

What made that possible:

- **The comparison table carries every entry** and sits in the first screen, before any prose. A skimmer gets the complete answer without scrolling.
- **Cards are grouped, not one-per-fragrance.** The three 91% dupes share one card, the three Louis Vuitton clones share another, the four designer targets share a third. Individual cards were reserved for the two entries sitting at the 85% floor — where a buyer genuinely needs the reasoning — plus the exclusions.
- **The exclusions carry the piece.** Tier 3 explains *why* each candidate failed. That is the section no competitor will copy, because most of them have no floor to fail against.

**The grouping rule:** give a fragrance its own card when a reader needs to make a decision about it. Otherwise let the table speak. Twelve individual cards would have tripled the length and added nothing a skimmer would read.

---

## 3. Publishing Checklist

Every new article requires:

- [ ] Article HTML file itself — **uploaded, not created** (see §3.1)
- [ ] Filename verified character-for-character against the `index.html` link (see §3.1)
- [ ] `index.html` article card added
- [ ] `sitemap.xml` updated (see §3.3)
- [ ] OG image created (SVG + PNG, 1200×630) — **one per language** (see §3.2)
- [ ] OG image files uploaded to `assets/og/` and confirmed loading in a browser
- [ ] hreflang tags added for the bilingual pair (EN/ES), using **translated slugs**
- [ ] Manual sitemap submission to **Google Search Console**
- [ ] Manual sitemap submission to **Bing Webmaster Tools**
- [ ] Social preview re-scraped on Facebook, X and LinkedIn (each caches separately)

### 3.1 File Upload Rules

**Upload article files. Do not use GitHub's "Create new file".** Creating a file means typing the filename by hand, and the filename that gets typed tends to be the article's display title rather than its slug. See §7, 2026-07-27.

**The filename must match the `index.html` link exactly** — all lowercase, hyphens not spaces, `.html` extension present. GitHub Pages is case-sensitive.

```
index.html links to:  Articles/decoded-rayhaan-dupes-15-tested-12-cleared
file must be named:   decoded-rayhaan-dupes-15-tested-12-cleared.html
```

**Verify by clicking the card on the live homepage, not by looking at the repo.** A mismatched filename renders a perfect homepage and 404s on click — the failure is invisible until someone tries to read the article.

**Spanish articles use translated slugs, not an `-es` suffix.** Existing convention: `por-que-los-dupes-tom-ford-private-blend-son-mas-dificiles`, not `why-tom-ford...-es`. The `hreflang` pair must point at the real translated slug or it promises Google a URL that does not exist.

### 3.2 OG Image Spec

1200×630, PNG for the meta tags plus SVG for the archive, at `assets/og/`. **One image per language** — a Spanish article sharing the English card looks unfinished.

**Measure the text; do not position it by eye.** Spanish runs roughly 15–25% longer than English for the same content. A layout that fits in English will overflow in Spanish — headline off the canvas, labels bleeding past their pills. Auto-fit the type to the content column and verify the rendered result rather than trusting the source.

**Check for elements that share a row.** If a pill row and a URL sit on the same line, size the pills against the column *minus* the URL width. Sizing against the full column works right up until a longer label collides.

### 3.3 Sitemap

**Derive `sitemap.xml` from `index.html`'s article cards** rather than maintaining a list by hand — the same reasoning as deriving `BRAND_INDEX` from `VERIFIED_DB` in `WORKER_PROTOCOLS.md`. A hand-kept list drifts the first time an article ships and the list is not updated.

Include `xhtml:link` hreflang alternates for every EN/ES pair. **Only pair articles that are genuinely translations** — a wrong pairing tells Google two unrelated pages are versions of each other.

Set `lastmod` only where the real date is known. Stamping today's date across every URL tells Google the whole site changed.

**Article-Driven Update Trigger** (see also `WORKER_PROTOCOLS.md` §10): every article publish triggers a same-session `worker.js` DB review. For every fragrance the article recommends as a dupe, check whether it's already in the DB and whether the DB's classification matches the article's. Do not defer this — the SNOI/Aventus contradiction happened specifically because this review was delayed.

---

## 4. Fact-Verification Standard

**Same strictest standard applies across both the DB and articles — no lighter bar for editorial/long-form content.**

- **Source hierarchy:** brand-official > Fragrantica/Basenotes/Parfumo > enthusiast/Reddit
- **Multiple independent sources required** wherever possible before a fact is locked (perfumer credits, release dates, match claims)
- Same rigor as `WORKER_PROTOCOLS.md` §12.7 Non-Fabrication Check: every claim must be traceable to a real, identifiable source
- If our own research contradicts an existing DB entry or a prior article, the newer, better-sourced research takes precedence — and the older content gets corrected, not left standing

---

## 5. Proofread & Sign-Off Protocol

### 5.1 Confidence-Based Fix Rule

- **High confidence** (typos, spelling, punctuation, mechanical grammar): fix inline without waiting for approval
- **Lower confidence** (factual claims, structural changes, tone shifts, anything 🔴 High Priority): surface the full list first, get explicit sign-off before touching the article

Same severity levels as `WORKER_PROTOCOLS.md`:
- 🔴 HIGH PRIORITY — grammar errors, factual errors, contradictions with the DB or other articles
- 🟡 MEDIUM PRIORITY — awkward phrasing, missing context, stale information
- 🟢 LOW PRIORITY — consistency issues, minor stylistic improvements

### 5.2 Drafting vs. Proofreading

- **Drafting is iterative.** Building/editing an article section-by-section, going back to revise a part, adding a section later — all normal, no batching rule applies here.
- **The proofread pass is one batch.** Walk the entire article first, log every issue found, then apply all fixes together in one pass — not one-by-one as each is spotted. Same reasoning as `WORKER_PROTOCOLS.md` §6.1: every touch is a chance to introduce a new error, so fixes get bundled.

### 5.3 Bilingual Requirement

Full grammatical proofread required for every article, in both English and Spanish, before shipping. No exceptions.

---

## 6. Spanish Terminology Glossary

Living document. Starts empty except for confirmed corrections; grows every time a translation correction pattern is caught during a Spanish proofread pass.

| Incorrect | Correct | Notes |
|---|---|---|
| materiales primas | materias primas | Caught during Tom Ford Private Blend ES translation proofread |
| puntan | puntúan | Verb *puntuar* takes the accent in the third person plural. Caught in Rayhaan ES proofread |
| pesar (la evidencia) | sopesar (la evidencia) | *Pesar* is physical weight; *sopesar* is weighing up evidence. Rayhaan ES |
| se vende contra X | se vende como alternativa a X | Calque of "marketed against". Rayhaan ES |
| fuera de blanco | fuera del objetivo | Calque of "off-target"; *fuera de blanco* is not idiomatic. Rayhaan ES |

**Watch for English calques generally.** The Rayhaan proofread caught four in one article, all of them grammatically valid Spanish that no native speaker would write — "un pozo profundo de comparaciones del cual beber" for *a deep well to draw on* being the clearest. Idioms translate badly; rewrite the thought rather than the words.

**Check gender agreement across the whole article, including the JSON-LD.** A pronoun referring to a fragrance must agree consistently. If an FAQ answer appears in both the rendered page and the schema, **both copies must change together** or the schema stops matching the page and Google flags it.

---

## 7. Incident Log

Living document. We do not backfill incidents that weren't recorded at the time — this starts with the one confirmed incident and grows from real events going forward, the same way `WORKER_PROTOCOLS.md`'s "Why These Protocols Exist" section is built from specific real failures.

### 2026 — Le Male / Ultra Male Mixup

**What happened:** During Afnan 9PM research, the wrong target fragrance ("Le Male" instead of "Ultra Male") was used as the comparison target.

**How it was caught:** Carlos caught the error before publish.

**Resolution:** Full reshoot of the research against the correct target — not a reframe of the existing draft. Verified facts must be sourced and locked to the *correct* subject before publication, not adjusted after the fact to fit what was already written.

### 2026-07-27 — Article Filenames Created Rather Than Uploaded

**What happened:** Both Rayhaan articles (EN and ES) were added to `Articles/` using GitHub's **Create new file** rather than **Upload files**. The filenames were typed from the articles' display titles instead of their slugs, producing:

```
Decoded rayhaan dupes 15 tested 12 cleared
Probamos 15 dupes rayhaan doce superaron el 85
```

against the required:

```
decoded-rayhaan-dupes-15-tested-12-cleared.html
probamos-15-dupes-rayhaan-doce-superaron-el-85.html
```

Three faults at once — capitalised first letter, spaces instead of hyphens, and no `.html` extension.

**How it was caught:** Carlos clicked through from the live homepage and got a 404. **The homepage itself rendered perfectly**, because the cards only need the link text to be correct, not the target to exist. Nothing in the repo looked wrong at a glance; the file list was the only place the problem was visible.

**Diagnosis:** the repo folder listing showed the two new files formatted differently from every other article in the directory. The commit messages read "Create …" where every other article read "Upload …" or "Update …", which identified the cause directly.

**Resolution:** both files renamed via the pencil/edit icon. Verified with a live click-through rather than a repo inspection.

**Rules added:** §3.1 — upload rather than create, verify the filename character-for-character against the `index.html` link, and confirm by clicking the live card. Recorded because this failure is silent: the site looks fully published and only fails at the moment a reader tries to read something.

---

*End of protocols.*
