---
name: viber
version: 1.0.0
description: 'The Viber regime — disciplined vibe-engineering. While a project declares Viber, every agent works under it: relocatable knowledge lands under .viber/, code and root-files stay untouched, open questions / answered decisions / learned facts go to the memory ledger, deferred items surface when unblocked, and drafts stay revisable in [DR]. Its commands are the sibling skills vinit (entry), vcompact (making room) and vflow (task-scale flows). Not for choosing a tech stack (techstack), writing the rulebook (agents-md), closing design topics one by one (close-topics), or running builds and tests.'
when_to_use: Any work inside a project whose AGENTS.md declares Viber — routing outputs, capturing to the memory files, checking supervision/structure/lifecycle rules, or on /viber and "vibe-engineering with discipline" requests. Also when an agent is about to place a knowledge artifact anywhere and does not know why.
argument-hint: "[the work under viber, or status to read where the project stands]"
---

# Viber — the regime, not a task

Viber guides the workflow without controlling the code. This skill is the standing posture; the heavy specs
live in `references/` and load one at a time.

## First act — activation check

Read `AGENTS.md`. Viber is active when it carries a Viber declaration — the `## Viber` section or any clear
sentence ("This project uses Viber", "Vibe Mode On"). No declaration → this skill does not apply: work
normally, and say once that `/vinit` would set the regime. Never write or remove the declaration yourself.

## Standing behaviors

- **Umbrella first.** Participating Skills' relocatable knowledge goes to `.viber/<original-relative-path>`.
  Layout homes beat the umbrella: run output → `artifacts/<producer>/`, agent temp → `scratch/<task>/`,
  utilities → `tools/`, operations → `scripts/`; root-files (`AGENTS.md`, `README.md`) and all code stay.
- **Capture on arrival.** A question deferred → `memory.md` (with what blocks it). A question answered —
  explicit or implied → `settled.md` (answer + reason, marked provisional during [DR]). A fact learned about
  the user or project → `learnt.md` (evidence + implication). Record when it happens, not at session end.
- **Honest gaps.** An unanswered decision stays `pending — not assumed`; never fill it with a plausible default.
- **Draft posture.** During [DR] docs and prior answers are the current best, not law (`thaw`); formal
  decision records begin only at [IP].
- **Router stance.** Know where the project stands (phase, completed, open, blocked) and surface deferred
  questions when their blockers clear — guidance, never control; the user decides.

## Load exactly one reference

| The question | Read |
|---|---|
| Phases, skills, commands, project states [DR][IP][PP] | `references/lifecycle.md` |
| Where does this artifact go? Supervision active? Participation? | `references/supervision.md` |
| Canonical layout, home of every file kind, git treatment | `references/structure.md` |
| Memory files: templates, field rules, move-on-answer discipline | `references/memory.md` |
| Progress tracking, next-step logic, skill suggestions, warnings | `references/router.md` |
| A subsystem diagram (render or edit) | `assets/diagrams/*.mmd` |
| Bootstrapping a memory file from scratch | `assets/templates/*.md` |

## Commands (sibling skills)

| Command | Does |
|---|---|
| `/vinit` | enter Viber: registry, memory files, layout duties, the AGENTS.md declaration, start the flow |
| `/vcompact` | make room without loss: archive finished history to `.viber/.compact/<id>/` |
| `/vflow` | build task-scale mini-lifecycles under `.viber/flow/` |

## Layout

```text
viber/
├── SKILL.md              this posture
├── references/           lifecycle · supervision · structure · memory · router
└── assets/
    ├── diagrams/         the four flow diagrams (.mmd, obey use-mmd)
    └── templates/        empty memory.md / settled.md / learnt.md
```

## What this skill is not

Not the lifecycle steps themselves (`idea-md`, `steering`, FULL CODE do those), not a tech-stack chooser,
not the rulebook writer, not an executor — Viber makes the right things visible at the right time and
leaves every decision with the user.
