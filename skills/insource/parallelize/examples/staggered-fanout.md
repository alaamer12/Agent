# Worked example — staggered fan-out against a shared rate limit

**Job:** add four provider adapters to a service. Each adapter has its own client code and tests, but every test
suite hits **one shared sandbox** that allows a handful of requests per second and locks out on a burst.
Language-agnostic; the scheduling shape is what matters.

## The plan stated in chat

```markdown
## Fan-out plan — adapters for providers A–D

**Why parallel:** four adapters, four disjoint folders, one adapter contract. Written together they finish in the
time of the slowest; written serially they take four times as long.
**Snapshot:** main branch at <commit>; adapter contract frozen in step 0.

| # | Slice | Output | Owns | Depends on | Risk | Wave |
|---|-------|--------|------|------------|------|------|
| 0 | adapter contract + shared HTTP client with token bucket | `adapters/contract.*`, `adapters/http.*` | these paths | — | high | main, before wave 1 |
| 1 | provider A adapter + tests | `adapters/a/` | that folder | 0 | med | 1 |
| 2 | provider B adapter + tests | `adapters/b/` | that folder | 0 | med | 1 |
| 3 | provider C adapter + tests | `adapters/c/` | that folder | 0 | med | 1 |
| 4 | provider D adapter + tests | `adapters/d/` | that folder | 0 | low | 1 |
| 5 | shared retry policy + sandbox cleanup harness | shared paths | shared paths | 0 | high | main, during wave 1 |

**Main agent keeps:** the contract and HTTP client (0), the shared retry/cleanup work (5), final integration.
**Waves:** wave 1 = slices 1–4 + main's slice 5.
**Stagger:** `each 0/15/30/45 + main 60` — the sandbox rate limit is per second and shared, not per agent.
**Verification:** each slice runs its own adapter suite against the sandbox; main runs the full suite plus a
rate-limit stress check.
**Out of scope:** adding a fifth provider, caching, client UI.
```

Because the plan is staggered, the schedule is stated with it:

```markdown
| Agent | Wave | Delay | Wave-relative start | Why |
|---|---|---|---|---|
| Main | 1 (own slice) | 60s | 1:00 | Its retry harness also hits the sandbox |
| W1 (A) | 1 | 0s | 0:00 | First starter; probes the limit |
| W2 (B) | 1 | 15s | 0:15 | Same sandbox |
| W3 (C) | 1 | 30s | 0:30 | Same sandbox |
| W4 (D) | 1 | 45s | 0:45 | Same sandbox |
```

## What happened

1. **Before the wave**, the main writes the adapter contract and the token-bucket client, with unit tests that do
   not touch the sandbox. Pre-wave work is never delayed — it is what lets the wave start.
2. **Wave 1 launches all four slices.** Slice 3's brief opens with its sleep line (W1 gets no block):

   ```
   SCHEDULE: sleep 30s before doing anything else. Do not read, write, or run project commands
   before the sleep completes. After it, re-read the files you own; the tree may have changed.
   ```

   and still carries the contract verbatim, its owned folder, and the do-not-touch list.
3. **The main waits 60s before touching its own slice**, but answers subagent questions during that minute and
   watches the first results. The delay governs file work, not conversation.
4. **Slice 3 starts at 0:30 and still hits the sandbox limit.** It does not retry blindly: the brief told it to
   surface a rate-limit block as a blocked slice. The main has it hold until the bucket refills, records the real
   capacity, and leaves the schedule alone — the burst was a fixed limit, not a scheduling mistake.
5. **Slice 4 finishes early** and offers to write provider C's schema mapper to unblock it. Refused: C's folder is
   not slice 4's to write. The main re-briefs C alone instead.
6. **Slice 1's output turned out to be a dependency of slice 3**, not just a sibling: C needs A's pagination
   shape. The 30s delay never solved that — a delay is a floor, not an authorization. The main moves C to a
   second one-slice wave after A lands; since the spec applies per wave, that wave has one member and starts at 0.
7. **Integration:** main merges in dependency order (contract → A → B/D → C), writes the shared retry policy once,
   and runs the stress check that fires requests above the limit on purpose.

## The report

> Ran 4 adapter slices in one staggered wave (`each 0/15/30/45 + main 60`) against a shared sandbox. Main wrote
> the contract and HTTP client before launch and its own retry harness after a 60s delay. Slice 3 was re-run alone
> in wave 2 because it consumed slice 1's pagination shape — a real dependency the stagger could not remove. All
> suites and the rate-limit stress check pass. Wall-clock cost of the stagger: about 45s on the last starter.

## Why it worked

- The stagger protected one shared resource; it was not used to fake ordering between slices.
- Delays were absolute sleeps before any read or write, and every delayed brief said so.
- The main delay applied only to the main's own slice; pre-wave interfaces and wave launch were immediate.
- The real dependency (C on A) was fixed by a wave, not by a longer sleep.
- Ownership held under pressure: the fast slice was refused C's folder and the main absorbed the re-run.
