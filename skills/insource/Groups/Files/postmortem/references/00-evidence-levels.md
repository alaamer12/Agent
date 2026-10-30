# Evidence levels — V0 to V5

The single number that stops a postmortem from lying. Claim the level the evidence supports, then say why not
higher. "Verified" without a level is an opinion.

| Level | Name | What must exist | What it still does **not** prove |
|---|---|---|---|
| **V5** | Proven by construction | The failure mode is impossible in the new code — e.g. the resource is no longer shared, the unbounded loop is bounded by type, the state cannot exist. Plus a test that would crash if it did. | Nothing about the rest of the system; you removed the class, not all classes |
| **V4** | Deterministic reproduction | A reproducer that failed **before** and does not fail **after**, same input, same environment, N ≥ 20 runs each way (or a loop of 1000 iterations) | Behavior on other inputs, other environments, other timings |
| **V3** | Statistical verification | The fix was exercised enough for a confidence statement: e.g. 3 × MTBF of soak, or N instances × T hours, or 10 k requests at the failing rate — with the arithmetic shown | Rarer variants of the same bug; conditions outside the tested distribution |
| **V2** | Fault injection / simulation | The specific mechanism was forced (clock skew, kill the connection, inject the delay, exhaust the pool) and the system now behaves correctly under the same injection | That the mechanism occurs in production at that rate |
| **V1** | Indirect evidence | Logs, metrics, traces or code reading show the path is taken and now produces the right result — but nothing reproduced the failure | Causality; correlation is doing the work |
| **V0** | Heuristic / unverified | A plausible fix, a reading of the code, "should work", a field report that stopped | Anything. This is a hypothesis with a commit |

## Writing the claim

```text
Achieved: V3 — statistical verification.
Why not V4: the failure depended on a state that the harness cannot create deterministically
            (the race needs two real requests in the same millisecond); forcing it would change the code
            under test. We ran 6 instances × 18 h = 108 instance-hours against an MTBF estimate of 31 h,
            which is 3.5 × MTBF ≈ 97% confidence of catching a repeat (e^(-3.5) ≈ 3%).
Why not V5: the shared timer still exists; it is now reset on reconnect, which corrects the state rather
            than preventing the overlap.
```

Rules:

- **N is always stated.** "Extensively tested" is V0 wearing a suit.
- **The failing direction is shown.** A test that never failed on the old code demonstrates nothing about
  this bug — it may be testing something else.
- **A level applies to a claim, not to the whole document.** Different sections may be at different levels:
  the root cause may be V5 (proven by the reproducer) while "does not recur under production load" is V3.
- **Downgrade when unsure.** A V3 claim that is really V1 is worse than an honest V1, because the next
  incident will be planned against it.
- **Never use the level to close the section.** After the level comes the watch period and the re-open
  criteria ([`01-rare-bug-verification.md`](01-rare-bug-verification.md)).

## Common overclaims, and the honest rewrite

| Written | Reality | Rewrite |
|---|---|---|
| "Fixed" | code merged, never run against the old failure | "Fix merged at `<sha>`; V0 until the reproducer in `verification/` runs green (tracked A1)" |
| "Tested thoroughly" | one manual pass | "V1: manual pass on 3 screens; automated regression pending" |
| "Cannot happen anymore" | the trigger was narrowed | "V5 for the triggering path; the underlying invariant is still unguarded (§16 A2)" |
| "Monitored, so we would know" | an alert exists that never fired during the incident | "Alert `<name>` exists and did not fire; detection analysis §17 explains why" |
| "Root cause confirmed" | the most plausible of three theories | "Strongly supported, not proven: theory B is still consistent with the logs (§9)" |

## Where the level is used elsewhere

- §13 states the level and the arithmetic.
- §14's verification table is the evidence for it — each row should map to a level.
- §15 is the level's justification when the answer is "cannot fully verify".
- §16 must contain an action that would raise the level next time (usually the regression test or the alert).
