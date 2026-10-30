# Tool Tiers, Consolidation, and Topic-Based Discovery

This reference applies in **both modes**. It covers three things the agent must get right before naming any tool: how candidates are *found*, how candidates are *classified*, and how a consolidated tool is weighed against several specialists.

## Part 1: Discover by topic, never by recall

The candidate set for any decision comes from **searching the topic**, not from what the agent remembers. Memory is a source of extra search seeds at most; it never defines or prunes the candidate set.

### How to search

- Phrase queries as the **need**, not as product names. The form is "[concern] [libraries / packages / crates / modules] for [ecosystem]", for example "validation libraries for JavaScript", "validation libraries for .NET", "data transformation packages for Python", "job queue options for Go", "retry crates for Rust". Search the registries and sources native to the ecosystem (package registry, official docs, first-party libraries), not only generic web results. The agent must not start from "Zod vs Yup" because it already knows those two.
- Run **several queries per concern**, from different angles: the plain topic, a comparison or "best of" angle, a recent-changes angle, and the **higher-tier angle** (see Part 3) such as "all-in-one toolkit for [concern A] and [concern B]" or "[ecosystem] library that handles [A], [B], and [C] together".
- Read the **dates** of what comes back. An old "best libraries" list is evidence of what was popular then, not now.
- Build the candidate list **from the results**. If a result surfaces a tool the agent has never heard of, it goes in the list and gets verified like any other. If a tool the agent expected is missing from the results, that is information, so check why (stagnant, superseded, renamed) rather than adding it back from memory.
- After the list exists, verify each serious candidate per Step 0 of `process.md` (maintenance, recent changes, current sentiment).

### Why this rule exists

A recalled shortlist is always shaped by what was prominent at training time. It over-represents old incumbents, misses recent entrants, and, most relevant here, almost never contains tools from a *different tier* than the one the agent had in mind. Topic searches are what surface a consolidated alternative the agent didn't think to look for.

## Part 2: The four tiers

Classify every candidate by **breadth of scope**:

| Tier | What it is | Typical shape |
|---|---|---|
| **Library** | Does one job; the application calls it | A validator, a retry helper, a date utility |
| **Meta-library** | Covers several concerns in one coherent model, even if it does not match a specialist's depth on each | A toolkit that offers validation, retries, timeouts, and more under one abstraction |
| **Framework** | Provides the structure of an application or a layer of it; the framework calls the application's code | UI frameworks, web or backend frameworks, desktop frameworks |
| **Meta-framework** | Built on or around a framework and decides the surrounding application concerns for you: routing, rendering or hosting model, data access conventions, build and deploy | An opinionated layer or distribution that turns a framework into a full application platform |

Notes on classification:

- The tier describes **scope breadth, not quality or popularity**. A meta tool is not better or worse than a specialist by default, and a higher tier is **never better just for having more features** (see "Surplus capability is a cost, not a credit" below).
- A tool can sit at different tiers for different concerns. Classify it against the concerns *this project* would use it for.
- The distinguishing feature of a meta tool is that it **replaces several independent tools at once** and gives them a single model (one error type, one composition style, one set of conventions), usually at some cost in per-concern depth.
- **The tiers are scope labels, not a taxonomy to force.** Ecosystems differ: some ship a batteries-included platform and standard library, so one framework may already cover what elsewhere takes a meta-framework, and the boundaries blur. When a candidate doesn't fit a tier cleanly, use the scope question below and say so rather than forcing a label.
- If a candidate's tier is unclear, decide by asking: how many of the project's needed concerns would this one dependency replace?

## Part 3: Consolidated vs. specialist, in both directions

The same project need can often be met two ways: **one higher-tier tool** (meta-library or meta-framework), or **several lower-tier tools** (separate libraries, or a framework plus libraries). Neither is the default. Evaluate both for every group of related concerns, and do it for the primary level too (a framework plus its own libraries versus a meta-framework).

### What favors consolidating

- **One model across concerns.** Consistent error handling, composition, and typing across what would otherwise be several unrelated APIs.
- **Less glue.** Separate tools need adapters, shared types, and agreed conventions; a consolidated tool already has them.
- **Interaction correctness.** Concerns that must cooperate (for instance retries that respect a timeout budget) are easier to get right when one tool designs them together.
- **Smaller footprint** in dependencies to track, upgrade, and audit, when the consolidated tool replaces many.

### What favors specialists

- **Depth where it matters.** A dedicated tool is often stronger at its one job than the corresponding part of a meta tool. If one concern is critical to the project, depth on that concern can outweigh everything else.
- **Independence.** Swapping one specialist later is cheaper than unwinding a pervasive abstraction.
- **Lower paradigm cost.** Some meta tools impose a programming model across the codebase. If the team or the existing code doesn't fit that model, the consolidation pays back less than it costs.
- **Ecosystem fit.** Specialists often have richer integrations, docs, and community answers for their narrow area.

### Surplus capability is a cost, not a credit

A tool's value to this project is the set of capabilities the project will **actually use**. Features it will never touch add no benefit, and they are not free: they bring conventions to follow, build and runtime requirements, extra concepts for the team, a larger upgrade surface, and constraints on hosting and structure. Carrying them is a cost.

