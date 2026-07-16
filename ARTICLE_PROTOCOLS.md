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

---

## 3. Publishing Checklist

Every new article requires:

- [ ] Article HTML file itself
- [ ] `index.html` article card added
- [ ] `sitemap.xml` updated
- [ ] OG image created (SVG + PNG, 1200×630)
- [ ] hreflang tags added for the bilingual pair (EN/ES)
- [ ] Manual sitemap submission to **Google Search Console**
- [ ] Manual sitemap submission to **Bing Webmaster Tools**

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

---

## 7. Incident Log

Living document. We do not backfill incidents that weren't recorded at the time — this starts with the one confirmed incident and grows from real events going forward, the same way `WORKER_PROTOCOLS.md`'s "Why These Protocols Exist" section is built from specific real failures.

### 2026 — Le Male / Ultra Male Mixup

**What happened:** During Afnan 9PM research, the wrong target fragrance ("Le Male" instead of "Ultra Male") was used as the comparison target.

**How it was caught:** Carlos caught the error before publish.

**Resolution:** Full reshoot of the research against the correct target — not a reframe of the existing draft. Verified facts must be sourced and locked to the *correct* subject before publication, not adjusted after the fact to fit what was already written.

---

*End of protocols.*
