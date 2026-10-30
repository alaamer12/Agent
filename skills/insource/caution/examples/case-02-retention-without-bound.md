# Case 02 — "Keep every event forever, we have space"

> No attacker anywhere in this case. The consequence is arithmetic: a rate with no ceiling, a backup window, and
> a deletion duty that nobody planned for.

## The setting

A notes product logs every sync operation, payload included, "so we can debug later". The question was whether
to add pruning. The answer:

> "Keep everything, storage is cheap. We have space."

## Screen

| Question | Reading |
|---|---|
| protection declined? | yes — the retention limit and the purge path are declined |
| unbounded growth? | yes, a rate with no ceiling, already accumulating |
| irreversible? | partially — you can stop growing, but a year of payloads is already written, and deleting it later is a migration |
| outward-facing? | the data itself is internal; the obligation to delete it is not |
| knowledge test | **fails**: "storage is cheap" is a cost claim, and it is wrong at this rate — the expensive parts are the backup window, restore time, and deletion |

Grade: **DANGER** — growth is already running, no ceiling, and the answer shows a cost estimate that does not
survive the arithmetic.

## The card

```text
!! DANGER — "keep everything, storage is cheap"
What is gone: the retention bound and the purge path — nothing will ever leave this table automatically
How it fails: at 300k events/day × ~1.8 KB (payload included) the table grows ~540 MB/day ≈ 200 GB/year raw,
             ~275 GB/year with indexes. The nightly backup is 3 h for 120 GB today; it stops completing before
             the year ends. And a deletion request means scanning every payload ever written.
If it happens: "The events table reached 1.1 TB, the nightly backup silently exceeded its window for three
                weeks, and the restore test failed on the first real request; three days of events were lost
                when the disk filled."
Blast radius: one growing table → backup SLA, restore time, restore cost, and every user-deletion request
Undo cost: now — one scheduled purge + exclude payloads. Later — a multi-day migration, a backup redesign,
           and the historical payloads stay until deleted
Cheapest adequate option: 90-day retention for payloads, keep metadata for a year; exclude the export path's
           payloads entirely
```

> **Are you sure?** Reply "yes, accept the risk" to proceed — or set the window you actually need and we move on.

## Why this is DANGER and not WARN

Growth with a known rate and a date is cheap to fix **now** (one job, one column excluded) and expensive later
(a migration on a terabyte table plus a restore redesign). The severity matrix grades on the *undo cost curve*,
and this curve bends fast: the first pain date is inside the year, and the answer's own justification ("we have
space") is the part that is wrong. When the user is right about the cost — "we keep 3 months, it fits the
backup" — the same topic is a NOTE.

## Outcome

> "ok, 90 days of payloads is fine, keep the counters."

Then: the purge job lands with the feature, the payload column is dropped from the export path, and the
conversation closes with one line:

> Accepted — payloads 90 days, counters kept, purge job in the same release.

The residual 90-day window was the user's own limit, so it is not a new cost to disclose. The card's job ended
when the answer changed; nothing is written to a file, and the implementation details stay in the implementation.

## The variants this case is here to separate

| Answer | Grade | Why |
|---|---|---|
| "keep everything forever, storage is cheap" | DANGER | no ceiling, wrong cost model |
| "keep everything forever, we accept the restore-time growth" | NOTE | informed; the answer itself names the cost |
| "keep 30 days, that's the compliance window" | CLEAR | policy-bounded, informed |
| "add a cap later if it gets big" | WARN | recoverable, but the pile keeps growing until then; mention the first-pain size once |

## What this case teaches

1. **Inflation needs no attacker.** A rate × time is enough; the card's job is to put a date on the growth.
2. **Undo cost, not drama, sets the grade.** One job now versus a migration later.
3. **A wrong cost estimate is a knowledge gap.** "Cheap" is a claim about bytes, not about backups, restores, and
   deletions.
4. **The user often chooses a bounded version of exactly what they said.** The card made the bound visible; the
   answer got better without anyone arguing about the product.
