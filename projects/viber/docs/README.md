# Viber — Design Draft Set

> Provenance drafts for the Viber skill suite shipped at `Groups/Viber/{viber, vinit, vcompact, vflow}`
> (source tree `F:\Projects\Agent\skills\insource`). These docs are the design; the skills are the
> enforceable artifact. Future direction changes land in the skill files first, then here.
> Read exactly the doc your task names — each owns one concern; the others are links, never repeats.

| Document | Concern it owns |
|---|---|
| `lifecycle.md` | the four lifecycle phases inside project phases [DR][IP][PP], their Skills, shared/intermediate capabilities, the commands (7.8), the Skills inventory |
| `router.md` | the Router layer — tracking, next-step logic, suggestions, warnings, state |
| `supervision.md` | the umbrella — activation, participation, rerouting rule |
| `structure.md` | the canonical layout — root-files, code, `tools/`, `scripts/`, `artifacts/`, `scratch/`, `.viber/` |
| `memory.md` | the conversational ledger — `memory.md` / `settled.md` / `learnt.md` |
| `init.md` | `vinit` — the entry command spec |
| `compact.md` | `vcompact` — the compaction command spec |
| `flow.md` | `vflow` — the task-scale flow command spec |
| `diagrams/` | the renderable `.mmd` flow diagrams, one per doc (+ one legacy png) |

**Standing instruction:** update this index in the same change whenever a document is added, removed or
moved — a stale map rots the territory it describes.