Apply this at every tier. It matters most when comparing a framework with its meta-framework, or a specialist with a meta-library, because the higher tier's pitch is its extra scope.

**Usage test.** For each capability that makes the higher-tier option attractive, ask: does a requirement of *this* project need it, now or at a trigger we can name? Count only capabilities that pass. If what is left after the test is small, the higher tier is paying for itself with little, and the simpler option should win.

**Also weigh how easy the frequent operation is.** Ask what the project does most often (adding another page, another endpoint, another form) and how much ceremony each option puts around it. A project that repeats one simple operation many times can be better served by the plainer tool, even if the richer one is more capable overall.

**Start-simple is a valid answer.** If the higher-tier capability might become necessary later, check the upgrade path. When moving up later is reasonably cheap, choosing the simpler tool now and naming the trigger for moving up beats paying for the capability in advance.

The reverse also holds: when the project does use the extra scope (for instance it truly needs what the higher tier bundles), the usage test passes and the higher tier can win clearly. The test is about *this project's* usage, not a preference for small or large.

### How to decide

1. List the concerns the project needs (in ultra mode, the Step 2.5 inventory; in normal mode, the concerns directly in scope of the decision).
2. Mark which are **critical-depth** for this project (a weaker implementation would hurt it) and which are **commodity** (adequate is enough).
3. For each plausible consolidated tool, check how many of the needed concerns it covers at adequate depth and how many it covers only nominally, and run the usage test above: list what it brings that the project will not use, and count that as carried weight, not as a benefit.
4. Weigh the paradigm cost against the team and the existing code, and check for an **escape hatch**: can the specialist be used for the critical concern while the rest stays in the meta tool?
5. Choose. The answer may be fully consolidated, fully separate, or a **hybrid** (meta tool for the commodity concerns, a specialist for the critical one). State what drove it.

Rules of thumb that are easy to violate:

- Do not choose consolidation just because it reduces the number of dependencies, and do not choose specialists just because each is individually stronger. Tie the choice to this project's critical concerns and constraints.
- Do not count a nominal feature as coverage. If the meta tool "supports" a concern but the project would need a plugin or workaround for what it actually requires, that concern is not covered.
- Do not treat more features, or a higher tier, as better in itself. Capabilities the project won't use count for nothing and cost something.
- Evaluate the consolidated option with the same Step 0 verification as every other candidate.

## Part 4: Illustrations

These show the shape of the reasoning; every specific claim about a named tool must be verified fresh.

- **Several supporting concerns, one critical.** A service needs validation, retries, timeouts, and structured error handling. Suppose a topic search surfaces a meta-library covering all four under one model. If validation is the critical-depth concern (complex schemas, many consumers), a hybrid fits: the meta-library for retries, timeouts, and error handling, with a dedicated validator where schema depth matters. If all four are commodity needs and the team is open to its programming model, going fully consolidated can beat four separate libraries plus glue.
- **A small team on a simple system.** The same concerns may favor four small independent libraries if the meta tool's paradigm would be heavier than the whole problem.
- **Capability the project doesn't need.** A back-office application with around fifty pages behind a login has no search-engine visibility requirement and no need for server rendering. A UI framework with a router can serve it directly, and adding a page is just adding a route and a component. The meta-framework's headline capabilities would be carried unused, along with its conventions and runtime requirements, so the plain framework is the better fit. The call flips if a requirement appears that the meta-framework's extra scope actually serves (public pages that must be indexed, for instance). The same reasoning applies one level down to libraries.
- **Primary level.** A framework plus separately chosen routing, rendering, and data-loading libraries versus a meta-framework that bundles those decisions. The same weighing applies: how many of the project's needs the meta-framework covers at adequate depth, and how much of its convention set the project is willing to adopt.

## Part 5: Ecosystem is a variable, not an assumption

The skill must not carry a hidden default ecosystem. Rules:

- **Fixed ecosystem.** If the existing code, the team's skills, or a stated constraint fixes the language or platform, search and compare inside it. Its own conventions apply: package registry, standard library, first-party packages, and its idea of what a framework is.
- **Open ecosystem.** If it is not fixed, the ecosystem choice is part of the decision (team skills, deployment target, library depth for the project's critical concerns, hiring, long-term support). Discover candidates in each plausible ecosystem and compare.
- **Platform first.** In every ecosystem, check what the **platform already provides** (standard library, runtime features, first-party packages) before external candidates. How much it covers varies widely by ecosystem, so "platform covers it" is a common verdict in some and rare in others. Never assume it from another ecosystem's habits.
- **Application model is itself a choice.** Many ecosystems offer several distinct models for the same kind of application (server-rendered pages, a client-rendered UI, a hybrid, a cross-platform UI layer). Treat the model as a decision with trade-offs and apply the usage test to each model's distinctive capabilities, rather than assuming the model the agent knows best.
- **Do not transplant tool patterns.** A problem solved by a separate library in one ecosystem may be a language feature, a platform API, or a single dominant package in another. Re-derive from the topic search in the ecosystem at hand.

Cross-ecosystem illustrations are in `examples/polyglot-walkthrough.md`.
