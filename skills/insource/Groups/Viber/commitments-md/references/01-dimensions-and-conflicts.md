# Dimensions, real conflicts, and the question bank

> Everything below is **illustrative, not exhaustive and not web-specific**: a CLI tool, a game, an embedded
> system, a data pipeline and a library each come with their own dimensions and tensions. Use these as
> examples to recognize the shape, then write the project's own set - unlisted dimensions and hybrid answers
> are always acceptable.

## Candidate dimensions (illustrative, not a closed list)

Use only the ones the project actually has - an unused dimension in the document is noise:

`[performance]` · `[latency]` · `[throughput]` · `[accuracy]` · `[battery use]` · `[install size]` ·
`[memory]` · `[SEO]` · `[accessibility]` · `[DX]` (developer experience) · `[ecosystem maturity]` ·
`[maintainability]` · `[time-to-market]` · `[bundle size]` · `[security]` · `[privacy]` · `[cost]`
(hosting/infra/ops) · `[design fidelity]` · `[i18n]` · `[offline behavior]` · `[test rigor]` ·
`[portability]`

## Example conflicts (the shape, across domains)

| Pair (example) | The tension, concretely | What a decision sounds like |
|---|---|---|
| Performance vs **ecosystem maturity** | A newer, faster option with a thin ecosystem against a mature one with more packages, answers and hires | "We take the faster option and absorb the ecosystem risk, or we take the mature one and pay in performance." Name the side chosen. |
| **Accuracy** vs **battery use** (on-device sensing) | Sampling more often improves accuracy and drains the battery | "Sample every N on battery; full rate while charging" - a conditional commitment. |
| **Throughput** vs **cost** (data pipelines) | More parallel workers finish sooner and cost more | A budget number plus a batch-size policy resolves it. |
| **SEO** vs rich interactivity (content sites) | Crawlable content favors server rendering; heavy client interactivity favors SPAs | Often *resolvable* (SSR + islands) - that is a cost in build complexity, not necessarily a loss. Decide which side pays when they do collide. |
| **Time-to-market** vs polish dimensions | Shipping sooner means accepting known gaps in [performance], [accessibility], [test rigor] | "MVP: ship with N gaps listed; post-launch: close them." The gaps are part of the commitment. |
| **DX** vs runtime performance | Abstractions that make developers faster can cost runtime | "We accept X% overhead for the DX gain" - with a measured % where possible. |
| **Design fidelity** vs accessibility | Pixel-perfect custom UI vs semantic, standards-based components | "Accessibility wins; the design adapts." or the reverse - never left implicit. |
| **Privacy** vs analytics-driven goals | Rich measurement vs data minimization | Usually a hard constraint: privacy floor outside the trade space. |
| **Install size / bundle size** vs feature richness | Every feature ships bytes | A budget number is the resolution: "≤ N MB installed; features above it lazy-load or drop." |

**Test every "conflict" for a both-satisfying solution before recording it.** If SSR gives SEO and the
interactivity, if semantic HTML gives accessibility and SEO at once, the pair is compatible and the only
price is effort - which belongs in the plan, not in the commitments. Recording fake trade-offs teaches
agents to sacrifice things for nothing.

## Compatible pairs (list them, so nobody pays for them)

- **Security + maintainability** - fewer data paths and fewer custom mechanisms.
- **Accessibility + clarity** - both force plain structure and explicit labels.
- **Performance + accessibility** (lean interfaces) - fewer resources, fewer traps.
- **Latency + cost** (with batching) - one policy serves both.

These are examples, not axioms: verify in this project's context; list the ones that hold.

## Conditional priorities

- **By phase:** "MVP: ship; v1: performance and a11y; scale: cost per request."
- **By surface:** "Mobile web matters more than desktop polish."
- **By audience segment:** "Authors' writing flow > readers' discovery in phase 1."

The condition is part of the statement: `Before launch, [time-to-market] outranks [performance]; after
launch the order flips.`

## The question bank - one per tension

Ask only the rows that apply; phrase every one as a choice, never as a request to list preferences:

1. "When <X> and <Y> point in opposite directions, which one wins - and what do we accept losing?"
2. "What must we **never** sacrifice, even for a preferred goal?" (hard constraints)
3. "What does 'good enough' mean for <dimension> - a number, or a named check?"
4. "Does this priority change with the phase? What flips it?"
5. "Is there an option that gives us both? If yes, is the extra effort acceptable?"
6. "Who arbitrates later? If a future task finds a new conflict here, who decides?"

## Reading commitments back - the format that holds

Every committed priority is one line of the same shape:

```
[dimension] > [dimension]  |  horizon: <phase>  |  accept: <the price>  |  bar: <number/check>
```

Example: `[SEO] > [interactivity] | horizon: MVP | accept: more build complexity from SSR | bar: all
content pages crawlable with JS disabled`.

Anything that cannot fill this line is an open question, not a commitment.
