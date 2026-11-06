# Execution and delegation - research duties are mandatory, delegation is conditional

Reveal's investigation is organized into specialized research responsibilities. Whether they run as parallel
subagents or as sequential passes by one agent depends entirely on the harness. The architecture adapts; the
research objectives and quality do not.

## The core rule

**Research responsibilities are mandatory; agent delegation is conditional.** Reveal must always perform the
full broad, multi-dimensional investigation regardless of environment capability. It never downgrades the
*what* because of a constraint on the *how*.

## The research responsibilities

These are roles in the investigation, not required agent definitions. One agent doing them sequentially, or
ten agents doing them in parallel, produce the same coverage:

- Name and identity research (dimension A)
- Features and functionality research (B)
- Market and business research (C, G)
- Geography and localization research (D)
- History and viability research (E, J)
- Popularity and user-base research (F)
- Developer / open-source research (H)
- Community and social research (positioning evidence, I)
- Application-store research (F, G, D for mobile)
- Customer-experience research (reviews, complaints, I)
- Independent competitor discovery (the snowball frontier from [`02`](02-discover-projects.md))

## When delegation is available and useful

If the harness supports subagents / parallel execution, fan out for coverage and speed:

1. Divide the investigation into specialized tasks (usually by dimension-cluster or by competitor-batch, or
   both - a grid of "these competitors × these dimensions").
2. Give **every** delegated task the *same* project brief and the *same* shared objective, so parallel work
   stays comparable and mergeable.
3. Run the independent investigations in parallel.
4. Let discoveries propagate - a competitor one researcher finds is handed to the others so it is not
   re-discovered or missed.
5. Consolidate into one unified investigation; the parent owns synthesis and scoring, not the children.

Use the `subagent` skill's brief shape when present (Context → Goal → How → Autonomy Bounds → Output
Contract), and demand the full evidence artifact, not a recap: each researcher returns ledger rows with URLs
and labels, because the parent cannot re-derive a source it never saw. Overlap tasks *deliberately* when
independent verification of a load-bearing claim is worth the duplicate cost; avoid overlap otherwise.

## When delegation is not available

If the harness offers no subagents, no parallelism, no agent-to-agent communication, no background execution,
and no particular orchestration framework - Reveal performs the **same responsibilities itself, sequentially**,
with whatever search/fetch tools it has. It must not assume any of those capabilities exist, and their absence
must never prevent completion. The report at the end of a solo run and a fanned-out run should be
indistinguishable in coverage; only the wall-clock differs.

## Adaptive prioritization by project type

Not every idea needs equal effort on every dimension. Weight the research to the nature of the project while
keeping discovery broad:

- **Mobile app** → heavy app-store + localization + download/review research.
- **Open-source dev tool** → heavy repository, GitHub activity, community, and "alternatives in the same lane"
  research.
- **Regional/local business** → heavy geography, language, payment-rails, and native-language-web research.
- **Social/community platform** → heavy audience, UX, existing-community, and network-effect research.
- **SaaS/B2B** → heavy G2/Capterra/review-site, pricing, integration, and funding research.

State the weighting chosen, in the plan, so the user sees where the effort is going and why.

## Cross-research validation (one agent or many)

Regardless of execution mode, before scoring:

- merge duplicate competitor discoveries;
- cross-reference findings across dimensions;
- verify important claims with independent sources;
- resolve or record conflicts;
- preserve every source URL and evidence label;
- note missing information and run additional targeted searches to fill it.

Do not concatenate researcher outputs into the report. Analyze and synthesize them into one coherent
competitive landscape - the synthesis is the deliverable.

## Completion criteria - the investigation, not the tasks

The run is done when the *investigation* is complete, which is not the same as "all subagents returned":

1. every relevant dimension has been adequately explored;
2. major direct and indirect competitors are identified;
3. smaller, obscure, emerging, and defunct projects have been considered;
4. competitors have been investigated beyond name-matching;
5. important findings carry supporting evidence in the ledger;
6. similarity and differentiation are assessed with stated reasoning;
7. significant gaps and limitations are disclosed;
8. further searches are producing diminishing returns.

A run that ticks all its tasks but stops short of these is incomplete, and must say so rather than present a
confident report on a thin base.
