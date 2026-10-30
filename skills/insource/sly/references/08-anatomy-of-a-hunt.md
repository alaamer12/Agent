# Anatomy of a hunt - the domain-neutral spine

The concrete cases live in `../examples/` so this file can stay abstract on purpose: nothing here should make
a future hunt think it already knows the shape of its problem. Read this when a hunt is going badly and you
need to find which step you skipped.

## The spine, and what each step is for

```text
ask  ->  class  ->  goal/value/test  ->  prove the block  ->  families  ->  parity gate  ->
score  ->  choose or ask  ->  verify the value landed  ->  record
  |        |             |                    |                |            |          |
  |        |             |                    |                |            |           wrong route chosen because
  |        |             |                    |                |             |           clever beat fit
  |        |             |                    |                |             a breach route
  |        |             |                    |                |             still in the ranking
  |        |             |                    |                routes all one family
  |        |             |                    workaround designed for a block that was never real
  |        |             still naming the blocked thing in the goal
  |        effort mis-set: afternoon on a snag, two minutes on a blocker
```

## The eight ways a hunt goes wrong

Each is a check, not a moral. `scripts/routes.py` enforces the ones with mechanical shapes.

| # | Failure | Detected by | Repair |
|---|---|---|---|
| 1 | Goal never separated from method - the hunt optimizes for restoring access instead of delivering value | goal-drift: the goal text still names the blocked thing | rewrite the goal line in the user's language ([`01`](01-goal-and-value-extraction.md)) |
| 2 | Block taken on faith after one failure | block: not verified, fewer than two evidence signals | work the false-block catalog ([`02`](02-verifying-the-block.md)) |
| 3 | Options that are one option in costumes | diversity: fewer than three routes, or all in one family | force a second family before scoring ([`00`](00-route-families.md)) |
| 4 | A parity breach surviving to the ranking because it scored highest | parity: vetoed, excluded | gate before scoring, always ([`04`](04-access-parity.md)) |
| 5 | Same method retried with cosmetic parameter changes | repeat: matching target and mechanism | two strikes, then switch family |
| 6 | Route chosen on ingenuity, or picked without any axis scored | unscored: missing axes | score all eight, recommend one ([`05`](05-scoring-and-tradeoffs.md)) |
| 7 | Undocumented dependency presented as solid | fragile: no detection note | state what breaks it and how you'll notice |
| 8 | Feature looks alive but the value never arrived | only visible at the end, which is why the test exists | run the acceptance test and report the number |

## The three checks that catch most bad hunts

Ask them in this order, at any step, and they cost seconds:

1. **Could I state the goal without the blocked thing in it?** If not, stop generating routes and fix the
   framing. Everything downstream inherits this error.
2. **Do I have two independent signals that this is blocked?** If not, keep reading rather than routing.
3. **Would an ordinary user of that system have received this?** If not, the route is not a route.

## Where the effort actually goes

Experienced agents put work in the wrong place in a predictable way: hours on implementation detail for a
route that dies at the parity gate, or hours on route generation when the block was a wrong parameter. The
timeboxes in [`06`](06-effort-scaling-and-stop-rules.md) exist to force the cheap steps first - classify,
prove, frame - because they are the steps that can cancel the expensive one.

## What a finished hunt leaves behind

A route that was chosen for reasons someone else can check, a record of the alternatives and the trade-offs,
an acceptance number that proves the value landed, a named fragile spot with a detection mechanism, and a
re-check condition for the day the block disappears. If any of those five is missing, the hunt is not
finished - it is merely paused.
