# main — core screen inventory (`/pages main`)

Owns the main pages of the `<docs>/pages/` tree, the root index's main map (categories), and
the cross-page decision sections — states, splits, exclusions (kind=main), redirects — plus the
role/surface notes. The shared laws and the tree schema live in the skill root (`SKILL.md`,
`../references/pages-tree-format.md`) — this file is the workflow.

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

Not-a-page decisions recorded explicitly: transient conditions are **states** (the root index's
States section, or depth inside the owning page); one short decision is a **modal**; a route
that only hands off is a **redirect** (the root index's Redirects section) — a recorded
decision with reason and user-visible behavior, never a silent bounce.

## Step 3 — Present and ask in ONE round

The shared law applies; the one message carries: the tree with symbols (`✓ ~ ? ✗`), proposed
splits and redirects with what became what and why, exclusions stated for confirmation, then
all open questions as a numbered list. Wait for one reply.

## Step 4 — Resolve and lock

Apply answers: confirmed exclusions get their written reason; added screens land in the right
category; removed screens become exclusions with the user's stated reason; accepted splits
record old route, new routes, tests, date; accepted redirects record type and what the user
sees. Nothing stays `uncertain` past this step without becoming an Open Decision entry.

## Step 5 — Write the pages tree

Produce/update the `<docs>/pages/` tree per `../references/pages-tree-format.md`: one file
per confirmed page (encouraged frontmatter — commonly `name`/`url`/`access`, extensible with any
fields/tags the project needs — a purpose description, an internal sketch
— simple by default, as full as the page requires; the format's §3), a shard `index.md` in every
directory, and the root index's typed map carrying kind,
access, status and the decision sections. Every page's canon location and build story follow
`../references/output-contract.md`. Documents this pass defers to `/pages secondary` are noted
on the map for that mode, not written here; conditional screens discovered here — "what happens
after payment?" — get a page file with a family pointer on the map, their anatomy
`/pages complementary`'s job. The tree is the contract: any later skill adding a page updates
its file and the indexes in the same change.

## Step 6 — Report

Counts by kind and segment; which screens are new against existing route files; splits and
redirects recorded; exclusions recorded; what's next (`/pages secondary` for trust docs,
`/pages complementary` for conditional surfaces, then `/prototype` or `/planner`).

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
| **States are planned, not implied** | empty/loading/error/filtered-empty get a States entry (root index) or depth in their page; unplanned states are how blank screens ship |
| **Discipline rows never enter the map without project fit** | the catalog is the strongest guessing tool there is, and guessing is what the exclusion record exists to stop |

## References (this mode)

| File | Owns | Read when |
|---|---|---|
| `references/data.csv` | the 492-row candidate catalog with prevalence tiers and aliases | Steps 0–1 |
| `references/sources.md` | prevalence method, per-discipline sources, extension rules | judging or adding a row |
| `references/category-patterns.md` | category families, universal baseline, screen-implying signals, coverage checks | Step 1 |
| `references/split-and-redirect.md` | the six split tests, settings split, redirect types | Step 2 |
| `references/decision-recording.md` | decision classes, exclusion anatomy, evidence hierarchy, supersession | Steps 4–5 |
| `../references/pages-tree-format.md` | the pages tree schema itself | Step 5 |
| `../references/output-contract.md` | register → canon → build: the one output story | Step 5 |
| `research/screen-inventory-research.md` | how the catalog was built (provenance) | extending the catalog |