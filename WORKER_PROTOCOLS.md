# worker.js Maintenance Protocols

**Location:** `github.com/raven6724/decodedscents/WORKER_PROTOCOLS.md`
**Live Worker:** `decodedscents.cfe1585.workers.dev`
**Last updated:** 2026-07-02

---

## Why These Protocols Exist

`worker.js` is the primary functional file of decodedscents.com — it powers the dupe search that is the site's core value proposition. When this file breaks, the site's central feature stops working.

**Failure modes we have already experienced or narrowly avoided:**

1. **Truncation from incremental edits** — repeated string-replacement chains have corrupted the file in prior sessions, requiring full manual recovery from the live Cloudflare source.
2. **Broken JavaScript syntax from mismatched braces** — on the first Afnan article DB update attempt, a Python transformation script consumed the closing brace of the previous last entry, invalidating the entire file. Caught pre-deployment via `node --check` only.
3. **Contradictory data between DB and published articles** — before the Afnan article DB update, the site listed Supremacy Not Only Intense at 88% match to Creed Aventus, directly contradicting the article's Tier 3 Cautionary Tale classification.
4. **Interconnected data structure oversight** — VERIFIED_DB, ALIASES, and DUPE_TO_ORIGINAL are three separate tables that must be updated together. Missing an ALIASES or DUPE_TO_ORIGINAL entry means the dupe exists in the DB but users can't find it via search.
5. **Guessed retailer URLs producing 404 links** — early plans for FragranceNet URLs relied on pattern-matching against other entries. All guessed URLs must be verified before deployment or omitted.

These protocols exist to make sure none of these failure modes repeat.

---

## 1. File Architecture

The file is one JavaScript module (~398KB / ~3,925 lines) organized into these structures, in order of appearance:

| Section | Purpose | Approx. lines |
|---------|---------|---------------|
| Constants | API keys for Anthropic and Together | 1-10 |
| **VERIFIED_DB** | The core fragrance database. Keys are target-fragrance strings (lowercase), values are `{original, dupes}` objects. | 13-1620 |
| `normalize(q)` | Search query normalization | 1622-1641 |
| **ALIASES** | Short-name → target mapping. When someone searches "sauvage" it maps to "dior sauvage". | 1644-2449 |
| `lookupVerified(query)` | The DB lookup function | 2451-2479 |
| **STANDALONE_FRAGRANCES** | Small object for fragrances that stand alone without target mapping | 2484-2489 |
| **DUPE_TO_ORIGINAL** | Reverse lookup: dupe-name → target. When someone searches "opus noir" it maps to "xerjoff opera". | 2495-3538 |
| `lookupAsDupe(query)` | The dupe reverse-lookup function | 3540-3623 |
| `SYSTEM_PROMPT` | Claude Haiku prompt for AI fallback | 3625-3644 |
| `buildImagePrompt` | Image generation prompt builder | 3646-3673 |
| `CORS` | CORS header config | 3676-3681 |
| `repairJSON` | JSON repair utility | 3683-3695 |
| Main handler | The `export default { fetch }` request handler | 3697-3857 |
| `json` helper | Response helper | 3859-end |

**Key insight for any DB update:** VERIFIED_DB, ALIASES, and DUPE_TO_ORIGINAL are interconnected. Adding a new fragrance to VERIFIED_DB without also updating ALIASES and DUPE_TO_ORIGINAL means users can only find it if they type the exact target key. That is not acceptable.

---

## 2. Change Categorization

Every worker.js modification falls into one of these categories. Each has its own protocol.

| Category | Description | Required data structure updates |
|----------|-------------|--------------------------------|
| **A. New Target Fragrance** | Adding a new original fragrance and at least one dupe. Example: adding "creed aventus absolu" | VERIFIED_DB + ALIASES + DUPE_TO_ORIGINAL |
| **B. New Dupe for Existing Target** | Adding a dupe to a target that's already in VERIFIED_DB. Example: adding Thameen Carved Oud to Tom Ford Oud Wood | VERIFIED_DB + DUPE_TO_ORIGINAL |
| **C. Correction of Existing Entry** | Fixing a match percentage, notes, or `whySimilar` text on an existing entry | VERIFIED_DB only |
| **D. Removal of Existing Entry** | Removing a dupe or target that no longer qualifies. Example: removing SNOI from Creed Aventus dupes | VERIFIED_DB + ALIASES + DUPE_TO_ORIGINAL |
| **E. URL Patching** | Adding a verified FragranceNet URL to an entry that lacked one | VERIFIED_DB only |
| **F. Bug Fix / Function Change** | Modifying the JavaScript logic (search, lookup, handler) | Function code only, no data changes |

**All categories require the same pre-change protocol.** Different categories have different execution complexity but the same safety requirements.

---

## 3. The 85% Rule — What Qualifies for VERIFIED_DB

**Only entries meeting these criteria go into VERIFIED_DB:**

1. **85% or higher similarity** to a specific single-target designer/niche fragrance
2. **Verified by multiple community sources** (Fragrantica, Parfumo, Basenotes, Reddit r/fragrance, reviewer accounts we trust)
3. **A clear single target** — not "in the DNA family of X" or "adjacent to Y" or "hybrid of X + Y"
4. **Consistent execution** — batch variation acknowledged but not so severe that the dupe fails half the time

**Categories that stay ARTICLE-ONLY and never go in VERIFIED_DB:**

