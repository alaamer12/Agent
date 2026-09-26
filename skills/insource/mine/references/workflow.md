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

A different task asks a different question, and the goal generalizes to it: not
"why is this the way it is" but "which of these should I use — and prove it."
"Find the best 5 OCR libraries and test them on hard scans" doesn't want a
description of five libraries; it wants five of them *run* against inputs that
break the weak ones, and a ranked, evidence-backed pick. Same engine (plan real,
distinct candidates and get them approved; interrogate each past the surface;
accumulate cross-checked evidence; distill once at the end), different
interrogation: *read* the source to understand it, or *run* it to decide between
it and its rivals. `references/run-mining.md` is that second mode in full; the
four phases below are written to serve both.

## This skill is task-based — what a source is, how you mine it, where candidates come from

`/mine` is not a GitHub skill that happens to also work elsewhere — it's a
general deep-research skill whose *sources* and *mining technique* adapt
to whatever the task actually points at. "Mine the top 20 enterprise
projects" points at GitHub repositories. "Mine 50 dashboard designs" points
at visual design references. "Mine how the major frameworks document
migration" points at *documentation sets*. "Mine the research on X" points
at papers. "Mine the last decade of incident postmortems about Y" points at
an ecosystem of org-authored writing. The four-phase shape (plan → mine →
track budget → distill) and the general discipline (chase why, not just
what; census every source before interpreting it; checkpoint after every
source; no templated final output) stay constant across all of them. What
changes per task is: what counts as a "candidate," what tool is best for
reaching it, what its census numbers are, and what "what → why" concretely
means for that kind of source.

Start at `references/source-ecosystems.md` — one block per ecosystem this
skill knows how to reach (codebases, visual/design, documentation sets,
research literature, specs and standards, package registries, discussion
corpora, postmortems and org writing, datasets), each answering the same six
questions: candidate, discovery, reach, census, why, dedup/traps. Those
blocks are the accumulated result of actually doing runs, and they're
additive — the list is not a whitelist. `references/search-and-mining-technique.md`
then holds the long-form technique for the ecosystems where the digging
itself needs more room than a block gives (GitHub codebases, visual/design).
A task pointing at something with no block and no section yet still follows
the same general discipline: work "The generic shape" at the end of
`source-ecosystems.md`, apply it to the new domain rather than treating the
absence as permission to fall back to something narrower, and write the
block afterward.

What a source *is* is only the first axis. The **second** is how you interrogate
it: **read-mining** (the default throughout this file — reach, census, chase the
why) answers "what does this class of thing look like, and why"; **run-mining**
(put each candidate through an identical, measured trial) answers "which of these
is best — prove it," which is what "find the best 5 OCR libraries and test them on
hard scans" or "try 5 styles on this screen" actually wants. The **third** is
where candidates come from: **found** instances you discover, or **authored**
approaches you build yourself to one spec before any trial can compare them (a
styles bake-off has no five ready-made artifacts to fetch — you make them).
`references/run-mining.md` is the second mode in full; it reuses this spine —
plan → mine → budget → distill, and census → dig → why → checkpoint → ledger —
with each part given a run-mode reading, so nothing here is GitHub-only or
read-only. The axes compose freely: a run-mine of authored candidates is usually
*seeded* by a quick read-mine of the credible option space. Which method and
which provenance a task wants is settled at the top of Phase 1, exactly like its
source type.

## Phase 1 — Build and propose the plan

Before any mining happens, produce a source plan using
`assets/source-plan-template.md` and get explicit user approval on it.
Do not start mining on an unapproved plan.

### Identify the source type and check for the best tool first

