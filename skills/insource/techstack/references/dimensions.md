# Dimensions Checklist

Use this while doing Step 3/4 of the process. Not exhaustive — invent additional dimensions where the project calls for it. Not every dimension applies to every decision, and dimensions should be weighted by what this project's priorities (Step 1) actually make relevant, not treated as equally important by default.

- **Ecosystem** — size, maturity, and breadth of libraries/plugins/community support. Matters more for projects likely to need lots of third-party integration; matters less for a narrow, self-contained tool.
- **Maintenance** — how actively developed, release cadence, responsiveness to issues, bus factor (one maintainer vs. an organization/foundation behind it). Matters more for anything long-lived or mission-critical; verify this via Step 0, don't assume from memory.
- **API design** — simplicity and ergonomics vs. low-level control exposed. Matters more when team skill/onboarding speed is a priority; matters less if the team already has deep expertise.
- **Abstraction level** — high-level convenience vs. ability to drop to lower-level access when needed. A technology that's *only* high-level can become a ceiling later if the project needs something the abstraction doesn't expose — check whether an escape hatch exists.
- **Quality** — overall implementation quality, stability, track record (bug history, security track record, breaking-change frequency).
- **Performance** — efficiency under the *relevant* workload, not performance in the abstract. A technology can be "slow" in general benchmarks but perfectly fine for a workload that never stresses the bottleneck that makes it slow — always tie this back to what the project will actually do.
- **Fit against requirements** — how well it satisfies the project's specific stated needs, including the concrete feature list (see `examples/feature-fit-examples.md`). This is usually the dimension that should carry the most weight, since it's directly tied to what the user asked for.
- **Carried weight** — capabilities, conventions, and requirements the tool brings that this project will not use (extra concepts to learn, build or runtime constraints, a larger upgrade surface). Unused features are a cost, not a benefit. Matters most when comparing a tool with its higher-tier counterpart; the plainer option often wins when the project uses little of the extra scope, and loses when it uses most of it.
- **Design/architecture** — quality of the underlying architecture and its long-term implications (e.g. does it lock the project into patterns that become painful to unwind later).
- **User-specific dimensions** — anything the user has flagged as mattering that doesn't fit the above: licensing terms, team familiarity/existing skill, compliance requirements, a specific integration they already depend on, budget/cost of hosting or tooling.

## Using the checklist without over-mechanizing it

The point of this checklist is to make sure nothing relevant gets silently skipped — not to produce a scored table for every comparison. For a straightforward decision, naming the two or three dimensions that actually drove the call is enough. Reach for a fuller explicit walk-through when the decision is close, high-stakes, or the user asks for the full reasoning.
