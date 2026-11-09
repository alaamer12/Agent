---
name: mine
description: 'Runs a deep, budgeted, multi-source dig to understand not just what a class of thing looks like but WHY — and, when asked to decide or compare, runs the options through a fair trial and ranks them. Three modes: read-mining (census repos, docs, papers, datasets, documents, talks — and chase their why), run-mining (put each candidate through an identical hard-case trial and measure), and case-mining (enumerate a topic''s distinct concrete situations — "mine 50 cases of hard-scenario debugging" — each actionable on its own and attested by a source or labeled derived). The user can direct the how, not just the what — "/mine this PDF, 100 pages per subagent" is honored literally. Long artifacts get a noise-and-density map first so budget goes to signal; reach pipelines (PDF to text, OCR, transcription) are picked by searching the current tool landscape, gated on one real sample. Read-mining ends as a distilled document; run-mining as a ranked verdict with a score table and probe; case-mining as a coverage-mapped catalog of case cards, where the count is a coverage target, never padding. Runs resume from plan.md plus a per-source checklist. Trigger on "/mine", "mine" a topic, resuming a dig, "find the best 5 libraries for X and test them on hard cases", or "collect / enumerate the cases of X" (its failure modes, hard-scenario debugging, every way Y breaks). Approve a verified source plan first.'
---

# /mine

> Given a task, plan a set of real, distinct candidates — or the distinct
> *cases* of a topic — and interrogate each the way the task needs: *read* it to
> understand not just what's there but *why*, *run* it through a fair, identical
> trial to measure and rank, or *enumerate* the concrete situations into a
> coverage-mapped catalog where each case stands alone — ending with one
> distilled document (read), one tested verdict (run), or one case catalog (case).

