# Failure Modes & Standing Guardrails (Stack-Independent)

Use during ANALYZE (classify what you see) and UP (avoid re-introducing). If the repo has its own SEO postmortem/playbook docs (grep for `seo`/`postmortem` in `docs/`), read them first — they encode this codebase's specific root causes.

## Recurring Failure Modes (archetypes, seen across stacks)

| Mode | Symptom | Rubric damage | Fix pattern |
|---|---|---|---|
| **Client init gate replaces SSR body** — a provider/adapter renders a spinner/fallback until a client effect runs; server HTML = loader only. Fingerprint: head passes, ALL body checks 0; browser DOM looks perfect | varies by stack (React `useState(false)+useEffect`, Blazor `prerender:false`, `v-if="hydrated"`, SPA without prerender) | catastrophic (Headings+Body+Media+ratio → 0) | P13 — synchronous init or render children on server/first paint |
| **Head data on the slow lane** — uncached fetch in metadata path; TTFB eats the 500 ms budget; title/description arrive too late | head tags exist in full response but score 0 in budgeted mode; `raw` mode passes, `wincher` mode fails | Title exists, Meta, early elements | P10 — cached/cross-request metadata lane |
| **Optimizer image wrapper** hides the raw `<img alt>` from first packet | Media 0/4 | P7 |
| **Alt from filename** (`logo.png` → "Logo") — misses localized keyword | Media 0/4 | P7 alt builder from entity data |
| **Second `<h1>`** introduced in a client template or a hidden SEO block alongside the visible one | h1 count 0/4 | P3 — grep subtree before finishing |
| **Generic labels** (`Performance`, `About the fund`) or only ONE keyword subheading | subheadings 0-1/2 | P4 — interpolate name into ≥2 heading templates |
| **Icon-SVG card chrome in the raw crawl path** — ~10 KB markup/section, near-zero visible text | ratio <2% → 0-1/3 | P8 — facts-as-sentences; move chrome behind client boundary or into prop-injection |
| **Numeric/ID URLs** after migration | URL −5 | P9 — slug column wired everywhere (canonicals, sitemap, links) |
| **Title drift after content edits** — appended modifiers push >70 chars or duplicate the keyword | −6 length, −4 stuffing | P1 — template owns the title; editors own the name only |
| **h1 == title core** after suffix-strip (`{Name} \| Site` vs `{Name}`) | −2 | P3 trap — differentiator on one side, verify after every title change |
| **Keyword/language mismatch** — Arabic keyword audited against the `en` variant (or `?lang=en` served under `lang="ar"` doc) | Headings/Body/Meta collapse together | audit each locale variant with its own keyword; keep `<html lang>` honest (P11) |
| **NULL-conditional media rendering** — `{logo ? <img/> : null}` silently deletes the scored tag | Media 0/4 | fallback image with keyword alt, or flag as data gap |
| **Sitemap/canonical/internal-link disagreement** on trailing slash, lang param, or country scope | consolidation/indexing drift | P11/P12 — one funnel generates every URL |

## UP-Mode Guardrails (auto-fix safety)

1. **Never sacrifice the visible design for score** — add hidden/slot-injected crawler layers, don't restyle user UI (the two-layer model exists precisely for this).
2. **Never hard-code per-entity copy** — patterns wrap data; a second entity must score identically with zero manual work.
3. **Never duplicate a heading by adding a second h1/h2** — extend templates instead.
4. **Respect repo conventions** — package managers, env policy, existing metadata helpers, shell preferences.
5. **Distinguish code fixes from data fixes** — missing slugs/logos/descriptions are CMS/admin work; report them, don't paper over with fallback junk.
6. **Verify, don't assert** — final claim requires a `seo_audit.py` run at target; `--mode raw` vs budgeted mode separates timing from content.
7. **Regression watch**: after ANY title/heading template change, re-run the audit — the cheapest points (h1≠title, length window) are the easiest to knock out accidentally.
8. **Cannibalization check before optimizing a family** — if two routes answer the same query, pick the owner, merge or redirect the rest; optimizing both hurts both.
9. **Detection honesty** — "no structured data / no meta X" from raw HTML is a *hypothesis*, not a finding: JS-injected markup is invisible to it. Confirm with a rendered check before reporting (or report the limitation explicitly).
10. **Never trade the ceiling for the floor** — filling Body word gaps with near-identical boilerplate across an entity family reaches 100/100 and creates a scaled-content liability (`content-quality.md`). If that's the only way to pass, report it as a data gap instead.

## Eval-Driven Maintenance

This skill ships `evals/evals.json` — realistic prompts with atomic expected behaviors, including adversarial cases (wrong premise → should be rejected; out-of-scope request → should defer; over-claim → should refuse). After editing any pattern or threshold, re-read the affected eval entries and verify the skill text still produces the asserted behavior; add an entry for every new failure mode.

## Approved Cost Trades (menu — pay knowingly, note it in the report)

Every one of these was proven necessary to reach 100 on real pages; each buys specific points at a named cost. Apply [as needed], never reflexively:

| Trade | Buys | Cost accepted |
|---|---|---|
| Separate cached lane for metadata fetch (P10), duplicate query on cold hit | Title-exists within budget | one extra backend round-trip |
| Short staleness window on head/discovery caches (minutes-hours) | head-flush latency + stampede protection | renames/price fixes visible late |
| Render lane stays fresh (per-request dedupe, not long cache) | h1/alt keyword accuracy | repeated DB hits under crawl storms |
| Raw `<img>` over optimizer wrapper (P7) | Media 4/4 | larger unoptimized payload to users |
| Hidden crawler prose alongside visible UI (P5) | Body 28 + ratio | duplicated content bytes in the document |
| Move styled icon-heavy chrome out of first-packet path (P8) | ratio ≥2% | that text enters the stream later/nested |
| Server-render header chrome even when a client header also exists (P3/P13) | h1 guarantees | duplicated header work; watch post-hydration double h1 (DOM debt, invisible to first-packet scoring) |
| `Vary: Cookie/Accept-Language` for locale consistency | canonical variant stability | fragmented CDN cacheability |

## Site-Wide Enhancement Sweep (run after per-page fixes; recurring misses found in real audits)

- [ ] A cached metadata getter **exists and is actually used** — a written-but-uncalled fast lane is a hidden P10 breach
- [ ] Listing/hub pages have a **server-rendered h1** and hub link coverage ≥ entity count (P15)
- [ ] Family **sub-pages/tabs** (news/history/compare-style routes) inherit only the layout h1 — give each the P4+P5 treatment; they otherwise hold Title/Meta/URL points and zero Body points
- [ ] No family route is fully client-rendered (a `Suspense fallback={null}` shell page has no static text at all)
- [ ] FAQ structured data generated from existing prose (P14)
- [ ] Entity schema carries `alternateName` for bilingual consolidation (P14)
- [ ] List-level metadata/schema scoped away from detail routes (P16)
- [ ] Sitemap internal-consistency: every entity under its own locale only; caps/pagination match entity counts (P15/P16)
- [ ] Data completeness enforced upstream: slug backfill, required logo, required entity copy — with an admin-side check so fail-silent components don't hide gaps (P16)
- [ ] Worst-case gates exist: gate-test fixtures for the LONGEST and SHORTEST entity name, keyword-at-char-200 description, non-transliterable slug source; templates assert their own output (data-gates.md)
- [ ] **Drift sweep (P17):** grep for duplicated metadata/title/description constructs — ≥2 near-copies means consolidate into the funnel first; then re-audit EVERY route consuming the funnel, because the reported failure is rarely the only drifted one
