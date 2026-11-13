# main — core screen inventory (`/pages main`)

Owns `PAGES.md` §4 (categories), §7 (states), §8 (splits), §9 (exclusions, kind=main),
§10 (redirects), and the §3 role/surface table. The shared laws and the file schema live in
the skill root (`SKILL.md`, `../references/pages-md-format.md`) — this file is the workflow.

**The output is a decision document, not a list.** Each entry records *why* the screen exists
(or doesn't).

## Step 0 — Read before asking

Read every project-context source: architecture docs, README/AGENTS, design briefs; route
files (a route that exists is a screen that exists); API/data-model docs (entities imply
screens); `DECISIONS.md`, tickets, any previous map. Then name the product's
**discipline(s)** — a fintech CRM is `fintech` + `crm` — and read the matching rows of
`references/data.csv` plus the universal rows. Recorded decisions carry forward as explicit
exclusions, never as ignored facts.

## Step 1 — Draft the category tree

Categories derive from the product's domain and jobs — `references/category-patterns.md`
explains the families and derivation. Three passes: **universal** baseline rows →
**discipline** signature screens (union when several) → **project** evidence that adds,
alters, or rules out.

Each category: slug, one-line purpose, and candidate screens as
`Name · /route — one-line description — ✓confirmed / ~inferred / ?uncertain`.

**Prevalence is a reading order, not a mandate.** `core`(≥85)/`common`(65–84) draft first;
`optional`(35–64) only when the project meets their precondition; `niche`(<35) only when the
user's words point at them. Say "commonly present", never "95% of users". When the catalog
and the project disagree, the project wins and the disagreement becomes a recorded exclusion.

## Step 2 — Mixed concerns: split, modal, redirect, or state

Check every candidate for one screen carrying several jobs (>5–7 independent sections, >3
questions, per-section save/validation/permission, role-disjoint sections, `?tab=` URLs,
conjunction titles, support docs explaining tabs). Split when **two or more** of the six
tests pass (back-button, deep-link, mental-model, complexity, audience, lifecycle) — full
tests, canonical settings split, and route conventions: `references/split-and-redirect.md`.

Not-a-page decisions recorded explicitly: transient conditions are **states** (§7); one short
decision is a **modal**; a route that only hands off is a **redirect** (§10) — a recorded
decision with reason and user-visible behavior, never a silent bounce.

## Step 3 — Present and ask in ONE round

One message: the tree with symbols (`✓ ~ ? ✗`), proposed splits and redirects with what
became what and why, exclusions stated for confirmation, then all open questions as a
numbered list. Wait for one reply. Never drip questions.

## Step 4 — Resolve and lock

Apply answers: confirmed exclusions get their written reason; added screens land in the right
category; removed screens become exclusions with the user's stated reason; accepted splits
record old route, new routes, tests, date; accepted redirects record type and what the user
sees. Nothing stays `uncertain` past this step without becoming an Open Decision row.

## Step 5 — Write PAGES.md

Produce/update `PAGES.md` per `../references/pages-md-format.md`, with every row's canon
location and build story following `../references/output-contract.md` — the whole file schema,
including the §5 secondary handoff (documents this pass defers to `/pages secondary` are
listed there, not duplicated here) and §6 complementary registration (conditional screens
discovered here — "what happens after payment?" — enter §6 with family pointers; their
anatomy is `/pages complementary`'s job). The file is the contract: any later skill adding a
screen updates it in the same change.

## Step 6 — Report

Counts by section; which screens are new against existing route files; splits and redirects
recorded; exclusions recorded; what's next (`/pages secondary` for trust docs, `/pages
complementary` for conditional surfaces, then `/prototype` or `/planner`).

## The catalog — `references/data.csv`

492 candidate screens, 30 disciplines: `discipline,category,page,route,kind,prevalence,tier,
basis,confidence,aka,notes`. Query with any search tool: `^healthcare,` for a discipline,
`^universal,` for the baseline, `,(login|sign in|signin),` to find a screen by any of its
names before inventing one. Prevalence method, sources, and how to extend rows:
`references/sources.md`.

## Rules specific to this mode

| Rule | Why |
|---|---|
| **Split on concerns, not tables** | users think in jobs, not schemas — settings split by scope, not by database entity |
| **A redirect is a recorded decision** | `/reset-password` → `/forgot-password` must carry reason + what the user sees, or it becomes a broken link later |
| **States are planned, not implied** | empty/loading/error/filtered-empty get §7 rows; unplanned states are how blank screens ship |
| **Discipline rows never enter the map without project fit** | the catalog is the strongest guessing tool there is, and guessing is what the exclusion record exists to stop |

## References (this mode)

| File | Owns | Read when |
|---|---|---|
| `references/data.csv` | the 492-row candidate catalog with prevalence tiers and aliases | Steps 0–1 |
| `references/sources.md` | prevalence method, per-discipline sources, extension rules | judging or adding a row |
| `references/category-patterns.md` | category families, universal baseline, screen-implying signals, coverage checks | Step 1 |
| `references/split-and-redirect.md` | the six split tests, settings split, redirect types | Step 2 |
| `references/decision-recording.md` | decision classes, exclusion anatomy, evidence hierarchy, supersession | Steps 4–5 |
| `../references/pages-md-format.md` | the PAGES.md schema itself | Step 5 |
| `../references/output-contract.md` | register → canon → build: the one output story | Step 5 |
| `research/screen-inventory-research.md` | how the catalog was built (provenance) | extending the catalog |