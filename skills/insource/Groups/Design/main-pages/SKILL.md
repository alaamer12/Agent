---
name: main-pages
description: 'Plans the complete page/screen inventory for any product before design or implementation begins. Detects the product discipline (healthcare, CRM, banking, education, marketplace, logistics, and 24 more) and uses a researched catalog (references/data.csv, ~490 screens with prevalence tiers and alternate names) to propose what products in that space normally ship - then prunes it against the project own docs, routes, entities and recorded decisions. Groups screens into functional categories (e.g. Auth, Onboarding, Dashboard, Settings), detects mixed concerns and splits bloated screens (e.g. settings by personal/workspace/organization scope), records redirect-instead-of-page decisions (e.g. forgot-password without reset-password), and marks every screen confirmed/inferred/uncertain. Records explicit exclusions with reasons and delivers a confirmed PAGE-MAP.md the prototype, design, and implementation skills can build from. Never invents pages the product does not need; never skips pages it does. Use when someone says: plan my pages, what screens do I need, map out the app, page inventory, screen list, or starts a prototype/design without an agreed screen set.'
---

# main-pages — screen inventory planning

Before any screen is designed or built, the full set of screens must be
agreed on. This skill derives that set from three layers — the universal
patterns every account product shares, the patterns of the product's
discipline, and the project's own evidence — groups them into functional
categories, splits mixed concerns, confirms each screen and each exclusion
with the user, and delivers a **`PAGE-MAP.md`** that becomes the single
source of truth every downstream skill reads.