Read `references/workflow.md` first — it is the actual skill: the four
phases (plan → mine → track budget → distill), the tool-check step and the
extraction bootstrap (search the *current* tool landscape rather than trusting
memory for converters, gate the chosen one for accuracy on a real sample,
prove the PDF→text / OCR / transcript pipeline once by
hand, then codify it as a script in the run's `tools/` for every subagent),
the mining-directive rules (the user may specify the *how* — "each subagent
reads 100 pages" — and it gets honored literally and recorded in the plan),
the read-vs-run-vs-case choice inside "mine" — understand a source by reading
it, decide between candidates by running them through a trial (see
`references/run-mining.md`), or enumerate a topic's concrete situations into a
catalog of actionable, evidenced cases (see `references/case-mining.md`) — the
per-source checkpoint habit (free-form in
shape — never a fill-in template —
but with a content floor every checkpoint must clear: the source's ground
census first — plus the noise-and-density structure split, pages read/skimmed/
skipped, for any artifact too big to read in one pass (see
`references/noise-and-density.md`) — the why and the cost, and a closing
ledger of the URLs actually
touched — see Phase 2 in `workflow.md`) — plus the run-state discipline: the
plan is written to `<run>/plan/plan.md` *while it's being built* with a
`checklist.md` of every unit in mining order, so any session can resume an
interrupted run in sequence from disk instead of re-planning it — and every
non-negotiable, all with
their reasoning. This file is a map, not a summary — nothing here is restated
there in less detail, so don't try to run `/mine` from this file alone.

## This skill is task-based — what a source is, how you mine it, where candidates come from

The default mental model is GitHub *reading*, but `/mine` adapts to whatever
the task actually points at, along three axes. **(1) What a source is** —
`references/source-ecosystems.md` indexes everything it can mine (codebases,
visual/UI references, documentation sets, research papers, specs and standards,
package registries, discussion corpora, postmortems, datasets, document files —
PDFs, ebooks, scans — and time-based media like talks and recordings), each with where
its candidates come from, what tool reaches it, and its census numbers; an
ecosystem with no block yet is mined by that file's "generic shape" and gets its
block written afterwards. For file and media sources the source
isn't readable until it's *converted* — text extraction, OCR, transcription —
and the converter is picked by **searching the current landscape instead of
recalling tool names** (the field turns over monthly; neither open-source nor
paid is the default winner), verified by an **accuracy gate** on one real
sample of the content, proven once by the main agent, then codified into the
run's `tools/` scripts that every subagent calls
(`search-and-mining-technique.md` → "The extraction bootstrap");
long artifacts get a noise map first so agents read signal and not a table of
contents (`references/noise-and-density.md`). **(2) How you interrogate it** — *read-mining* (reach
a source, census it, chase its why) is the default, but a task like "find the
best 5 OCR libraries and test them on hard scans" or "try 5 styles on this
screen" is answered by *running* each candidate through an identical, measured
trial (`references/run-mining.md`), and a task like "mine 50 cases of
hard-scenario debugging" or "every way this API fails" is answered neither as an
essay nor as a ranking but by *enumerating the concrete situations* themselves —
each one actionable on its own and attested by a source or labeled derived —
which is the third method (`references/case-mining.md`). **(3) Where candidates
come from** — *found* (real repos, packages, screens you discover) or *authored*
(approaches or styles you build yourself in order to compare); in case-mining
the same split reads as *attested* (documented in real sources) vs *derived*
(reasoned out of the scenario space). The modes
compose: a run-mine of authored candidates is usually seeded by a quick read-mine
of the option space, and a case-mine is usually seeded by reading the sources
that attest its cases. See `references/workflow.md` → "This skill is task-based —
what a source is, how you mine it, where candidates come from" and "Settle the
mining method and the candidate provenance first."

Alongside the three axes, the user may attach **mining directives** — explicit
instructions about *how* to mine ("each subagent reads 100 pages", "read every
ADR before any code", "OCR the scans, then skim"). Directives override the
skill's defaults for the choices they cover (split size, fan-out, reading
depth, reach method), never for the discipline they don't (census, noise map,
checkpoint floor, ledger, fairness), are recorded in the plan, and get flagged
— with a proposed nearest reading — when impossible as stated. Within-source
fan-out (subagents splitting *inside* one artifact by page range) exists
exactly for these; see `workflow.md` → "Honor mining directives" and "Who
performs the deep mining."

## Where everything lives

| File | What it's for | Read it when |
|---|---|---|
| `references/workflow.md` | The full four-phase process, source-type and mining-method identification, mining directives, plan-as-file + the resume protocol, the run directory (static + dynamic folders), and every non-negotiable rule | Always, before doing anything — and first thing on any "continue/resume the mining" ask |
| `references/source-ecosystems.md` | Every ecosystem `/mine` can mine, one block each: candidate, discovery, reach, census, where the "why" lives, dedup traps — plus what counts as a ledger entry there | Always, right after `workflow.md` — it's how you decide what kind of source this task is; the "generic shape" is what you use when nothing matches |
| `references/search-and-mining-technique.md` | The ground census (measured size, composition and structure — commands, plus the traps that make a count quietly wrong), the source ledger (URLs touched, role tags, commit/DOI pinning, credential scrubbing), the extraction bootstrap (pick converters by searching the current landscape and gating accuracy on a real sample — never from memory, prove the pipeline once by hand, codify it in `tools/`, hand it to every subagent), then long-form technique for the two ecosystems that need it (GitHub, visual/design): concrete search technique, the what→why→cost chase, summary-vs-synthesis writing test | Always, before Phase 2 — "The ground census" and "The source ledger" are source-type-general and get read every run; the per-source-type sections only as the task needs them, "The extraction bootstrap" whenever sources need converting, and "Writing the final document" before Phase 4 |
| `references/noise-and-density.md` | Detecting and mapping useless content before spending reading budget: front matter, indices, TOCs, running boilerplate, blank/scan artifacts, web-capture junk, media filler — measured profiling, sample-verify-before-skip, the structure split reported into the census, and page-range splitting by signal | Before reading any artifact too big to read in one pass (book, scan, long report, transcript, scraped corpus), and always before assigning page ranges to subagents |
| `references/run-mining.md` | The run-to-decide mode: what makes a trial fair, hard-edge-case fixtures, found-vs-authored candidates, the run record + provenance ledger, safety and budget of running untrusted code, and the ranked verdict a bake-off ends in | When the task asks you to **compare, choose, or test** rather than **understand** — decided at the Phase 1 method call, then read in full before Phase 2 |
| `references/case-mining.md` | The enumerate-the-situations mode: mapping the scenario space without padding or duplication, attested-vs-derived cases, per-case evidence, the situation→recognition→handling→cost chase, and the case catalog it ends in | When the task asks you to **collect or enumerate the concrete cases** of a topic (failure modes, hard scenarios, every way it breaks) rather than understand or rank it — decided at the Phase 1 method call, then read in full before Phase 2 |
| `assets/source-plan-template.md` | The plan shown to the user for approval in Phase 1 — persisted as `<run>/plan/plan.md` from the moment it's built, with the approval and amendments recorded in it (has read-mining, run-mining, and case-mining candidate tables) | Building the plan |
| `examples/distillation-excerpt.md` | Shows the tone/shape of a real Phase 4 **read-mining** output (free-form synthesis) | Unclear what "free-form distillation" should look like |
| `examples/run-mining-excerpt.md` | Shows the shape of a Phase 4 **run-mining** output — score table, ranked verdict, "when you'd pick the other one" | Unclear how a tested comparison should read |
| `examples/case-mining-excerpt.md` | Shows the shape of a Phase 4 **case-mining** output — coverage lead, per-case cards with attested/derived/inferred markers, the dedup that collapses a padded count to the honest one | Unclear how a case catalog should read |
| `scripts/fetch_repo.sh` (Linux/macOS) / `scripts/fetch_repo.ps1` (Windows) | Verify and clone GitHub repos — codebase-source tasks only | Phase 1 link verification, Phase 2 reaching a codebase source |

Pick the fetch-repo script matching the shell/OS actually in use in this
environment; both take equivalent flags and produce the same JSON output
shape — see either script's `--help`/comment-based help, or
`references/workflow.md`, for exact usage and the one flag (`--depth`
vs. `-Depth`) that isn't expressed identically between them. There's no
equivalent bundled script for the other ecosystems — but "no script" is not
"no tool": reach them with whatever fits, and look before assuming hand
fetching is all there is. And "no *bundled* script" doesn't mean "no script,
ever": a conversion pipeline the main agent proves during a run (PDF→text,
OCR, HTML→Markdown, transcription) gets codified into that run's `tools/`
directory — a script later sources, and every subagent, use instead of
re-deriving (see the extraction bootstrap). A docs-set task often has a sibling skill already
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
Case-mining needs no bundled script either — its machinery is the scenario-space
enumeration and the per-case evidence, and it reaches its attesting sources with
the tools read-mining already uses (`references/case-mining.md`).

**Verification status:** `fetch_repo.sh` has been run against real GitHub
repositories (verify success/failure, clone success/failure, destination
conflicts) and its behavior confirmed directly. `fetch_repo.ps1` is a
faithful line-by-line port of the same logic but has not been executed
against a real PowerShell environment — no PowerShell interpreter was
available to test it while building this skill. Treat its exact behavior
as unconfirmed until it's actually been run once in a real Windows/
PowerShell environment.
