# Case 03 — one unsupervised decision, recorded and reported

> Worked example, invented for teaching. Shows dtb's method running inside an iwts delegation: decide the
> internal thing, record it, and stop only for the call that genuinely belongs to the user.

**The setup.** The user says *"the dashboard is unusable on our real data — take it to done, iwts."* The run
opens its ledger at `docs/decisions/states.md` (the project's docs folder) and works unsupervised; every
lasting decision gets its own file beside it.

Mid-run the objective forces a hard choice: where do the daily aggregates come from?

## The decision, worked

```text
Question    Does the dashboard compute daily totals at read time, or are they materialized as rows are written?
Context     Measured: 4.1 M event rows, 270-day window. The heaviest card takes 6.8 s; on a phone it times out
            behind the spinner. Writes are ~18 k/day, append-only (verified against the ingest path).
            Constraints: single Postgres instance, no new infrastructure agreed, the user is asleep.
Options     A read-time aggregation, add indexes
            B materialized daily totals, recomputed on write (trigger-ish path in the ingest service)
            C materialized totals + a nightly job that recomputes the last N days
            D a cache layer in front of A
Choice      B
Accepted    B gives up C's self-healing (a missed update stays missed until noticed) and A's zero schema change
Reversal    the recompute_range() adapter in aggregates.py — one file; the table and its callers stay put
Uncertainty assumed rows are never edited after the fact. Evidence: the ingest path is append-only in code,
            but a manual correction path exists in admin tooling and was not read end to end.
```

Steelman of the loser, written before choosing: *A is one migration and no write-path risk.* It fails on the
measured number: an index helps a `GROUP BY` on a bounded window, not on 4.1 M rows over 270 days at phone
latency — and A's cost is paid by every visitor on every load, while B's is paid once per write.

Why **not D**: a cache over a slow correct answer hides the problem and adds a staleness question the user never
asked about — complexity not paid for by a present requirement.

Why **not C**: it is B plus an operation someone must own, on a project with no job runner and nobody awake to
agree to run one. Rejected as unearned operational cost, and recorded as the fix if the append-only assumption
turns out to be wrong.

**Kept the seam anyway**, because the uncertainty is real: `recompute_range(days)` already exists as the single
entry point that C would need. If the admin-correction path turns out to edit history, switching to C touches
that function and a scheduler, not the dashboard.

## What was *not* decided alone

Backfilling 270 days of history is a 5–7 hour table scan on the production instance, and the run had to choose:

- it **did** build the aggregate table, the write path, and the query swap on a staging copy;
- it **did not** start the production backfill. That is significant cost and an externally visible consequence
  on a live database — a user-owned call under iwts's stop conditions, not an implementation detail.

`docs/decisions/states.md` at the moment autonomy stopped:

```markdown
# iwts state — objective: dashboard usable on real data · updated 2026-10-28 · commit 8f2c1ab · app 1.4.2
status: blocked-on-user (start the 270-day production backfill? ~5-7 h scan on the main instance, or accept
  aggregates from today forward and let history fill in over time)
remaining: [x] aggregate table + write path · [x] dashboard reads aggregates · [x] staging backfill + timing
            · [~] production backfill (needs go) · [ ] the two slowest cards need a per-day breakdown drill-in
decisions: read-time vs materialized totals -> materialized, recomputed on write - aggregation-at-write.md;
            decided-not-asked: staging backfill run without go (read-only cost) - see same record
uncertainties: append-only assumption not verified through the admin correction path; if wrong, add the nightly
               recompute (option C) — reversal is one function, see the record
findings: the export path still reads raw events (fine today, slow at 10 M) — parked, not started
```

The record itself, `docs/decisions/aggregation-at-write.md` - anchored Date 2026-10-28 · Commit 8f2c1ab ·
App-Version 1.4.2 (unchanged since the previous record) - is the shared template
([`../../iwts/assets/decision-record-template.md`](../../iwts/assets/decision-record-template.md)) filled with
exactly the six blocks above — and note that its first line is the **question**, not the answer. A successor who
finds "totals are materialized" with no question cannot re-decide anything; they can only obey it.

## Handover

The record was written where it lives: `docs/decisions/aggregation-at-write.md`, committed with the code it
explains - thin modes, one destination, no staging folder and no later move. The ask-decision (backfill waits
for the user) is stated in the same file.

One line to the user when they woke:

> Dashboard cards now read materialized daily totals instead of scanning 4.1 M events: heaviest card 6.8 s →
> 90 ms, and mobile no longer times out. Cost: writes now maintain an aggregate row, and history is only
> correct from the backfill point unless we schedule a recompute. Reversal: `recompute_range()` in one file.
> **One question waiting:** run the 270-day production backfill (~5–7 h scan) or start aggregates from today?

Two things that did **not** happen: no redesign of any card, and no question asked about whether to add a table,
an index, or a column — all invisible, all delegated, all recorded.
