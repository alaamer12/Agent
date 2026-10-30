# Case 01 — "add search" is not one component

> Worked example, invented for teaching. The numbers are the point: sizing was measured, not assumed.

**The ask.** "Add search to the listings page." One line, in a product with an approved three-screen design
where the search field is already drawn. Stack: a server-rendered app over [Postgres], ~12 k rows growing
weekly, mobile traffic dominant, two languages with accents.

## Step 1 — the outcome sentence

Not "a box that filters the list" but:

> a visitor finds the right listing in under two seconds from a partial, accented, or over-specific query —
> and gets a useful answer when nothing matches, on a phone, on a slow connection.

That sentence immediately implies more than a box: tokenization that respects accents and both languages, a
no-results state distinct from the empty state, a payload small enough for mobile, and a lookup that does not
degrade as rows grow.

## Step 2 — enumerate, then prune

| Candidate system | Present requirement breaks without it? | Verdict |
|---|---|---|
| normalization/tokenization | yes — "café" must match "cafe", and English queries must match the second language | **build** |
| index (avoid scanning) | yes at 12 k and growing: measured `ILIKE '%s%'` on the table = 340 ms cold, no use of existing indexes under mobile latency | **build** |
| filters combining with the query | yes — the design already shows two filter chips; chips that ignore the query are a behavior bug | **build** |
| ranking (which match first) | yes — a name match should beat a description match, or the top result looks wrong | **build (light: field weights)** |
| pagination | yes — a matched set can be 1,400 rows | **build** |
| no-results + loading + error states | yes, user-visible | **build, inside the approved style** |
| typo tolerance / synonyms | no — nothing in current data or behavior *requires* it to work; it is a nice-to-have | **finding, not built** |
| external search service | no — solves a scale problem this product does not have, and adds an operational dependency and a per-month cost | **rejected; revisit at ~1 M rows** |
| incremental index refresh pipeline | no — writes are ~40/day; rebuild-on-write is enough | **simplified: no pipeline** |
| search analytics | no | **finding** |

Six built, four declined. The declines are decisions too — each one is a line in the report, not silence.

## Step 3 — the ledger for the one real choice

```text
Question   Where does matching happen, and with what engine?
Options    A ILIKE '%q%' over the table          B app-side full inverted index (in memory)
           C Postgres full-text: tsvector column + GIN index   D managed external search service
Criteria   correctness on accented/bilingual text · latency at 12k on mobile · operations owned by a 2-person
           team · reversibility · cost
Choice     C — normalization and tokenization are exactly what tsvector does, no new service to run, and the
           data stays the source of truth
Accepted   C gives up A's zero moving parts (a trigger/refresh path is now required to keep the column
           current) and D's relevance features (facets, typo tolerance) which the requirements do not need yet
Steelman A "one line, no machinery": stays correct at 300 rows, silently becomes a 340 ms full scan that
           grows with the table; the failure is scheduled, not hypothetical
```

```sql
-- C, concretely: one generated column + one index, and the seam the app talks to
ALTER TABLE listings ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS
    ( setweight(to_tsvector('simple', unaccent(title)), 'A')
    || setweight(to_tsvector('simple', unaccent(body)),   'B') ) STORED;
CREATE INDEX listings_search_idx ON listings USING gin (search_tsv);
```

The [Postgres] choice is an *answer to this measurement*, not a rule. At 300 rows option A is the professional
choice and C is a liability; at 2 M rows or with relevance work required, D becomes honest and its cost is
surfaced to the user as a decision, not adopted quietly.

## Step 4 — the seam, so the tier can change later

```ts
// The page and the filter chips depend only on this; the engine behind it is the agent's decision.
interface ListingSearch { find(q: Query, f: Filters, page: number): Page<Listing> }
// today: PostgresSearch   ·  tomorrow, if the data forces it: ExternalSearch  — one adapter swaps
```

Because the seam exists, nothing above the line is visible to the user: same field, same chips, same result
card, same copy. The improvement is entirely underneath.

## What stayed the user's

Field placement, the chips, card layout, the word "Listings", empty-state copy tone. Two proposals were
written instead of applied: the no-results state needed a line of copy nobody had drafted (proposed in the
design's voice, one line, awaiting a word choice), and a sort affordance the design did not show at all.

## The report, one line

> Search runs on a weighted full-text index with accent folding and combines with the existing filters;
> results look exactly like the design, first paint went 340 ms → 22 ms on the phone profile; cost: a refresh
> path now keeps the index column current; reversal: one adapter in `listing_search.py`. Findings not built:
> typo tolerance, search analytics, external engine (revisit ~1 M rows).
