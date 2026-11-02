# Evidence plan: the four kinds of proof, and what makes each honest

## The sorting question

For each criterion, one test: **what kind of thing settles it?**

- A number settles it → benchmark (call the `benchmark` skill). Speed, memory, accuracy, throughput, latency
  at scale, file/bundle size, cold-start cost.
- **How a dependency actually behaves settles it → `learning-test`.** "Does the index get used for *my*
  query shape?", "what happens at the exact boundary case?", "does it silently fall back?" - docs are often
  silent precisely where it matters and memory is stale; a learning-test probes the real library and records
  its real behavior. A benchmark number measured on top of unverified behavior is a number about something
  you don't yet understand.
- A source settles it → research. API surface, extension availability, license, platform support,
  known defects - these are *facts*, and measuring them with a proxy benchmark is how confident wrong
  answers get produced.
- Neither settles it → fit/judgment. Team familiarity, maintenance taste, architectural cleanliness. These
  are argued against the project's own stated goals - and where the trade genuinely depends on user
  priorities ("we value minimal deps vs fastest queries"), ask one focused question instead of scoring it
  yourself.

The common failures run both directions: benchmarking something docs answer in minutes (fake rigor), and
*assuming* behavior a learning-test would falsify (the R-tree that looked indexed but wasn't). Sort every
criterion explicitly.

## When benchmarks are the right tool, make them mean it

- **Real data, real shape.** The project's distribution: their point count, their radius widths, their
  payload size. A uniform-grid synthetic dataset can crown a winner that loses on real coordinates.
- **Real environment.** Normal mode measures what the deployment feels like; ultra mode (noise-fighting)
  is for micro-differences where the gap is close. State which was used and why.
- **Budget first.** Expected run time changes what's worth measuring - ask if unspecified; 5 minutes buys
  ~10 iterations, an hour buys 100+ and tighter gaps. Decide *before* running whether the budget allows
  resolving the closest criterion, and say which comparisons remain coarse.
- **Isolation, always.** The benchmark skill's rule: install/measure in isolated environments (a project-local
  `[venv]`, `[npm ci --prefix]`, a `[temp dir]`) - never pollute the machine while deciding for it.

## When research is the right tool, make it current

- context7 if installed, else official docs; **version-matched** to what the project uses or would adopt.
  For a library question, that answers API/behavior/limits for the right major; a memory-based answer about
  a fast-moving dependency is not evidence.
- Prefer documented numbers ("RTREE vtable ships in the standard SQLite build") over folklore.
- Save the citation trail per finding - the verdict quotes sources, and the user may need to check.

## Mixed-criteria honesty

A decision often resolves one criterion by measurement and another by argument (R-tree wins the timing test;
"no exotic dependency" wins by a documented availability fact; team comfort is argued). The plan names, per
finalist, which kind of evidence will carry which criterion, so the verdict can say exactly how much of it
was measured and how much was judgment.
