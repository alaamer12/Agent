# The 100-Point Rubric — Exact Sub-Checks (Stack-Independent)

Implemented by `<skill-dir>/scripts/seo_audit.py`. Reference implementations exist in the wild as Wincher's on-page audit; thresholds below match its model.

**Crawler behavior to replicate:** fetch with a bot User-Agent; read the response **streamingly** with a patience budget — [wincher ≈ 500 ms] [googlebot ≈ 5 s] [raw = no limit]. Content arriving after the budget is invisible. Text inside `<script>`, `<style>`, `<noscript>` never counts. Keyword matching normalizes text: lowercase, strip diacritics/tashkeel (Arabic: أ/إ/آ→ا, ة→ه), then substring/word counting. Elements count **in raw HTML only** — CSS (`display:none`, `sr-only` clipping) is irrelevant to the parser; a JS-hydrated DOM is irrelevant.

## Title — 27

| Check | Max | Rule |
|---|---|---|
| Title exists | 7 | `<title>` non-empty, arrived within budget |
| Keyword in title | 8 | 1-2 mentions = 8; ≥3 = 4 (stuffing); 0 = 0 |
| Length | 6 | 30-60 chars = 6; <30 = 3; 61-70 = 3; >70 = 0 |
| Keyword position | 6 | first-occurrence position score ≥80 = 6; ≥50 = 3; <50 = 0 |

## Headings — 20

| Check | Max | Rule |
|---|---|---|
| Keyword in h1 | 5 | h1 exists, in budget, contains keyword |
| h1 length | 2 | ≤ 40 chars |
| Keyword position in h1 | 5 | same tiers as title |
| h1 count | 4 | exactly 1 (0 or ≥2 = 0) |
| h1 ≠ title | 2 | title core (split on `\|`, `-`, `–`) normalized must differ from h1 normalized |
| Keyword in h2/h3 | 2 | present in subheading text; one heading with keyword = partial (1/2) |

## Body — 28

| Check | Max | Rule |
|---|---|---|
| Word count | 14 | ≥500 = 14; ≥300 = 7; ≥100 = 3; else 0 — visible text only |
| Keyword mentions | 14 | ≥3 = 14; 2 = 7; 1 = 3; 0 = 0 |

## Meta — 5
Keyword in `<meta name="description">` within budget = 5. Nothing else is checked here, so a keyword-bearing fallback template makes this unlosable. (SERP display, unscored: keep the keyword within the first ~50-60 chars — mobile truncates near 120; keyword-atomic truncation per `data-gates.md`.)

## Media — 4
≥1 `<img>` in-budget whose `alt` contains the keyword = 4. The attribute is read from HTML — the image is never fetched, so CDN/encoding/hosting are irrelevant. No `<img>` in raw HTML, or alt from filenames/generic text, = 0.

## Code — 6

| Check | Max | Rule |
|---|---|---|
| External CSS | 3 | any `<link rel="stylesheet" href>` (non-`data:`) in budget |
| Visible source code % | 3 | visible-text chars ÷ total response bytes: ≥2.0% = 3; ≥1.0% = 1; else 0 |

The % is a **text-to-HTML ratio**: framework runtime payloads (streaming JSON/RSC/hydration scripts), inline SVG icon sets, and class-attribute bloat inflate the denominator without adding visible text. Fixes: move heavy styled chrome out of the first-packet crawl path, and add plain-tag prose.

## URL — 10

| Check | Max | Rule |
|---|---|---|
| Keyword in URL | 5 | full normalized keyword in URL = 5; ≥1 keyword *word* present = 3; else 0 (transliterated slugs win via word match) |
| HTTPS | 5 | URL starts with `https://` — skip (N/A) for local-file audits; applicable scores renormalize |

## Total

`sum(earned) / sum(applicable max) × 100`. 100 requires every applicable check at max. Traps that most commonly cost points after content edits: h1 == title core (2), second `<h1>` appearing in a client template (4), a missing image alt keyword (4), and head-emitting data on a slow uncached path (timing budget).
