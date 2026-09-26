# /mine — run-mining: put each candidate through a fair trial

This file covers the second way to interrogate a source. `workflow.md` and
`search-and-mining-technique.md` describe **read-mining** — reach a source,
census it, chase its *why*, write a checkpoint. That answers "what does this
class of thing look like, and why." A different class of task asks a different
question, and reading can't answer it:

- *"Find the best 5 OCR libraries and test them on hard scans."*
- *"Which of these date/ID/state/queue options actually survives my edge cases?"*
- *"Try 5 visual styles on this screen and tell me which is right."*
- *"Three ways to structure this — build each small and measure."*

For these, the source isn't read, it's **run**. This is **run-mining**: build a
controlled, identical trial, exercise each candidate against it, measure what
comes out, and let the accumulated evidence produce a **decision** — a ranked,
tested recommendation — rather than a description. `/mine` does both; which one
a task wants is settled in Phase 1 (see `workflow.md` → "Settle the mining
method and the candidate provenance first").

Nothing here is tied to a language, package manager, framework, or model
runtime. The pattern is the same whether the candidates are libraries in some
ecosystem, renderings of a UI style, a model checkpoint, a database engine, a
specification run through a conformance suite, or an algorithm you wire three
ways. Where a concrete shape is unavoidable, it is named as *one* example, never
the required one (this is the polyglot discipline `workflow.md` already applies
to source types, applied to the *method* instead).

## Run-mining is not a separate skill — it reuses the whole spine

Everything structural in `/mine` still applies, with each piece given a
run-mode reading. Do not fork a parallel process; map onto the existing one:

| Read-mining piece | What it becomes when you run instead of read |
|---|---|
| The candidate list (Phase 1) | The **contenders** — and they may be *authored*, not just found (next section) |
| The ground census (Phase 2) | The **run record**: what you actually installed/loaded/ran — version, environment, install command, the fixture set exercised, and the score. Same idea as "what you reached as a fraction of the whole": without it, "library X won" means nothing. |
| The source ledger (Phase 2) | The **provenance ledger**: commit-pinned repo URL *or* registry + exact version + artifact checksum, model weight hash, the file path of the probe you ran. "I ran this and got this" must be re-runnable by a stranger. |
| The what→why→cost chase | The **result→cause→tradeoff chase**: it scored this way; why (which fixture broke it, which design choice forced it); what winning cost (memory, cold-start, license, maintenance, the thing it only does well because the fixtures flattered it). |
| The checkpoint file | A **probe note** — the run record, the scores, the cause-and-cost, and the exact repro. One per candidate, same durable-notes purpose. |
| The distillation (Phase 4) | The **verdict** — see "What run-mining ends in" below. |
| Solo / subagents | Unchanged; a per-candidate probe is *more* naturally parallel than a per-source read. The contract still demands the full artifact, not a recap. |

The budget discipline is unchanged in spirit but shifts where it bites: the
expensive unit is no longer "reading one more file" but "installing/building
/booting one more thing." See "Budget and safety of running things."

## Candidate provenance: found vs authored

Read-mining always *finds* candidates — the repos, screens, papers, packages
already exist. Run-mining splits:

- **Found candidates** already ship as a thing you can point at — the 5 OCR
  libraries, the 3 message queues. Discovery is exactly the Phase 1 candidate
  search for that ecosystem; then you run them.
- **Authored candidates** are approaches you *instantiate yourself* before any
  trial exists — "try 5 styles on this screen," "compare three state-management
  shapes," "wire the retry four ways." Here a candidate is a technique, so the
  run-mining plan enumerates the techniques, and each one gets built to the
  *same* spec before it can be compared. Building them to the same spec is most
  of the work and most of the risk (see "Fairness is the whole game").

The two modes **compose**, and usually should: a run-mine of authored candidates
is often *seeded* by a quick read-mine of how the field does it — read six real
implementations to learn the credible option set, *then* run the three that look
live. Say in the plan which mode seeds which, so the reading pass isn't mistaken
for the deliverable.

Authored candidates also change the distinctness picture: two styles that both
resolve to "flat, one accent, system font" are the same candidate wearing two
names. Dedup the *approaches* before you build them all, not after.

## What makes a trial fair — fairness is the whole game

A run-mine earns trust exactly as far as every candidate faced the *identical*
test. One candidate getting an easier fixture, a warmer cache, or a metric tuned
to its strengths, and the ranking is theatre. So a probe is specified once and
applied uniformly. The parts:

1. **The criterion, fixed before you run anything.** What "best" means for *this*
   task, written down as a measurable target: accuracy on the hard set, p95
   latency, peak memory, lines of glue to integrate, "renders without a horizontal
   scroll at 320px." Name what you are *actually* trying to learn and name the
   *proxy* you're measuring — they are never the same thing, and a proxy you
   forgot to distrust is how a benchmark lies confidently.
2. **A frozen input corpus — and it must be hard.** A fixed, versioned set of
   inputs the same for every candidate. Pick inputs from where the task
   *breaks*, not where it's easy: for OCR, handwriting, a skewed phone photo,
   low contrast, two-column layout, a non-Latin script, a dense table with no
   ruling — not a clean screenshot of a sans-serif paragraph, which every
   library passes and which ranks nothing. A fixture set that all candidates
   ace has bought you a tie and burned the budget. State each case's difficulty
   and why it's in the set.
3. **A uniform trial.** The identical call/operation per candidate — same input
   bytes, same settings where comparable, same warm/cold discipline, same
   machine. One run is anecdote; repeat enough that a win clears the noise
   (a couple of runs, or the one number that's genuinely deterministic).
4. **A per-candidate adapter.** The thin, *equal-effort* layer that plugs each
   candidate into the uniform trial. Keep it as thin and as symmetric as you can
   — a lopsided adapter (one candidate pre-configured, another left on defaults)
   quietly measures your wiring, not the candidate. This is the single easiest
   place to smuggle in an unfair result.
5. **A pass gate before a score.** Does it even *work* — install, run, return
   the right shape — as distinct from *how good* it is. Report gate-failures as
   their own outcome; a library that crashed isn't a "low score."
6. **Determinism / reproducibility record.** The version, the environment, any
   seed, the exact command. A result nobody can re-run is a claim, not evidence.

## Census and ledger when you run

Same duty as in read-mining — bound your claims and make them re-checkable —
different fields. Capture while you run, never from memory afterwards (the
invention failure mode is identical: reconstructed "I tested ~4 versions" lists
that never happened).

- **Run record** (the census): candidate + exact version/build, where it came
  from (source commit / registry release / model file hash), the environment you
  ran it in, how many fixtures you actually executed vs how many were in the set,
  and the score on each metric. "Tested 6 of 20 hard cases before it hung" is a
  reach bound in exactly the way "read 15 of 32,818 files" is — state it.
- **Provenance ledger** (the source ledger, reused): for each candidate, the
  pinned source — registry URL **with version**, or commit-pinned repo path — and
  the path to the adapter/probe you ran and the cached raw result. A recommendation
  with no matching "and here's the run that produced it" line is the same tell in
  run-mining that an uncited claim is in read-mining: it wasn't really checked.
  Scrub secrets and signed-URL query strings exactly as the read-mining ledger
  rule requires — install URLs and model endpoints carry tokens too.

## Budget and safety of running things

**Budget.** Installing, compiling, downloading a model, or booting an emulator is
the bulk cost, and it can dwarf everything else — a single heavy build can eat a
whole budget. Before committing, sanity-check what "run all N candidates" actually
costs, and note in the plan that run-mining estimates are the shakiest kind.
Time-box any one build (a candidate you cannot get running inside its slot is a
result: *failed to run in budget*, recorded, not silently dropped). Cache
everything you fetched/built under `sources/` so a re-run doesn't re-pay it. This
all sits under the same Phase 3 rule: the estimate plans the list, it does not cap
a candidate that's genuinely worth the time.

**Safety.** Running code you pulled from a registry is running *untrusted* code.
Default to least-trust: an isolated environment, no secrets or credentials
reachable from inside it, no privileged filesystem or network, and no executing
native/unpacked payloads casually on the host machine. Treat "install this package
and run it" with the same care the repo's own security rules treat secrets — a
package is arbitrary code with your tokens in scope if you let it be. When a
candidate is too hazardous to run (unverifiable provenance, needs root, wants your
credentials), that is a legitimate *did-not-run* outcome to record, not a challenge
to route around.

## What run-mining ends in

A run-mine's deliverable is **decision-shaped, not essay-shaped** — that is the
one place `/mine` deliberately *does* impose structure, and it's the same reason
the ground census is the one non-free-form part of a read checkpoint: some
content only lands as a table. The verdict is:

- **The score table** — one row per candidate, the metrics down the columns,
  gate-failures marked, reach bounds ("6/20 cases") shown. This is the spine a
  reader checks you against.
- **The ranking, with the reason** — not just "X > Y" but the *cause* (which
  fixture separated them) and the *cost* (what X's win gives up).
- **"When you'd still pick the other one"** — an honest bake-off names the
  conditions that flip it (the runner-up wins once inputs are clean; the slower
  one wins on memory; the "worse" library is the only one with a license you can
  ship). A recommendation with no stated flip-condition is marketing.

Around that structure, the *prose* stays free-form exactly as the read distillation
does — the reasoning, the surprises, the "two of these were secretly the same
engine" observation, the leftover uncertainty, are written as understanding, not
filled into boxes. Where a metric was subjective (a lot of "which style looks
right"), carry a stated-vs-judged label the same way read-mining carries
`stated`/`inferred`, and say who judged it. The final document rules in
`workflow.md` → Phase 4 hold; only the skeleton-in-spite-of-yourself prohibition
relents for the score table, because there the comparison *is* the point.

Keep the reproducible probe itself in the run directory (adapters, the frozen
fixtures, the runner, the raw results) — for a run-mine, unlike a read-mine, the
code you wrote to test is a first-class output the user may want to re-run or
extend.
