# Viber — `vcompact` (Making Room)

## 1. Overview

`vcompact` is Viber's compaction Skill and a Viber **command** (`viber` skill → `references/lifecycle.md` 7.8 — a real Skill whose
name carries the `v` prefix). It takes the resources a project accumulates — settled memory rows that
became history, superseded doc iterations, finished task trails, artifact batches worth keeping — and
moves them into a timestamped, indexed archive under `.viber/.compact/<id>/`, freeing the active workspace
for new work. It runs when the user asks or when the Router flags that an area has grown fat with history;
it is always optional — "in order to free space, if needed."

The command:

```text
/viber compact                 # compact an area the user or Router named
/viber compact restore <id>    # move an archive back
```

Once implemented, its `SKILL.md` carries `viber: part` — and as a Viber Skill it always participates under
supervision (`viber` skill → `references/supervision.md` 3).

### Core Principle

**Make room, not losses.** Compaction turns hot clutter into cold, indexed history. If you cannot say how
every file comes back, you have not compacted — you have deleted.

---

## 2. What "Space" Means

Two budgets exhaust, and compaction serves both:

- **Disk** — every generation of drafts, iterations, and reports piling up in the active tree.
- **Attention** — the real one. A 900-line `settled.md` is unreadable context: every future session re-pays
  for history nobody revisits. The active file should hold current truth; history belongs where it stays
  findable but stops costing attention.

---

## 3. When It Runs

| Trigger | Who decides |
|---|---|
| The user asks ("free some space", `/viber compact`) | the user picks the scope |
| The Router flags a bloated area (finished history outweighing active content) | the Router flags; `vcompact` + the user decide what moves |

Never: silent background compaction, scheduled compaction, or compaction of anything still active. "If
needed" is a human call.

---

## 4. What Compacts (illustrative, not exhaustive)

| Target | Moves | Stays |
|---|---|---|
| Memory sediment | `settled.md` / `learnt.md` rows long-applied and dormant | open questions, recent and operative rows, one pointer line |
| Superseded docs | older spec/draft iterations replaced by current versions | the current version |
| Finished task trails | subagent reports, session records of closed work | their findings, already living in memory/spec |
| Keeper artifacts | generated output worth tracing but not hot (normally purged instead) | a pointer describing what was there |
| Anything the user marks inactive | per the user's word | everything not named |

**Never compacted:** open `memory.md` questions, current specs, in-progress work, code, root-files. An
ambiguous target is **asked, with a recommendation** — the supervision pattern (`viber` skill → `references/supervision.md` 5.3),
never a silent judgment call.

---

## 5. The Archive

```text
.viber/.compact/
├── index.md                       one line per compaction: id · date · trigger · reason · contents
└── <id>/                          id = YYYYMMDD-HHmm-<slug> — sortable, human-readable, never reused
    ├── manifest.md                every moved path, its origin, why, and how to restore
    └── …the moved files…          original relative layout preserved; browsable, never zip-buried
```

- The archive lives under `.viber` like all Viber state (`viber` skill → `references/structure.md` 3.7).
- Files **move**, they do not merge, rewrite, or compress — the archive is the same tree, just cold.
- The slug names the compaction (`lean-memory`, `phase2-closeout`) so the index reads like a diary, not a
  dump.

---

## 6. The Manifest

Written **first**, before any file moves — an archive without a manifest is a rumour:

| Field | Content |
|---|---|
| Date · trigger · reason | when, who asked (user / Router flag), and why now |
| Moved table | `archived path ← original path — what it was`, one row per file |
| Restore | the exact command, and any caveats (collisions to expect) |
| Scope note | what was considered and deliberately left active |

A later session should need nothing else to trust the archive.

## 7. Pointers at the Origin

After the move, every origin gets a one-line pointer, so no reader is ever confused by a vanished file:

- in a memory file: `> 14 rows compacted → .viber/.compact/20261115-1830-lean-memory/`
- for a moved doc set: one `.compacted.md` note in the directory that held it.

Pointers are the only residue in the active area — cheap, honest, and removable on restore.

---

## 8. Restore

`/viber compact restore <id> [paths…]`:

1. Read the manifest; move the named files back to their recorded origins.
2. Remove the pointer lines; mark the index row `restored`.
3. Any origin already occupied → **ask the user** (merge, rename, or abort); never overwrite.

Restore is a first-class half of the skill: compaction that cannot be undone is deletion wearing a feature
name.

---

## 9. Git Treatment

`.viber/.compact/` is **committed by default** — preserved knowledge, exactly what the umbrella is for.
The judgment case is size: an archive batch heavy in binaries (screenshots, builds) gets the standing
question — **keep (commit) or purge** — because artifacts are disposable by design (`viber` skill → `references/structure.md` 3.5)
and `vcompact` never silently inflates the repository.

---

## 10. What Compaction Is Not

- **Not backup** — Git history is. Compaction moves the working set to cold storage inside the project.
- **Not deletion** — every path is restorable through its manifest.
- **Not archiving-by-zip** — the archive stays a browsable file tree.
- **Not a reviewer of quality** — it does not judge whether a doc was good, only whether it is done.
- **Not automatic** — user-triggered or user-approved, always.

---

## 11. How It Connects

| Component | Relationship |
|---|---|
| `memory` | Settled rows that became history are the prime target; open rows are protected. The memory files stay lean ledgers. |
| **Router** | Flags bloated areas (`viber` skill → `references/router.md`); never compacts anything itself. |
| `lifecycle` | Shared/intermediate Skill (`viber` skill → `references/lifecycle.md` 7.7) — accumulation is phase-blind, so compaction runs in any phase. |
| `supervision` | Lives wholly under the umbrella; ambiguous targets follow the ask-and-recommend rule. |
| `structure` | Keeper artifacts graduate (structure 3.5) into the archive; disposable ones purge instead — the user's call on binary-heavy batches. |

---

## 12. Rules

- **Move, never destroy; write the manifest first.**
- **Active is never compacted** — open questions, current specs, in-progress work stay hot.
- **Ambiguous → ask and recommend**, never assume (`viber` skill → `references/supervision.md` 5.3).
- **Every origin keeps a pointer; every compaction keeps an index line.**
- **Id format `YYYYMMDD-HHmm-<slug>`, unique and never reused.**
- **Restore uses the manifest; collisions ask; nothing is overwritten.**
- **Binary-heavy batches: keep-or-purge is the user's decision.**

---

## 13. Boundaries

### vcompact SHOULD

- Make the active area smaller while keeping history reachable.
- Record everything it moved, with origins and a restore path.
- Respect the memory files' live/ledger split.
- Ask on every judgment call and state its recommendation first.

### vcompact SHOULD NOT

- Delete, rewrite, merge, or compress content.
- Touch code, root-files, or active work.
- Run on a schedule or without a user trigger/approval.
- Compact an area it cannot fully describe in a manifest.
- Grow the repository silently with large binaries.

---

## 14. Flow

The compaction pipeline is diagrammed in [`compact-flow.mmd`](../assets/diagrams/compact-flow.mmd): trigger → select → protect
active → id → manifest → move → pointers → (keep-or-purge on binaries) → done, with restore looping back.

---

## 15. Open Items

1. **Flag threshold.** When the Router calls an area "grown fat" — a line budget per active file, a
   ratio of history to current content, or judgment left fully human.
2. **Batch shape.** One archive per compaction session (bundle) vs narrow per-area archives — affects how
   restores are named.
3. **Archive aging.** Whether a `.compact` archive itself may eventually be purged (archiving the archive),
   and after what user-decided horizon.
