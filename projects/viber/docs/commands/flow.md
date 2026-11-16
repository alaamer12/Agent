# Viber — `flow` Command (`vflow`)

> The `vflow` command spec: task-scale mini-lifecycles under `.viber/flow/`, `sequence.md` as the source of truth.

## 1. Overview

`vflow` builds **flows**: task-scale lifecycles the project defines for itself — small subsets of Viber's own
lifecycle that chain the steps for a recurring class of work. Using vflow is like building a mini-Viber: the
same anatomy (phases in order, gates between them, Skills doing the work), scoped to one repeated journey —
say, "what we always do when creating a new page".

Each flow is a **simple folder** under the umbrella: `.viber/flow/<name>/` (e.g. `.viber/flow/create-new-page/`),
holding three files. The command:

```text
/viber flow create <name>    # grill the steps into a new flow
/viber flow list             # what flows this project has
/viber flow edit <name>      # revise one
```

As a Viber command (`../regime/lifecycle.md` 7.8), its real Skill name carries the `v` prefix: `vflow`.

### Core Principle

**A flow is Viber at task scale.** Same parts, smaller scope — and like any draft, the flow is the project's
current best routine, revisable, never a cage.

---

## 2. What a Flow Is

A flow is one named journey through existing Skills and gates. It is:

- **A route, not a ruler.** It sequences work; it never overrides project policy (`AGENTS.md`, supervision,
  memory rules) — where a flow step contradicts Viber, Viber wins and the flow is corrected.
- **Composed of existing Skills.** Steps call `grill-me`, `steering`, FULL CODE's work, `commit` — whatever
  the project already has. A flow that invents a step nothing owns is a gap for `adapt` to close, not a
  paragraph to write.
- **Simple by design.** Three small files. If a flow grows machinery, it is trying to become a second Viber
  and failing at being a routine.

**Worked example — illustrative only, not a default or template:**

```text
feature → document it → grilling → re-document → implement → test → verify → commit
```

A feature arrives, gets drafted into a doc, is grilled until answers settle, the doc is rewritten with them,
built, tested, verified, committed. One project's rhythm; `vflow` output is always the project's own naming of
its steps.

---

## 3. The Flow Folder

```text
.viber/flow/<name>/
├── lifecycle.md     what this flow is · its stages · its gates
├── lifecycle.mmd    the flow drawn — obeys the diagram rules (use-mmd)
└── sequence.md      the source: every step's full contract
```

- **Folder name** = the class of work, slugified (`create-new-page`, `hotfix`, `deck-authoring`).
- Lives under `.viber` like all project knowledge (`../regime/structure.md` 3.7): committed, visible, restorable.

### Truth order

When the three files disagree, **`sequence.md` is the source** — it carries the step contracts.
`../regime/lifecycle.md` is the readable map, `lifecycle.mmd` the picture. Fix a disagreement by editing the prose and
the diagram to match the sequence, or revising the sequence itself if the sequence is what changed.

---

## 4. The Three Files

### 4.1. `../regime/lifecycle.md`

The flow's small version of Viber's lifecycle: one paragraph on what the flow is for, the ordered stages with
one line each, and the gate that ends each stage. Written so a new agent can read it in ten seconds and know
what kind of journey it's signing up for.

### 4.2. `lifecycle.mmd`

The flow diagram. It obeys `use-mmd`: names on nodes, meaning on edges, status by color, legend as swatches,
no sentences, no placeholders. It draws what `sequence.md` defines — nothing more.

### 4.3. `sequence.md` — the source

The authoritative table, one row per step:

| # | Step | Does | Skill / command | Input | Output | Done-gate | On-fail |
|---|---|---|---|---|---|---|---|
| 1 | feature | state the ask in one paragraph | — | the user's request | ask sentence | ask is testable | re-ask |
| 2 | document it | draft the feature doc | `document` | ask sentence | draft doc | draft exists | — |
| 3 | grilling | settle every open point | `grill-me` | draft doc | answered points | no open question left | continue |
| 4 | re-document | rewrite with the answers | `document` | answers | final doc | doc matches answers | → 3 |
| … | | | | | | | |

The table is illustrative: the example's real steps, columns, and count are the project's call — but every
row must answer its column, or the step is not executable, just described.

---

## 5. How a Flow Runs

1. Work matches a flow's trigger (the user names it, or the Router suggests it — `../regime/router.md` 5.7).
2. The agent reads `sequence.md` and walks the rows in order: run the step through its Skill, check the
   done-gate, follow the on-fail route on a miss.
3. Findings and decisions that surface during the run go where Viber says — `.viber/memory.md` while open,
   `settled.md` once answered (`memory.md`). The flow routes work; the memory files keep its record.
4. A step discovered mid-run that the sequence missed updates `sequence.md` in the same change — the
   write-back duty, applied to flows.

---

## 6. Relationship to Viber

| Component | Relationship |
|---|---|
| `vflow` | Viber command (`../regime/lifecycle.md` 7.8): grills the steps, writes the three files, registers the flow. |
| `lifecycle` | A flow is a subset of it — stages speak the project's existing step names, never invent a parallel vocabulary. |
| **Router** | Suggests a flow when current work matches one; tracks its steps like any workflow state. |
| `adapt` | A flow step no Skill owns is a recurring-need signal — adapt closes the gap; the flow then references what adapt settled. |
| `supervision` | Flow folders live under the umbrella like all knowledge (5.1); during [DR] flows are revisable. |
| `structure` | `.viber/flow/` is part of the umbrella tree — never at the root, never inside `artifacts/` or `scratch/`. |

---

## 7. Rules

- **Three files, one folder, one flow.** No fourth file grows silently; extra prose belongs in `sequence.md` rows.
- **`sequence.md` is the source.** Map and diagram follow it; disagreement is a defect fixed toward it.
- **Steps reference existing Skills**; an unowned step is an `adapt` signal, not a placeholder.
- **Flows order work, never govern it** — project policy outranks any flow row.
- **Keep flows small**: a flow past roughly ten steps is two flows, not one long one.
- **Write-back**: a discovered step lands in `sequence.md` in the same change (`use-mmd` governs the diagram's update).
- **Illustrative ≠ default**: the example flow is an example; every flow the project names is its own.

---

## 8. Boundaries

### vflow SHOULD

- Grill the user for stages, gates, and failure routes before writing files.
- Compose steps from registered Skills and commands.
- Keep the three files tiny and the sequence table the source of truth.
- Route a flow's open questions and answers into the memory files.

### vflow SHOULD NOT

- Copy Viber's four phases wholesale into a "flow" that is just Viber again.
- Add machinery beyond three simple files.
- Let a flow step contradict `AGENTS.md`, supervision, or memory rules.
- Present the example feature-flow as a standard any project must follow.
- Treat a flow as settled law during [DR] — it is the project's best routine so far (`thaw`).

---

## 9. Flow

The vflow pipeline is diagrammed in [`diagrams/flow-flow.mmd`](../diagrams/flow-flow.mmd): create → grill steps → write the three
files → a run walks the sequence with gates → findings land in memory.

---

## 10. Open Items

1. **Trigger matching.** How the Router decides "this work matches `create-new-page`" — a trigger line in
   `../regime/lifecycle.md`, keywords from the flow's name, or the user's word only.
2. **Flow self-refinement.** Beyond write-back of missed steps: whether a finished run should propose gate or
   order edits (sequence.md evolution with evidence).
3. **Flow-of-flows.** Whether one flow may call another (a commit step that runs the `hotfix` flow) — allowed,
   banned, or asked.
