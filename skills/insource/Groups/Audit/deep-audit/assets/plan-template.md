# <project> — <what this reconciliation does> Plan

## Context

Why this plan exists: what triggered it (user ask + census results), the problem it addresses in
two or three sentences, and the intended end state. A reader who skipped the whole audit
understands from this section alone what is being fixed and why now.

Census basis: N files read end-to-end by M read-only auditors; findings — X boundary violations,
Y contradictions, Z invented assertions, … ; the worst K items named here.

## Decisions taken (owner answers)

| # | Question | Answer | Where it lands |
|---|---|---|---|
| D1 | … | … | wave(s), file(s) |

Deferred (asked later / logged as open, never guessed): list with what blocks each.

## Phase 0 — Baseline and safety

- gate command + current counts (regression bar)
- working-tree / teammate check
- stale-only ledger corrections (no content moves)

## Phase 1 — Record decisions

- exact decision-home file(s); revision rows for superseded answers

## Phase 2 — Structures created

| New home | Contents | Wave |
|---|---|---|
| path/ | what lands there and from where | |

## Phase 3 — Boundary moves (per-area batches)

Each batch: source section → destination; originals become intent + pointer; inbound links
rewritten; history preserved via git mv; per-batch commit.

## Phase 4 — Contradictions and inventions sweep

Item-by-item: current homes, chosen truth, files rewritten, deletions named, falsified strings
added to the final sweep list.

## Phase 5 — New owning docs

| Doc | Content | Replaces |
|---|---|---|

## Phase 6 — Lesson folding

| Class | Symptom | Owning doc | Prevention law |

## Phase 7 — Rulebook and sync blocks

- every description/index line updated for files rewritten or moved
- multi-home list with change triggers
- rulebook rows that stopped being pending

## Verification gates

After EVERY phase:

```
<gate command>        # e.g. the project's checker/tests/lint
<grep sweeps>         # falsified strings must return only deliberate history
```

End-to-end: decision-coverage check (each D# referenced by the docs obeying it), defect-inventory
closure (every finding resolved or explicitly deferred with reason), gate at baseline or better.

## Critical files

The list implementers touch most; read them fully before editing, re-check for teammate changes
per wave.

## Honest scope trims

Deliberately untouched, with why: churn-with-no-consumer moves, prototype/runtime code fixes
outside doc scope, explicitly deferred questions with structured `Pending (Drafting)` markers, git operations left to the owner.
Each trim is a named decision, never a silence.