# Mining plan — <topic>

**Source type:** <name the ecosystem from `references/source-ecosystems.md`
— "Codebase/GitHub" | "Visual/design references" | "Documentation sets" |
"Research literature" | "Specs/standards" | "Package registries" |
"Discussion corpora" | "Postmortems/org writing" | "Datasets" | "Document
files (PDF/scan/book)" | "Time-based media" | other,
described in a clause. If none fits, say so and that you're mining it by that
file's generic shape — the list is an index, not a whitelist>

**Mining method:** <"Read-mining — understand the sources (reach, census, chase
the why; ends in a free-form distillation)" | "Run-mining — decide and rank (put
every candidate through ONE identical, measured trial; ends in a tested verdict
with a score table)" | "Case-mining — enumerate the topic's concrete situations
into a catalog (each case actionable on its own, attested by a source or labeled
derived; ends in a case catalog whose count is a coverage target)" | "Both — a
short read pass to map the credible option space, then run the contenders" — the
task's verb is usually the tell ("why/how does" → read; "best N / test / compare
/ try versions" → run; "50 cases / every way X fails / hard-scenario X / the
situations where / playbook" → case); see workflow.md → "Settle the mining
method and the candidate provenance first", `references/run-mining.md` and
`references/case-mining.md`>

**Candidate provenance:** <"Found — real, existing artifacts to discover (repos,
packages, models, screens)" | "Authored — approaches you build to one common spec
in order to compare them (5 styles, 3 architectures)" — matters most for
run-mining: authored contenders must be built to the *same* fixture set and metric
before they're comparable, and near-identical approaches are collapsed to one
candidate before any of them is built. In case-mining the same axis reads as
"Attested — cases documented in real sources" | "Derived — cases reasoned out of
the scenario grid where no source writes them down"; state the expected split,
because an all-derived catalog is a list of guesses and an attested-only one
silently misses the holes nobody wrote up>

**Mining directives:** <the user's explicit instructions about *how* to mine,
quoted one per line and mapped to how this plan executes them — e.g.
'"each subagent reads 100 pages" → within-source fan-out, 7 subagents over
the body range 24–451 from the noise map, index skipped' |
'"read the ADRs first" → per-source procedure step before any code read' |
"none given — the skill's defaults govern". Directives are honored literally;
one that is impossible or self-contradictory as stated gets flagged here with
the nearest faithful reading proposed, never silently reinterpreted
(workflow.md → "Honor mining directives")>

**Unit of a source:** <what one candidate actually is in this ecosystem, since
it isn't always obvious and it sets the count: one repo vs one product's three
repos; one screen vs one flow; one doc site vs one page; one paper vs one
research line. Settle it here, because the budget arithmetic depends on it>

**Independence model:** <"True independents — every candidate a distinct, unrelated instance" | "Industry/products — sources are whole products/platforms; one product may contribute several candidates" — settled with the user before discovery started; if the user didn't specify, ask which they want first (workflow.md → "True-independents or industry/products — settle this before discovery")>