**The output is a decision document, not a list.** Each entry records
*why* the screen exists (or doesn't). An exclusion with a reason is as
valuable as an inclusion — it prevents the screen from being re-invented
later by an agent that didn't know the decision had already been made.

---

## What this is not

- It does not design screens (that is `prototype` or `impeccable`).
- It does not write legal/policy pages (that is `secondary-pages`).
- It does not plan implementation order (that is `planner`).
- It does not build anything.

It produces one artifact — `PAGE-MAP.md` — that those skills consume.

---

## Workflow

### Step 0 — Read before asking

Before asking the user anything, read every available source of project
context:

- Architecture docs, `README.md`, `AGENTS.md`, any design spec or brief
- Existing route files (`router.ts`, `app/routes/`, `pages/`, navigation
  declarations) — a route that exists is a screen that exists
- API or data-model docs — entities often imply screens (a `Playlist`
  entity implies a playlist detail screen)
- Any file that records product decisions: `DECISIONS.md`, tickets,
  architecture notes, previous `PAGE-MAP.md`

Then name the **discipline(s)**. A product can span several: a health
marketplace is `healthcare` + `marketplace`; a fintech CRM is `fintech` +
`crm`. Read the matching rows in
[`references/data.csv`](references/data.csv) and the universal rows.
The catalog is a candidate generator and a vocabulary source — evidence
from the project still decides.

Evidence from docs beats guessing. A decision already recorded (e.g.
"password reset is a magic link — no reset-password page") must be carried
forward as an **explicit exclusion** in the output, not ignored.

### Step 1 — Draft the category tree

Group candidate screens into **functional categories**. Categories are
derived from the product's domain and jobs, not from a fixed template —
[`references/category-patterns.md`](references/category-patterns.md)
explains the families and how to derive them.

Use three passes:

1. **Universal** — auth, onboarding, shell, settings, billing, error and
   shared states (`discipline=universal` in the CSV).
2. **Discipline** — the signature screens for this product family
   (`discipline=healthcare`, `crm`, `banking`, …). Take the union when a
   product spans disciplines.
3. **Project** — entities, routes, docs, tickets and recorded decisions
   that add, alter or rule out a screen.

Each category gets:
- A short slug (`auth`, `onboarding`, `dashboard`, `settings`, …)
- A one-line purpose statement
- Its candidate screens, each with:
  - Name + route hint (e.g. `Login · /login`)
  - One-line description of what it does
  - Confidence: `confirmed` (doc evidence), `inferred` (domain logic),
    `uncertain` (needs user input)

**Prevalence is a reading order, not a mandate.** `core` (≥85%) and
`common` (65–84%) rows are drafted first; `optional` (35–64%) rows are
included only when the project meets their precondition; `niche` (<35%)
rows are mentioned only when the user's own words point at them. Never
present prevalence as measured data, and never include a screen merely
because the catalog says most products have it.

Screens derived from docs are `confirmed`. Screens the domain implies
but docs don't address are `inferred`. Anything genuinely ambiguous is
`uncertain` and goes to Step 3 for the user.

### Step 2 — Find mixed concerns and split them

A draft is not done when every screen has a name. Check each candidate
for **mixed concerns** — one screen carrying several jobs:

- more than 5–7 independent sections, or more than 3 distinct questions;
- sections with their own save, validation, permission or lifecycle;
- different roles seeing disjoint sets of sections;
- a URL that needs `?tab=` to reach a section;
- a title that is a conjunction ("Account, Billing and Team");
- support docs that must explain which tab to open.

Split when **two or more** of the six tests pass: back-button,
deep-link, mental-model, complexity, audience, lifecycle. The full tests,
split shapes and the canonical settings split (personal → workspace →
organization → admin) live in
[`references/split-and-redirect.md`](references/split-and-redirect.md).

Also decide what is **not** a page:

- transient feedback and data conditions are **states** (`kind=state`);
- one short decision is a **modal**;
- a route that only hands off is a **redirect**.

A redirect is a decision, not a missing screen. Record the reason and
what the user sees. A silent bounce is only acceptable for a pure alias.

### Step 3 — Ask in one round

Present the full draft category tree to the user in a single message.
Do not ask questions one at a time. For each `uncertain` screen, ask
directly whether it exists and, if relevant, how it works. For each
documented exclusion, state it and ask the user to confirm or correct it.
For each proposed split or redirect, state what was one screen, what it
became, and why.

Format: show the tree as a readable list, mark `confirmed` / `inferred` /
`uncertain` per screen, then list proposed splits and redirects, then ask
all open questions in a numbered list. One message, all questions, wait
for one reply.

Symbols: `✓` confirmed, `~` inferred, `?` uncertain, `✗` proposed exclusion.

```
Auth
  ✓ Login · /login  (confirmed — docs show credential flow)
  ✓ Signup · /signup  (confirmed)
  ~ Forgot Password · /forgot-password  (inferred — typical for credential
    auth; not mentioned in docs — does this page exist, or is reset handled
    another way e.g. magic link?)
  ✗ Reset Password · /reset-password  (excluded — docs say reset is a
    magic link in email, no page needed — confirm?)

Settings  (proposed split)
  was one page; becomes:
  ✓ Profile · /settings/profile
  ✓ Account · /settings/account
  ✓ Security · /settings/security
  ✓ Notifications · /settings/notifications
  ✓ Billing · /settings/billing
  Tests: model, complexity, deep-link, audience. Appearance and language
  stay as sections of Account.
  ? Team members · /settings/members  (uncertain — are workspaces in v1?)

Onboarding
  ✓ Welcome / topic picker · /onboarding  (confirmed — doc §cold-start)
  ? Post-signup profile step  (uncertain — is there a profile completion
    step after signup, or does onboarding go straight to the feed?)
...

Questions:
1. Forgot Password: magic link or dedicated reset page?
2. Are team workspaces in v1? If yes: members, roles, invites, audit log.
3. Does the proposed settings split match your mental model?
```

### Step 4 — Resolve and lock

Apply the user's answers. For every exclusion the user confirmed, write
the reason in the exclusion record. For every screen the user added,
place it in the right category. For every screen the user removed, record
the exclusion with their stated reason. For every accepted split, record
the old route, the new routes, the tests, and the redirect. For every
accepted redirect, record the type and what the user sees.

Do not proceed to Step 5 until all `uncertain` items are resolved.

### Step 5 — Write PAGE-MAP.md

Produce `PAGE-MAP.md` at the project root (or the path the user specifies).
Read [`references/page-map-format.md`](references/page-map-format.md) for
the exact format. The file contains:

1. **Context** — project, discipline(s), platforms, roles, sources read
2. **Legend** — status and kind vocabulary
3. **Roles and surfaces** — who sees what, and each role's landing route
4. **Category sections** — each with its screens (name, route, kind,
   status, confidence, evidence, notes)
5. **States** — shared conditions that are not routes
6. **Splits** — what was one screen, what it became, the tests, the date
7. **Exclusions** — every screen considered and explicitly decided
   against, with the reason and a revisit trigger
8. **Redirects** — from, to, type, reason, what the user sees
9. **Open decisions** — anything deferred (the user said "decide later");
   these are TODOs, not gaps
10. **Coverage** — counts and the completeness checks

The file is the contract. Any skill that later adds a screen must update
`PAGE-MAP.md` in the same change, not in a follow-up.

### Step 6 — Report

Tell the user:
- How many categories, routes and states are in the confirmed map
- Which screens are new (not yet in any existing route/page file)
- Which screens were split, and which redirects were recorded
- Which exclusions were recorded
- What to do next (e.g. "run `/prototype` to build from this map" or
  "run `/planner` to sequence implementation")

---

## The catalog — `references/data.csv`

492 candidate screens across 30 disciplines, each with an estimated
prevalence and an evidence basis. Columns:

```
discipline,category,page,route,kind,prevalence,tier,basis,confidence,aka,notes
```

| Column | Meaning |
|---|---|
| `discipline` | `universal` or an industry/product family |
| `category` | Functional family inside the product |
| `page` | Human-readable screen name |
| `route` | Route hint; `-` for states |
| `kind` | `page`, `subpage`, `modal`, `state` (redirects are recorded in the map, not the catalog) |
| `prevalence` | Estimated share of products in that discipline, 0–100 |
| `tier` | `core` ≥85, `common` 65–84, `optional` 35–64, `niche` <35 |
| `basis` | `universal`, `product-tour`, `regulation`; extended rows may add `domain-model` or `research` |
| `confidence` | Confidence in the estimate: `high`, `medium`, `low` |
| `aka` | Alternate names users may say |
| `notes` | Scope caveats, redirect alternatives, state-vs-page warnings |

```bash
# Use rg, grep, Select-String or the agent's search tool; patterns are equivalent.
# Everything a discipline typically has
^healthcare,

# The universal baseline
^universal,

# Find a screen by any of its names before inventing one
,(login|sign in|signin),
```

**Prevalence is an estimate, not a statistic.** It is calibrated from
public product navigation, documentation and tours. Say "commonly
present", never "95% of users need this". When the estimate and the
project's reality disagree, the project wins, and the disagreement is
recorded as an exclusion.

---

## Rules that never bend

| Rule | Why |
|---|---|
| **Read first, ask second** | Questions the docs already answer waste the user's time and signal the agent didn't do its job |
| **One round of questions** | Dripping questions one at a time is the most disruptive thing an agent can do mid-planning |
| **Every exclusion is recorded** | An unrecorded exclusion gets re-invented by the next agent. The reason is the memory. |
| **Confirmed and inferred are distinct** | Labelling a guess as confirmed corrupts the doc. Mark inferred clearly. |
| **Prevalence is not evidence** | A common screen the product does not need stays out. The catalog ranks candidates; the project decides. |
| **Never invent screens the domain doesn't need** | A screen that makes no sense for this product's reality doesn't go in the map, even if it's "common" |
| **Split on concerns, not tables** | Users think in jobs, not schemas. Split settings by scope, not by database entity. |
| **A redirect is a recorded decision** | `/reset-password` → `/forgot-password` must carry its reason and what the user sees, or it becomes a broken link later |
| **States are planned, not implied** | Empty, loading, error and filtered-empty are part of the map; unplanned states are how blank screens ship |
| **PAGE-MAP.md is the output, not a chat list** | The map must be a file. A list in chat disappears; a committed file persists. |

---

## References

| File | Owns | Read when |
|---|---|---|
| [`references/data.csv`](references/data.csv) | 492 candidate screens across 30 disciplines, with prevalence tiers, alternate names and state/redirect warnings | Step 0–1, naming the discipline and drafting candidates |
| [`references/sources.md`](references/sources.md) | Method behind the prevalence estimates, representative sources per discipline, limits, and how to extend the catalog | Step 0–1, judging a row or adding one |
| [`references/category-patterns.md`](references/category-patterns.md) | Category families, universal baseline, domain signatures, signals that imply screens, pruning and coverage checks | Step 1, deriving the category tree |
| [`references/split-and-redirect.md`](references/split-and-redirect.md) | Page-vs-state-vs-modal-vs-redirect tests, six split tests, canonical settings split, route conventions, redirect types | Step 2, finding mixed concerns and choosing redirects |
| [`references/page-map-format.md`](references/page-map-format.md) | Exact `PAGE-MAP.md` schema: section order, field names, exclusion/redirect/split blocks, coverage checks | Step 5, writing the output file |
| [`references/decision-recording.md`](references/decision-recording.md) | How to record a "no" — decision classes, exclusion anatomy, reason quality, evidence hierarchy, supersession | Steps 4–5 |