- 🟡 Inspired-By Interpretations that lack a clean single target (Supremacy Collector's Edition, Afnan 9PM Rebel)
- 🔴 Cautionary Tales that don't actually match their claimed target (Supremacy Not Only Intense)
- Sub-85% matches (Afnan Rare Carbon at 70-78%, Afnan Mirsaal With Love at 70-80%)
- Fragrances with severe reformulation issues where current batches don't match older reviews

**When our own research contradicts an existing DB entry (like SNOI), the article research takes precedence.** The DB gets fixed.

---

## 4. Pre-Change Protocol

**Before touching worker.js, do all of these in order. No exceptions.**

### 4.1 Download Current Live worker.js

Never edit from memory or from a stale copy. The current live worker.js is the only source of truth.

- Log in to Cloudflare Dashboard
- Workers & Pages → decodedscents worker
- Edit code (Quick Edit or full editor)
- Copy the entire file OR use the download option
- Save locally

### 4.2 Save a Backup

Before any modification session, save a timestamped copy:
```
worker.js.backup-YYYY-MM-DD-HHMM
```

If deployment breaks, this is the recovery source.

### 4.3 Map All Change Locations

For every planned modification, identify:
- **Which structures need changes?** (VERIFIED_DB, ALIASES, DUPE_TO_ORIGINAL, STANDALONE_FRAGRANCES)
- **What existing entries need to be preserved?**
- **What entries need to be removed?**
- **What entries need to be added?**
- **What line numbers are involved?** (use `grep -n` to locate)

### 4.4 Verify No Conflicts

Grep the source file for terms related to the new entry:
```bash
grep -ni "supremacy silver" Worker.js
grep -ni "9pm\|ultra male" Worker.js
grep -ni "hacivat\|hawas black" Worker.js
```

Zero results confirms clean add. Any hits require manual review.

### 4.5 Verify Retailer URLs

For every FragranceNet URL:
- Never guess a URL slug
- Get the actual affiliate URL from the FragranceNet/Rakuten publisher interface
- Format: `https://click.linksynergy.com/link?id=qPG3GkVv1uU&offerid=507761.XXXXXXXXX&type=2&murl=...`
- If URL is unavailable, OMIT the `fragranceNetLink` field entirely — do not guess

For non-Amazon retailers (Jomashop, theduabrand.com, oakcha.com):
- Do not add a separate URL field for these retailers
- Instead, embed a prominent disclosure in `whySimilar`:
  - `"BEST PRICE AT JOMASHOP (~$XX)"` for Jomashop-primary
  - `"AVAILABLE DIRECT AT theduabrand.com"` for Dua Brand-primary
- Include the entry in VERIFIED_DB if it meets the 85% rule regardless of retailer

### 4.6 Sign-Off Before Writing Script

Present the change plan to Carlos before writing any transformation script:
- List of specific changes across all 4 data structures
- Match percentages and community sources for new entries
- FragranceNet URLs (verified or omitted)
- Estimated file size delta

Only after explicit approval do we write the script.

---

## 5. Schema Requirements

Every new entry must match the existing schema exactly. Copy from existing entries, do not invent structure.

### 5.1 Target Entry Schema

```javascript
"lowercase target name": {
  original: {
    name: "Full Name EDP",           // Include format suffix (EDP/EDT/Extrait) where relevant
    brand: "Brand Name",
    price: "$XXX",                   // Retail price as string with $ prefix
    scentFamily: "Category",         // e.g. "Woody Oriental", "Fruity Chypre"
    notes: {
      top: ["Note1", "Note2"],       // Arrays of strings, capitalize each note
      middle: ["Note1", "Note2"],
      base: ["Note1", "Note2"]
    },
    amazonLink: "https://www.amazon.com/s?k=Brand+Name+Fragrance+perfume+buy&tag=decodedscents-20&i=beauty",
    fragranceNetLink: "https://click.linksynergy.com/link?id=qPG3GkVv1uU&offerid=507761.XXXXXXXXX&type=2&murl=...",  // Optional, only if verified
    description: "One-line description of the fragrance."
  },
  dupes: [
    // Array of dupe entries — see 5.2
  ]
}
```

### 5.2 Dupe Entry Schema

```javascript
{
  name: "Dupe Name EDP",
  brand: "Brand",
  price: "$XX",
  similarity: 87,                    // INTEGER between 85 and 100, no ranges
  fragranceNetLink: "...",           // Optional, only if verified
  scentFamily: "Category",
  amazonSearch: "Brand Name Target Original",  // Text used for Amazon search
  amazonLink: "https://www.amazon.com/s?k=Brand+Name+Target+Original&tag=decodedscents-20&i=beauty",
  fragranticaQuery: "Brand Simple Name",
  notes: { top: [...], middle: [...], base: [...] },
  sharedNotes: ["Note1", "Note2"],   // Subset of notes present in BOTH dupe and target
  whySimilar: "Explanation with community sources embedded. Include performance caveats, batch variation notes, and non-Amazon retailer disclosures where relevant.",
  communitySource: "Comma-separated list of source names"
}
```

### 5.3 ALIASES Schema

```javascript
"short search term":                                 "full target key",
"another alias for the same target":                 "full target key",
```

Add aliases for:
- Common short names (e.g., "aventus absolu" → "creed aventus absolu")
- Brand + short name (e.g., "creed aventus absolu" → "creed aventus absolu")
- Any way users might search for the target

### 5.4 DUPE_TO_ORIGINAL Schema

```javascript
"lowercase dupe name": "target key",
"brand lowercase dupe name": "target key",
"lowercase dupe name edp": "target key",
```

Add multiple variations for each dupe:
- Bare name (e.g., "9pm" → "jean paul gaultier ultra male")
- With brand prefix (e.g., "afnan 9pm" → "jean paul gaultier ultra male")
- With format suffix (e.g., "9pm edp" → "jean paul gaultier ultra male")
- Brand + name + format (e.g., "afnan 9pm edp" → "jean paul gaultier ultra male")

---

## 6. Execution Protocol

### 6.1 The Non-Negotiable Rule

**Never edit worker.js incrementally.** Every change goes through a Python transformation script that:

1. Reads the current file into memory in one operation
2. Applies all changes to the in-memory content
3. Writes the entire new file in one operation

**Incremental string-replacement chains directly in the editor are forbidden.** They have corrupted the file in prior sessions.

### 6.2 Transformation Script Template

```python
#!/usr/bin/env python3
"""
Transform worker.js: apply [description of changes]
"""
import sys

SOURCE = "/path/to/current/worker.js"
OUTPUT = "/path/to/new/worker.js"

# Read entire file preserving line endings
with open(SOURCE, 'rb') as f:
    content = f.read().decode('utf-8')

original_length = len(content)
original_lines = content.count('\n') + 1
print(f"Source: {original_length} bytes, {original_lines} lines")

# ============================================================
# STEP 1: [description of change]
# ============================================================
OLD_TEXT = 'exact old text to find'
NEW_TEXT = 'exact new text to replace with'

if OLD_TEXT in content:
    content = content.replace(OLD_TEXT, NEW_TEXT)
    print("✓ Step 1: [description]")
else:
    print("✗ Step 1 FAILED: Could not find pattern")
    sys.exit(1)

# ... more steps

# Write output preserving line endings
with open(OUTPUT, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

new_length = len(content)
new_lines = content.count('\n') + 1
print(f"\nOutput: {new_length} bytes, {new_lines} lines")
print(f"Delta: +{new_length - original_length} bytes, +{new_lines - original_lines} lines")
```

### 6.3 Windows Line Endings

The file uses Windows `\r\n` line endings. All Python string operations must preserve this. Always:
- Read the file as bytes then decode
- Use `\r\n` explicitly in search patterns
- Write with `newline=''` to prevent Python from converting `\n` to `\r\n` on some platforms

### 6.4 Search Pattern Precision

**When searching for text to replace, include enough context to guarantee uniqueness.** A pattern that matches multiple locations will corrupt the file.

Bad: `"scentFamily": "Woody Oriental"` (appears many times)
Good: The full opening line of a specific entry with brand and price

### 6.5 The Closing Brace Trap

**Critical lesson from the Afnan DB update:** when adding new entries to the end of VERIFIED_DB or any other object, the search-and-replace pattern must not consume the closing brace of the previously-last entry.

If the file structure is:
```javascript
  "last entry": {
    ...
  }
};
```

And you want to add new entries before the `};`, your replacement must:
1. Restore the `}` that closes the previously-last entry
2. Add a `,` after it (since it's no longer last)
3. Add the new entries
4. Restore the `};` that closes the object

Do not assume the closing `}` is preserved automatically.

---

## 7. Validation Protocol

**Before deploying any modified worker.js:**

### 7.1 JavaScript Syntax Check

```bash
node --check worker.js
```

Must return with no output (exit code 0). Any syntax error means the file will not deploy successfully.

### 7.2 Structural Counts

Verify expected entry counts:
```bash
# Number of h2 sections, structural landmarks
grep -c 'export default' worker.js       # Should be 1
grep -c '^};' worker.js                  # Should be 6 (VERIFIED_DB, ALIASES, STANDALONE, DUPE_TO_ORIGINAL, CORS, main handler)
```

### 7.3 Change-Specific Verification

For each change made, grep to confirm:
- The old content is removed (`grep -c "old string" worker.js` = 0)
- The new content is present (`grep -c "new string" worker.js` = expected count)
- No unintended duplications

### 7.4 File Size Sanity Check

Compare source and output:
- Delta should match approximately what was added/removed
- If output is dramatically smaller than source, content was accidentally deleted
- If output is dramatically larger, content may be duplicated

### 7.5 Diff Review

Optional but recommended for large changes:
```bash
diff worker.js.backup worker.js | head -100
```

Read the diff before deploying.

---

## 8. Deployment Protocol

### 8.1 Backup First

Confirm the timestamped backup exists locally. If deployment breaks, this is the recovery source.

### 8.2 Cloudflare Steps

1. Log in to Cloudflare Dashboard
2. Navigate to Workers & Pages → decodedscents worker
3. Click "Edit code" or "Quick Edit"
4. **Note the current deployment date/version** (for potential rollback reference)
5. Select all existing code (`Ctrl+A` / `Cmd+A`)
6. Delete
7. Paste the new worker.js content
8. Verify the paste completed (scroll to bottom, confirm main handler is present)
9. Click "Save and Deploy"
10. Wait for the deployment confirmation

### 8.3 Alternative Deployment Method

If the Quick Edit paste UI fails (which can happen when the file exceeds browser paste limits around 400KB):

- Use `wrangler deploy` from the CLI (most reliable for large workers)
- Or upload via Cloudflare's file picker if available

### 8.4 Post-Deployment Wait

Wait 30-60 seconds after deployment before running post-deployment tests. Cloudflare edge propagation is fast but not instant.

---

## 9. Post-Deployment Test Protocol

**Immediately after deployment, run these tests on decodedscents.com:**

### 9.1 Baseline Test

Search for a well-known target that was in the DB before this update:
- Expected: results appear
- If no results: something is broken, roll back

### 9.2 New Entry Tests

For every new target key added, search for:
- The target name exactly (e.g., "Creed Aventus Absolu")
- A short-name alias (e.g., "Aventus Absolu")
- A dupe name that should route to this target (e.g., "Vanguard" or "Maison Asrar Vanguard")

Expected result: the same target entry appears for all three queries.

### 9.3 Modified Entry Tests

For any entry that had dupes added or removed, search for the target and verify:
- New dupes appear in the results list
- Removed dupes do NOT appear in the results list
- Existing dupes are unchanged

### 9.4 Search Mapping Tests

For every new DUPE_TO_ORIGINAL mapping, search for the dupe name and verify it routes to the correct target.

### 9.5 Cross-Article Consistency Test

If this DB update was driven by an article, do a spot check:
- Read a section of the article
- Search the site for the dupe mentioned
- Verify the site's classification matches the article

**If the site shows a dupe at a higher match percentage than the article, or shows a dupe the article specifically called cautionary, the DB is contradicting the article.** Fix immediately.

### 9.6 Fallback Test

Search for something NOT in the DB (e.g., a made-up fragrance name):
- Expected: AI-generated fallback response appears
- If no fallback: the main handler may have broken

### 9.7 Similarity Percentage Display Verification

For every entry appearing in search results:
- **Displayed percentage matches the DB value exactly** — if the DB says `similarity:87`, the search result must show 87%, not 85% or 90%
- **No formatting errors** — percentages should render as integers with `%` suffix, not decimals or strings
- **No missing percentages** — every dupe must show a similarity value

**Sorting verification:**
- Dupes must appear from **highest similarity to lowest** (closest to the 85% floor)
- Example expected order for Creed Aventus: CDNI 94% → Supremacy Silver 84% (post-Afnan update)
- If dupes appear in the wrong order (e.g., 84% before 94%), the frontend sort logic may be broken

**Test procedure:**
1. Search for a target with multiple dupes (e.g., "Tom Ford Oud Wood" now has 4 dupes)
2. Read the displayed similarity value for each dupe
3. Compare against the DB entries (look up in worker.js)
4. Verify order is descending
5. Verify all dupes shown are 85%+ (no sub-85% leaks)

**If any percentage is wrong or the order is broken:**
- Do NOT accept "close enough" — the whole point of curator accuracy is precise numbers
- Check whether the issue is a DB error (fix in worker.js) or a frontend display error (fix in the site's JS)
- Roll back and diagnose before further changes

### 9.8 Notes Display Verification

For every entry in search results, verify that:

**Original fragrance notes:**
- Top, Heart (Middle), and Base notes all display
- Each layer labeled correctly
- Notes match what's in worker.js exactly (spelling, capitalization, order)
- No missing notes (e.g., top layer shows 3 notes when DB has 4)
- No duplicate notes across layers unless intentionally listed both places

**Dupe fragrance notes:**
- Same three-layer display
- Match worker.js exactly
- No layer collapsed or omitted

**Shared notes highlighting:**
- The `sharedNotes` array should be visually distinguished on the site
- Each shared note that appears in the display must actually be present in BOTH the target and the dupe notes lists
- No shared notes that don't actually exist in one or both fragrances

**Test procedure:**
1. Search for a fragrance we recently added or modified (e.g., "Nishane Hacivat")
2. Compare displayed notes side-by-side with worker.js
3. Check both the original AND every dupe entry
4. Verify shared notes highlighting works correctly

**Common issues to watch for:**
- Frontend markdown/HTML escape issues (special characters like `&` breaking display)
- Truncation of long note lists
- Case-sensitivity bugs (DB has "Black Currant", display shows "black currant")
- Note order changed from DB to display

---

## 10. Article-Driven Update Trigger

**Every article published triggers a DB review.** No exceptions.

### 10.1 The Review Checklist

When any article ships, immediately after publish:
- List every fragrance the article recommends as a dupe
- For each, check the DB:
  - Is this fragrance already in the DB?
  - If yes: does the DB match the article's assessment?
  - If no: does this fragrance meet the 85% rule?
- If any updates are needed, schedule a worker.js update

### 10.2 Priority Order

If multiple updates are needed:
1. **Critical fixes first** (DB contradicting article — e.g., the SNOI issue)
2. **New Real Dupes** that clear 85% (e.g., Afnan 9PM → Ultra Male)
3. **New target keys** for fragrances not previously covered
4. **URL patches** and enhancements

### 10.3 Batch Efficiency

Group related updates into one deployment. Each Cloudflare deploy carries small risk — fewer, larger batches are safer than many small ones.

**But don't wait so long that critical fixes sit unaddressed.** SNOI at 88% Aventus was in the DB throughout the Afnan article research and publication because the DB update was deferred. That's a mistake we want to avoid.

---

## 11. Retailer Handling

### 11.1 Amazon

- Primary retailer for the site's affiliate strategy
- Every VERIFIED_DB entry should have an `amazonLink` field
- Use the tag `decodedscents-20` in all Amazon URLs
- Format: `https://www.amazon.com/s?k=...+perfume&tag=decodedscents-20&i=beauty`
- When the exact product isn't consistently available on Amazon (Jomashop-primary items), still include the Amazon link but add prominent Jomashop disclosure in `whySimilar`

### 11.2 FragranceNet (via Rakuten)

- Optional but valuable for commission
- Publisher ID: `qPG3GkVv1uU`
- Merchant ID: `216`
- URL format: `https://click.linksynergy.com/link?id=qPG3GkVv1uU&offerid=507761.XXXXXXXXX&type=2&murl=...`
- **Never guess URL slugs.** Get the actual URL from the FragranceNet/Rakuten publisher interface.
- If URL cannot be verified, omit the `fragranceNetLink` field. The button just won't appear — cleaner than a 404.

### 11.3 Non-Affiliate Retailers (Jomashop, theduabrand.com, oakcha.com, Maison Asrar)

- Do not add a new URL field for these retailers
- Do not create a "jomashop button" without frontend changes
- Instead, embed disclosure in the `whySimilar` text:
  - `"BEST PRICE AT JOMASHOP (~$XX)"` for Jomashop-primary items (Thameen Carved Oud, Maison Asrar Vanguard)
  - `"AVAILABLE DIRECT AT theduabrand.com"` for Dua Brand items (Popped Cherry)
- The curator honesty principle is preserved: readers see the fragrance exists and know where to find it, but the site doesn't earn commission on those purchases

### 11.4 Brands to Never Link to FragranceNet

Per historical policy:
- Dossier (their own website is primary)
- Dua Fragrances (direct-to-consumer only)
- Fragrance World (unclear licensing)
- Rayhaan (limited FragranceNet availability)

These brands can be in the DB with Amazon links only.

### 11.5 Affiliate Link Verification (Established 2026-07-14, Extended 2026-07-20)

**Established after live-testing revealed that Amazon search-URL affiliate links (`/s?k=...&tag=...`) frequently return empty results, and FragranceNet listings sometimes carry a vial or body-spray rather than the actual bottle we're recommending.** Extended 2026-07-20 to cover Perfumania and Shop Simon — same principle applies to any retailer whose fallback URL is a search page rather than a verified product page. The site's honest-curation promise is violated more by dead or misleading links than by missing ones.

#### 11.5.1 The Rule

No affiliate link goes into `worker.js` unless the destination has been verified in-browser to lead to a real, correct-format product page for the exact fragrance we're recommending. **This applies equally to all 4 retailer partners: Amazon, FragranceNet, Perfumania, and Shop Simon.**

#### 11.5.2 "Correct-format" definition

The linked listing must match on all three:
- **Product**: exact fragrance, not a differently-named product sharing keywords
- **Concentration**: EDT ≠ EDP ≠ Parfum ≠ Extrait. Salvo body spray is not Salvo EDP; Blue Talisman Extrait is not Blue Talisman EDP.
- **Size**: full bottle (typically 100ml or 3.4oz), NOT sample vials, decants, or travel sprays unless that's explicitly what we're recommending

#### 11.5.3 Verification workflow (per fragrance × per affiliate)

**Step 1 — Search the affiliate** (Amazon with `tag=decodedscents-20`, FragranceNet via Rakuten deep-link, Perfumania, or Shop Simon).

**Step 2 — Categorize the result:**

| Result | Action |
|---|---|
| ✅ In-stock, correct-format product page | Use direct product URL (`/dp/ASIN` for Amazon; direct product URL for others) |
| ⏸ Out-of-stock but real product page exists | Still valid to include — "notify me" is honest; user can act |
| ❌ Only vial / decant / body spray / wrong concentration | Do NOT include; omit this affiliate |
| ❌ Search returns no relevant or only unrelated products | Do NOT include; omit this affiliate |
| ❌ Product removed / 404 | Do NOT include |

**Step 3 — Fragrances that fail all affiliates:** Add a `directLink` to the brand's official product page (Velixir Icarus / Bujairami Executor / Louis Vuitton pattern). Users have a legitimate path to purchase; no affiliate revenue but no user deception.

**Step 4 — No brand-direct available either:** Ship with `fragranticaQuery` only. The Fragrantica button is always rendered from `name + brand` at render time (already in schema). Users can still learn more; they source the bottle themselves. Ship the honest empty state rather than fake buttons.

#### 11.5.4 URL format requirements

**Amazon:** `https://www.amazon.com/dp/ASIN?tag=decodedscents-20` — **never** `/s?k=search+query&tag=...`. Search URLs are unreliable; Amazon's search relevance changes and often returns empty for over-specific queries (e.g., "Ex Nihilo Blue Talisman EDP perfume buy" returns nothing usable). Direct-product URLs by ASIN are stable.

**FragranceNet:** Rakuten deep-link wrapping the direct product URL (`/cologne/brand/product-name/eau-de-parfum`), not the brand landing page. Verify the product URL resolves before wrapping in Rakuten deep-link.

**Perfumania:** Direct product page URL (`perfumania.com/products/product-slug`), not a search URL or brand collection page. Store as `perfumaniaLink` field on the entry. The client `perfumaniaDirectLink()` helper wraps it in the affiliate tracking format.

**Shop Simon:** Direct product page URL (`shopsimon.com/products/product-slug` or verified brand-scoped listing), not a generic collection page. Store as `shopSimonLink` field on the entry.

**Brand-direct (fallback):** full HTTPS URL to the specific product's page, not the brand homepage. Store as `directLink` field. Client renders as "🌐 Buy at [Brand]" button.

#### 11.5.5 lastVerified field (mandatory on all affiliate links)

Every affiliate link record must include a `lastVerified` field with the ISO date the link was checked in-browser:

```js
{ amazonLink: "https://www.amazon.com/dp/B06XVY9VBY?tag=decodedscents-20", lastVerified: "2026-07-14" }
```

**Why:** without this field, we cannot distinguish "recently verified working link" from "added blind years ago." A stale link and a wrong link look identical from outside. The Blue Talisman FragranceNet link was probably legitimate when added — the retailer changed it to a vial listing at some point. Tracking `lastVerified` lets the audit script (§11.5.7) prioritize the stalest links for re-checking.

Bump `lastVerified` any time the URL is re-checked in-browser, even if unchanged.

#### 11.5.6 Verification cadence — Hybrid (D)

**On new entries:** verify before adding (§11.5.1). Non-negotiable.

**On existing entries:**
1. **Ambient repair.** Every time an entry is touched for any reason (adding a dupe, fixing a price, adding a variant), audit its affiliate links as part of the change. Bump `lastVerified` on links kept; remove/replace links per §11.5.3.
2. **Periodic small audits.** At session-end when time allows, audit ~10 entries from the "stalest lastVerified" list produced by §11.5.7's script. No time pressure; small batches compound.

**Do not:** block new DB work waiting for the retroactive audit to complete. New entries ship under the verified protocol immediately; old entries repair ambiently. Otherwise progress halts indefinitely on an audit that grows faster than we can catch it.

#### 11.5.7 Retail-audit script

A standalone Python script that reads `VERIFIED_DB`, groups every affiliate URL by fragrance, and outputs a checklist prioritized by staleness (missing or oldest `lastVerified` first). Carlos works through the list in a browser, marks each as kept/removed/replaced; Claude runs a repair migration per §6.1.

The script converts "audit the DB" from a vague task into a concrete spreadsheet-shaped job.

Script lives at `audit_affiliate_links.py` in the repo. Three output formats supported: `--format=text` (checklist with checkboxes), `--format=csv` (spreadsheet import), `--format=summary` (counts only).

#### 11.5.8 Client-side render (Index.html)

The Index.html render is data-driven per §11.5 (established 2026-07-20). Every retailer button renders **only if the corresponding field exists on the DB entry**:

- `amazonLink` → renders 🛒 Amazon button
- `fragranceNetLink` → renders 🏪 FragranceNet button
- `perfumaniaLink` → renders 🏪 Perfumania button
- `shopSimonLink` → renders 🛍️ Shop Simon button
- `directLink` → renders 🌐 Buy at [Brand] button (with brand name interpolated)
- Fragrantica button always renders (informational, not commerce)

No fallback search URLs. Entries with no verified affiliate links display only Fragrantica plus (optionally) a `directLink` button — the honest empty state.

This applies to both original and dupe cards. Dupe cards use `sp.amazonLink`, `sp.fragranceNetLink`, `sp.directLink` fields.

#### 11.5.9 Documentation of link changes

Every link-verification decision (kept / removed / replaced with `directLink` / left with no buy button) is noted in the change log per Section 16, same as any other DB change. The **reasoning** matters as much as the change — "removed FragranceNet because it linked to a vial not the bottle" is more useful in six months than "removed FragranceNet link."

#### 11.5.10 Scope limitations

- **US Amazon only.** International Amazon accounts are not currently supported by the DecodedScents affiliate setup.
- **Rakuten/FragranceNet US only.** Same as above.
- **Perfumania and Shop Simon US only.** Same as above.
- If we expand to other markets, this section gets revised.

---

## 12. Content Proofreading Protocol

Every entry in worker.js contains customer-facing content — `whySimilar`, `description`, `communitySource`. This text displays directly in search results. It must meet the same editorial standard as our published articles.

**This protocol applies at two triggers:**

1. **Before deploying any new or modified entry** — proofread the new content before deployment
2. **Periodic full-DB reviews** — schedule at least quarterly, or when a batch of new content is added

### 12.1 What to Proofread (Field by Field)

**`name` field:**
- Correct spelling of fragrance and format (EDP, EDT, Extrait)
- Consistent capitalization (e.g., "Not Only Intense EDP" not "not only intense edp")
- Format suffix matches actual product (don't call an EDP an EDT)

**`brand` field:**
- Correct spelling and capitalization of brand name
- Consistent with other entries from the same brand (e.g., always "Afnan" not "AFNAN" or "afnan")
- Compound brand names formatted consistently (e.g., "Maison Alhambra" not "Maison alhambra")

**`price` field:**
- Includes `$` prefix
- Whole numbers preferred (`$28` not `$28.00`)
- Realistic current retail (not stale from years ago)
- For originals: matches actual current MSRP within reason
- For dupes: matches typical Amazon pricing within reason

**`similarity` field:**
- Integer between 85 and 100 (below 85 shouldn't be in DB)
- Defensible against community consensus, not aspirational
- Matches or slightly conservative vs. article claims

**`notes` field (top/middle/base):**
- Each note capitalized (e.g., "Bergamot" not "bergamot")
- Multi-word notes use consistent capitalization (e.g., "Black Currant" not "black currant" or "Blackcurrant" in one entry and "Black Currant" in another)
- Note names match Fragrantica/official brand sources
- No made-up notes (this is the Saramito / "fig and juniper" fabrication risk)

**`sharedNotes` field:**
- Must be a strict subset of notes present in BOTH the dupe and the target
- Consistent spelling/capitalization with the `notes` field
- Meaningful shared notes only — not "musk" if it's a base note in every fragrance

**`whySimilar` field — the most customer-facing text:**
- Grammar and spelling correct
- No fabricated claims (community sources, perfumer credits, match percentages must be traceable)
- Performance caveats included where relevant (weak longevity, batch variation, reformulation issues)
- Non-affiliate disclosures embedded where relevant (`"BEST PRICE AT JOMASHOP (~$XX)"` for Jomashop-primary)
- Quotes from community sources are actually verifiable
- Reads with curator voice, not marketing hype

**`communitySource` field:**
- Sources are real and identifiable
- Comma-separated for consistency with existing entries
- Dates included where recent (e.g., "2024-2026")
- No vague "Reddit community" without specifying subreddit
- Uses proper capitalization for reviewer names and publications

**`amazonSearch` and `amazonLink` fields:**
- Search terms return relevant products on Amazon
- Not a broken search that returns irrelevant items
- URL properly encoded (spaces as `+`)
- Amazon tag is `decodedscents-20`

**`fragranceNetLink` field (if present):**
- URL was verified against actual FragranceNet product page
- Uses `linksynergy.com/link?id=qPG3GkVv1uU&offerid=507761.XXXXXXXXX` format
- Not guessed from patterns

**`fragranticaQuery` field:**
- Returns the correct product when searched on Fragrantica
- Simple product name (brand + fragrance), not overly specific

**`description` field (originals only):**
- Grammar and spelling correct
- Under 200 characters (displays inline in search results)
- Curator voice, not marketing copy
- Factually accurate

### 12.2 Cross-Entry Consistency Checks

Beyond individual field proofreading, check:

**Brand consistency across the file:**
```bash
# Find all entries by a brand
grep -c 'brand:"Afnan"' worker.js
grep -c 'brand:"Rasasi"' worker.js
```

Are the same brand names spelled identically? Any typos in one entry that don't match the others?

**Fragrance in multiple targets:**
```bash
# Check if a dupe appears in multiple targets
grep -c 'name:"Maahir Black Edition"' worker.js
```

If a dupe appears in multiple targets, is that intentional (some dupes legitimately match multiple originals) or accidental duplication?

**Notes pyramid consistency:**
When the same fragrance appears as an original in one entry and as a target-notes reference in another, do the notes match?

### 12.3 Cross-Article Consistency Checks

For every dupe recently added via an article-driven update:
- Read the article's section on that fragrance
- Read the DB's entry for that fragrance
- **Do they agree on match percentage, notes, whySimilar reasoning, and community sources?**
- Where the article makes a nuanced claim (e.g., "community split", "batch variation", "reformulation issue"), does the DB reflect that nuance?

### 12.4 Systematic Full-DB Proofread

For quarterly full-DB reviews (or after large batch updates):

1. **Generate an entry list:**
   ```bash
   grep -oE '"[a-z][a-z ]+ [a-z]+"\s*:\s*\{' worker.js | sort -u > /tmp/all_targets.txt
   ```

2. **Work through each target entry systematically:**
   - Read the target's `description` — proofread as if reading a curator article opening
   - Read each dupe's `whySimilar` — proofread as if reading a curator article body
   - Check `similarity` matches community consensus

3. **Log issues found:**
   Use the same severity levels as our article proofread protocol:
   - 🔴 HIGH PRIORITY: grammar errors, factual errors, contradictions with articles
   - 🟡 MEDIUM PRIORITY: awkward phrasing, missing context, stale information
   - 🟢 LOW PRIORITY: consistency issues, minor stylistic improvements

4. **Batch fixes:**
   All fixes from a proofread session go into ONE worker.js update per the Execution Protocol (Section 6). Never fix individual issues incrementally.

### 12.5 Sign-Off Required

After every proofread pass:
- List issues found by severity
- Get Carlos's approval on which fixes to apply
- Apply fixes via a transformation script
- Verify via `node --check` and structural counts before deployment

**Same protocol as article proofreading — no unilateral fixes.**

### 12.6 Documented Standing Fabrication Risks

Historical failure modes in worker.js content:

1. **Fabricated perfumer credits** — never add a perfumer to a `whySimilar` unless independently verified (this was the Saramito pattern)
2. **Fabricated note pyramids** — retailer descriptions (especially Perfume.com, some Amazon listings) can be AI-generated or wrong. Only use Fragrantica or official brand sources.
3. **Fabricated community quotes** — every quote in `whySimilar` must be traceable to a real reviewer, forum post, or article
4. **Optimistic match percentages** — don't inflate `similarity` beyond what community consensus supports
5. **Stale reformulation information** — some entries reference "excellent longevity" when the current batch has been reformulated with weaker performance (this happened with Mirsaal With Love)

### 12.7 Non-Fabrication Check

Before deploying any new entry, ask:
- Can I point to the specific Fragrantica reviewer for every quote?
- Can I trace the note pyramid to the official brand source?
- Is the match percentage defensible against multiple community sources, not just one enthusiastic reviewer?
- If a perfumer is credited, was that verified in a source we trust?

**If any answer is uncertain, revise before deploying.**

---

## 13. Ongoing Quality Assurance & Monitoring

Beyond one-off proofreading (Section 12), the DB and site need continuous monitoring to catch issues that only surface over time. These checks catch drift, staleness, and broken references that accumulate quietly.

### 13.1 Orphan Reference Detection

**Problem:** When entries are removed from VERIFIED_DB (like SNOI from Creed Aventus dupes), orphaned entries can remain in ALIASES or DUPE_TO_ORIGINAL pointing to targets that no longer exist or fragrances that no longer appear.

**Check monthly:**

```bash
# Extract all target keys from VERIFIED_DB
grep -oE '"[a-z][a-z ]+ [a-z]+"\s*:\s*\{' worker.js | sed -E 's/^"([^"]+)".*/\1/' | sort -u > /tmp/db_keys.txt

# Extract all target references from ALIASES (values, not keys)
sed -n '/const ALIASES/,/^};/p' worker.js | grep -oE ':\s*"[^"]+"' | sed -E 's/^:\s*"([^"]+)".*/\1/' | sort -u > /tmp/alias_targets.txt

# Extract all target references from DUPE_TO_ORIGINAL
sed -n '/const DUPE_TO_ORIGINAL/,/^};/p' worker.js | grep -oE ':\s*"[^"]+"' | sed -E 's/^:\s*"([^"]+)".*/\1/' | sort -u > /tmp/dupe_targets.txt

# Find orphans (targets referenced but not defined)
comm -23 /tmp/alias_targets.txt /tmp/db_keys.txt
comm -23 /tmp/dupe_targets.txt /tmp/db_keys.txt
```

Any output from those `comm` commands is an orphan that needs cleanup.

### 13.2 Affiliate Link Health Monitoring

**Amazon:**
- Amazon can silently deactivate affiliate accounts if activity is unusual
- Check monthly: log in to Amazon Associates dashboard and verify the `decodedscents-20` tag is active
- Test click-through on a few live entries — should show "Report abuse" or similar Amazon UI, not "Invalid tag"
- If deactivated: pause site or fall back to non-affiliate links, then investigate

**FragranceNet via Rakuten:**
- Rakuten publisher accounts can be terminated for policy violations
- Check monthly: log in to Rakuten Advertising and verify publisher status
- Test click-through on a FragranceNet-linked entry — should route to a real product page, not a 404 or redirect
- If a specific FragranceNet URL 404s (product delisted): update the entry to remove `fragranceNetLink` or find the current URL

### 13.3 Price Staleness Monitoring

**Problem:** Prices go up. Original fragrance MSRPs increase periodically. Dupe prices fluctuate with Amazon inventory. Stale prices in the DB erode trust.

**Check quarterly:**

For high-traffic entries (originals with retail $200+ and dupes over $50), verify prices are within ~20% of current market:
- Original MSRPs: check the brand's official website
- Dupe prices: check current Amazon listing
- If drift exceeds 20%, update the entry

**Priority entries to check first:**
- Creed Aventus original ($435 in DB — check current)
- Tom Ford Private Blend originals ($285-475 range)
- Initio Oud for Greatness ($325+)
- Baccarat Rouge 540 ($325+)

### 13.4 Reformulation Tracking

**Problem:** Fragrances get quietly reformulated. Community-reported reformulations can drastically change what a dupe actually smells like.

**Monitor Fragrantica community reviews for:**
- Recent (last 6 months) reviews mentioning reformulation
- Community complaints of "watered down", "weaker", "different from what it used to be"
- Explicit brand statements about reformulation

**Historical known issues:**
- Afnan Mirsaal With Love — reformulated late 2024, weaker performance, oud accord removed (documented in Afnan article)
- Maison Alhambra product renames often coincide with reformulation (Toscano Leather → Smoky Touch, Woody Oud → Dark Aoud)

**Action when reformulation is confirmed:**
- Update the entry's `whySimilar` to include a reformulation caveat
- If the reformulation drops match below 85%, consider removing the entry entirely

### 13.5 Search Query Monitoring (Google Search Console)

**Problem:** People search for things we don't cover. Every uncovered search is a missed opportunity to add DB entries.

**Check monthly in Google Search Console:**
- Performance → Queries
- Filter for queries with impressions but low CTR (people searching but not finding what they need)
- Look for fragrance names in the results

**Common patterns worth adding to DB:**
- Popular fragrances that don't have DB targets yet
- Common dupe names people search for that aren't mapped in DUPE_TO_ORIGINAL
- Misspellings that could become ALIASES entries

### 13.6 Cross-Article Reference Integrity

**Problem:** When we publish curator articles, they link to DB entries. If a DB entry is later removed or changed, the article reference can become inaccurate or broken.

**Check after every DB update:**

For each removed or significantly modified entry:
- Search the site's articles for references to that fragrance
- Verify the article's claims still align with the DB
- If a mismatch exists, update either the DB or the article to reconcile

**Example:** If we ever remove the Vanguard entry from DB, the Afnan article's callout ("Maison Asrar Vanguard is the cleaner Absolu match") no longer has a corresponding search result — creating reader confusion.

### 13.7 Consistency Between Site and DB

**Manual quarterly test:**

1. Pick 5 random entries from worker.js
2. Search for each on decodedscents.com
3. Compare displayed data against the DB:
   - Match percentage displays correctly
   - Notes display correctly (all three layers, correct capitalization)
   - Price displays with `$` prefix
   - Retailer buttons appear (Amazon, FragranceNet if applicable, Fragrantica)
   - `whySimilar` and `communitySource` text render without HTML escaping issues

Any mismatch is either a DB data issue or a frontend rendering bug. Diagnose which layer is at fault before fixing.

### 13.8 Fabrication Audit (Deep Content Review)

**Annual audit — pick 20 entries at random:**

For each `whySimilar` claim:
- Can we trace the community source citation to a real Fragrantica reviewer, Basenotes thread, or article?
- Are the quoted phrases actually from the cited source (not paraphrases presented as quotes)?
- Are match percentages defensible against multi-source community consensus?

For each `notes` list:
- Do the notes match Fragrantica's official pyramid for that fragrance?
- Any invented notes that don't appear in the brand's own materials?

**If fabrication is found in an entry:**
- Do NOT quietly fix and move on
- Flag it in the change log
- Consider a broader audit — if one entry has fabricated content, others by the same author/session might too

### 13.9 Backup Rotation

Maintain rolling local backups of worker.js:
- After every deployment, save `worker.js.backup-YYYY-MM-DD-HHMM`
- Keep the last 5 backups locally
- Once a month, archive one backup to long-term storage (GitHub release, Google Drive, etc.)

If the site catastrophically fails and Cloudflare version history is unavailable, having a recent local backup is the difference between minutes of downtime and hours.

---

## 14. Emergency Rollback

**If a deployment breaks the site, roll back immediately.**

### 12.1 Cloudflare Version History

Cloudflare Workers maintains automatic version history:
1. Cloudflare Dashboard → Workers & Pages → decodedscents
2. "Deployments" or "Versions" tab
3. Find the last known good version (before the bad deployment)
4. Click "Rollback" or "Promote" that version to production

### 12.2 Manual Backup Restoration

If Cloudflare version history isn't accessible:
1. Locate the local backup file (from Pre-Change Protocol step 4.2)
2. Follow the Deployment Protocol in Section 8 to redeploy the backup

### 12.3 Post-Rollback Diagnosis

Do not attempt another deployment until the failure is understood:
- Compare the failed worker.js against the good backup
- Identify what specifically broke (syntax? logic? data structure?)
- Update these protocols if a new failure mode was discovered
- Only redeploy after the transformation script is proven correct

---

## 15. Standing Rules (Non-Negotiable)

1. **Never edit worker.js incrementally.** Always use a Python transformation script that reads, modifies, and writes the entire file.

2. **Always download the current live worker.js before any change.** No editing from memory or stale copies.

3. **Always create a timestamped backup before deployment.**

4. **Always run `node --check` before deployment.**

5. **Never guess retailer URLs.** Verify or omit.

6. **Never add unverified perfumer credits, match percentages, or community sources.** Every claim in `whySimilar` and `communitySource` must be traceable to a real source.

7. **Never let the DB contradict a published article.** When an article publishes, review the DB the same session.

8. **Never add sub-85% matches to VERIFIED_DB.** Article-only if borderline.

9. **Non-affiliate honesty is preserved in the DB.** Jomashop-primary items get JOMASHOP disclosure in `whySimilar`, not hidden behind Amazon buttons.

10. **When a search returns no results, the AI fallback is expected.** Do not add speculative entries just to fill gaps.

11. **Every new or modified entry must be proofread before deployment.** Same standard as our article proofread protocol — grammar, factual accuracy, cross-article consistency, no fabricated content. The `whySimilar` and `description` fields are customer-facing text.

12. **Schedule quarterly full-DB proofread passes.** Legacy entries can accumulate errors that weren't caught when they were added. Systematic review keeps quality high across the entire database.

13. **Every post-deployment test must verify similarity percentages display correctly AND sort in descending order down to the 85% floor.** Wrong percentages or broken sort order breaks the site's core promise of accurate curator ranking.

14. **Every post-deployment test must verify notes display correctly** — all three layers, correct capitalization, matching worker.js exactly. Notes are the primary content shoppers use to decide.

15. **Perform ongoing monitoring per Section 13** — orphan detection, affiliate link health, price staleness, reformulation tracking, search query monitoring, cross-article reference integrity, site-to-DB consistency, fabrication audits, and backup rotation. Set calendar reminders for the recurring checks.

---

## 16. Change Log Template

Every worker.js update should log the change here:

```markdown
### YYYY-MM-DD — [Change Description]

**Trigger:** [Article name, bug report, or maintenance reason]

**Changes:**
- VERIFIED_DB: [what changed]
- ALIASES: [what changed]
- DUPE_TO_ORIGINAL: [what changed]

**Validation:**
- Node syntax check: ✓
- Structural counts: ✓
- Live search tests: [list of queries tested]

**File size delta:** +/- XXX bytes, +/- XX lines

**Deployment date:** YYYY-MM-DD HH:MM
```

---

## 17. Recorded Change History

### 2026-07-02 — Afnan Article DB Sync

**Trigger:** Afnan curator article published, DB out of sync

**Changes:**
- VERIFIED_DB:
  - Removed Supremacy Not Only Intense from Creed Aventus dupes (was incorrectly listed at 88%)
  - Added Supremacy Silver (84%) to Creed Aventus dupes with performance caveat
  - Added Thameen Carved Oud (89%) to Tom Ford Oud Wood dupes with Jomashop disclosure
  - Added new key: "jean paul gaultier ultra male" with Afnan 9PM (87%)
  - Added new key: "nishane hacivat" with Rasasi Hawas Black (90%)
  - Added new key: "creed aventus absolu" with Maison Asrar Vanguard (88%) with Jomashop disclosure
- ALIASES:
  - Removed 1 SNOI alias
  - Added 7 new aliases for Ultra Male, Hacivat, Aventus Absolu
- DUPE_TO_ORIGINAL:
  - Removed 3 SNOI mappings
  - Added 20 new mappings for Supremacy Silver, 9PM, Hawas Black, Vanguard, Carved Oud
- FragranceNet URLs added for: JPG Ultra Male, Supremacy Silver, Afnan 9PM, Rasasi Hawas Black

**Validation:**
- Node syntax check: ✓
- File size delta: +7,517 bytes, +65 lines
- Bug caught pre-deployment: initial transformation script consumed the closing `}` of the previous last entry (Xerjoff Opera). Fixed by restoring `},` in replacement text.

**Deployment date:** 2026-07-02 (deployed before session context; deployment date approximate)

---

### 2026-07-04 — Sort-Order Bug Fix (Dupe Display Order)

**Trigger:** Live testing revealed 14 entries were displaying dupes in raw DB insertion order, not descending by similarity percentage. Tom Ford Oud Wood showed 89% → 91% → 90% → 85% instead of 91% → 90% → 89% → 85%.

**Changes:**
- Added `.sort((a,b)=>(b.similarity||0)-(a.similarity||0))` before `.slice()` in two response paths in worker.js
- Both direct-lookup path (line ~3849) and dupe-lookup path both now sort before returning top 5

**Validation:**
- Node syntax check: ✓
- Post-deploy behavior: Oud Wood confirmed sorting 91→90→89→85 ✓
- 14 previously-affected entries verified correct on live site

**File size delta:** +261 bytes, +5 lines

**Deployment date:** 2026-07-04 (verified live 2026-07-13 — 14 out-of-order entries confirmed correctly sorted post-deploy)

---

### 2026-07-13 — Search-Matching Bug Fix (normalizeLight)

**Trigger:** Users searching for concentration variants (e.g. "Sauvage Elixir", "Light Blue Pour Homme", "Baccarat Rouge 540 Extrait") landed on the base fragrance instead. Original `normalize()` function stripped differentiator terms (pour/homme/elixir/extrait/parfum/edt) from queries before alias lookup, causing collisions.

**Changes:**
- Added new `normalizeLight()` function that preserves concentration/gender differentiator terms
- Modified `lookupVerified()` to try `normalizeLight()` first before falling back to aggressive `normalize()`
- Original `normalize()` kept for backwards compatibility on legitimate over-normalization cases

**Validation:**
- Node syntax check: ✓
- 5 target searches (Sauvage Elixir, Light Blue Pour Homme, BR540 Extrait, Aventus Absolu, Sauvage Elixir alternate spelling) all now resolve to correct entries
- 5 regression checks passed (base entries still resolve correctly)

**Related future work:** the variant-picker UX (planned) will resolve variant disambiguation at the UI layer. When variant tabs ship, `normalizeLight` can be simplified. Until then, this fix protects users searching by exact product name.

**File size delta:** +1,126 bytes, +26 lines

**Deployment date:** 2026-07-13 (deployed as part of stacked deploy with FAMILIES, variant-picker UI, Blue Talisman, and Sauvage dupe additions)

---

### 2026-07-13 — FAMILIES Map Added (Step 2 of Variant Picker)

**Trigger:** Design step for variant-picker UI. Step 2 of the hybrid approach: add DB structure now so Step 3 UI has data to consume.

**Changes:**
- Added `const FAMILIES` map (chosen for single-source-of-truth over per-entry `family` field to avoid drift risk)
- 7 families detected via automated concentration-strip rule (baccarat rouge 540, dior sauvage, dolce gabbana light blue, giorgio armani acqua di gio, jean paul gaultier le male, narciso rodriguez, versace eros)
- Each family: `variants` array, `defaultVariant` (dupe-count proxy with manual overrides for tied cases)
- Purely additive — no existing code reads FAMILIES yet, so no user-visible behavior change on deploy

**Validation:**
- Node syntax check: ✓
- Structural counts: ✓ (`^};` bumped 6 → 7 for new map)
- Referential integrity: ✓ all 14 variant references resolve to real VERIFIED_DB keys
- Regression: ✓ normalizeLight and sort fix both intact

**File size delta:** +1,639 bytes, +38 lines

**Deployment date:** 2026-07-13 (stacked deploy with subsequent variant-picker changes)

---

### 2026-07-13 — Flagship Default Overrides (5 of 7 Families)

**Trigger:** Design review of automated defaults revealed dupe-count proxy was wrong for flagship-recognition cases. Sauvage EDP is more flagship than Sauvage Elixir despite fewer dupes; searching bare "Sauvage" should land on EDT, not Elixir.

**Changes (5 defaults overridden):**
- Dior Sauvage: elixir → base sauvage (EDT is the world's best-selling cologne)
- Baccarat Rouge 540: extrait → base 540 (EDP is the iconic version)
- Le Male: elixir → base le male (1995 flagship vs. 2022 flanker)
- Acqua di Giò: parfum → EDT (1996 original vs. 2022 concentrated)
- Versace Eros: eros edt → base eros (iconic 2012 EDT)

**Not overridden:** Light Blue (correct already) and Narciso For Her (correct already).

**Reasoning noted for protocol memory:** dupe-count is a reasonable *starting* proxy for the automated migration, but for high-recognition flagship products it should be manually overridden. This is judgment overlay on the automated rule, not a rule failure.

**File size delta:** −29 bytes (some default variant strings shortened).

**Deployment date:** 2026-07-13

---

### 2026-07-13 — FAMILIES Labels Restructured; 2 Families Removed for Data Issues

**Trigger:** Client-side render logic tried to derive tab labels by stripping the family-key prefix from each variant. Fell apart on "base" variants — e.g. Baccarat Rouge 540 EDP would show as "EDT" because there was no differentiator to strip. Labels needed to be explicit data, not derived at render time.

**Changes:**
- `FAMILIES` variants restructured from raw strings `["k1", "k2"]` to `[{key, label}, {key, label}]`
- Explicit labels added: `EDT`, `EDP`, `Parfum`, `Elixir`, `Extrait`, `Women's`, `Men's` (curator judgment on Light Blue "Women's/Men's" call vs. mechanical "EDT/Pour Homme")
- **Narciso Rodriguez family removed** — both DB entries stored the same product (For Her EDP). Not a family; a duplicate. Adding tabs would show two identical fragrances.
- **Versace Eros family removed** — the base `versace eros` and `versace eros edt` entries appeared to be a duplicate; investigation pending.
- Worker code (`fdef.variants.includes(matchedKey)`) updated to `fdef.variants.some(v => v.key === matchedKey)` for new shape.

**Curator honesty note:** shipped 5 clean families rather than 7 flawed ones. Both Narciso and Eros stayed in DB (users searching them still got results) but no variant tabs shown until data quality was fixed.

**Deployment date:** 2026-07-13

---

### 2026-07-13 — Variant Picker UI Shipped (Step 3)

**Trigger:** Step 3 of variant-picker plan — worker payload + client render code shipped together (chosen Option 1: don't half-ship).

**Changes:**
- Worker `/search` response now includes `matchedKey`, `familyKey`, and `family` fields when the query resolves to a family-member entry (via reverse-lookup on `VERIFIED_DB`)
- `Index.html` gains `.variant-tabs` and `.variant-tab` CSS matching existing site design tokens
- Render logic includes variant tabs when `data.family` exists and has 2+ variants
- Tab click handler calls `doSearch(v.key)` — reuses existing fetch flow rather than adding a new one

**Live behavior verified:**
- "Dior Sauvage" → EDT with `EDT / Elixir` tabs, EDT active ✓
- "Sauvage Elixir" → Elixir with `EDT / Elixir` tabs, Elixir active ✓
- Tab clicks re-search cleanly ✓
- Non-family entries (Oud Wood, Aventus) show no tabs ✓

**Deployment date:** 2026-07-13 (Cloudflare worker + GitHub Pages Index.html)

---

### 2026-07-13 — Blue Talisman EDP + Extrait Added

**Trigger:** New DB entries for popular fragrance, per curator request. Full research completed via §12.7 Non-Fabrication Check + Similarity Cross-Reference Protocol.

**Changes:**
- Added Blue Talisman EDP (Ex Nihilo, $355) — 1 dupe: Velixir Icarus @ 91%
- Added Blue Talisman Extrait de Parfum (Ex Nihilo, $385) — 1 dupe: Bujairami Executor @ 87%
- Added 7 ALIASES entries for common search variants
- Added `ex nihilo blue talisman` FAMILIES entry (defaultVariant: EDP per flagship rule)

**Research honesty notes:**
- **Turathi Electric downgraded and excluded**: initial derived 89% based on ScentClones "closest clone" claim and one Fragrantica "1:1" hyperbole. Note-pyramid analysis later showed significant divergence (Grapefruit/Apple/Vanilla replacing Ginger/Georgywood/Ambrofix). Side-by-side owner review explicitly rated it 70-80%. Corrected to 83% and excluded. Example of research protocol catching a phantom number before ship.
- **Blue Enchantment excluded**: only source was Perfume Parlour's own site. Tier D self-serving only, no independent verification.
- **Art of Universe / Legacy / Azure Royal**: all researched, all landed 82-83%, all Inspired-By tier only.

**Category:** E (New Data Structure Addition)

**Deployment date:** 2026-07-13. Post-deployment verified 5 search variants all resolve correctly.

---

### 2026-07-14 — Blue Talisman Affiliate Links Cleaned + §11.5 Established

**Trigger:** Carlos tested affiliate links in browser; found Amazon search-URL pattern returned empty results for BT entries, and FragranceNet linked to a vial (not the $355 bottle) for BT EDP.

**Changes:**
- BT EDP: removed dead Amazon search URL and misleading FragranceNet vial link; Fragrantica only
- BT Extrait: removed dead Amazon search URL; already had no FragranceNet
- Velixir Icarus dupe: replaced dead Amazon search URL with `directLink` (velixirparfums.com)
- Bujairami Executor dupe: replaced dead Amazon search URL with `directLink` (bujairami.com.au) + verified real FragranceNet 100ml product page

**Broader lesson (led directly to §11.5 protocol):** the entire DB uses Amazon-search-URL affiliate pattern that we now know is unreliable. Established §11.5 Affiliate Link Verification Protocol same day.

**§11.5 established rules (same day):**
- No affiliate link ships without in-browser verification of destination
- Amazon `/dp/ASIN?tag=` only — never `/s?k=` search URLs
- FragranceNet must be direct product URL, verified real bottle (not vial/body spray/wrong concentration)
- `lastVerified` ISO date field mandatory
- Fallback ladder: verified affiliate → `directLink` → `fragranticaQuery` only
- Cadence D (Hybrid): ambient repair + periodic small audits

**Retail audit script:** `audit_affiliate_links.py` written same day. 548 existing affiliate links initially, 0 verified — worked through via hybrid cadence.

**Deployment date:** 2026-07-14

---

### 2026-07-14 — Dior Sauvage EDT: 3 Dupes Added

**Trigger:** Curator request to research 4 candidates. All 4 researched via §12.7 protocol; 3 cleared 85% floor.

**Additions to VERIFIED_DB entry:**
- Armaf Ventana @ 90% — highest independent-source consensus of any Sauvage dupe researched
- Afnan Modest Une @ 89% — Gadgetmix "indistinguishable in the air"
- Maison Alhambra Salvo EDP @ 85% — just clears floor; note pyramid strong but performance weaker

**Excluded honestly:**
- CdN Urban Man Elixir @ 83% — mixed evidence, "50/50 Aventus/Sauvage" per iFragranceOfficial. Inspired-By tier only.
- Brand-correction: candidate was listed as "Al Haramain Salvo" but Salvo is Maison Alhambra. Caught during research; corrected before ship.

**Affiliate link handling per §11.5:**
- Ventana: verified Amazon `/dp/B06XVY9VBY?tag=` + FragranceNet direct URL (both browser-tested)
- Modest Une: FragranceNet direct URL only (no Amazon coverage verified)
- Salvo EDP: no buy links (FragranceNet has body spray, Amazon coverage not verified) — Fragrantica only. Honest empty-state.

**Deployment date:** 2026-07-14. Post-deployment verified all 4 dupes render in correct 92 → 90 → 89 → 85 descending order.

---

### 2026-07-16 — Supremacy Silver 84% → 85% Correction

**Trigger:** Carlos noticed the Afnan Supremacy Silver dupe entry was stored at 84% similarity — below the §3 85% floor. Full research per §12.7 to reconfirm honest number.

**Changes:**
- Similarity: 84% → 85% (at the floor)
- `whySimilar` text rewritten: removed misleading "4-5 hour longevity" claim (contradicted by 2026 blind tests), added honest community-split framing, noted the "synthetic pineapple" critique
- `communitySource` expanded to reflect ScentClones, Parfumei, PickMyClone, Parfumo, Fragrantica

**Research findings:**
- ScentClones 2026 blind tests: 90-95% after maceration (discounted for maceration caveat)
- Parfumei aggregated: 80-90% range top tier
- PickMyClone: consistently flags "synthetic pineapple" and "less sophistication"
- Parfumo owner-of-both comparison: real compositional gaps in opening
- 85% at floor honestly reflects "real dupe DNA, real gaps"

**Follow-up:** Sub-85% DB audit run same day found 0 other violations across 211 dupe records. Silver was a genuine one-off.

**Deployment date:** 2026-07-16

---

### 2026-07-16 — Narciso Rodriguez and Versace Eros Rebuilt from Fragrantica Ground Truth

**Trigger:** Investigation of the two families that had been removed from FAMILIES on 2026-07-13 revealed both had partially-fabricated notes (§12.7 non-fabrication violation), not just duplicate entries.

**Findings:**
- "narciso rodriguez for her" entry was labeled "For Her EDP" but had notes mixing EDT (2003) and EDP (2006) elements plus fabricated notes (Jasmine wasn't in either)
- "versace eros" entry was labeled "Eros" with $115 pricing (EDP retail) but notes matching the EDT
- Both were rebuilt from scratch rather than surgically patched — cleaner provenance trail

**Changes:**
- Deleted `narciso rodriguez for her` entry, added `narciso rodriguez for her edt` (2003 launch, Nagel & Kurkdjian, Floral Musky, notes verified per Fragrantica ID 209)
- Deleted `versace eros` entry, added `versace eros edp` (2020 launch, Aromatic Fougere, notes verified per Fragrantica ID 62762)
- Removed 4 suspect dupes (Narissa For Her EDP 88%, Supremacy Pink 85%, Ambery Mint on Eros mislabel) — all were rated against the wrong reference
- ALIASES: bare "eros" → `versace eros edt` (flagship 2012 original); bare "narciso rodriguez for her" → `narciso rodriguez for her edt`
- FAMILIES: added `narciso rodriguez for her` family (EDT default) and `versace eros` family (EDT default)

**Curator honesty note:** shipped with corrected new entries having 0 dupes each (honest empty state) rather than migrating phantom similarity numbers. The removed dupes may or may not clear 85% against the corrected originals — can be re-researched later if desired.

**Deployment date:** 2026-07-16

---

### 2026-07-16 — Dossier Aromatic Star Anise Ambient Repair (Audit Batch 0)

**Trigger:** First §11.5.6 ambient repair while touching the Dior Sauvage EDT entry for other reasons. Existing Dossier Aromatic Star Anise dupe used the old broken Amazon search-URL pattern.

**Changes:**
- Removed `amazonSearch` and `amazonLink` (broken /s?k= search URL, and per §11.4 Dossier shouldn't link to Amazon anyway)
- Added `directLink: "https://dossier.co/products/aromatic-star-anise"` (verified working)
- Added `lastVerified: "2026-07-16"` timestamp
- Price updated $29 → $30 (verified against dossier.co)

**Bonus finding logged for future queue:** Dossier makes "Spicy Star Anise" specifically inspired by Sauvage Elixir — potential future addition to Sauvage Elixir dupe list if it clears 85%.

**Deployment date:** 2026-07-16

---

### 2026-07-20 — Rayhaan Sub-batch A1 (Lion + Wolf + Aquatica)

**Trigger:** First real batch of the Rayhaan expansion project. 8 of 15 Rayhaan candidates cleared research + 5 more in later sweep. Sub-batch A1 covers the highest-similarity subset (91% each).

**Changes:**
- Added Rayhaan Lion @ 91% as 2nd dupe on existing Ultra Male entry (target: JPG Ultra Male)
- Added new entry `azzaro the most wanted edp intense` ($95, Sweet Spicy, notes verified per Fragrantica) + Rayhaan Wolf @ 91% as its dupe
- Added new entry `creed virgin island water` ($345, Citrus Tropical, notes verified per Fragrantica) + Rayhaan Aquatica @ 91% as its dupe
- 11 new ALIASES (7 for TMW EDP Intense including "TMW Intense" shortcut, 4 for Creed VIW)
- 9 new DUPE_TO_ORIGINAL entries (3 per Rayhaan dupe for search coverage)
- **Ambient repair:** Ultra Male original and 9PM dupe both had old broken Amazon search URLs — replaced with verified `/dp/ASIN` URLs and `lastVerified` timestamps

**Verified ASINs (in-browser 2026-07-20):**
- Ultra Male: B06XD7L7VR (200ml EDT)
- 9PM: B07W83T4PR (100ml EDP)
- Rayhaan Lion: B0DQFL8H9V
- Azzaro TMW EDP Intense: B08ZFKB8ZK
- Rayhaan Wolf: B0GYCYQDS7
- Creed VIW: B074KJTT4P
- Rayhaan Aquatica: B0G2JR6JJ1

**Excluded from Rayhaan research:**
- Imperia @ 84%: note-pyramid gap on Aventus (missing Pineapple/Blackcurrant/Birch signature molecules)
- Rayhaan Elixir @ 82%: Turathi Electric profile — hype claims vs. detailed sources showing compositional gaps and layering advice from ScentClones

**Result:** DB grew from 114 → 116 entries. Deploy stacked with 6 new /dp/ASIN verified links.

**Deployment date:** 2026-07-20 (Cloudflare)

---

### 2026-07-20 — Rayhaan Sub-batch A2 (Pacific Aura + Divine) + LV directLinks

**Trigger:** Continuation of Rayhaan expansion — Pacific Aura + Divine at 89% each. Divine is first women's Rayhaan to clear the DB floor.

**Changes (initial A2 migration):**
- Added new entry `louis vuitton pacific chill` ($300, Aromatic Fruity) + Rayhaan Pacific Aura @ 89% as its dupe
- Added new entry `louis vuitton attrape reves` ($350, Oriental Floral) + Rayhaan Divine @ 89% as its dupe
- 10 new ALIASES (3 for Pacific Chill, 7 for Attrape-Rêves including diacritic variants)
- 6 new DUPE_TO_ORIGINAL entries

**LV directLinks follow-up (same day, after user testing):**
- Initial A2 ship gave both LV originals "Fragrantica-only" per §11.5 fallback ladder (rationale: Amazon US doesn't stock the real LV products, LV product page returned 410 on initial check)
- Carlos noticed the "no buy buttons at all" is a broken UX
- Hunted harder — found current working LV product URLs
- Added `directLink` fields with `lastVerified: "2026-07-20"` to both LV originals

**Verified URLs (in-browser 2026-07-20):**
- Rayhaan Pacific Aura: Amazon B0FCV5SSCQ
- Rayhaan Divine: Amazon B0FYZJHF74
- LV Pacific Chill: https://us.louisvuitton.com/eng-us/products/pacific-chill-nvprod7220018v/LP0460
- LV Attrape-Rêves: https://us.louisvuitton.com/eng-us/products/attrape-reves-nvprod1160017v/LP0083

**Honest process critique noted:** The initial fallback-ladder invocation was too eager. §11.5 says "no verified affiliate link" triggers the fallback — one dead URL should signal to search for the new URL, not give up. Noted for future migrations.

**Result:** Batch A complete. DB: 118 entries. First women's Rayhaan live.

**Deployment date:** 2026-07-20 (Cloudflare)

---

### 2026-07-20 — Index.html Render Fix + §11.5 Extended to All 4 Retailers

**Trigger:** After A2 deploy, Carlos noticed LV originals still showed all 4 retailer buttons (Amazon, Perfumania, Shop Simon, Fragrantica) that led to broken search fallbacks — even though the DB entries had no `amazonLink` or `fragranceNetLink` fields.

**Root cause:** Index.html render logic hardcoded all 4 retailer buttons to always render, with search-URL fallbacks (`perfumaniaLink(orig.name, orig.brand)`, `shopSimonLink(orig.name, orig.brand)`) when specific product fields weren't present. Same broken-search-URL pattern §11.5 was written to catch — just on the client side instead of the DB side.

**Changes (Index.html):**
- Both render paths (split view + standalone view) updated to be data-driven:
  - Amazon button: renders only if `orig.amazonLink` exists
  - FragranceNet button: renders only if `orig.fragranceNetLink` exists
  - Perfumania button: renders only if `orig.perfumaniaLink` exists (was: always as fallback)
  - Shop Simon button: renders only if `orig.shopSimonLink` exists (was: always as search URL)
  - NEW: `directLink` button renders "🌐 Buy at [Brand]" if `orig.directLink` exists
  - Fragrantica button: always renders (informational, not commerce)
- Same treatment applied to dupe cards
- Added `.btn-direct` CSS (gold theme matching site design tokens)

**Changes (WORKER_PROTOCOLS.md §11.5):**
- Extended URL format requirements to explicitly cover Perfumania and Shop Simon (same rule as Amazon: no search URLs)
- Added §11.5.8 Client-side render section documenting the data-driven button pattern
- Added `perfumaniaLink` and `shopSimonLink` field types to the schema

**Honest tradeoff named:** Entries in the audit backlog that don't have real affiliate fields will show fewer buttons than before. Temporarily sparser, but every remaining button is a real one. As ambient repair progresses, buttons come back verified.

**Live testing verified:**
- LV Pacific Chill → Buy at Louis Vuitton + Fragrantica ✓
- LV Attrape-Rêves → Buy at Louis Vuitton + Fragrantica ✓
- Blue Talisman EDP → Fragrantica only (honest empty state) ✓
- Creed Aventus → Amazon + FragranceNet + Fragrantica (audited entries keep their buttons) ✓
- Dior Sauvage → tabs + all dupes render with appropriate buttons ✓

**Deployment date:** 2026-07-20 (GitHub Pages)

---

## Appendix A: Reusable Command Reference

```bash
# Locate all fragrance target keys in DB
grep -oE '"[a-z][a-z ]+ [a-z]+"\s*:\s*\{' Worker.js | sort -u

# Find all references to a specific fragrance name
grep -ni "fragrance name" Worker.js

# Get section line boundaries
grep -n "^};" Worker.js

# Count entries in DUPE_TO_ORIGINAL (approximate)
sed -n '/const DUPE_TO_ORIGINAL/,/^};/p' Worker.js | grep -c ':'

# Show what's between two line numbers
sed -n '1615,1670p' Worker.js

# Verify Windows line endings preserved
file Worker.js  # Should show "with CRLF line terminators"
```

---

## Appendix B: Contact and Escalation

- Primary maintainer: Carlos (raven6724)
- Cloudflare account: decodedscents.cfe1585.workers.dev
- GitHub repo: github.com/raven6724/decodedscents
- Domain: decodedscents.com
- Analytics: GA4 G-3KS1C0WH40
- Affiliate: Amazon (tag decodedscents-20), FragranceNet via Rakuten (publisher qPG3GkVv1uU, MID 216)

---

*End of protocols.*
