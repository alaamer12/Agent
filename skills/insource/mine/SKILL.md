---
name: mine
description: Runs a deep, budgeted, multi-source research dig to understand not just what a class of thing looks like, but WHY — the decisions, tradeoffs, and constraints behind it, both explicit (stated) and implicit (only inferable). Task-based: sources and technique adapt to what's asked — real GitHub codebases for "top enterprise projects," visual/design references (screens, dashboards, UI patterns) for "50 dashboard designs," or other source types the task points at. Ends by writing one free-form distilled document of everything learned — never a templated report or per-source recap. Trigger this whenever the user says "/mine", asks to "mine" a topic, or asks for a deep dive, deep research, or comprehensive understanding across multiple top/best real-world examples — especially with a budget like "top 20," "for an hour," or "as deep as you can go." Always propose a verified source plan and get explicit user approval before mining starts — never start digging without an approved plan first.
---

# /mine

> Given a topic, plan a set of real, distinct sources (codebases, design
> references, or whatever the task points at); dig into each to
> understand not just what's there but *why*; end with one distilled
> document of everything learned.

Read `references/workflow.md` first — it is the actual skill: the four
phases (plan → mine → track budget → distill), the tool-check step, the
per-source checkpoint habit (free-form notes, not a fixed template — see
Phase 2 in `workflow.md`), and every non-negotiable, all with their
reasoning. This file is a map, not a summary — nothing here is restated
there in less detail, so don't try to run `/mine` from this file alone.

## This skill is task-based, not GitHub-only

The default mental model is GitHub, but `/mine` adapts to whatever the
task actually points at — a topic about designs mines visual references
instead of repos; something with Figma access could mine Figma files. See
`references/workflow.md` → "This skill is task-based, not GitHub-only"
and "Identify the source type and check for the best tool first."

## Where everything lives

| File | What it's for | Read it when |
|---|---|---|
| `references/workflow.md` | The full four-phase process, source-type identification, and every non-negotiable rule | Always, before doing anything |
| `references/search-and-mining-technique.md` | Parallel sections per source type (GitHub, visual/design) — concrete search technique, the what→why→cost chase, summary-vs-synthesis writing test | Before Phase 2 (mining) and Phase 4 (writing) — read the section(s) matching this task's source type |
| `assets/source-plan-template.md` | The plan shown to the user for approval in Phase 1 | Building the plan |
| `examples/distillation-excerpt.md` | Shows the tone/shape of a real Phase 4 output | Unclear what "free-form distillation" should look like |
| `scripts/fetch_repo.sh` (Linux/macOS) / `scripts/fetch_repo.ps1` (Windows) | Verify and clone GitHub repos — codebase-source tasks only | Phase 1 link verification, Phase 2 reaching a codebase source |

Pick the fetch-repo script matching the shell/OS actually in use in this
environment; both take equivalent flags and produce the same JSON output
shape — see either script's `--help`/comment-based help, or
`references/workflow.md`, for exact usage and the one flag (`--depth`
vs. `-Depth`) that isn't expressed identically between them. There's no
equivalent script yet for visual/design or other source types — Phase 1
link verification there is a direct fetch, per `workflow.md`.

**Verification status:** `fetch_repo.sh` has been run against real GitHub
repositories (verify success/failure, clone success/failure, destination
conflicts) and its behavior confirmed directly. `fetch_repo.ps1` is a
faithful line-by-line port of the same logic but has not been executed
against a real PowerShell environment — no PowerShell interpreter was
available to test it while building this skill. Treat its exact behavior
as unconfirmed until it's actually been run once in a real Windows/
PowerShell environment.
