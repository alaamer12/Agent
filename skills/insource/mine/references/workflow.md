# /mine — full workflow logic

Read this in full before running a `/mine` task. It covers the reasoning
behind each phase: building the plan, mining each source, tracking budget,
and writing the final document.

## Why this exists

A shallow research pass on "how do enterprise projects structure
themselves" produces a list of facts — file layouts, naming conventions,
tools used. That's not what's being asked for. The actual goal is
understanding **why** those facts are the way they are: what constraint,
tradeoff, prior failure, team structure, or scaling pressure led to a
specific decision, repeated across enough real, distinct sources that
patterns (and genuine outliers) become visible — not from one source, but
from accumulated, cross-checked digging.

This only works if two things hold: the sources are genuinely different
from each other, and the digging on each one goes past the surface (past
"here's what this is" into "here's why it's this way and not the obvious
alternative").

## This skill is task-based, not GitHub-only

`/mine` is not a GitHub skill that happens to also work elsewhere — it's a
general deep-research skill whose *sources* and *mining technique* adapt
to whatever the task actually points at. "Mine the top 20 enterprise
projects" points at GitHub repositories. "Mine 50 dashboard website
designs" points at visual design references (screenshots, a design
reference library, a Figma file). Something else entirely might point at
a different source type again. The four-phase shape (plan → mine → track
budget → distill) and the general discipline (chase why, not just what;
checkpoint after every source; no templated final output) stay constant
across all of them. What changes per task is: what counts as a
"candidate," what tool is best for reaching it, and what "what → why"
concretely means for that kind of source.

`references/search-and-mining-technique.md` has parallel sections for
source types this skill has needed technique for so far (codebase/GitHub,
visual/design) — read whichever section(s) actually match the task. That
file's sections are illustrations of the same underlying approach applied
to two domains, not an exhaustive list of what this skill supports: a
task pointing at a source type with no dedicated section yet still
follows the same general discipline (search professionally for both
candidates and a fitting tool, chase what → why → cost, checkpoint after
every source, distill without a template) — apply that discipline to the
new domain rather than treating the absence of a matching section as a
reason to fall back to something narrower.

## Phase 1 — Build and propose the plan

Before any mining happens, produce a source plan using
`assets/source-plan-template.md` and get explicit user approval on it.
Do not start mining on an unapproved plan.

### Identify the source type and check for the best tool first

Before discovery search, work out what kind of source this task actually
points at (codebase/GitHub, visual/design references, or something else),
since that decides both where candidates come from and what tool is worth
checking for. This is a judgment call from the task's wording — state it
plainly in the plan's "Source type" field so the user can correct it at
approval time if it's wrong, rather than asking up front.

**The principle: manual search-and-fetch is the fallback, not the
default.** For almost any source type, some purpose-built tool may exist
that reaches that source more directly, more completely, or with less
work than piecing it together by hand — an indexed Q&A layer over a
class of repository, a curated reference library for a design domain, a
direct API into the platform the source actually lives on. Before
assuming none exists, look. This holds regardless of which specific
tools happen to exist today — new ones appear, existing ones change,
and this skill should keep working the same way when that happens rather
than being tied to whichever tool happened to be current when the skill
was written.

Concretely, that means: don't skip straight to "check the MCP registry
for DeepWiki" as if that's the whole of this step. The actual step is
*"is there a specialized tool for reaching this kind of source at all,
and if I don't already know of one, go find out"* — treat an unfamiliar
source type exactly like a familiar one: search for a fitting tool before
concluding manual work is the only option.

Two examples of what this looks like in practice, for illustration only —
not an exhaustive or authoritative list, and not a claim that these
remain the best (or only) option going forward:

- *For codebase/GitHub sources*, a tool like DeepWiki — an MCP connector
  providing pre-indexed, deep documentation and Q&A for a large number of
  GitHub repositories — can surface architectural detail and rationale
  without the manual search/fetch/read cycle, when it covers a candidate.
