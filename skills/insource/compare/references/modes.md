# Comparison Modes

## Open-Ended Comparison (default)

Search or inspect broadly for aspects that distinguish the subjects. Surface the dimensions that actually matter for the user's decision, then compare on those.

Use when:
- The user says "compare X and Y" without naming axes.
- The subjects are named concepts, technologies, products, processes, strategies.
- You need to discover what the real trade-offs are.

Process:
1. Research/inspect each side independently.
2. List candidate differences.
3. Cluster into 4–8 high-signal dimensions.
4. Apply quality filters.
5. Write point-by-point.

## Dimension-Based Comparison

Stay strictly inside a defined set of axes.

Use when:
- The user explicitly names dimensions ("compare on reactivity and memory").
- The subject type is local artifacts (files, modules, projects) and a focused set is natural.
- A previous open-ended pass produced too many axes and the user wants a tighter cut.

Process:
1. If the user gave dimensions → use them exactly.
2. If none given for files/modules/projects → derive a short high-signal set from the artifacts themselves (e.g. responsibility, coupling, test coverage, public API, error handling) and state the set up front so the user can correct it.
3. Gather evidence for every subject on every dimension only.
4. Apply quality filters per dimension.
5. Write point-by-point on those dimensions only.

Do not invent extra dimensions "for completeness." Length must stay proportional to genuine differences on the chosen axes.
