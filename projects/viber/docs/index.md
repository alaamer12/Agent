# Viber — Design Draft Set

> Design drafts for the Viber skill suite shipped at `skills/{viber, vinit, vcompact, vflow, adapt}`
> (this project: `F:\Projects\Agent\projects\viber`). These docs are the design; the skills are the
> enforceable artifact. See `PIPELINE.md` at project root for the draft-to-skill workflow.
> Read exactly the doc your task names — each owns one concern; the others are links, never repeats.

## Regime — how Viber governs a project

Local index: [regime/index.md](regime/index.md)

| Document | Concern it owns |
|---|---|
| `regime/lifecycle.md` | the lifecycle phases inside project phases [DR][IP][PP], their Skills, shared/intermediate capabilities, the commands (7.8), the Skills inventory |
| `regime/router.md` | the Router layer — tracking, next-step logic, suggestions, warnings, state |
| `regime/supervision.md` | the umbrella — activation, participation, rerouting rule |
| `regime/structure.md` | the canonical layout — root-files, code, `tools/`, `scripts/`, `artifacts/`, `scratch/`, `.viber/` |
| `regime/memory.md` | the conversational ledger — `memory.md` / `settled.md` / `learnt.md` |

## Commands — the v-commands

Local index: [commands/index.md](commands/index.md)

| Document | Concern it owns |
|---|---|
| `commands/init.md` | `vinit` — the entry command spec |
| `commands/compact.md` | `vcompact` — the compaction command spec |
| `commands/flow.md` | `vflow` — the task-scale flow command spec |

## Diagrams

Local index: [diagrams/index.md](diagrams/index.md)

| Path | Contents |
|---|---|
| `diagrams/` | renderable `.mmd` flow diagrams, one per doc (+ one legacy png) |

**Standing instruction:** update this index in the same change whenever a document is added, removed or
moved — a stale map rots the territory it describes.