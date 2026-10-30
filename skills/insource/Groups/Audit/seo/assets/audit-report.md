# SEO Audit Report — {scope} ({mode}: analyze | up)

**Stack:** {framework} · rendering {SSR|SSG|hybrid|CSR+prerender} · head emitted via {mechanism}
**Date:** {date} · **Budget:** {wincher 500ms | google | raw} · **Verification:** `{exact commands run}`
**Scope resolution:** target "{user words}" → {N} routes: {list, each with reason (single / family: list·detail·tabs·taxonomy·compare)}

## Executive Summary
- Overall health: {one paragraph, findings labeled fact/estimate/hypothesis}
- Top {3-5} priority issues, quick wins identified
- Floor vs ceiling note: {first-packet state} + {family-uniqueness state, if applicable}

## Scores

| Page | Keyword (per variant) | Before | After | Gate |
|---|---|---|---|---|
| /{route} | {kw-ar} / {kw-en} | {score or AT-RISK} | {score or —} | {PASS/FAIL} |

**Score-stack line** per passing page (shows which patterns carry the score — read at a glance):
`Title 27 (P1,P10) + Headings 20 (P3,P4) + Body 28 (P5,P6) + Meta 5 (P2) + Media 4 (P7) + Code 6 (P8) + URL 10 (P9,P12) = 100`
Cost trades applied (from the guardrails menu): {list, or "none"}.

## Assumption Ledger (data-gates.md Step 0 — required even when everything scores)

| Value · window | Template assumes | Measured (max/nulls) | Guaranteed by | Decision |
|---|---|---|---|---|
| `name` → title 30-60 / h1 ≤40 | ≤ ~{N} chars | max={X}, nulls={Y} | VARCHAR({n}) | CHECK constraint is a real bound — assert only |
| `description` → meta ≤160 | keyword before char {Z} | max={X} | TEXT, no bound | gate at template (B) + upstream enforce (A) |
{decision is one of: A enforce upstream · B template gate (keyword-atomic ladder + assert + log) · C accept — never "assumed"}

## Findings

For **each** issue use this shape (no invented findings; every claim cites its evidence artifact):

> **Issue:** {what's wrong}
> **Impact:** High | Medium | Low ({which rubric points or which indexing risk})
> **Evidence:** {how it was measured — command/output/file:line + date; label fact/estimate/hypothesis}
> **Fix:** {specific change, pattern id P1-P14, applied file:line or required data}
> **Priority:** {1-5}

Group by: Crawlability/Indexation → Technical (timing, P10/P13) → On-Page (P1-P9) → Content quality (`content-quality.md`) → Locale/i18n (P11).

## Timing Findings

| Page | TTFB | head arrives | h1 arrives | raw-vs-budget delta | Action (P10) |
|---|---|---|---|---|---|

## Not Fixable By Code (data gaps — route to CMS/admin)
- {entity}: missing logoUrl → Media 0/4 (P7) · missing copy → Body risk (P5) · customSlug NULL → URL −5 (P9)
{do not paper over with boilerplate — see guardrail 10}

## Prioritized Action Plan
1. **Critical** — blocks indexation/score entirely (P13 gates, 500-heads, noindex leaks)
2. **High-impact** — multi-point rubric losses
3. **Quick wins** — single-check fixes (alt builder, fallback templates, hreflang self-ref)
4. **Long-term** — content-quality layers, scheme migration if applicable (P11)

## Applied Changes (up mode only)
- `file:line` — what changed, which pattern it implements

## Residuals & Risks
- {failing check + reason + next step} · standing repo risks ({cite repo postmortem/playbook docs if present})
