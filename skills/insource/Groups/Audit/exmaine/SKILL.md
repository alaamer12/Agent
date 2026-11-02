---
name: exmaine
description: >-
  Examine a project from the inside out, starting at AGENTS.md: follow every doc path it
  declares (design docs, units, glossary, commitments, decisions, skill sources), read them,
  sweep the code against what the docs claim, and deliver a complete overview that orients an
  agent fully around the project. Strictly static and read-only: never runs install, test, build
  or serve commands - files are only read; anything unprovable by reading is reported as an
  unverifiable runtime claim, never assumed. /exmaine full runs the complete examination: every
  area checked against its stated intent, broken pointers and orphan code recorded in a gap
  ledger, ending with the full project overview. Use when asked to exmaine/examine/inspect the
  project, to get oriented in an unfamiliar repo, 'read the docs and check the code', or before
  a large task needing whole-project understanding. Not a verdict run ('is this complete and
  verified?' = please-verify), not refactoring proposals, not runtime debugging.
---

# Exmaine

Understand the project **as its own documents claim it exists** — then check whether the code
agrees. The deliverable is a complete, honest overview: what this project is, how it is built,
what is consistent, what diverged, and what cannot be known without running it.

## The hard constraint

Static, read-only, always. Allowed: reading files, listing directories, grep/glob, read-only git
queries (`git log`, `git status`, `git show`). Forbidden: executing anything the project owns —
install, test, build, lint, serve, migrations, scripts, CI — and any write. "Passes" here means
*is consistent and wired by construction*, proven statically; where only execution could settle a
question, say exactly that and move on. File existing is not proof of behavior — it is a
finding-level at best (see `references/03`).

## The path

1. **Start at AGENTS.md** (or the project's declared entry doc). No AGENTS.md? Record it as
   finding #1, fall back to README + manifests + CI to infer structure.
2. **Follow the doc chain.** Every path the entry doc references gets read: design docs, units
   catalog, GLOSSARY, COMMITMENTS, IDEA.md, SYSTEM-COMPONENTS.md, decision records, and the
   sources listed in its Skills section. Then the paths those docs reference — breadth-first,
   bounded. A referenced file that doesn't exist is a finding, not a dead end.
   `references/01-doc-chain.md`
3. **Extract the intent ledger.** Each doc makes claims ("module X does Y", "runs on Z", "the
   flow is A→B→C"). Collect them as (claim, source, code to look for) — this is what step 5
   checks against. Never invent claims the docs don't make.
4. **Sweep the code statically**: entry points, module map, wiring, configuration, dependency
   manifests, CI definitions, tests-as-written. Secrets: names and presence only, never values.
   `references/02-code-sweep.md`
5. **Cross-check**: every ledger claim gets code evidence; every code module gets either a doc
   claim or an orphan flag. Evidence level per item, not vibes.
6. **Report the complete overview** — identity, structure, behavior map, health, gaps, and the
   runtime-unknown list. Shape: `references/03-full-examination.md`.

## Commands

| Command | Run |
|---|---|
| `/exmaine` | Steps 1–4 + overview of what was found: orientation without verdict-style claims |
| `/exmaine full` | All six steps: per-area intent checks, gap ledger, doc-vs-code cross-check, full project overview |
| `/exmaine <area>` | Steps 1–5 scoped to one directory/module/doc the user names |

Default when the user says just "exmaine the project": run `/exmaine`, and say in one line what
`full` would add.

## What it never does

- Runs or installs anything; edits anything.
- Claims runtime behavior from static reading — runtime questions go to the
  runtime-unknowns list for the user to settle.
- Pads the overview with restated doc text; the value is the **cross-check**, not the echo.
- Judges quality or proposes refactors — findings are consistency facts ("doc says X, code does
  Y, pointer broken"), not opinions.

## Boundaries

| Situation | Skill |
|---|---|
| "Is this work actually complete and sufficiently verified?" → verdict (COMPLETE/INCOMPLETE/BROKEN) | `please-verify` |
| "What is this binary/website really doing?" black-box inspection | `dig-binary` |
| Fixing what the sweep finds | explicit user request, then normal coding skills |
| Deep multi-source research about the world, not this repo | `deep-research` |

`please-verify` answers *is it true and done* against requirements with an evidence ladder;
`exmaine` answers *what is this project and does it agree with itself* and leaves with an
overview. A project may call either; they don't replace each other.

## Resources

- `references/01-doc-chain.md` — starting files, following references, reading skills sources
- `references/02-code-sweep.md` — static sweep map: entries, wiring, config, deps, CI, tests
- `references/03-full-examination.md` — intent cross-check, evidence levels, gap ledger, overview shape
- `examples/orientation-walkthrough.md` — a short worked pass on a small fictional project
