# Option discovery

Goal: the option list is *complete enough that the winner is on it*, and demonstrably filtered by the
project's constraints rather than by the agent's memory.

## How to widen before you narrow

- **Name families, then members.** For a problem like "spatial query in SQLite" the families are: scan
  (bbox math in SQL), index (R-tree virtual table), bucket (geohash/H3 prefix), extension (SpatiaLite-style
  geo layer), and "don't" (cache/lookup table, precomputed pairs). Members under each come from docs, not
  recall. This prevents the classic failure: the shortlist is the two options the agent has heard of.
- **The incumbent is an option.** Whatever the project does today stays in the list ("keep the bbox scan") -
  migration cost is real and the comparison must show the winner beats *the status quo*, not a strawman.
- **The zero-option check.** Before deep research, ask whether a standard-library or DB-native feature
  already solves it. Discovering that wins the decision outright and cheaply.
- **Sources, in order:** user's named candidates → project code and docs (precedent) → context7 if
  installed, else official docs for the versions in use → one general web search for alternatives the
  ecosystem actually uses. Stack Exchange/blog opinions are coloring, never evidence.

## Constraint filter (applied at listing)

Each option gets `fits constraints?` immediately, with the violation named in a clause:

```
option            family    fits?  note
bbox in SQL       scan      yes    no extension
RTREE vtable      index     yes    built into SQLite compiles? check the project's build first
SpatiaLite        ext       NO     needs loadable extension; project ships bundled SQLite without it
PostGIS move      replatform NO    constraint: database stays SQLite
```

An option killed by a constraint is *reported, not hidden* - the user may know the constraint is softer than
it looked (e.g. "we can actually ship the extension"), and a visibly filtered list is what makes the verdict
trustworthy.

## Pre-filtering to finalists

More than ~5 workable options: cheap research (docs and feasibility) narrows to 2-5 before any benchmark.
Pick finalists by *decision-relevance*, not familiarity: keep the ones that could plausibly win on the
success bar; drop the ones that lose on a documented fact (no measurement needed to see a full scan loses
at 5M rows). Always report what was dropped and the fact that dropped it.

## When the list can't be found

Some choices are genuinely two-option problems (the ecosystem has two libraries). Saying "the viable space
is just A, B, and status-quo" after honest searching is a complete answer - the requirement is *searched*,
not *long*.
