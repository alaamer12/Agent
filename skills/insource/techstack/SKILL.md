---
name: techstack
version: 1.0.3
author: Amr
specialized: none
description: 'Recommend a technology/framework/library/tech stack (mobile, web, backend, desktop, infra) in any language or platform via rigorous, current, requirements-driven evaluation, never memorized popularity. Trigger on "recommend a tech stack", "React Native vs Flutter", choose/add/replace-tech requests. Discover by topic search, never memory; classify by scope; weigh consolidated vs specialists; count only features the project will use. Pin every capability claim to the candidate''s latest stable version (from registry/releases, not memory) and ground it in real-world proof - before calling a capability awkward, find a real app that does it. Surface parity is not implementation parity - probe how daily-used capabilities are delivered. Compare via a yes/no capability matrix; split a product''s distinct modes into separate candidate rows. Weigh the dimensions that matter; state trade-offs honestly. Two modes: normal (primary tech plus close dependencies) and ultra (every real need), on "ultra"/"full coverage".'

argument-hint: "[normal|ultra] <what to choose or evaluate>"
---

# Tech Stack Recommendation

Choosing a tech stack is a many-dimensional decision, not a lookup. The point of this skill is for the agent to actually think it through and land on the best answer for the user — not hand over a neutral comparison and leave the decision to them. This skill is self-contained: it does not depend on any other skill to reach its conclusion.

## Modes

- **Normal (default):** the five-step process in `references/process.md`, unchanged.
- **Ultra:** the same process plus a concern inventory that covers the whole system, so every real need gets a deliberate decision. Triggered by an explicit signal from the user ("ultra", "full coverage", "every aspect of the system", or similar). Ultra ignores "we can build it ourselves" as a reason to leave a real need unassigned, but it stays grounded: every concern must trace back to something the system actually needs, and "not needed here" and "deferred" are valid verdicts. Ultra is breadth proportional to the system, never a license to over-engineer. Read `references/ultra-mode.md` in full when running in ultra mode.

State which mode is running in the first line of the response. If the mode is not specified, use normal. If the project is non-trivial and the user may not know ultra exists, add one line at the end saying it is available.

Read `references/process.md` in full before doing any real work under this skill — it holds the five-step process (verify, understand requirements & features, existing-project context, dimensions, decide with trade-offs) and is short enough to load every time this skill triggers.

## Neutrality rule

This skill is ecosystem-agnostic. The core steps never name a product, language, or ecosystem, and the agent never defaults to the one it knows best. Establish whether the user's language or platform is fixed (then stay inside it) or open (then the ecosystem is part of the decision). Named tools appear only in `examples/`, across several ecosystems, always marked illustrative; every real recommendation comes from fresh topic searches in the user's ecosystem.

## Quick orientation

1. **Discover by topic, then verify.** Candidates come from topic searches ("[concern] [libraries or packages] for [ecosystem]"), never from recall, and include tools from other tiers. See `references/tiers-and-discovery.md`.
2. **Verify first — against the current version, with real-world proof.** Never recommend from memory. Find each candidate's actual latest stable version (registry/releases/changelog) and pin every capability claim to it; before calling a capability awkward or impossible, search for a real app that does it. See `references/process.md#step-0` and `references/evidence.md`.
3. **Requirements before options.** Figure out what the project actually needs — priorities *and* the specific capability list — before recommending anything. Questions are formulated fresh per project, never recited from a memorized list, and there is no fixed cap: if the agent does not understand the user's full goal, it asks as many questions as it takes, in rounds, until it can state the goal back — see `references/question-method.md`.
4. **Existing project?** Determine what kind of change is being asked for before proposing a stack. See `references/process.md#step-2`.
5. **Weigh dimensions (including consolidated vs. specialist tools), decide, be honest about trade-offs.** See `references/process.md#step-3` and `#step-4`.
6. **Establish mechanism from public sources, not reverse engineering.** Equal feature lists and API shapes hide different internals — how each constantly-used capability is delivered (native vs re-implemented, surfaced hooks vs pierced internals) is what splits a tie. The evidence is already public: docs, the component's own source on the repo, its issue tracker and discussions, Q&A sites. See `references/dimensions.md` §Mechanism.
7. **Compare hard capability gates with a yes/no matrix.** Derive binary questions from the project's requirements, answer them identically for every candidate, and split a product's distinct modes into separate rows — one brand can hide opposite answers. A "no" on a must-have disqualifies; the dimensions then weigh the survivors. See `references/capability-matrix.md`.