Before discovery search, work out what kind of source this task actually
points at, since that decides both where candidates come from and what tool
is worth checking for. Name the ecosystem from `references/source-ecosystems.md`
(codebase, visual/design, documentation set, research literature,
spec/standard, package registry, discussion corpus, postmortem or org
writing, dataset — or none of them, in which case use that file's "generic
shape"). This is a judgment call from the task's wording — state it plainly
in the plan's "Source type" field so the user can correct it at approval
time if it's wrong, rather than asking up front. Two mistakes are common in
both directions: reading a documentation or research task as if it were
really a codebase task because that's the best-documented ecosystem here,
and reading a task as "too vague for /mine" because no block matches it —
the second is exactly what the generic shape exists to handle.

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

A few examples of what this looks like in practice, for illustration only —
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
- *For documentation sets*, the fitting tool may already be installed
  alongside this skill rather than needing a connector at all: a docs
  scraper (in this repo, the `scrape` skill) turns a whole documentation
  site into local Markdown you can grep properly, which is a different
  class of evidence from reading pages one at a time. Check for a
  sibling skill with a name matching the source type before assuming
  hand-fetching.
- *For research literature, specs, registries, and discussion corpora*,
  the platform's own public API is usually the tool — a search endpoint that
  returns an honest total count and structured metadata in one request beats
  any number of web searches against the human-facing site, which typically
  hides both. `source-ecosystems.md` names the specific endpoints per
  ecosystem, with what's been verified here and what hasn't.

Don't treat any of these as *the* answer for their category, and don't
stop looking once one of them is found to not apply — if a task's source
type doesn't obviously match one of them, that's not a signal to fall
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

### Settle the mining method and the candidate provenance first

Two more readings shape the run before discovery, and both go on the plan so the
user can correct them at approval, exactly like "Source type":

- **Method — read-mining or run-mining.** The task's verb is usually a strong
  tell. "Understand / how does / why / what do they do" points to **reading** the
  sources. "Find the best N / which one / test them / benchmark / compare / try N
  versions / see what happens" points to **running** each candidate through a
  trial (`references/run-mining.md`). Name the chosen method in the plan's
  "Mining method" field. Ask before discovery only when it's genuinely ambiguous
  — "look into OCR libraries" could be a survey *or* a bake-off — because the two
  plan different candidates and cost very differently: installing and running one
  candidate can outweigh reading five, so picking the wrong method mis-sizes the
  whole budget.
- **Candidate provenance — found or authored.** "Best 5 OCR libraries" names
  **found** candidates that already exist, to discover and then run; "try 5
  styles on this screen" names **authored** candidates — approaches you build
  yourself to one spec before anything can compare them. State which, because it
  changes discovery (search a registry vs enumerate the credible option set, often
  via a short read-mine first), the distinctness check (two authored styles that
  collapse to the same thing are one candidate, and you catch that before building
  all five), and the plan's cost. Record it in "Candidate provenance."

Method and provenance cross-cut the ecosystem and independence choices below,
they don't replace them: a run-mine still names its source type (usually a package
registry, a model hub, or authored implementations) and still settles
true-independents vs industry/products for its contenders. The four phases then run
identically; only the interrogation step inside Phase 2 swaps from reading to
testing, and the Phase 4 deliverable from a distillation to a verdict.

### True-independents or industry/products — settle this before discovery

A second reading of the task decides what counts as a source: whether the
user wants **true independents** — every candidate a distinct, unrelated
instance (for codebases, a different project; for visuals, a screenshot
from a different product each), maximising breadth — or
**industry/products** — sources are whole products/platforms in the
domain, so one product may legitimately contribute several candidates
(e.g. mining "50 dashboard designs" via Airflow's dashboard plus four
other real products' dashboards). The two readings change discovery
(search "best <N> <topic> projects" vs search per-product), the
distinctness check, and dedup pressure — which is why this must be
settled *before* the "Finding candidates" step below, not after a
candidate list already exists. When the user didn't specify, ask
explicitly which they want before starting discovery — unlike source type
or criteria, this one isn't reliably guessable from wording. State the
chosen reading plainly in the plan (alongside "Source type") so it can be
corrected.

### Finding candidates

Use search to build the candidate list, adapted to the source type — the
"Discovery" line of the matching block in `references/source-ecosystems.md`
says where candidates come from in that ecosystem. Concretely, for the two
that need the most explanation:

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
  A documentation task's candidates are doc *sets*, not articles about
  documentation; a research task's are the papers themselves, not a
  survey's summary of them (a survey is a fine *discovery* instrument and
  a poor *source* — the same distinction as an awesome-list versus the
  repos it lists); a standards task's are the normative documents, not
  blog explainers of them.

