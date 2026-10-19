---
name: techstack
description: Recommend a technology/framework/library/tech stack (mobile, web, backend, desktop, infra) through rigorous, current, requirements-driven evaluation — never from memorized popularity or "what's usually used." Trigger on "what should I use to build X", "recommend a tech stack for...", "React Native vs Flutter vs...", "best framework for...", "should we use X or Y for this feature", or any choose/add/replace-tech request, new or existing project. Verify current ecosystem state via search first (tech rises, stagnates, gets superseded — memory alone isn't enough); dig into the project's actual priorities and specific required features before recommending; weigh multiple dimensions (ecosystem, maintenance, API design, abstraction, quality, performance, fit-to-requirements) rather than picking the most popular option; state trade-offs honestly, no "clear winner" with no caveats. For an existing codebase, first check what kind of change is being asked for.
---

# Tech Stack Recommendation

Choosing a tech stack is a many-dimensional decision, not a lookup. The point of this skill is for the agent to actually think it through and land on the best answer for the user — not hand over a neutral comparison and leave the decision to them. This skill is self-contained: it does not depend on any other skill to reach its conclusion.

Read `references/process.md` in full before doing any real work under this skill — it holds the five-step process (verify, understand requirements & features, existing-project context, dimensions, decide with trade-offs) and is short enough to load every time this skill triggers.

## Quick orientation

1. **Verify first.** Never recommend from memory. Check current maintenance/ecosystem state before naming anything — see `references/process.md#step-0`.
2. **Requirements before options.** Figure out what the project actually needs — priorities *and* the specific capability list — before recommending anything. Questions are formulated fresh per project, never recited from a memorized list — see `references/question-method.md`.
3. **Existing project?** Determine what kind of change is being asked for before proposing a stack. See `references/process.md#step-2`.
4. **Weigh dimensions, decide, be honest about trade-offs.** See `references/process.md#step-3` and `#step-4`.

## Bundled resources

- `references/process.md` — the full five-step process; read this every time.
- `references/question-method.md` — the *method* for generating the right questions for any project on the fly (universal axes: dominant constraint, concrete capabilities, existing footprint, scale, team/ops reality, hard constraints) — not a fixed list of questions to recite. Consult this every time real questions need to be asked, for any domain, including ones not anticipated in advance.
- `references/dimensions.md` — the dimension checklist with guidance on when each one matters; consult while doing Step 3.
- `references/feature-fit-examples.md` — worked examples (mobile, web, backend) of the *pattern* that a capability can be easy in one stack and a workaround in another; illustrative only, not a lookup table — verify specifics fresh for whatever the user actually names.
- `assets/recommendation-template.md` — the shape a final recommendation should take when the user wants it written up rather than just spoken conversationally.

## Anti-patterns (see `references/process.md` for the full list)

- Recommending from popularity/familiarity without tying it to this project's stated priorities
- Skipping requirements-gathering and jumping straight to a recommendation
- Treating the "what kind of app" category as the whole picture and ignoring specific named capabilities
- Reciting a memorized question list or a memorized "usual options for this situation" shortlist instead of formulating both fresh for the actual project
- Presenting strengths without trade-offs, or vice versa
- Proposing a stack for an existing project without first clarifying what kind of change is wanted
- Handing back a neutral side-by-side instead of an actual decision when the user asked for a recommendation