- *For visual/design sources*, a tool like Mobbin — an MCP connector
  providing a searchable library of real app/web UI screens, with tools
  to search and fetch full images for visual inspection — can replace ad
  hoc image search/scraping, when access to it is available (tools like
  this are sometimes paid, so availability isn't guaranteed).

Don't treat either of these as *the* answer for their category, and don't
stop looking once one of them is found to not apply — if a task's source
type doesn't obviously match either example, that's not a signal to fall
back to manual work; it's a signal to search for what does fit.

The check-and-offer sequence, for whatever tool (if any) turns out to
apply:

1. **Check tool availability first**, before starting candidate discovery.
   If a fitting tool is already present and connected in this
   conversation, no search or suggestion step is needed — just note it's
   available and proceed to build the plan; it'll be used during mining
   (Phase 2).
2. **If not already connected, actively search for one** — the MCP
   registry, or general knowledge of what exists for this domain — using
   keywords drawn from the source type and topic (e.g. for a codebase
   task: the topic plus "documentation," "wiki," "code search"; for a
   design task: the topic plus "design reference," "UI library,"
   "screens"; for anything else, the same pattern applied to that
   domain). Don't stop at one query if the first doesn't surface
   anything plausible — try a couple of angles before concluding nothing
   fits.
3. **Build the candidate plan as normal first** (see "Finding candidates"
   below) — a tool's presence doesn't change which candidates go on the
   plan, only how they get mined once approved.
4. **After the plan is built, before presenting it for approval**, if a
   fitting tool was found but isn't connected, ask the user whether to
   install/connect it for this run or proceed with the traditional
   manual approach. Use `suggest_connectors` if the registry search found
   it (per this environment's standard connector-suggestion flow — these
   are third-party MCP apps, offered as a choice, never connected or used
   without the user picking them). Fold this into the same message that
   presents the plan for approval, rather than a separate round-trip —
   the user should be able to approve the plan and choose a mining
   approach in one response. If the tool is known to require payment or
   a paid plan, say so plainly when offering it, so the choice is
   informed.
5. If the user declines, or no fitting tool is found or available to
   them, proceed with the manual technique in
   `references/search-and-mining-technique.md` for that source type —
   the manual path is always the fallback and is fully sufficient on its
   own; not finding a specialized tool is a normal outcome, not a failure
   of this step.
6. If the user picks a tool, use it as the primary means during Phase 2
   for any candidate it covers, falling back to manual search/fetch for
   anything it doesn't cover or doesn't answer well — the two aren't
   mutually exclusive within a single run.

### Finding candidates

Use search to build the candidate list, adapted to the source type:

- **Codebase/GitHub**: something like `"best <N> <topic> projects
  github"`, refined by whatever criteria the user gave (a year, "by
  stars", a sub-domain). Scoped to real, existing, actively-maintained
  GitHub projects — not blog posts, newsletters, or aggregated
  "best practices" articles (those may surface during discovery, but
  aren't candidates themselves).
- **Visual/design**: a design reference tool's own search (e.g. Mobbin's
  screen search) if connected, or general image/web search against
  design gallery sources otherwise (Dribbble, Behance, Awwwards, Mobbin's
  own public site, or whatever the topic naturally points at). Candidates
  here are individual images/screens/flows, not whole sites necessarily —
  "50 dashboard designs" likely means 50 individual screenshots, possibly
  drawn from fewer than 50 distinct products.
- **Other source types**: apply the same underlying principle — find
  real, existing instances of the thing the task asks about, from
  sources that actually contain it, not secondary commentary about it.

If the user gave no explicit "top by what" or selection criteria, use
judgment on the most natural reading for the topic and state that basis
plainly in the plan's "Discovery method" field — the user corrects it at
approval time if it's wrong, rather than being asked up front.

The user may also specify mining categories instead of one flat count —
e.g. "5 frontend, 5 mobile, 5 microservices" rather than "15 projects";
when they do, build the candidate list to those per-category quotas
(each category mined with its own discovery search), and show the
categories as such in the plan.

### Distinctness at planning time — real for codebases, not for visuals

Two candidates count as distinct if they're plausibly different on their
face. For codebase sources, a glance-level judgment (different primary
language, architectural category, scale, problem space) is genuinely
sufficient at planning time — real, large projects rarely collide
structurally by accident, so this check does real work before any mining
starts. If two candidates that looked distinct at a glance turn out, once
mining is underway, to converge more than expected on some dimension,
that convergence is itself a piece of gained knowledge worth including in
the final document — it is not evidence the plan was flawed, and not a
reason to swap the candidate out mid-run.

For visual/design sources, this glance-level check is **not** reliable —
two dashboard screenshots can look meaningfully different by name/source
and still turn out to be near-duplicates (the same product, a template
reused across products, two crops of the same screen) only once actually
looked at. Don't try to pre-filter this hard at plan time for visual
candidates; it isn't where this problem can actually be caught. Collect
first, then dedup by visual inspection — see "Phase 2 →
visual/design-specific: dedup after collection" below.

### Verifying links

Every URL in the plan must be checked before the plan is shown to the
user — the exact check depends on source type:

- **Codebase/GitHub**: use `scripts/fetch_repo.sh --verify <url>` (or
  `scripts/fetch_repo.ps1 -Verify <url>` on Windows — same flags in
  spirit, same exit codes, same JSON shape). It checks the repo exists
  and is reachable (via `git ls-remote`, so it's cheap: no clone happens)
  and returns a single line of JSON (`status: "verified"` or
  `"not_found"`). Replace any candidate that comes back `not_found`
  before presenting the plan.
- **Visual/design or other non-repo sources**: fetch the URL directly and
  confirm it resolves to the claimed content (no 4xx/5xx, not a dead
  link, not a redirect to something unrelated). There's no equivalent
  script for this yet — do it with a direct fetch.

Don't present a plan with a known-broken link and a caveat; fix it first
in either case.

### Estimating project count for a time budget

When the user gives a time budget ("run for an hour") instead of a count,
the plan still needs a concrete candidate list, which means estimating how
many sources fit the budget. Use a rough per-source estimate (based on
the topic's likely complexity — a codebase generally takes longer to mine
deeply than a single screenshot) purely to size the initial list — state
this estimate and its basis in the plan so the user can adjust the count
before approving.

This estimate is a **planning tool, not a runtime cap.** Once mining
starts, per-source time is not fixed or equally divided — some sources
will yield much more than others and legitimately take longer. Adjust
live against the total remaining budget (see "Phase 3" below), not
against a fixed per-source allotment.

### Who performs the deep mining

Decide before presenting the plan, and state it as its own line in it so
the user can choose:

- **Solo** — the main agent mines every source sequentially. Slower, but
  each source's full detail stays directly in the working context that
  later writes the distillation.
- **Subagents** — one subagent per source (or per category when the plan
  has categories), run in parallel. Faster wall-clock; each returns its
  own checkpoint notes. The cost is context: the parent only ever sees
  what a subagent returns, never its raw digging, so the brief must
  demand the full evidence rather than a thin recap.

If the user picks subagents and a `/subagent` skill exists in this
environment, read its `SKILL.md` and build every mining brief with its
mandatory structure (Context → Goal → How → Autonomy Bounds → Output
Contract). Where it doesn't exist, the minimum professional shape it
teaches still applies to a mining brief:

- **Context** — topic, source type, this task's discovery criteria, and
  the what→why→cost discipline from
  `search-and-mining-technique.md`; hierarchical slice only, never the
  whole conversation.
- **Goal** — one precise sentence: mine exactly this one source, write
  its checkpoint file.
- **How** — the exact tools allowed (`fetch_repo.sh`, DeepWiki, image
  fetch), required process steps, hard boundaries (mine only this
  source; don't touch other candidates; don't start related work).
- **Autonomy bounds** — an executor, not a decision-maker: surface any
  choice and stop instead of deciding.
- **Output contract** — return the complete checkpoint file itself,
  written to the run's `checkpoints/` directory under its numbered name
  (same free-form rules as Phase 2 step 4) — never a summary.

The parent then treats each returned checkpoint as a claim, not a fact:
spot-check a sample of sources' evidence before Phase 4 distills from
them. Either way, the progress line after each source (Phase 2 step 5)
is still reported by the parent, covering whichever agent actually did
the digging.

## Phase 2 — Mine each source

For each approved candidate, in order:

0. **Reach the source**, using whatever the source type calls for:
   - Codebase/GitHub: clone it locally first, using `scripts/fetch_repo.sh
     --dest <path> <repo-url>` (or `scripts/fetch_repo.ps1 -Dest <path>
     <repo-url>` on Windows). Mining actual file/module structure and
     reading real source is far more reliable against a local checkout
     than piecing the codebase together through one-off GitHub UI/API
     fetches. Use a fresh destination per project and a shallow clone by
     default — both scripts default to depth 1; for a full clone with
     complete history, omit `--depth` on the bash script or pass `-Depth
     0` on the PowerShell one, only when a specific investigation
     genuinely needs deep commit history (see
     `search-and-mining-technique.md` → "Read commit history and churn as
     evidence"). If reaching the source fails despite having verified it
     in Phase 1 (rare — e.g. deleted or made private in between), treat
     it the same as a Phase 1 verification failure: flag it and either
     substitute a replacement candidate or ask the user how to proceed,
     don't silently skip the source.
   - Visual/design: fetch/retrieve the image via the chosen tool (Mobbin's
     screen-detail fetch, if connected) or via direct image fetch/download
     otherwise. Keep a local reference (path or retained fetch result) to
     each collected image before moving to analysis — the dedup step
     below needs all collected images available together, not fetched
     one-by-one and discarded immediately after each individual analysis.
1. Dig into the source using the technique appropriate to its type — see
   `search-and-mining-technique.md` for concrete method per source type
   (GitHub: README/docs/ADRs/PRs/commit history; visual: layout, color,
   spacing, hierarchy, and what a design choice trades off). Not a fixed
   checklist regardless of type — chase whatever this specific source
   actually offers.
2. Keep pushing past the first-level "what" into "why": why does this
   look the way it does, why was it chosen over an apparent alternative,
   what tradeoff or constraint forced the decision, what's stated
   explicitly versus only inferable from the source itself.
3. When you've reached a point of genuinely diminishing returns on a
   source — the same observation keeps repeating with nothing new
   surfacing — move on. Don't pad a source with restated findings just to
   look thorough; move the saved time to the next source instead.
4. **Write a checkpoint file for this source before moving to the next
   one.** One file per source, saved to a working directory for this run
   (e.g. `checkpoints/01-<source-name>.md`, numbered in mining order).
   This is the agent's own durable notes on what was just learned — the
   same habit a person doing this kind of research would have, jotting
   down what they took from each thing they studied rather than trying to
   hold all N sources in their head until the very end. It also means the
   run can recover cleanly from an interruption or a context-window
   problem: re-reading the checkpoint files for sources already mined
   restores exactly what was learned, without redoing that work or
   losing it.

   **There is no fixed template for this file, deliberately** — the same
   reasoning as Phase 4's final document applies at the single-source
   scale. A checkpoint forced into identical headers every time ("What
   this is / Findings / Confidence notes / Anything unusual") flattens
   whatever was actually learned into the shape of the template rather
   than the shape of the understanding, and a codebase and a design
   screen don't have the same things worth saying about them anyway.
   Write it the way *you'd* actually want to read it back later with zero
   memory of having done this mining — full sentences or notes, dense or
   sparse, in whatever order the source's own logic suggests. The only
   real requirements: it should capture the *why* and *cost* behind
   what's notable about this source, not just a "what was found" list;
   it should say plainly where a conclusion is inferred rather than
   stated, so that distinction survives into Phase 4; and it should be
   usable on its own — complete enough that a fresh instance of the agent
   picking the run back up from just this file (plus the others like it)
   wouldn't need to redo the mining to reconstruct what was learned. A
   "mined successfully, see above" placeholder fails that test even
   though it's technically a file.
5. **Separately, report one short progress line** before continuing:
   `Finished <source> — now moving to <next source>.` This is simple
   user-facing feedback, distinct from the checkpoint file (which is the
   agent's own working notes, not shown to the user unless asked) — both
   happen after every source, they're not alternatives to each other.

### Visual/design-specific: dedup after collection

For visual/design sources specifically (not codebases — see "Distinctness
at planning time" in Phase 1 for why codebases don't need this), once a
batch of candidate images has actually been collected, look at all of
them together before doing deep per-image analysis on any of them, and
remove near-duplicates (the same screen, a trivial crop/resolution
variant, the same template reused across two listed products). This is a
visual judgment, not a metadata one — file names or source URLs looking
different doesn't mean the content is different. Do this once, after
collection and before the deep analysis pass, so the expensive step (full
what/why/cost analysis per image) isn't spent on redundant sources. If a
removal drops the candidate count below what the plan called for, pull in
a replacement from the same discovery method used originally, rather than
silently finishing with fewer sources than planned.

## Phase 3 — tracking a time budget

If the environment has real background/async execution available, use it
to track elapsed time properly (e.g. schedule a wake/ping after the
budgeted duration) rather than relying purely on self-tracking.

Otherwise, self-track: check the current time between sources (not
mid-source — don't interrupt digging on one source to check a clock) and
compare against the total budget. As the remaining budget shrinks, weigh
it against how many candidates are left — this is where "some sources
take longer than others" gets reconciled with an overall time box: it's
fine to spend more time on a source that's yielding real depth and less on
one that plateaus quickly, as long as the running total stays roughly on
track to cover the full candidate list. If it's clear the full list won't
fit the remaining budget, say so plainly rather than silently truncating
the list or silently rushing through remaining sources shallowly.

## Phase 4 — the final document

This is the actual deliverable, and it is deliberately **not a template.**
Do not organize it by source-by-source sections, and do not organize it
by imposed cross-cutting themes either (no "Section 1: State Management
Patterns, Section 2: Color Theory" skeleton decided in advance). The
document is a distillation — write it the way someone who has genuinely
absorbed a subject would explain what they now understand, in whatever
shape that understanding actually takes. It is not trying to prove
thoroughness, cover every candidate evenly, or perform completeness —
sources that yielded little can be mentioned briefly or not at all; a
single unusually revealing source can dominate the writing if that's
where the real insight came from. This holds the same way regardless of
source type — a run mining visual designs earns exactly as much
free-form synthesis as one mining codebases, not a more structured
"gallery" format just because the sources were visual.

The per-source checkpoint files from Phase 2 are the raw material for
this phase — re-read them before writing, rather than relying purely on
whatever's still fresh in working context, especially on a long run.

There is no fixed structure to fill in here beyond this: it should read as
one coherent piece of understanding, not a report, not a table, not a
per-source recap. If a natural shape emerges from what was actually
learned — chronological, causal, by tension/tradeoff, whatever — let it
emerge from the content, not from a template decided before mining began.
