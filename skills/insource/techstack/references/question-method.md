# Question Formulation Method

There is no fixed bank of questions to recite here, by design. A pre-written list per domain (mobile/web/backend/infra...) inevitably goes stale, misses domains it didn't anticipate, and tempts the agent to ask questions that don't fit the actual project just because they're on the list. Per `/polyglot`: never restrict to a rigid fixed list — instead, teach the underlying method and let the agent formulate the specific questions dynamically for whatever is in front of it.

## The method

For any project, in any domain, ask what's actually undetermined across these universal axes. Not every axis applies to every project — pick the ones genuinely open, skip the ones already answered by context, and phrase the question in the vocabulary of the actual domain rather than these abstract labels.

1. **Constraint that dominates** — what does success get measured against above everything else: speed of delivery, long-term maintainability, raw performance, cost, safety/compliance, something else? This is usually the single highest-value question, since it reorders every other trade-off.
2. **Concrete capability list** — not the project's category, but the specific things it must actually do. This is where feature-fit lives (see `examples/feature-fit-examples.md` for the pattern, not a checklist to copy) — a capability that's trivial in one technology can be a workaround in another, and the category name alone never reveals that.
3. **Depth of a demanding capability** — when a capability sounds unusual or resource-intensive, ask how far it goes, since "a little" and "a lot" of the same capability often point at different technologies (e.g. "some background work" vs. "sustained high-throughput background processing").
4. **Existing footprint** — is this landing inside something that already exists (a codebase, a team's operational experience, an existing vendor relationship, a design system)? An existing footprint changes the calculus from "best in isolation" to "best fit here" — this is also where Step 2 (existing-project awareness) gets triggered.
5. **Scale and shape of demand** — how much load, how many users/requests/connections, how bursty or steady, growing how fast? Only worth asking when the project has a demand axis at all (not every kind of project does).
6. **Team and operational reality** — what does the team already know, what do they want to own operationally versus hand off, what's the long-term maintenance appetite?
7. **Hard external constraints** — budget, licensing, compliance, data residency, platform mandates — anything non-negotiable that isn't really a preference but a wall.

## How to use this on an unfamiliar domain

The method above is written at the level of "what varies across any engineering decision," so it should transfer even to a domain not explicitly anticipated (e.g. embedded systems, data pipelines, ML training infrastructure, game engines). Walk the seven axes, decide which ones are live unknowns for *this* project, and phrase concrete, natural questions in that domain's own vocabulary. Pick the axes that are genuinely open and phrase them naturally; how many to ask is governed by the next section, not by a fixed number.

## When the goal itself is unclear

The seven axes assume the agent already understands what is being built. If it does not, start one level higher, with the goal, before any technology question:

- **What is this for, and for whom?** The people or systems that use it, and what they are trying to accomplish.
- **What does success look like, and what would failure cost?** How the user will know it worked, and what hurts if it doesn't.
- **How long should it live?** Throwaway experiment, product that must grow, or system of record. This reorders almost every trade-off.
- **What already exists or is already decided?** Code, team, vendors, deadlines, commitments.
- **What have they already tried or ruled out, and why?** Past failures carry hidden requirements.

A user who says "I want to build X" has usually described a category, not a goal. Ask until the real goal is clear.

## How many questions

There is no fixed cap. Scale to the gap in understanding:

- **Goal and capabilities clear (or discoverable from context):** ask few or none and go on to the recommendation.
- **Some axes open:** ask about those, grouped together, at the level of detail the decision needs.
- **The goal itself is unclear:** ask a lot, as many as it takes. A recommendation built on a misunderstood goal wastes the whole exercise, and asking is far cheaper than redoing it.

How to ask many questions well:

1. **Look before asking.** Exhaust available context first (conversation, files, existing code, docs).
2. **Ask in rounds, adaptively.** Start with the goal-level questions, then let each answer decide the next round. Do not pre-write a long list; later questions depend on earlier answers.
3. **Group and order.** Put related questions together, most decision-changing first, so the user answers in one pass instead of facing an interrogation.
4. **Make them easy to answer.** Offer concrete options and a structured choice tool when natural, allow "not sure" and "don't care," and say why a question matters when it isn't obvious.
5. **Reflect back.** Before recommending, restate the understood goal, priorities, and capability list in a few lines and let the user correct it.
6. **Know when to stop.** Stop when the agent can restate the goal accurately and no plausible answer to any remaining question would change the recommendation. Questions beyond that are noise.
7. **Never block.** If the user declines or brushes past the questions, fall back to the labeled general recommendation described in Step 1 of `process.md`, and say plainly what was assumed.

The quantity allowance does not relax the quality rule: every question must come from this project's own facts, not from a memorized list.

## Formulating the actual candidate technologies

Candidates come from topic searches (see `tiers-and-discovery.md`), including tools at other tiers than the obvious one.

Once answers come back, do not map them onto a memorized shortlist ("mobile + speed priority = X, Y, Z"). Re-derive the live candidate set for *this* combination of answers, verified as current per Step 0 of the process — the right contenders for "needs offline-first sync and modest team size" look different from "needs offline-first sync and a large existing native codebase," even though both mention offline-first sync. A rigid, pre-baked "usual options for this situation" list is the same anti-pattern as a rigid question list, just one step further down the process — avoid it the same way.

## What "look before you ask" still means here

Before generating any questions, check available context (docs, existing code, prior conversation) the same way Step 1 of the process describes — the method above is for what to ask once a genuine gap remains, not a script to run through regardless of what's already known.
