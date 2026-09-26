---
name: mine
description: Runs a deep, budgeted, multi-source dig to understand not just what a class of thing looks like but WHY — and, when the task asks you to decide or compare, to actually run the options through a fair trial and rank them. Task-based on three axes: what a source is (GitHub repos, visual/UI references, documentation sets, research papers, specs and standards, package registries, discussion corpora, postmortems, datasets, or whatever the task points at); how you interrogate it (read-mining — census the source and chase its why; or run-mining — put each candidate through an identical, hard-case trial and measure); and whether candidates are found or authored (5 real OCR libraries vs 5 visual styles you build to compare). Read-mining ends as one free-form distilled document; run-mining ends as a tested, ranked verdict with a score table and a kept, reproducible probe. Trigger whenever the user says "/mine", asks to "mine" a topic, or wants a deep dive across multiple real-world examples — including executable asks like "find the best 5 libraries for X and test them on hard edge cases" or "try 5 styles on Y" — especially with a budget like "top 20" or "for an hour." Always propose a verified source plan and get explicit user approval before mining starts — never dig without one.
---

# /mine

> Given a task, plan a set of real, distinct candidates; interrogate each the
> way the task needs — *read* it to understand not just what's there but *why*,
> or *run* it through a fair, identical trial to measure and rank — and end with
> one distilled document (read) or one tested verdict (run) of what was learned.

Read `references/workflow.md` first — it is the actual skill: the four
phases (plan → mine → track budget → distill), the tool-check step, the
read-vs-run choice inside "mine" — understand a source by reading it, or
decide between candidates by running them through a trial (see
`references/run-mining.md`) — the per-source checkpoint habit (free-form in
shape — never a fill-in template —
but with a content floor every checkpoint must clear: the source's ground
census first, the why and the cost, and a closing ledger of the URLs actually
touched — see Phase 2 in `workflow.md`), and every non-negotiable, all with
their reasoning. This file is a map, not a summary — nothing here is restated
there in less detail, so don't try to run `/mine` from this file alone.

## This skill is task-based — what a source is, how you mine it, where candidates come from

The default mental model is GitHub *reading*, but `/mine` adapts to whatever
the task actually points at, along three axes. **(1) What a source is** —
`references/source-ecosystems.md` indexes everything it can mine (codebases,
visual/UI references, documentation sets, research papers, specs and standards,
package registries, discussion corpora, postmortems, datasets), each with where
its candidates come from, what tool reaches it, and its census numbers; an
ecosystem with no block yet is mined by that file's "generic shape" and gets its
block written afterwards. **(2) How you interrogate it** — *read-mining* (reach
a source, census it, chase its why) is the default, but a task like "find the
best 5 OCR libraries and test them on hard scans" or "try 5 styles on this
screen" is answered by *running* each candidate through an identical, measured
trial — `references/run-mining.md` is that whole method. **(3) Where candidates
come from** — *found* (real repos, packages, screens you discover) or *authored*
(approaches or styles you build yourself in order to compare). The modes
compose: a run-mine of authored candidates is usually seeded by a quick read-mine
of the option space. See `references/workflow.md` → "This skill is task-based —
what a source is, how you mine it, where candidates come from" and "Settle the
mining method and the candidate provenance first."

## Where everything lives

| File | What it's for | Read it when |
|---|---|---|
| `references/workflow.md` | The full four-phase process, source-type and mining-method identification, and every non-negotiable rule | Always, before doing anything |
| `references/source-ecosystems.md` | Every ecosystem `/mine` can mine, one block each: candidate, discovery, reach, census, where the "why" lives, dedup traps — plus what counts as a ledger entry there | Always, right after `workflow.md` — it's how you decide what kind of source this task is; the "generic shape" is what you use when nothing matches |
| `references/search-and-mining-technique.md` | The ground census (measured size, composition and structure — commands, plus the traps that make a count quietly wrong) and the source ledger (URLs touched, role tags, commit/DOI pinning, credential scrubbing), then long-form technique for the two ecosystems that need it (GitHub, visual/design): concrete search technique, the what→why→cost chase, summary-vs-synthesis writing test | Always, before Phase 2 — "The ground census" and "The source ledger" are source-type-general and get read every run; the per-source-type sections only as the task needs them, and "Writing the final document" before Phase 4 |
| `references/run-mining.md` | The run-to-decide mode: what makes a trial fair, hard-edge-case fixtures, found-vs-authored candidates, the run record + provenance ledger, safety and budget of running untrusted code, and the ranked verdict a bake-off ends in | When the task asks you to **compare, choose, or test** rather than **understand** — decided at the Phase 1 method call, then read in full before Phase 2 |
| `assets/source-plan-template.md` | The plan shown to the user for approval in Phase 1 (has both a read-mining and a run-mining candidate table) | Building the plan |
| `examples/distillation-excerpt.md` | Shows the tone/shape of a real Phase 4 **read-mining** output (free-form synthesis) | Unclear what "free-form distillation" should look like |
| `examples/run-mining-excerpt.md` | Shows the shape of a Phase 4 **run-mining** output — score table, ranked verdict, "when you'd pick the other one" | Unclear how a tested comparison should read |
| `scripts/fetch_repo.sh` (Linux/macOS) / `scripts/fetch_repo.ps1` (Windows) | Verify and clone GitHub repos — codebase-source tasks only | Phase 1 link verification, Phase 2 reaching a codebase source |

Pick the fetch-repo script matching the shell/OS actually in use in this
environment; both take equivalent flags and produce the same JSON output
shape — see either script's `--help`/comment-based help, or
`references/workflow.md`, for exact usage and the one flag (`--depth`
vs. `-Depth`) that isn't expressed identically between them. There's no
equivalent bundled script for the other ecosystems — but "no script" is not
"no tool": reach them with whatever fits, and look before assuming hand
fetching is all there is. A docs-set task often has a sibling skill already
installed that does the whole job (in this repo, `scrape` — a docs site in,
greppable local Markdown out); research/spec/registry/discussion sources
usually have an official search API that beats scraping their human-facing
site. Each block in `source-ecosystems.md` names what applies, and
`workflow.md` → "Identify the source type and check for the best tool first"
is the general rule behind it. Run-mining has no bundled script either — its
harness (frozen fixtures, a thin adapter per candidate, one runner) is written
fresh per task in the stack that fits; `references/run-mining.md` says how, and
keeps the same "look for a purpose-built tool first" habit (a benchmark runner,
a conformance suite, an eval harness, a visual-regression tool) before hand-rolling.

**Verification status:** `fetch_repo.sh` has been run against real GitHub
repositories (verify success/failure, clone success/failure, destination
conflicts) and its behavior confirmed directly. `fetch_repo.ps1` is a
faithful line-by-line port of the same logic but has not been executed
against a real PowerShell environment — no PowerShell interpreter was
available to test it while building this skill. Treat its exact behavior
as unconfirmed until it's actually been run once in a real Windows/
PowerShell environment.