**Budget:** <"N sources" | "~X minutes/hours">
<!--
  For a count-based budget, N is fixed by the user (or by "top 20" style
  phrasing in the request) — list exactly N candidates below.

  For a time-based budget, estimate a source count by dividing the total
  budget by a rough per-source estimate (see references/workflow.md →
  "Estimating project count for a time budget"), then list that many
  candidates. State the estimate and its basis plainly so the user can
  correct it before mining starts — this number is a planning estimate,
  not a per-source time cap; some sources will legitimately take longer
  than others once mining is underway.

  For run-mining the estimate is the shakiest kind: getting one candidate to
  install/build/boot can cost more than reading five, so sanity-check that setup
  cost before fixing N and say so in the basis (see run-mining.md → "Budget and
  safety of running things"). A candidate that can't build inside its slot is a
  recorded "did not run in budget" result, not a silent drop.

  For case-mining the count is a *coverage target*, not a quota to fill: price
  N honest, distinct, evidenced cases against the budget, and when the budget
  only supports fewer than were asked for, present the smaller list and say so
  plainly — padding to 50 with restatements of one handling is the exact failure
  this mode exists to prevent (see case-mining.md → "Coverage without
  duplication is the whole game").
-->

**Discovery method:** <how these candidates were found — e.g. "searched
'best enterprise-scale open source projects github 2026', cross-referenced
with GitHub stars/activity" for a codebase task, or "searched Mobbin for
dashboard screens across SaaS analytics products" for a visual task —
state this plainly so the user can judge whether the selection method
matches what they actually wanted>

**Mining tool:** <state which tool this run will use, how it was chosen, and
its status — converters/parsers are chosen by **searching the current
landscape, not memory** (open-source vs paid wins neither category by
default; standings move monthly) and then by the **accuracy gate** — one real
sample of the actual content verified against ground truth. e.g. "DeepWiki
(connected) — used where it covers a candidate, manual search as fallback" |
"Mobbin (available, requires your paid plan) — asking below whether to
connect it" | "`scrape` skill (installed here) — each doc set pulled to
local Markdown once, then grepped" | "ASR: searched 2026 landscape, gated
open model X vs paid Y on a 2-minute stretch of *this* audio — X fewer
errors and free; using X" | "OCR: paid Z beat the open options on this scan's
two-column pages by enough that verbatim quotes justify the spend — asking
below whether to use it or accept X's measured error rate" | "the domain's
official search API (arXiv / Crossref / RFC editor / registry) — no
connector needed, no bulk download" | "Manual search/fetch only — no
specialized tool found or available for this source type">

**Who performs the deep mining:** <"Solo — main agent mines every source
sequentially" | "Subagents — one per source/category in parallel; briefs
built with the /subagent skill if present (see workflow.md → 'Who
performs the deep mining')" | "Within-source fan-out — subagents split
*inside* one large artifact by page range / directory / date window (what
'each subagent reads 100 pages' means); ranges come from the noise map and
TOC, never raw page counts; per-slice part checkpoints stitched into one
source checkpoint" | "Case families — in a case-mine, one subagent per scenario
family, each brief carrying the shared axis grid so families tile the space
instead of emitting the same handling under two names">

**Extraction plan:** <for sources that aren't directly readable (PDFs, scans,
HTML, audio/video): the conversion chain you'll use — installed skill,
existing binary, or adapted fallback — and whether the pipeline has been
proven once by hand and codified into the run's `tools/` script that every
subagent will call (search-and-mining-technique.md → "The extraction
bootstrap"). State it here so the user sees fan-out rests on a tested
pipeline, not on twelve agents improvising the same OCR command. Omit for
sources that are already text.>

**Distinctness check:** <for a codebase task: "each candidate below is
judged distinct from the others at a glance (different language,
architectural approach, problem space, scale) — not verified by deep
mining; if candidates converge once mined, that's a finding to report,
not a flaw in this plan." For a visual/design task: "candidates are NOT
pre-filtered for distinctness at this stage — visual sources can look
different by name/source and still turn out to be near-duplicates once
actually viewed, so dedup happens after collection, before deep analysis
(see workflow.md → Phase 2). This plan may include sources that get
removed as duplicates once mining starts. For run-mining with authored
candidates: the *approaches* are deduped before building any of them — two named
styles that resolve to the same layout and tokens, or a contender that is just
another's thin wrapper, are one candidate, not two. For case-mining: two
situations whose recognition *and* remedy are the same are one case however
differently the sources name them — that merge is judged after collection, on
the written handling, never at plan time (case-mining.md → "Coverage without
duplication is the whole game").">

**Fair-trial sketch (run-mining only):** <the one test every contender faces —
the frozen input/fixture set (naming the deliberately-hard cases that break the
weak options and *why* each is in the set), the uniform operation applied
identically to all, the per-contender adapter, the pass gate vs the quality
metric, and what you're actually measuring vs the proxy you'll read. Omit this
field entirely for a read-mining run. See `references/run-mining.md` → "What
makes a trial fair.">

**Coverage plan (case-mining only):** <the scenario axes the space is mapped
onto (e.g. phase × environment × artifact × trigger-shape — settled from the
sources that attest the cases, never a guessed generic grid), the families with
their target case counts, the expected attested/derived split, and the hardness
bar (cases that defeat the obvious approach outrank table stakes). Omit this
field entirely for read- or run-mining runs. See `references/case-mining.md` →
"Coverage without duplication is the whole game".">

## Candidates

| # | Source | URL | Why it's a plausible candidate | Link status |
|---|--------|-----|-------------------------------|-------------|
| 1 | <name> | <url> | <one clause — why it's distinct/relevant/"top"> | ✅ verified |
| 2 | <name> | <url> | <one clause> | ✅ verified |
| ... | | | | |

<!--
  Every URL must be checked before this plan is shown to the user — no
  4xx/5xx, and it must actually resolve to the claimed source (not a
  redirect to an unrelated page, a dead fork, an archived placeholder,
  etc.). For codebase sources, use scripts/fetch_repo.sh --verify (or
  fetch_repo.ps1 -Verify). For visual/design or other non-repo sources,
  fetch the URL directly and confirm it resolves to the claimed content.
  Mark status accordingly; don't include a candidate whose link doesn't
  verify — find a replacement instead.
-->

### Candidates — run-mining variant

Swap the table above for this one when Mining method is run-mining (or for its
run portion in a both-modes plan). It records the trial, not just a link;
authored contenders have no URL yet — they have a spec they'll all be built to.

| # | Contender | Found / authored | Source, or the shared spec it'll be built to | The hard cases it must clear | Metric(s) | Obtained? |
|---|-----------|------------------|----------------------------------------------|------------------------------|-----------|-----------|
| 1 | <lib or approach> | found: `pkg@vX` | <install cmd / pinned repo path> | <2–3 inputs that break the weak ones, + why> | <accuracy@hard · p95 · peak-mem · …> | ✅ installs+runs |
| 2 | <approach> | authored | <one-paragraph spec, identical for all> | <same frozen set> | <same metrics> | ✅ builds+runs |
| ... | | | | | | |

<!--
  Same verification duty as the read table, but the gate is "does it obtain and
  run," not "does the link resolve": for found candidates pin the exact registry
  version / commit and confirm it installs and starts inside the sandbox; for
  authored candidates confirm the shared spec is buildable once before
  instantiating all of them. A contender that won't obtain/run at planning time
  is replaced or noted, exactly like a broken link. List the SAME fixture set and
  metrics for every row — that uniformity is what turns the eventual ranking into
  a comparison instead of five unrelated demos.
-->

### Candidates — case-mining variant

Swap the table above for this one when Mining method is case-mining. The rows
are **cases**, not sources: sources appear in the evidence column, one source
may back several rows, and one row may cite several sources. Derived cases have
no URL — they carry the grid cell and the reason the situation must be possible.

| # | Case (situation, one line) | Family / grid cell | Attested / derived | Backing evidence (source URL, or derivation) | Distinct handling — why it merges with no other row |
|---|------------------------------|--------------------|--------------------|-----------------------------------------------|-------------------------------------------------------|
| 1 | <the hard situation> | <phase × artifact × trigger …> | attested | <postmortem / thread / guide URL> | <what its remedy does that no other row's does> |
| 2 | <the hard situation> | <cell> | derived | <the axes it falls out of + why reachable> | <one clause> |
| ... | | | | | |

<!--
  Verification here has two gates, not one. Attested rows: the cited URL must
  resolve (same no-4xx / no-unrelated-redirect duty as the read table) AND the
  source must actually document both the situation and the handling — a URL
  that merely mentions the symptom downgrades the row to derived, recorded as
  such rather than quietly kept. Derived rows: the derivation must name real
  cells of the settled coverage grid, not "logically possible". The count is a
  coverage target: if the honest, distinct, evidenced set comes out smaller
  than the user asked for, present the smaller list with the reason — padding
  rows to hit N is the one outcome worse than missing the number
  (case-mining.md → "Coverage without duplication is the whole game").
-->

---

Reply to approve this plan as-is, or tell me what to change — swap a
specific candidate, adjust the count, change the discovery criteria, or
anything else.
<!--
  If Mining tool above is "available but not yet connected," fold the
  connect/decline choice into this same message (e.g. via
  suggest_connectors) rather than a separate follow-up — the user should
  be able to approve the plan and settle the mining approach together. If
  the tool requires payment (e.g. Mobbin), say so plainly here too.
-->
I'll only start mining once this list is approved.

**Status:** draft, presented <date> — approval recorded in this file when
given (approved as-is / with these edits), along with any mid-run amendments
in a change-log below. This file is the run's resume anchor: a later session
reads it plus `checklist.md` and continues in this recorded sequence — same
directives, same approval — instead of re-planning
(workflow.md → "The plan is a file from the moment it exists" and "Resuming
an interrupted run").
<!--
  Persistence is part of planning: write this plan into
  `<run-dir>/plan/plan.md` while building it (before the approval round-trip),
  and generate `plan/checklist.md` from the candidate table above — one line
  per unit in mining order (per slice for within-source fan-out), statuses
  pending / in progress / done (timestamp + checkpoint path) /
  failed-in-budget / swapped (reason). Tick it as Phase 2 runs; on resume the
  checklist is state and this file is history.
-->
