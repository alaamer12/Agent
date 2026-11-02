---
name: thebest
description: 'Evidence-based option choice for THIS project: gather proof, hand the user a verdict - "this is likely best for us, based on these tests and research" - and stop; the USER decides (dtb is the reverse). Frame hard constraints first (stack, platform, license, AGENTS.md) and eliminate violating options visibly, before testing. List ALL viable ways (user candidates, ecosystem standards, codebase precedents, lesser-known families), never a remembered shortlist. Map each criterion to its evidence: numbers -> /benchmark (real data, isolated environments), actual library behavior -> /learning-test, facts -> research (context7 if installed, else version-matched docs), fit -> argued; many decisions are pure research - a forced benchmark is fake rigor. Verdict carries confidence, runner-up with its flip condition, untested items. Use for "which approach/library for X", design forks, A-vs-B. Not fresh-stack picks (techstack), the measurement engine (benchmark), or an HTML decision page (decide).'
when_to_use: The user asks which method/library/approach to use for something, presents candidates to choose between, or a design fork needs an evidence-based verdict; also /thebest.
argument-hint: "[the decision, known options, and project constraints if already stated]"
---

# thebest - a verdict, not a pro/con list

The deliverable is one sentence the user can act on - *"X is likely the best fit for us, based on these tests
and this research"* - with the evidence, the confidence, and the conditions under which it would flip
attached. Everything before that sentence is the method below.

## Step 1 - Frame the decision (constraints first)

Establish, in writing in chat, before evaluating anything:

- **The actual question.** What is being optimized - speed, accuracy, memory, maintenance cost, DX - and for
  whom. "Which geolocation query method" hides it: is the win latency per query, or simplicity with zero
  extensions?
- **Hard project constraints.** The stack the project already committed to (the user said SQLite? SQLite.
  Any language, platform, license, team-skill, or infrastructure rules). Pull them from AGENTS.md, project
  docs, the conversation - not from assumptions. A constraint-violating option is **eliminated at listing,
  with the violation stated**, not quietly scored down.
- **Success bar.** What "good enough" looks like: a number ("handles our 12k points in <10ms/query"), a
  quality ("no native extension needed"). Without a bar, "best" is unfalsifiable.

## Step 2 - Discover all viable ways

Understand the full option space before ranking. Sources, all of them, cheaply:

1. **The user's named candidates** - always in the list, even if you doubt them.
2. **The ecosystem's standard ways** - official docs, library docs: **context7 if installed, else the web**;
   version-matched to what the project actually uses, never memory.
3. **The codebase itself** - what already solves adjacent problems here; the incumbent is a candidate too,
   and reuse beats adoption.
4. **Lesser-known families** - one deliberate search for approaches nobody mentioned (different algorithm
   families, DB-native features, standard-library options). Sometimes the proven built-in makes the whole
   decision moot - that is a find, not a dodge.

Output: an inventory the user can see - *option · family · how it works in one clause · fits constraints?*.
If it exceeds ~5 workable options, pre-filter to 2-5 finalists by cheap research (docs, not benchmarks), and
report what was dropped and why. The pre-filter exists so the expensive evidence step stays focused; it never
decides the winner.

## Step 3 - Classify the evidence each criterion needs

**Not everything is a benchmark.** Forcing measurement onto a question docs can answer is fake rigor; ask of
each criterion: *what kind of evidence settles it?*

| Criterion kind | Evidence | Notes |
|---|---|---|
| Measurable: speed, memory, accuracy, throughput, scale | **the `benchmark` skill** | it brings isolation, iteration counts, normal/ultra modes |
| Behavioral truth about a dependency: how it *actually* acts, its limits, the exact edge case docs don't cover | **the `learning-test` skill** | empirical probe of the real library - don't trust stale docs or guess the behavior |
| Documentable fact: API surface, extension/dependency availability, license, platform support, known limits | **research** | context7 if installed → official docs → web; cite what was read, for the version in use |
| Fit / judgment: maintenance style, team familiarity, architectural tidiness, DX | **explicit argument** | written as a comparison with reasons; where priorities genuinely differ, ask the user one focused question |

