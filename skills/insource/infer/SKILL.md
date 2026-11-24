---
name: infer
description: Disciplined inference from reference projects. Use when the user says "look at X", "infer from X", "do similar to X", "like they did", "use X as reference", or points at another project as a model. Classifies each reference decision by transferability, need-tests it against THIS project, and asks before adopting domain-specific architecture. Kills the "copy whole Y into X" anti-pattern.
---

# Infer

A reference project is a **menu**, not a blueprint. Order what fits this project's appetite.
Never bring the whole menu to the table.

## When this fires

Any instruction that points at another project as a model: "look at X", "do similar",
"infer from X", "like they did", "use X as reference", "how does X do it — do that."

## The loop

### 1. Inventory

Read the reference. List every architectural decision it makes — runtime, frameworks,
services, deployment targets, package structure, data flow, background workers, platform
targets. One line per decision. Do not filter yet.

### 2. Classify

Tag each decision with exactly one tier:

| Tier | What it is | Transfer rule |
|---|---|---|
| **Quality** | Universal engineering standards: strict typing, linting, test discipline, error contracts, naming conventions | Transfer freely. These improve any project. |
| **Tool** | Stack choices that serve any domain: a runtime, a framework, a validator, a CSS engine, a test runner | Transfer if compatible with THIS project's confirmed stack. One-line reason. |
| **Domain** | Architecture that exists because of the REFERENCE's problem: a processing service, a native mobile target, a media pipeline, a specific data model shape, a sync engine | **ASK.** The reference's need is not this project's need. State what need drove it in the reference, then ask whether THIS project shares that need. |
| **Scale** | Infrastructure that exists because of the REFERENCE's size: monorepo orchestration, worker pools, caching layers, CI complexity, multi-service deployment | **ASK.** State the scale trigger in the reference, then ask whether THIS project is at that scale or expects to be. |

### 3. Need-test

For every Domain and Scale decision, write one sentence:

> "In [reference], [decision] exists because [need]. Does [this project] have [need]?"

If the answer is not already settled in THIS project's docs or prior conversation, **ask the user**.
Do not answer it yourself by analogy. "They have it" is not evidence. "The prototype has a
mobile folder" is not evidence of native targets. "Ionic is in the stack" is not evidence of
Capacitor deployment.

### 4. Verdict

Produce a three-column table:

| Decision | Verdict | Reason |
|---|---|---|
| Strict TS | **Take** | Universal quality; user confirmed maximum strict. |
| Hono + Bun | **Take** | Tool; fits confirmed orchestrator runtime. |
| Orchestrator service | **Ask** | Domain; MuslimTube needs video ranking. Does Kabrha need server-side computation beyond PB CRUD? |
| Capacitor native | **Reject** | Domain; no native target confirmed. Prototype mobile folder is responsive web. |
| Turborepo | **Ask** | Scale; MuslimTube has 12 packages. Kabrha has 0 code. Justified now or premature? |

Present this table to the user BEFORE writing any architecture doc or code.
The user confirms, adjusts, or overrides. Then proceed with only the confirmed set.

### 5. Write from THIS project

Architecture docs describe what THIS project will build, grounded in THIS project's
requirements. The reference appears only as a cited inspiration for specific decisions
("error catalog pattern adapted from MuslimTube's `packages/errors`"), never as the
structural template. If a doc section exists only because the reference has it, delete it.

## Hard rules

- **Never skip the target's own gates.** If the architecture skill asks "does this app target
  multiple OS?", ask it — even if the reference answers yes. The reference is not the interviewee.
- **Existence ≠ requirement.** A service, a platform target, a worker, a package in the
  reference is evidence of the REFERENCE's needs only.
- **No silent adoption.** Every Domain/Scale decision that enters THIS project's docs has
  either a user confirmation or an explicit "user said infer freely" with the scope named.
- **Reject with reason.** A rejected decision gets one line explaining why it doesn't fit.
  This prevents the next agent from re-inferring it.
- **The reference is read-only.** Never modify the reference project. Never import its files.
  Extract patterns, not code.

## Clean exit

If the reference is small or the user's instruction is narrow ("just look at their tsconfig"),
skip the full loop. Classify the one decision, need-test it, take or ask. The loop scales
to the scope of the inference request.