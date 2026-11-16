# Viber Development Pipeline

> How design drafts become shipped agent skills. This document governs the project's own development — Viber applied to itself.

## The two layers

| Layer | Path | Phase | Nature |
|---|---|---|---|
| Design drafts | `docs/` | [DR] Draft | Provisional. Ideas get written, grilled, refined. Thaw posture applies — nothing here is law. |
| Shipped skills | `skills/` | [IP] In-Progress | Derived product. What users install and agents execute. Lean, imperative, token-efficient. |

The docs are the source of truth for **why**. The skills are the source of truth for **what the agent does**. When they diverge, the pipeline below defines which wins and how to reconcile.

## Stages

### 1. Draft

Write or refine in `docs/`. Use `close-topics` to walk one design area at a time, `grill-me` to stress-test decisions. Open questions stay visible — never silently omit an undecided point.

- One concern per file, at full depth.
- Diagrams live in `docs/diagrams/` as `.mmd` files; docs link to them, never inline mermaid.
- The `docs/README.md` index stays current (standing instruction inside it).

### 2. Settle

A topic closes when the user decides. Record the decision in the doc: what was chosen, what was rejected, why. Mark the section settled (a brief note, not a formal ADR — this project is still [DR]).

Settled content is stable enough to promote. Unsettled content stays in docs and does not leak into skills.

### 3. Promote

Port settled design into `skills/`. This is a **rewrite**, not a copy:

| Docs version | Skills version |
|---|---|
| Exploratory prose, alternatives, rationale | Imperative contracts: do X, then Y, gate on Z |
| Full context for a human designer | Minimal context for an agent executing a task |
| May explain the same concept twice across files | One home per concept; everything else is a link |
| Diagrams illustrate design reasoning | Diagrams show the agent's decision flow |

Promotion checklist:

1. Identify which skill owns the concern (`viber`, `vinit`, `vcompact`, `vflow`, `adapt`).
2. Write or update the reference file in `skills/<name>/references/`.
3. Update `skills/<name>/SKILL.md` dispatcher if the load-table or mode changed.
4. Update `skills/<name>/assets/` if templates or diagrams changed.
5. Add a back-link in the docs file: "Shipped as `skills/<name>/references/<file>.md`."
6. If the change adds/removes a skill or alters its phase, update `viber.json`.

### 4. Verify

Before shipping:

- Every relative link in the changed skill files resolves.
- Frontmatter: `name` matches folder, `description` is single-line ≤ 1024 chars.
- `viber.json` parses (`python -m json.tool viber.json`).
- No design rationale leaked into skill references (skills tell the agent what to do, not why the design exists).
- No settled decision contradicted by the skill's instructions.

### 5. Ship

From the insource registry root:

```bash
cd F:/Projects/Agent/skills/insource
python manager.py viber
```

This reads `viber.json` (resolved via `../../projects/viber/viber.json`), symlinks every listed skill into all agent roots, and reports relinked/unchanged/failed counts.

After install: verify a symlink resolves (`test -f ~/.qoder/skills/viber/SKILL.md`).

## Sync rules

| Situation | Action |
|---|---|
| Doc changes materially (new decision, altered flow) | Re-promote the affected skill reference. |
| Skill changes (bug fix, wording, new mode) | Add a note in the corresponding doc section. Full doc rewrite only if the design itself changed. |
| Doc and skill contradict | The skill wins for agent behavior (it's what executes). The doc wins for design intent. Reconcile by re-promoting or by updating the doc to reflect the shipped reality. |
| New skill added | Create `skills/<name>/`, add entry to `viber.json`, add doc coverage, run installer. |
| Skill removed | Delete from `skills/`, remove `viber.json` entry, mark doc section superseded, run installer (prunes dangling links). |

## What this pipeline is not

- Not a CI/CD system. No scripts, no automation beyond the existing manager. The agent walks these stages conversationally.
- Not a release calendar. Promotion happens when a topic settles, not on a schedule.
- Not a gate against iteration. Drafts can be re-opened (thaw). A shipped skill can be revised. The pipeline describes the flow, not a one-way ratchet.

## Layout

```
projects/viber/
├── README.md          project identity and map
├── PIPELINE.md        this file
├── viber.json         skill manifest (phases, entries, paths)
├── docs/              design drafts [DR]
│   ├── README.md      global index
│   ├── lifecycle.md   the lifecycle spec
│   ├── router.md      skill routing and fit
│   ├── supervision.md supervision umbrella
│   ├── structure.md   canonical project layout
│   ├── memory.md      memory ledger spec
│   ├── init.md        vinit spec
│   ├── compact.md     vcompact spec
│   ├── flow.md        vflow spec
│   └── diagrams/      .mmd sources + legacy png
└── skills/            shipped agent skills [IP]
    ├── viber/         regime dispatcher + references
    ├── vinit/         entry command
    ├── vcompact/      compaction command
    ├── vflow/         flow command
    └── adapt/         gap-filling intermediate
```