Produce per finalist: criterion → evidence kind → estimated cost. When benchmarks are in the plan, ask the
expected run time budget if unspecified (the benchmark skill's own rule) - a 5-minute run and an hour-long
one justify different rigor. If a criterion has no obtainable evidence here, say so now, not in the verdict.

## Step 4 - Run the evidence plan

- **Benchmarks:** on *this project's realistic data shape and size* (their 12k rows, their payload format),
  never toy numbers that flatter one option. In isolated environments per the `benchmark` skill - no global
  pollution. Measure what Step 3 promised; if the question is "which is faster in production", normal mode
  (the deployment as-is) is the honest number.
- **Learning-tests:** when a criterion is *how a library actually behaves* (does its index kick in for my
  query shape? what does it do on the boundary case?), run a `learning-test` against the real dependency
  rather than trusting the docs or memory. Numbers come from `benchmark`; ground truth comes from
  `learning-test`.
- **Research:** primary sources for the installed/considered version; record the finding and where it came
  from.
- **Record the negatives:** the test that couldn't run, the docs that couldn't be found, the assumption you
  couldn't verify. The verdict's honesty depends on them.

## Step 5 - Hand the verdict back; the user decides

**thebest is an evidence-gathering service that ends with a recommendation - the decision belongs to the
user.** The agent runs the tests and research, then *reports*; it does not pick for the project, does not
install the winner, does not start building it. This is the dividing line with `dtb`: there the agent is the
anonymous decision-maker, choosing how to build; here the agent is the analyst and the user is the judge.
Deliver the verdict in this shape (full format: `references/03-verdict.md`) and stop for the user's call:

```text
VERDICT: <choice> is likely the best fit for us.          <- "likely", never "objectively"
Based on:  <the 2-4 decisive measurements/findings, with numbers and sources>
Confidence: high/medium/low + why
Runner-up: <option> - loses on <deciding criterion> by <gap>; becomes the pick if <condition>
Flips if:  <the data/scale/requirement change that would change the answer>
Untested:  <what was decided without measurement, and why that's acceptable>
```

The runner-up line is what makes the verdict usable: the user learns not just the winner but the *condition*
the choice rests on. "12k rows now, 5M later" is a decision the user may need to know is scheduled.

The verdict is handed over, not enacted - the user picks. If they choose differently from the recommendation,
that's legitimate: they may hold priorities (risk appetite, roadmap, taste) the evidence couldn't measure.
Record their choice as the decision; do not re-litigate it.

## Boundaries

| Not this | Go instead |
|---|---|
| Choosing a fresh stack for a new project from requirements | `techstack` |
| The measurement engine itself - how to isolate, iterate, fight noise | `benchmark` (thebest decides *whether and what* to measure, then calls it) |
| Empirically probing how a library actually behaves | `learning-test` (thebest calls it for behavioral criteria) |
| A shareable HTML decision page over researched candidates | `decide` (run it after the verdict when the decision must travel) |
| Custom-building when a proven solution exists | `take-a-breath` logic - it is folded into Step 2 as the "built-in makes it moot" check |
| **Who decides** - thebest gathers evidence and *recommends*; the **user** decides. `dtb` is the opposite: there the **agent is the anonymous decision-maker**, choosing *how* to build work the user already owns the *what* of. If the user explicitly wants the agent to just choose and proceed, that is `dtb`/`iwts`, not this | `dtb`, `iwts` |
| Implementing anything | the verdict is the deliverable; the user says go |

## Files

| Need | Load |
|---|---|
| Option discovery: sources, pre-filter rules, what "all viable" honestly covers | `references/01-option-discovery.md` |
| Evidence plan: sorting criteria to benchmark / learning-test / research / argument; realism of data, time budgets | `references/02-evidence-plan.md` |
| Verdict format, confidence wording, flip conditions, reporting negatives | `references/03-verdict.md` |
| Worked example: GPS radius queries (bbox vs R-tree vs geohash) under the SQLite constraint | `examples/gps-under-sqlite.md` |
