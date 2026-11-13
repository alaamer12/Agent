---
name: pick
description: "Pick the right PRODUCTION library for a development task instead of hand-rolling it - answers lookup questions from data.csv, a verified catalog across UI pieces, TypeScript correctness, data layer, backend runtime, testing, tooling and CLI. Core stance: a maintained production library beats self-implementation for anything an agent would otherwise build twice (vaul for bottom sheets instead of a DIY sheet; typia/zod for narrowing-validating instead of type gymnastics). Recommends one library with task, why, when_not, and alternatives; records only what was verified against npm/docs, never memory. Triggers: pick a library for X, what should I use for toasts/bottom sheets/drag-drop/validation/jobs, is there a library for this, don't hand-roll this, /pick. Not for deciding a tech stack (techstack), nor for inventing new categories the catalog does not cover without saying so."
when_to_use: A task calls for a component or mechanism a library probably already owns — before writing custom code for UI pieces, validation, state, fetching, jobs, CLI UX, tests, or tooling.
argument-hint: "[<task or keyword>|list|categories|refresh]"
disable-model-invocation: true
---

# pick — production libraries over self-implementation

**The stance:** if a maintained library owns the mechanism, use the library; spend custom
code only where the catalog has no answer, and say so out loud. Hand-rolling a bottom sheet,
a focus-trapped dialog, an OTP paste field, a retry/backoff loop, or a TS narrowing dance is
re-implementing something with a verified owner.

The catalog is **`data.csv`** — one row per library, 22 comma-free fields: what it is, task it
replaces, languages/runtime served (js;ts;hybrid…), GitHub, package, docs, changelog/migration
URL, license, **verified adoption number**, what it excels at, why to use, when to use,
**when NOT to use**, alternatives, tags, and provenance (`curated` vs `verified`, date, source).
This file is only the wrapper; the data holds the knowledge.

## Commands

| command | behavior |
|---|---|
| `/pick <task or keyword>` | search `data.csv` (name/task/tags/what); recommend the ONE row; state task, excels, when_not, alternatives — and check the project's own `package.json` first: an installed listed library wins; a competitor gets flagged, not churned |
| `/pick list [category]` | the active rows, grouped by category, one line each |
| `/pick categories` | category census + row counts (finds thin coverage) |
| `/pick refresh` | the discovery loop (below) — grow and re-verify the catalog |

Task not covered → say "outside the catalog", recommend from verified knowledge with the
same fields, and propose a row. Never silently stretch a near row to fit.

## Answer discipline

- One recommendation when the catalog has a clear owner; menus only when the user asks.
- `when_not` is part of the pick, always delivered — a library recommended without its boundary
  is a future migration.
- Trust levels differ and are said: `verified` rows carry checked npm/docs/adoption at
  `verified_on`; `curated` rows are taste imports awaiting verification; `-` in adoption means
  never measured — do not cite numbers memory gives you.
- Rows never change by vibe: a pick that turns out wrong is fixed by re-verifying the row and
  editing it (with its adoption/date updated), not argued around in chat.

## The refresh loop (how the catalog grows)

Time-boxed: ~10 minutes. Start a background counter writing remaining seconds to
`/tmp/pick-loop-remaining.txt` (one line, integer; write `DONE` to `/tmp/pick-loop-state.txt`
at zero). Loop until the file says `DONE`:

1. **Read the current records** — `data.csv` full, plus `/pick categories` census for gaps.
2. **Think un-viewed perspectives** — mechanisms agents hand-roll that a production library
   already owns: new categories first (mobile/RN pieces, i18n/intl, date-time, PDF/media,
   observability, PWA/offline, security/sanitizing, editors, machine interfaces…), then thin
   categories needing depth. The test for a candidate: "someone is definitely writing this
   by hand today."
3. **Verify each candidate** — registry (`registry.npmjs.org/<pkg>`: version, license,
   recency), downloads (`api.npmjs.org/downloads/point/last-week/<pkg>` → the adoption
   field; <~10k/wk rejected unless category-defining niche, which gets said in when_not),
   docs URL resolves. Dead or deprecated projects are excluded or retired with a pointer to
   their successor. **Not used by 10 people** is the user's rule: adoption is a number, not a
   feeling.
4. **Update records** — append rows (`source=loop:<date>`), re-verify touched `curated` rows
   to `verified`, retire dead ones.
5. **Refactor the CSV if needed** — new column when a real field lacks a home, category
   splits when one swallows the rest; structure follows the data, not the other way round.
6. **Check time** — read the temp file; loop, or finalize.

Waves of parallel research agents are allowed and encouraged (the `parallelize` method: agents
research and RETURN rows — `data.csv` has one writer, the main agent, who integrates every
result). Verification of adoption numbers and live docs is the agents' job, never memory.

## Row schema

`name,category,task,what,langs,runtime,github,pkg,docs,changelog,license,adoption,excels,why,when_to_use,when_not,alternatives,tags,confidence,status,verified_on,source`
— 22 fields, comma-free content (semicolons inside prose; `-` unknown). `confidence` is
`curated|verified`; `status` is `active|emerging|maintenance|unmaintained|retired` — a pick
whose status is not `active` says so in the answer (vaul: still the best drawer, but budget
for a fork); never reorder columns without
fixing every row in the same change.