Whatever the ecosystem, prefer the domain's own index or search API over
general web search when it has one — it returns real counts and structured
metadata, and general search quietly returns commentary instead.

If the user gave no explicit "top by what" or selection criteria, use
judgment on the most natural reading for the topic and state that basis
plainly in the plan's "Discovery method" field — the user corrects it at
approval time if it's wrong, rather than being asked up front. (The
independence model is *not* resolved this way — see the question before
this section; discovery searches are shaped by whichever model was
settled on.)

The user may also specify mining categories instead of one flat count —
e.g. "5 frontend, 5 mobile, 5 microservices" rather than "15 projects";
when they do, build the candidate list to those per-category quotas
(each category mined with its own discovery search), and show the
categories as such in the plan.

### Distinctness at planning time — reliable only where content can't be copied

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

For source types whose content can be copied, this glance-level check is
**not** reliable — and how far that reaches depends on the ecosystem, not on
how careful the planner is. Two dashboard screenshots can look meaningfully
different by name/source and still turn out to be near-duplicates (the same
product, a template reused across products, two crops of the same screen)
only once actually looked at. The same failure has an exact analogue
elsewhere: one paper as its preprint and its published version, one doc set
reachable through four versioned URLs, one package and its thin fork, one
postmortem retold as a conference talk. Don't try to pre-filter this hard at
plan time for those ecosystems; it isn't where the problem can actually be
caught. Collect first, then dedup on the content — see "Phase 2 → dedup
after collection" below. (Codebases are the exception where the glance
genuinely holds: two large real projects rarely collide structurally by
accident.)

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

Per-source effort differs by an order of magnitude across ecosystems, and the
difference is worth naming in the plan: a screen, a registry entry, or a
forum thread is minutes; a documentation set, a postmortem, or a paper is
tens of minutes; a long specification is more; a large codebase is the most
expensive thing on the list. Note too that for API-reachable ecosystems
(registries, literature, specs, discussion corpora) *discovery* is nearly
free while *full-text reach* is the bottleneck — listing 200 papers takes
seconds, reading 20 of them does not — so size the plan against reading, not
against finding.

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
  written to the run directory's `experience/` subdirectory under its
  numbered name, satisfying everything Phase 2 → "Write a checkpoint file"
  puts on the floor. Spell the census out in the brief rather than assuming
  it's implied: the parent never sees the subagent's checkout and cannot
  re-derive a file count, language split, or directory map afterwards, so
  those facts exist in the run only if the returned file carries them.
  Something like "the file must state what the source is in countable terms,
  what you actually read as a fraction of the whole, and why it's shaped that
  way — and it must end with the ledger of URLs you actually touched, because
  that's the only way I can check any of it once your checkout is gone" works,
  and "be detailed" does not. Never accept a returned message summarising the
  file instead of being the file.

With many subagents, don't repeat the common context in every spawn —
write one shared brief file once (e.g. `research/SHARED-MINING-BRIEF.md`,
like the worked example in this repo), containing the full `/subagent`
structure — Root, Role, Domain, the per-source process steps, hard
boundaries, Autonomy Bounds, Output Contract, and any output format spec
(e.g. an ASCII-map or checkpoint-skeleton convention). Copy the census step
and the checkpoint floor into that brief near-verbatim rather than
paraphrasing them short: with a dozen agents running blind and in parallel,
the brief is the only thing standing between them and twelve private
definitions of "be thorough". Each spawn then
carries only what differs: the assigned source(s) and exact output
paths, plus "read `<shared-brief-path>` first and follow it exactly."
One canonical brief also keeps every agent consistent, makes mid-run
corrections a single-file edit, and costs nothing to reuse across runs.

