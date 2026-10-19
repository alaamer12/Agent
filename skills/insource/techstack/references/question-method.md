# Question Formulation Method

There is no fixed bank of questions to recite here, by design. A pre-written list per domain (mobile/web/backend/infra...) inevitably goes stale, misses domains it didn't anticipate, and tempts the agent to ask questions that don't fit the actual project just because they're on the list. Per `/polyglot`: never restrict to a rigid fixed list — instead, teach the underlying method and let the agent formulate the specific questions dynamically for whatever is in front of it.

## The method

For any project, in any domain, ask what's actually undetermined across these universal axes. Not every axis applies to every project — pick the ones genuinely open, skip the ones already answered by context, and phrase the question in the vocabulary of the actual domain rather than these abstract labels.

1. **Constraint that dominates** — what does success get measured against above everything else: speed of delivery, long-term maintainability, raw performance, cost, safety/compliance, something else? This is usually the single highest-value question, since it reorders every other trade-off.
2. **Concrete capability list** — not the project's category, but the specific things it must actually do. This is where feature-fit lives (see `feature-fit-examples.md` for the pattern, not a checklist to copy) — a capability that's trivial in one technology can be a workaround in another, and the category name alone never reveals that.
3. **Depth of a demanding capability** — when a capability sounds unusual or resource-intensive, ask how far it goes, since "a little" and "a lot" of the same capability often point at different technologies (e.g. "some background work" vs. "sustained high-throughput background processing").
4. **Existing footprint** — is this landing inside something that already exists (a codebase, a team's operational experience, an existing vendor relationship, a design system)? An existing footprint changes the calculus from "best in isolation" to "best fit here" — this is also where Step 2 (existing-project awareness) gets triggered.
5. **Scale and shape of demand** — how much load, how many users/requests/connections, how bursty or steady, growing how fast? Only worth asking when the project has a demand axis at all (not every kind of project does).
6. **Team and operational reality** — what does the team already know, what do they want to own operationally versus hand off, what's the long-term maintenance appetite?
7. **Hard external constraints** — budget, licensing, compliance, data residency, platform mandates — anything non-negotiable that isn't really a preference but a wall.

## How to use this on an unfamiliar domain

The method above is written at the level of "what varies across any engineering decision," so it should transfer even to a domain not explicitly anticipated (e.g. embedded systems, data pipelines, ML training infrastructure, game engines). Walk the seven axes, decide which ones are live unknowns for *this* project, and phrase concrete, natural questions in that domain's own vocabulary. Do not force all seven into one exchange — ask the two or three that would most change the recommendation, and let the rest surface naturally as the conversation continues.

## Formulating the actual candidate technologies

Once answers come back, do not map them onto a memorized shortlist ("mobile + speed priority = X, Y, Z"). Re-derive the live candidate set for *this* combination of answers, verified as current per Step 0 of the process — the right contenders for "needs offline-first sync and modest team size" look different from "needs offline-first sync and a large existing native codebase," even though both mention offline-first sync. A rigid, pre-baked "usual options for this situation" list is the same anti-pattern as a rigid question list, just one step further down the process — avoid it the same way.

## What "look before you ask" still means here

Before generating any questions, check available context (docs, existing code, prior conversation) the same way Step 1 of the process describes — the method above is for what to ask once a genuine gap remains, not a script to run through regardless of what's already known.
