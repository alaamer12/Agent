# Waves and gates — executing the reconciliation

A wave is one dependency-level of the plan: a coherent set of changes that leaves the corpus in a
state the gate can meaningfully verify. Waves are executed in order, each ending in ONE commit.

## Why waves and not batches of convenience

Content moves depend on structures existing first (a doctrine home must exist before a pillar's rule
can be pointed at it); corrections depend on decisions being recorded (moving content to a
destination the owner has not chosen is guessing); documentation waves depend on data-shape waves
(the schema invents nothing the docs claim). Ordering by dependency makes each wave independently
verifiable — which makes rollback possible and teammate conflicts legible.

## Canonical wave sequence

| # | Wave | Done when |
|---|---|---|
| 0 | Baseline | Gate command captured as the regression bar; working tree re-checked for teammate-authored dirty files; stale-only ledger corrections (things already resolved that still say pending) land |
| 1 | Decisions recorded | Owner answers exist in the project's decision home, dated, with prior-decision revisions marked as revisions |
| 2 | Structures created | New homes (folders/files/indexes) exist with real content — an empty scaffold is NOT done; existence never counts as substance |
| 3 | Moves (per-area batches) | One area per commit: content extracted to owners, originals reduced to intent+pointer, every inbound link rewritten, moved file keeps history (git mv) |
| 4 | Reconciliation sweep | Contradictions rewritten to the decided value in EVERY home; invented content deleted or declared; stale markers closed; terminology renamed |
| 5 | New owning docs | The doctrines/functions/playbooks the plan named, written with content — not stubs |
| 6 | Lesson folding | Known mistake-classes become prevention law inside their owning docs; no parallel catalog unless the project asked for one |
| 7 | Rulebook & index sync | Descriptions of every rewritten file updated in the same wave (half-described = half-moved); router indexes link new docs; sync/update all (see §Multi-home below) |
| 8 | Verification | Final gate + falsified-string sweep + decision-coverage check (every owner answer referenced by the docs that must obey it); report closes each defect row or defers it with a reason |

Small corpora merge waves 2–3 or 5–6; the sequence never inverts.

## The gate

Each wave ends behind a **verification adapter** — the project's own tool, discovered at census
time, not invented by this skill:

1. Find the strongest mechanical checker the corpus has (doc link/orphan checker, lint, tests,
   schema validator, build). Record the command in the plan.
2. Run it before committing the wave. **Red = fix inside the same wave.** A queued red state
   poisons every later wave's diagnosis.
3. If the corpus has NO checker, the wave's gate is the grep-equivalent (broken references,
   duplicate strings, falsified values) — and creating the missing checker is itself a legitimate
   finding for the plan's optional waves.
4. No wave commits with "will verify later".

## Atomic commit per wave

One commit = one wave = one reason. Message: imperative subject naming the wave; body carries the
what/why, the **gate result**, and every **deviation** from the approved plan with its reason —
e.g. chose path X over the plan's Y because three artifacts already used X; kept provenance content
in place instead of moving it because the move had no consumer. A deviation recorded later is
denial; recorded in the commit it is engineering.

Commit conventions follow the project's rulebook; this skill never imposes authorship trailers,
branch models, or push behavior (push stays the owner's call).

## Teammate safety

- Before every wave: check the working tree. Files changed that THIS run did not author are
  teammate state — re-read them, adapt additively, never revert/reformat/stash them.
- Concurrent edits on the same file: pause briefly, re-read, merge intent, proceed; on collision,
  surface it in the report instead of winning.
- History operations (reset/clean/amend/force) are outside the skill's authority — never initiated.

## Multi-home discipline (the sync/update law)

When the same meaning legitimately lives in several artifacts (spec + schema + code + docs), the
plan names a home per facet and lists the mirror locations with change triggers. Any wave touching
the meaning updates every listed location in the same commit; if a new mirror is discovered
mid-wave, update it and add it to the list in the same change. Prefer killing a mirror over
maintaining a mirror — a pointer is cheaper than a duplicate. (When the plan calls these a sync
block, the block rows are exactly that list.)

## Clean-empty exits

- A census with no findings: report, no edits. Done.
- A wave whose findings the owner declined: log the declination, keep the corpus as-is, continue
  the sequence.
- A plan whose approval changes mid-flight: fold the new owner request into the remaining waves
  immediately — an accreting scope is normal here, and the plan file is updated, not ignored.

## Failure protocol

A wave that cannot complete (missing authority, contradictory state, tool failure) stops the
sequence — finish, commit, report the blocker with options, and either fix inside the wave or
hand it to the owner. Never skip forward; a skipped wave silently re-opens every gate after it.