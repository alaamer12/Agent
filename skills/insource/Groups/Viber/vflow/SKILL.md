---
name: vflow
version: 1.0.0
description: 'Viber flow command: captures a recurring class of work as a task-scale mini-lifecycle — three small files under .viber/flow/<name>/: sequence.md (the source: per-step contract with skill, input, output, done-gate, on-fail), lifecycle.md (the readable map of stages and gates), lifecycle.mmd (the picture, per use-mmd). Steps compose existing Skills only; a flow orders work and never overrides project policy. Supports create / list / edit and running a flow step by step.'
when_to_use: /vflow, "how we always do X", the same multi-step sequence keeps being hand-assembled for the same kind of work, or current work matches an existing flow and its sequence should be followed.
argument-hint: "[create <name> | list | edit <name> | run <name>]"
---

# vflow — mini-Vibers for repeated work

A flow is Viber at task scale: same anatomy (stages, gates, Skills doing the work), scoped to one journey
like `create-new-page` or `hotfix`.

## create <name>

1. **Grill the steps** before writing anything: what starts this flow, the ordered steps, which Skill or
   command does each, what counts as done per step, what happens on a miss, where each step's output lands
   (umbrella rules apply).
2. Fill the three files from `assets/templates/` into `.viber/flow/<name>/` — sequence.md first (it is the
   source), then the map, then the diagram.
3. Steps must reference existing Skills. A step nobody owns is not invented — it is an `adapt` signal.
4. Keep it small: near ten steps max; longer is two flows.

## list / edit

List flows with one-line purposes from their lifecycle.md. Edits land in sequence.md first; map and diagram
follow it (truth order). During [DR] flows are revisable like any draft.

## run <name>

Read `sequence.md`, walk rows in order: run the step through its Skill → check the done-gate → on a miss
follow on-fail. Findings that surface go to the memory ledger (`viber` skill → `references/memory.md`). A
discovered step updates sequence.md in the same change.

## Load when detail is needed

| Need | Read |
|---|---|
| Full spec (truth order, rules, boundaries, open items) | `references/flow.md` |
| The pipeline diagram | `assets/diagrams/flow-flow.mmd` |
| Seeds for a new flow folder | `assets/templates/` |

## What this command is not

Not a second Viber (no copying the four phases), not a governor (project policy outranks any flow row),
not a place for machinery beyond three small files — and no invented steps: a flow is the project's route
through Skills it already has.