The parent then treats each returned checkpoint as a claim, not a fact:
spot-check a sample of sources' evidence before Phase 4 distills from
them. Include the census numbers in what you spot-check — they're the
cheapest claims in the file to verify (a file count or language split is one
API call) and the easiest to get subtly wrong, since a plausible number and a
measured one are indistinguishable on paper. And fetch one or two entries from
each sampled file's ledger: a URL that 404s, resolves to something unrelated,
or whose cited lines aren't in the page is how an invented citation shows
itself, and it is the cheapest early warning that a whole checkpoint is
unreliable rather than merely thin. Either way, the progress line
after each source (Phase 2 → "report one short progress line")
is still reported by the parent, covering whichever agent actually did
the digging.

## Phase 2 — Mine each source

Everything below reads for **read-mining**, the default. In a **run-mining** run,
the *interrogation* steps (0 reach, 2 dig, 3 push past what into why) become one
fair, identical **trial** instead of a read — `references/run-mining.md` holds the
whole mode. Every other Phase 2 obligation is unchanged and still applies: the
same run directory; "census before you interpret," but the census is a **run
record** (exact version/build, environment, install command, how many fixtures you
actually executed vs the frozen set, the score) instead of a file count; the same
one checkpoint file per candidate; the same closing **ledger**, now pinned to
registry+version+checksum (or commit) and the path to the probe you ran; the same
single progress line. Map the numbered steps: "Reach the source" → obtain and get
it running, in a sandbox, untrusted-code-safe; "ground census" → run record;
"dig / chase why" → run the trial, then chase result→cause→cost; "checkpoint" →
the probe note. Budget bites hardest in this phase, because getting one candidate
to build can consume the run — time-box a single build and record a candidate that
fails it as *did-not-run-in-budget*, never as a silent drop.

### The run directory

Every run gets one conventional directory named after the task:
`./mine/<kebab-cased-task>` (e.g. `./mine/50-dashboard-designs`) — this is
the default location; if the user names a different output location, use
that instead, keeping the same naming and subdirectory conventions below.
The directory has a fixed three-subdirectory shape:

| Dir | What goes in it |
|---|---|
| `sources/` | The approved plan, and everything collected to reach the sources — cloned checkouts, fetched images, raw fetch/API responses (each cached artifact carrying the URL it came from, so the ledger is reconstructable from disk and not just from memory). In run-mining, also the frozen fixture set, each candidate's thin adapter, the one runner, and cached installs/builds/artifacts, so a result is re-runnable without re-paying the setup |
| `experience/` | One checkpoint file per mined source — its ground census (what the source physically is, and what of it was actually reached), then what was learned from it and why, closing with the source ledger of URLs it touched (see "Write a checkpoint file" below) |
| `distillation/` | The final document plus the true full journey of the run — how discovery actually went, the cross-source ground table if you built one, the union of the per-source ledgers as the run's bibliography, category quotas met or missed, substitutions/dedup removals, budget reality vs estimate, tools used. In run-mining, the score table and ranked verdict live here too, and the reproducible probe is kept so the user can re-run or extend it |

