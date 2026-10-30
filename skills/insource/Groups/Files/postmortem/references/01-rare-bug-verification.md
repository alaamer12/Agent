# Rare and untestable bugs

When the failure is a once-per-100-hours event, "run it once and see" is not verification — it is a coin flip
that lands on "nothing happened". This file is the arithmetic that makes an honest rare-bug claim possible.

## The two numbers you need

**MTBF** (mean time between failures) — how often it fails *while it is running*:

```text
MTBF ≈ (total instance-hours observed) / (number of failures observed)
```

If the failure occurred once in 900 instance-hours across the fleet, MTBF ≈ 900 h. If it occurred 3 times in
900 h, MTBF ≈ 300 h. Use production data first; a lab estimate must say how it was derived.

**Soak duration** for a confidence target:

```text
P(no failure in T) = e^(−T / MTBF)          →  T = MTBF × ln(1 / (1 − confidence))
```

| Target confidence | Multiplier | Example with MTBF = 30 h |
|---|---|---|
| 63% | 1 × MTBF | 30 h |
| **95%** | **≈ 3 × MTBF** | **90 h** |
| 99% | ≈ 4.6 × MTBF | 138 h |

`3 × MTBF ≈ 95%` is the rule of thumb: if the bug would have appeared at its normal rate and nothing happened
for three full MTBFs, the fix very likely removed it. It is **not** proof — a fix that halves the rate needs
far more time to detect (see below).

**Instance-hours add up.** Ten parallel instances for 9 hours is 90 instance-hours — the same evidence as one
instance for 90 hours, and usually the only practical way to get there. Say the arithmetic explicitly:
`12 instances × 8 h = 96 instance-hours ≈ 3.2 × MTBF ≈ 96% confidence`.

## Rule of three

Zero failures in `n` instance-hours gives a 95% upper bound on the failure rate of about `3 / n`
(per instance-hour). 300 clean instance-hours → "with 95% confidence, the failure rate is below 1 in 100
instance-hours". Useful when there is no reliable MTBF to begin with.

## When you cannot run long enough

Choose acceleration techniques that preserve the mechanism, and say what each one distorts:

| Technique | Preserves | Distorts |
|---|---|---|
| Fault injection (kill connection, return 5xx, drop packets) | error paths, retries, recovery | timing distribution, load shape |
| Clock skew / time travel (libfaketime, mocked clock, `TZ` shifts) | TTL, expiry, scheduling, ordering | anything that reads real elapsed time |
| Timer shortening (`--interval 1ms` test build, feature-configured intervals) | the ordering/overlap that causes the race | CPU-relative behaviour, real scheduling pressure |
| Stress (connection churn, pool exhaustion, high concurrency) | contention, leaks under load | per-request latency, fairness |
| Replay of captured production traffic | real input distribution | the original timing and concurrency interleaving |

If none is safe, say so; that is a finding for §15, not a reason to fake a number.

## What to write when it cannot be verified

Allowed and expected:

```text
This fix cannot be fully verified. Mechanism: a timer reset across reconnects; the overlap needs two clients
reconnecting in the same millisecond. Forcing it deterministically would require changing the code under test,
which changes what is being tested (the V4 gap).

Evidence we do have:
- V2: injected 1,000 reconnect pairs with 0-2 ms offsets; overlap reproduced 11% of the time on the old build,
  0 times on the new one.
- V3: 14 instances × 9.5 h = 133 instance-hours against an MTBF estimate of 41 h (3.2 × MTBF, ≈ 96%).
- Production watch: 14 days with alert `sync_reconnect_overlap_total > 0` — silent.
Residual risk: the shared timer still exists (not V5); a third reconnect path added later would bypass the
reset. Action A3 adds a guard + test.
Re-open if: `sync_reconnect_overlap_total > 0`, or any crash signature matching `evidence/crash-*.dmp`.
```

Forbidden: "verified" with no N, "should be fine now", deleting the section because it is uncomfortable.

## Watch period and re-open criteria

The fix is not finished when it ships; it is finished when the watch window closes clean. Define both **before**
deploying:

- **Watch duration:** ≥ 3 × MTBF where the alert exists, otherwise ≥ 2 weeks and say the limit.
- **Exact alert/query:** the string someone can paste — `sum(rate(sync_reconnect_overlap_total[5m])) > 0`.
- **Re-open criteria:** the observable that means "the diagnosis was wrong" — the same crash signature, the
  same log line, the same metric moving, or a user report matching §5's reproduction steps.

## Common arithmetic mistakes

- Dividing hours by *workers* instead of counting instance-hours (10 workers × 1 h ≠ 1 h).
- Using wall-clock duration of the test campaign instead of running time (a 3-day campaign with 2 h of actual
  execution is 2 h).
- Treating 3 × MTBF as proof of removal when the fix only reduces the rate — for a rate cut you need to say
  which rate you are now claiming, and the soak only bounds the *old* rate.
- Computing MTBF from the incident's own uptime ("it ran 3 days before failing") — one sample is not a mean.
