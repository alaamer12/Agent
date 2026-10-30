# 11 — Attempt and escalation ladders (ordered tries with cost)

The rungs are not tests but **attempts**, ordered by preference, each with a cost, a timeout, an error
class, and an escalation policy. The outcome is "which rung answered" plus why the ones above it did not.

## Shape

**Python**

```python
@dataclass(frozen=True)
class Attempt:
    name: str
    cost: float
    timeout_ms: int
    calls: int = 1        # tries at this rung before escalating

def run_ladder(attempts, call, budget, cancelled=lambda: False):
    spent, log = 0.0, []
    for rung in attempts:
        if cancelled():
            return Outcome(None, log, "cancelled")
        for _ in range(rung.calls):
            if spent + rung.cost > budget:
                log.append((rung.name, "skipped", "budget"))
                return Outcome(None, log, "budget")
            spent += rung.cost
            try:
                return Outcome(call(rung), log, "ok")
            except Transient as e:
                log.append((rung.name, "retry", str(e)))       # stay on this rung
            except Permanent as e:
                log.append((rung.name, "abandoned", str(e)))
                break                                          # escalate
    return Outcome(None, log, "exhausted")
```

**Go** - `errors.Is` against sentinel classes decides retry-vs-escalate; the zero value is the bug, so
return a struct.

```go
for _, a := range attempts {
    res, err := a.Call(ctx)
    switch {
    case err == nil:
        return res, nil
    case errors.Is(err, ErrTransient) && a.retries > 0:
        a.retries--                       // repeat this rung
    case errors.Is(err, ErrPermanent):
        continue                          // escalate: never retry this rung
    default:
        return Result{}, fmt.Errorf("unclassified attempt error: %w", err)
    }
}
```

**Rust** - `or_else` chains are the compact form of the same idea.

```rust
a().or_else(|_| b()).or_else(|_| c()).unwrap_or_else(|e| fallback(e))
```

**TypeScript / C#** - null-coalescing is the degenerate ladder: `first() ?? second() ?? fallback()`.

## Where the compact forms stop being enough

`??` and `or_else` treat failure as a single bit. Escalation needs more:

| Need | Compact chain | Explicit ladder |
|---|---|---|
| Why rung 2 was skipped | no | yes (the log) |
| Per-rung timeout / budget | no | yes |
| Retryable vs terminal errors | no | yes |
| Cost accounting | no | yes |
| Cancellation between rungs | no | yes |
| Backoff per rung | no | yes |

Keep the compact form for cheap, side-effect-free alternatives (parse `x` as int, else float, else
give up). Reach for the explicit loop the moment an attempt costs money, time, or a user-visible retry.

## Policy knobs that must be data, not vibes

- **Order**: preference/quality vs cost vs latency. A fallback ladder ("cheapest that works") and a
  preference ladder ("best that works") are different orders of the same rungs.
- **Attempts per rung** and total attempt bound.
- **Budget**: money, tokens, wall-clock. Checked before the call, not after.
- **Escalation predicate**: which error class retries here, which escalates, which aborts the ladder.
- **Terminal rung**: the static copy, the cached value, the honest failure. A ladder that can exhaust
  without an answer is a 500 with extra steps.
- **Idempotency**: every rung must be safely re-runnable, or the ladder needs a reservation/release step.

## Failure modes

- **Retry storm**: the same rung retried by five layers at once. Bound it once, at the ladder.
- **Silent downgrade**: escalation succeeds and nobody learns the preferred rung failed. Emit the
  witness list into metrics, not only logs.
- **Timeout stacking**: each rung given the full request timeout, so worst case is N x timeout. Budget
  the deadline across rungs.
- **Fallback that lies**: serving stale data as if fresh. The outcome carries `source=rung.name` and the
  UI says so (see the `stateful` skill's `stale`/`degraded` treatment).
- **Unbounded chain**: dynamic rungs (from config) can produce a 200-attempt ladder. Cap the ladder
  length and assert it in a test.
- **Cost measured after the fact**: budget must gate the call or the guard is decorative.

## Seen in

LLM gateway routing and failover (Bifrost-style: rules choose a provider, then fallback on failure),
HTTP client retry policies, CDN/cache tiering (`L1 -> L2 -> origin -> static`), audio/video quality
ladders, payment retries across PSPs, build-system cache tiers, dependency resolvers trying versions
in order, and "escalate to a human" flows in support automation.