Create the directory at the start of Phase 2; every path this workflow
mentions ("a working directory for this run", "the run's checkpoints
directory") means these subdirectories. Solo and subagent runs write to
the same place — a subagent's output contract is its `experience/` file.

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
   - Any other ecosystem: follow the **Reach** line of its block in
     `references/source-ecosystems.md` (a docs scraper for documentation
     sets, an API plus full-text fetch for literature and specs, and so
     on). Two rules hold everywhere the source is remote: cache what you
     reached under `sources/` — the raw JSON, the downloaded PDF, the
     scraped Markdown — so a claim can be re-checked without re-fetching
     and the run survives an endpoint going down mid-run; and check size
     before downloading, since documentation sets and datasets are the
     largest disk hazards this skill meets. A partial reach that's
     honestly labelled beats a bulk download that eats the sandbox.
1. **Take the ground census before interpreting anything.** Get the countable
   facts about what this source physically *is* — its identity (exact
   instance, branch/version, license), magnitude (how many files, bytes, LOC,
   screens, entries), composition (what languages/materials/parts it's made
   of), arrangement (its top-level structure, with counts), and which method
   got you in. See `search-and-mining-technique.md` → "The ground census" for
   the five fields, copy-paste commands that produce them in seconds, and the
   traps that make a census quietly wrong. Run it *early*, not at write-up
   time: it costs one command on a checkout or one cached API response without
   one, and it also tells you how much of the source you're about to describe.
   A number you couldn't measure gets written as "not measured: <reason>" —
   never left blank, because a blank and an unavailable look identical to
   whoever reads this after the context is gone.
   The same step starts your **source ledger**: from the first fetch onward,
   write down each URL as you touch it (`tee -a` into a scratch file, or put
   the URL in the header of each artifact you cache under `sources/`). The
   ledger is a by-product of digging and is trivially accurate while you're
   digging; reconstructed from memory at write-up time it becomes a list of
   plausible-looking links, some of which you never requested — which is worse
   than having no list, because the parent verifies against it. See
   `search-and-mining-technique.md` → "The source ledger" for the role tags,
   commit/DOI pinning, and the credential-scrub rule.
2. Dig into the source using the technique appropriate to its type — see
   `search-and-mining-technique.md` for concrete method per source type
   (GitHub: README/docs/ADRs/PRs/commit history; visual: layout, color,
   spacing, hierarchy, and what a design choice trades off). Not a fixed
   checklist regardless of type — chase whatever this specific source
   actually offers.
3. Keep pushing past the first-level "what" into "why": why does this
   look the way it does, why was it chosen over an apparent alternative,
   what tradeoff or constraint forced the decision, what's stated
   explicitly versus only inferable from the source itself.
4. When you've reached a point of genuinely diminishing returns on a
   source — the same observation keeps repeating with nothing new
   surfacing — move on. Don't pad a source with restated findings just to
   look thorough; move the saved time to the next source instead.
5. **Write a checkpoint file for this source before moving to the next
   one.** One file per source, saved to the run directory's `experience/`
   subdirectory (see "The run directory" above; e.g.
   `./mine/50-dashboard-designs/experience/01-<source-name>.md`, numbered
   in mining order).
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
   sparse, in whatever order the source's own logic suggests.

   That rule is about **shape and voice**, and it is not a license to skip
   content. Below is the *floor* — what must exist somewhere in the file, in
   whatever form fits. Every one of these has a reason, and each one fails the
   run differently if missing:

   - **The ground census** (step 1 above). Without them the reader cannot
     weigh a single claim: "they hand-rolled their ORM" is a different act of
     engineering in a 40-contributor repo than in a 460-contributor one, and
     the parent writing the comparison cannot align this source against the
     others at all. Size, language/material composition, and the top-level
     arrangement are the shared spine of the whole run.
   - **What you actually reached, as a count next to the total.** "Read 15
     files of 32,818" or "viewed 1 screen of the 9-step flow" is what makes
     every absence claim honest, and it is the difference between a
     well-hedged conclusion and an unfalsifiable one.
   - **The *why* and *cost*** behind what's structurally notable, not a "what
     was found" list.
   - **`stated` vs `inferred` labels** on conclusions, each with its evidence
     pointer (file path, doc name, PR/issue, commit range, or "the design
     itself" for a visual inference), so the distinction survives into Phase 4.
   - **Anything the source refused to explain** — dead ends, contradictions
     between sources, questions you aimed and got nothing back from. A
     checkpoint that reads as though everything worked is less useful than one
     marking where the trail went cold.
   - **Self-sufficiency** — complete enough that a fresh instance of the agent
     picking the run back up from just this file (plus the others like it)
     wouldn't need to redo the mining to reconstruct what was learned. A
     "mined successfully, see above" placeholder fails that test even
     though it's technically a file.
   - **A source ledger as the file's last block** — every URL actually
     touched, tagged `reached` / `read` / `searched` / `partial` / `failed`,
     pinned to a commit or DOI+version where the thing can change underneath
     you, with credentials and signed-URL query strings scrubbed. This is what
     turns the evidence pointers above into things a person can click a month
     from now, after the checkout is gone; a path cited with no URL behind it
     is re-derivable only by whoever re-mines the source. Collected during the
     dig (step 1), not invented at the end.

   Before closing the file, test it cold: could a reader who has never seen
   this source say roughly how big it is, what it's built from, how it's
   arranged, what you actually looked at, why it's shaped that way — and
   **where to go look to check you**? If any one of those six fails, that's
   missing work — finish it while the source is still open rather than leaving
   a note to come back. The floor says *what must be answerable*, never what
   heading to write it under.

6. **Separately, report one short progress line** before continuing:
   `Finished <source> — now moving to <next source>.` This is simple
   user-facing feedback, distinct from the checkpoint file (which is the
   agent's own working notes, not shown to the user unless asked) — both
   happen after every source, they're not alternatives to each other.

### Dedup after collection — wherever content can be copied

For source types where two nominally different entries can be the same
content (visuals above all, but also papers, doc sets, package forks, and
retold postmortems — see "Distinctness at planning time" in Phase 1 for why
codebases generally don't need this), once a batch of candidates has actually
been collected, look at all of
them together before doing deep per-image analysis on any of them, and
remove near-duplicates (the same screen, a trivial crop/resolution
variant, the same template reused across two listed products; and in the
other ecosystems, one paper's preprint and its journal version, four versioned
URLs for one doc page, a package that is its upstream with a rename).
The judgment is on the *content*, not the
metadata — file names, DOIs, titles or source URLs looking
different doesn't mean the content is different. Do this once, after
collection and before the deep analysis pass, so the expensive step (full
what/why/cost analysis per source) isn't spent on redundant sources. If a
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

The deliverable's *shape* depends on the method settled in Phase 1. A
**read-mining** run ends as one free-form distilled document — everything below
this line, unchanged. A **run-mining** run ends as a tested **verdict**: a score
table (candidate × metric, gate-failures and reach bounds shown), a ranked
recommendation with the *cause* and *cost* behind each placement, and a
"when you'd still pick the other one" clause — `references/run-mining.md` → "What
run-mining ends in." Only that comparison table is structured, and only
deliberately: the score *is* the point there, which makes it the one place the
no-template rule yields — exactly as the ground census is the one fixed part of a
read checkpoint. The reasoning written *around* a verdict follows every
free-form-synthesis rule below, verbatim, and keeps the reproducible probe with it.

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

The per-source checkpoint files in the run directory's `experience/`
subdirectory are the raw material for this phase — re-read them before
writing, rather than relying purely on whatever's still fresh in working
context, especially on a long run. Write the final document to the run
directory's `distillation/` subdirectory, alongside the true full journey
of the run (see "The run directory" in Phase 2).

Re-reading them has a second payoff: the census line at the top of each
checkpoint is the run's quantitative spine, and it's the only material that
could support a size- or composition-based comparison. Decide from those
numbers whether such a comparison exists before writing — if several sources
line up on a threshold that tracks a qualitative difference you noticed,
that's a conclusion worth stating (as an observation about these sources,
never as a universal law). Where the numbers would help a later reader, keep
a plain cross-source table in `distillation/` — source, magnitude,
composition, how it was reached — as part of the run's journey, not as a
section of the distillation itself; the document stays prose. Label any column
measured inconsistently ("4 of 20 sources were reached without a tree listing,
so their cell is method-limited, not zero"), because a blank in a table reads
as a real measurement of nothing.

There is no fixed structure to fill in here beyond this: it should read as
one coherent piece of understanding, not a report, not a table, not a
per-source recap. If a natural shape emerges from what was actually
learned — chronological, causal, by tension/tradeoff, whatever — let it
emerge from the content, not from a template decided before mining began.
