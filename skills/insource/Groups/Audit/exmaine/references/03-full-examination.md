# /exmaine full — the complete examination and the overview

`full` is the whole path with every area cross-checked, ending in the one artifact that orients
an agent completely around the project: the overview. Procedure stays static/read-only; nothing
in this file licenses running anything.

## Pass order

1. Doc chain (reference 01) → intent ledger + pointer findings.
2. Code sweep (reference 02) → module inventory, wiring, E-levels, findings.
3. **Ledger pass-by-pass**: every claim gets a verdict line —
   `CONFIRMED (E2–E4, cited)` / `CONTRADICTED (doc says X, code does Y, both cited)` /
   `PARTIAL (exists, not wired / wired, inconsistent)` / `STATIC-UNRESOLVABLE (E5, runtime)`.
   A claim nobody checked is an unfinished examination; a claim "confirmed" without a citation is
   not a verdict.
4. **Reverse pass (code → docs)**: every real module/route/service answers "which doc claim owns
   you?" — the leftovers become the orphan list. This catches what the doc chain cannot: work
   nobody wrote down.
5. **Area sweep** for "everything passes and is intended": each area the project declares
   (pages/screens, API routes, jobs, storage, config, CI) gets a one-line health read from the
   ledger + sweep evidence. Areas with no declared owner go under "structure nobody claims".
6. **Gap ledger** — everything wrong, in one table, each row: kind (broken-pointer / unimplemented
   / orphan / contradiction / drift / secret-risk), location (file:line), both sides quoted short,
   severity (blocks-understanding / cosmetic).
7. **The overview** (shape below) + runtime-unknowns handoff list.

## The complete overview — report shape

Write it as the project's new map, not a dump. Sections, in order:

```text
# Exmaine: <project name>  — <date>, static pass, <N> docs / <M> source files scanned

## Identity            what the project is, in 3-5 honest sentences, from its own docs
                      cross-checked against the code (say if they disagree).
## How it is built     stack as declared + as found; entry points; run graph as wired
                      (bootstrap -> registration -> routes/modules); build/CI intents as written.
## Structure map       the module inventory: each area, its purpose (from docs or inferred,
                      labeled which), evidence level, main entry files.
## Behavior map        the flows the docs claim, each with where the code lives for every hop;
                      broken hops inlined as notes.
## Doc health          chain status: pointers read / broken / stale; which registries
                      (units, glossary, commitments) exist and match reality.
## Code health         wiring gaps, dead/undocumented modules, duplicate-truth constants,
                      config declared-vs-used table.
## Gap ledger          the table from step 6 — the fix list the user can act on.
## Runtime unknowns    what only execution settles, each with the project's own declared
                      command (quoted, not run). Ends the report; no offers, no guesses.
## One-screen takeaway  10 lines max: what this project is, the 3 things a newcomer must know,
                      the 3 biggest consistency risks, current trust level of its docs.
```

Length discipline: the overview is for re-orientation, so dense tables beat prose; anything that
restates a doc without adding evidence gets cut.

## Honesty rules for the verdict voice

- "Everything passes" may only be claimed at E4 ("consistent by construction, never executed")
  — never as "works". Whether it *works* is settled by running the runtime-unknowns list — the
  user's call and the user's machine, never exmaine's.
- Report the scan's own coverage: docs read vs existing, files scanned vs total, what was skipped
  and why (binary assets, vendor dirs). An overview that hides its blind spots is a false map.
- Findings are facts with citations; the overview contains zero recommendations unless the user
  asked for them after reading.

## When `full` is overkill

Single-directory question → `/exmaine <area>`. "Do you trust that this is done?" → not this
skill at all; `please-verify`. `/exmaine full` is for the moment someone needs to *hold the whole
project in their head, statically, honestly* — onboarding, takeover, pre-refactor orientation.
