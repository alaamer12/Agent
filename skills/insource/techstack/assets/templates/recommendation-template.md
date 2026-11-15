# Tech Stack Recommendation: [Project Name]

## Recommendation

**[Chosen technology/stack]** — stated plainly, first, before any supporting detail.

## Why

The 2-4 dimensions that actually drove this decision, each tied to a stated project priority or feature. Not an exhaustive dimension-by-dimension scorecard — just what mattered. If the decision was split by **mechanism** (the candidates tied on features but deliver a daily-used capability differently — native vs re-implemented, surfaced hooks vs pierced overrides), say so here and name the evidence, since that is the difference the feature table hides.

## Trade-offs

What is being given up by this choice. Named explicitly, not buried in a caveat at the end.

## Feature-specific notes

Any named feature from the requirements that is notably easy, awkward, or unsupported in this recommendation — called out directly rather than glossed over. A negative note here ("awkward", "unsupported") must have passed the real-world-proof check (`references/evidence.md` Part 2): if a real app does it, state "possible, proven by `[app]`, at `[mechanism cost]`" instead.

## Capability matrix

Show this when the decision turned on hard capability gates — a close call, a must-have capability, or a product whose distinct modes give different answers. Omit it for a trivial decision with no contested capability. Derive the columns from the project's requirements; split each product's decision-relevant modes into its own row (`references/capability-matrix.md`).

| Candidate (product — mode) | `[binary capability question 1]` | `[binary capability question 2]` |
|---|---|---|
| `[product] — [mode A]` | ✅/❌ `[mechanism note]` (`[version]`) | ✅/❌ `[mechanism note]` (`[version]`) |

Every cell is a version-pinned yes/no with a short mechanism note and its evidence; every disqualifying "no" passed the real-world-proof check. Below the table, state which gate eliminated which candidate and which row survives — the matrix is evidence for the decision above, not a neutral menu.

## If priorities shift

What fact or changed priority would change this recommendation (e.g. "if native feel becomes more important than delivery speed, reconsider [option B] instead").

## Verified as of

Record, per serious candidate, the **latest stable version number, its release date, and the source URL** it was checked against (`references/evidence.md` Part 1), plus the conversation date. Capability claims are pinned to those versions, not to memory. Note that this goes stale — encourage re-verification (and re-finding the latest version) if the recommendation is acted on much later.

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