## Bundled resources

- `references/process.md` — the full five-step process; read this every time.
- `references/evidence.md` — grounding every judgment: find each candidate's actual latest stable version and pin capability claims to it; search for real-world proof before any negative capability claim. Read at Step 0 and whenever a capability is asserted; applies in both modes.
- `references/question-method.md` — the *method* for generating the right questions for any project on the fly (universal axes: dominant constraint, concrete capabilities, existing footprint, scale, team/ops reality, hard constraints) — not a fixed list of questions to recite. Consult this every time real questions need to be asked, for any domain, including ones not anticipated in advance.
- `references/tiers-and-discovery.md` — applies in both modes: how to discover candidates by topic search, the four tiers (library, meta-library, framework, meta-framework), and how to weigh a consolidated tool against separate specialists in both directions. Read before naming any tool.
- `references/ultra-mode.md` — ultra mode: the concern-inventory method, the trace rule, verdicts, depth requirements, the DIY rule, and output shape. Read in full whenever running in ultra mode.
- `examples/ultra-examples.md` — worked illustrations of ultra mode, including an inflated anti-example. Illustrative only; tools named there must be verified fresh.
- `references/dimensions.md` — the dimension checklist with guidance on when each one matters; consult while doing Step 3.
- `references/capability-matrix.md` — the yes/no capability matrix: derive binary questions from the requirements, split a product's distinct modes into separate candidate rows, ground each cell, and let must-have gates disqualify before the dimensions weigh survivors. Read when structuring a comparison with real capability gates (Step 3/4).
- `examples/feature-fit-examples.md` — worked examples (mobile, web, backend, and the mechanism-parity case) of the *pattern* that a capability can be easy in one stack and a workaround in another, and that two candidates with equal feature lists can deliver the same capability through different internals; illustrative only, not a lookup table — verify specifics fresh for whatever the user actually names.
- `examples/capability-matrix-example.md` — worked illustrations of the matrix method: a product split into mode-rows with opposite answers, and a real application overturning an "awkward" verdict; illustrative only — verify named tools and find the real-world citations fresh.
- `assets/templates/recommendation-template.md` — the shape a final recommendation should take when the user wants it written up rather than just spoken conversationally.

## Anti-patterns (see `references/process.md` for the full list)

- Recommending from popularity/familiarity without tying it to this project's stated priorities
- Skipping requirements-gathering and jumping straight to a recommendation
- Treating the "what kind of app" category as the whole picture and ignoring specific named capabilities
- Building the candidate list from memory instead of topic searches, or considering only one tier of tool
- Recommending before the goal is understood, or limiting questions to a token few when the goal is still unclear
- Defaulting to one ecosystem's tools or habits (for example assuming a package-library answer where the platform already provides it, or vice versa) instead of working inside the user's actual ecosystem
- Treating more features, or a higher tier, as better in itself rather than counting only what the project will use
- Scoring two candidates equal because their capability lists match, without probing *how* each delivers the daily-used ones (native vs re-implemented internals, customization through surfaced hooks vs piercing workarounds like `:deep()`) — surface parity is not implementation parity
- Judging a candidate from a stale version, or asserting a capability without pinning it to the candidate's actual latest stable release found from an authoritative source
- Declaring a capability awkward, limited, or impossible from the API's shape without searching for real-world proof (a real app, case study, or production user) that it is done — a false "no" wrongly eliminates a viable candidate
- Collapsing a product's distinct modes into one comparison row, or silently picking the favorable mode, instead of splitting each decision-relevant mode into its own candidate with its own yes/no answers
- Reciting a memorized question list or a memorized "usual options for this situation" shortlist instead of formulating both fresh for the actual project
- Presenting strengths without trade-offs, or vice versa
- Proposing a stack for an existing project without first clarifying what kind of change is wanted
- Handing back a neutral side-by-side instead of an actual decision when the user asked for a recommendation
- (Ultra) Stopping at the primary framework and leaving supporting needs unaddressed, or dismissing a real need with "we can build it ourselves"
- (Ultra) Inflating the stack: adding tools whose concern has no trace to this system's requirements, or naming a tool without the system-specific detail that makes it actionable
