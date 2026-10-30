# Scoring routes and presenting the choice

Three clever options with no comparison is a coin flip with extra steps. Score the survivors so the pick is
defensible and so a reviewer can disagree with a number instead of guessing at a hunch.

## The eight axes

Score 1-5 (5 best). Anchors, so two agents score the same route similarly.

| Axis | 1 | 3 | 5 |
|---|---|---|---|
| **Achieves the real goal** | serves a fragment of the need | serves it with visible gaps | fully serves the goal as stated in [`01`](01-goal-and-value-extraction.md) |
| **Feasibility now** | needs something you cannot get | needs days of unknown work | buildable today with what is installed and entitled |
| **Reliability** | breaks without notice | breaks occasionally, detectable | stable, with failures you can see and recover from |
| **Maintainability** | only the author understands it | documented in code | documented, tested, and a stranger can change it |
| **Security and privacy** | touches data or trust in a way you would not ship | contained, some exposure | least privilege, consented, nothing sensitive leaves its boundary |
| **Cost and complexity** | ongoing money plus new moving parts | modest either | free-ish and simple |
| **Fit with existing architecture** | new paradigm, new infra, new dependency | adapter needed | uses the shape and libraries the project already has |
| **Fragility** (inverse of borrowing undocumented/unstable behavior) | depends on unstated internals that can change any day | depends on observed behavior you can monitor | depends on a published, versioned contract |

Fragility is the axis agents skip. A route that works because of an accident in someone else's
implementation is a scheduled outage; if it scores 1-2, say what will detect the break and what the
fallback is.

## Weights - declare them, do not invent them silently

Default weights when nothing else is known:

```text
goal 3.0 | feasibility 2.0 | reliability 2.0 | maintainability 1.0
security 2.0 | cost 1.0 | fit 1.0 | fragility 1.5
```

Adjust for what the project actually is: a prototype lowers maintainability and raises feasibility; a
regulated product raises security and reliability; a throwaway spike lowers almost everything except
feasibility. Write the weights in the record so the ranking is reproducible - `scripts/routes.py` takes
them from the plan file rather than assuming these.

## Worked comparison

Goal: the internal dashboard must keep showing trustworthy numbers after another team revoked access to the
spreadsheet it reads. Default weights, nothing exotic.

| Route | family | goal | feas | rel | maint | sec | cost | fit | frag | weighted | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Own table, synced nightly from the export they approve; the dashboard reads ours | reshape | 4 | 4 | 4 | 4 | 5 | 3 | 5 | 4 | 4.15 | decouples us; one new job to operate |
| Ask the owning team for a scoped service account and stay on their source | reroute | 2 | 4 | 5 | 4 | 5 | 4 | 5 | 5 | 4.04 | honest, boring, depends on their answer |
| Recompute the two derived columns ourselves from the database they both come from | rebuild | 4 | 3 | 4 | 4 | 5 | 4 | 4 | 4 | 4.00 | the real prize; needs their metric definitions |
| Read the figures off their published daily report, as any employee can | reroute | 3 | 5 | 3 | 3 | 5 | 5 | 3 | 2 | 3.63 | free today, fragile to a layout change |
| Free analytics SaaS fed by our warehouse | replace | 4 | 3 | 4 | 3 | 3 | 2 | 3 | 3 | 3.30 | works, and a data-sharing review first |
| Use the share link that leaked into a Slack screenshot | rebuild | **5** | 5 | 4 | 2 | 1 | 5 | 2 | 1 | **vetoed** | not ours to use; never enters the ranking |

Three lessons from the table. The top three are within 0.15 of each other, so the tie-breakers in the last
section - reversibility, fit, fragility - are doing the real work, not the arithmetic. The cheap and fragile
route loses to the one with a job to operate, which is the right verdict. And the route with the highest
*goal* score dies at the parity gate: **filter before you score, and let no vetoed route into the ranking at
all.** Its score is written here only to show that a high goal number is not evidence of a good route.

## Presenting the choice

Compress into the shape a decision-maker can act on - the same table the ask-tool expects:

```text
Option | What it is | What it fixes | Cost now | Cost later | Reversibility | Risk if wrong
```

Then:

- **Recommend one** and say why in a sentence. Options without a recommendation are homework.
- Name the **main trade-off you are accepting**, not the ones you avoided.
- Flag any contextual ToS/licensing/contract note in one line ([`04`](04-access-parity.md)).
- Ask **only** when the trade-off belongs to the user - money, product behavior, scope, risk, anything
  contractual. One focused question, with the options. Never implement before the answer.
- Decide yourself when the trade-off is technical and reversible, and say what you chose.

## Tie-breaks, in order

1. Higher `achieves the real goal` - a route that misses the goal is not a shortcut, it is a different product.
2. Less fragility - published contracts beat observed accidents.
3. More reversible - prefer the route you can exit in an afternoon.
4. Better fit - the project's existing shape is a real asset, not inertia.
5. Cheaper to operate, not cheaper to build.

If two routes still tie, that is information: they are probably the same route wearing different clothes, and
you have not generated enough diversity yet.
