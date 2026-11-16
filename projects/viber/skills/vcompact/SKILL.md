---
name: vcompact
version: 1.0.0
description: 'Viber compaction command: moves accumulated finished history — settled memory rows, superseded doc iterations, finished task trails, keeper artifact batches — into a manifest-first, restorable archive under .viber/.compact/<id>/, freeing active disk and attention while keeping everything reachable. Never touches active work; ambiguous targets are asked with a recommendation. Supports /vcompact restore <id> (move back, collisions asked). Not a backup, not a delete, not automatic — and not a cleaner for code.'
when_to_use: /vcompact, "free some space", the Router flags an active Viber area grown fat with history, or a phase closes and its finished records should go cold.
argument-hint: "[restore <id> | the area to compact — otherwise areas are proposed]"
---

# vcompact — make room, not losses

## Compact runbook

1. **Propose targets** (settled rows / superseded docs / finished trails / keeper artifacts) — list them;
   open questions, current specs, and in-progress work are never candidates.
2. **Ambiguous → ask** with a recommendation (the supervision pattern). Record the user's call.
3. **Create the id**: `YYYYMMDD-HHmm-<slug>` — unique, never reused.
4. **Write the manifest first**: date · trigger · reason · every moved path with its origin · restore steps.
5. **Move** files into `.viber/.compact/<id>/`, preserving relative layout — files move, never merge or compress.
6. **Leave pointers**: one line in each origin memory file or a `.compacted.md` note per moved doc set;
   add a line to `.viber/.compact/index.md`.
7. **Binary-heavy batch** → ask: keep (commit) or purge (artifacts are disposable). Never silently grow the repo.

## Restore runbook

`/vcompact restore <id> [paths…]` — read the manifest, move files back to recorded origins, remove pointers,
mark the index row restored. Occupied origin → ask (merge/rename/abort); never overwrite.

## Rules digest

- Move, never destroy; the manifest exists before the first file does.
- Every compaction is restorable — otherwise it is deletion wearing a feature name.
- User-triggered or user-approved only; no schedules, no silent runs.

| Need | Read |
|---|---|
| Full spec (targets, manifest fields, git treatment, open items) | `references/compact.md` |
| The pipeline diagram | `assets/diagrams/compact-flow.mmd` |

## What this command is not

Not a backup (git is history), not a zip (the archive stays browsable), not a judge of doc quality — it
sorts finished from active and keeps the finished reachable.
