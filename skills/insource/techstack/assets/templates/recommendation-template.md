# Tech Stack Recommendation: [Project Name]

## Recommendation

**[Chosen technology/stack]** — stated plainly, first, before any supporting detail.

## Why

The 2-4 dimensions that actually drove this decision, each tied to a stated project priority or feature. Not an exhaustive dimension-by-dimension scorecard — just what mattered.

## Trade-offs

What is being given up by this choice. Named explicitly, not buried in a caveat at the end.

## Feature-specific notes

Any named feature from the requirements that is notably easy, awkward, or unsupported in this recommendation — called out directly rather than glossed over.

## If priorities shift

What fact or changed priority would change this recommendation (e.g. "if native feel becomes more important than delivery speed, reconsider [option B] instead").

## Verified as of

Note that the ecosystem state (maintenance status, recent changes) was checked as of the conversation date, since this can go stale — encourage re-verification if this recommendation is acted on much later.

---

## Ultra mode variant

Use this shape when running in ultra mode. Keep the sections above and add the concern coverage between **Why** and **Trade-offs**.

### Concern coverage

| Concern | Why this system needs it (trace) | Choice | Detail for this system | Trade-off |
|---|---|---|---|---|

One row per concern with the verdict *Needed* (including *platform covers it*). Every row must have a trace to a requirement, feature, constraint, or scale fact. Detail means the semantics, settings, integration point, and cost that make the choice actionable, not just a tool name.

### Packaging

For each group of related concerns: whether it is served by one higher-tier tool, by separate specialists, or by a hybrid, with the one or two facts that decided it (which concern is critical-depth, paradigm cost, glue cost). When a higher-tier option was passed over, name the capabilities of it that this project would not use.

### Deferred

Each item: the concern, why it is not worth adopting yet for this system, and the concrete trigger that would change that.

### Not needed here

Each item: the concern and a one-line reason tied to this system.

Keep the whole section proportional to the system. A short list is a correct answer for a simple system.
