# 10 — Chain of responsibility (the ladder spread across owners)

Each rung is an object that either answers or passes the request along. The ladder's order becomes the
chain's composition order, and each rung can own its own dependencies, config, and tests.

## Shape

**Python**

```python
class Rung:
    name: str
    def handle(self, c: Call) -> Outcome | None: ...

def evaluate(chain: list[Rung], c: Call) -> Outcome:
    for r in chain:
        if (hit := r.handle(c)) is not None:
            return hit
    raise NoTerminalRung(chain)          # total, or loudly broken - never None
```

**Java**

```java
interface Rung { String name(); Optional<Outcome> handle(Call c); }

static Outcome evaluate(List<Rung> chain, Call c) {
    for (Rung r : chain) {
        Optional<Outcome> hit = r.handle(c);
        if (hit.isPresent()) return hit.get();
    }
    throw new IllegalStateException("chain has no terminal rung: " + c);
}
```

**Go** - the standard middleware idiom, where the chain is built by wrapping, not by listing.

```go
type Handler func(next Handler, c Call) Outcome

func Chain(hs ...Handler) Handler {
    return func(next Handler, c Call) Outcome {
        for i := len(hs) - 1; i >= 0; i-- {
            next = func(n Handler, cc Call) Outcome { return hs[i](n, cc) }   // composition order
        }
        return next(terminal, c)
    }
}
```

**Elixir** - a pipeline where each stage may short-circuit with `{:halt, outcome}`.

```elixir
Enum.reduce_while(chain, call, fn rung, c ->
  case rung.handle(c) do
    {:halt, outcome} -> {:halt, outcome}
    {:cont, next} -> {:cont, next}
  end
end)
```

## What changes when the ladder is an object graph

| Concern | Consequence |
|---|---|
| Ownership | each rung has a different author, so **composition order is a review surface** |
| State | a rung may memoize or mutate; matching stops being replayable unless you forbid it |
| Failure | a rung raising is different from a rung declining: decline means "not mine", raise means "I tried" |
| Termination | cycles are possible (A delegates to B, B to A) - bound it |
| Audit | the winner's name is available only if every rung is named |

## Pick it when

- Rungs have heavy, distinct dependencies (a risk service, a quota store, a model call) and one shared
  request type.
- Different teams own different rungs and must add one without editing the previous.
- The order is assembled per deployment (plugins, middleware stacks) rather than fixed in a file.
- Declining is cheap and handling is expensive - which is exactly what a chain optimizes.

Do not pick it when the rules are simple predicates over one value (use `02`/`07`), when the order must
be a reviewed list in one file, or when you need "all matches" semantics - chains short-circuit by
nature.

## Failure modes

1. **The wiring is the policy, and nobody reviews the wiring.** Print the composed chain at startup and
   assert its order in a test; a rung that never fires is otherwise invisible.
2. **Unreachable rungs.** Probe them:

```python
def unreachable(chain, probes):
    dead = []
    for target in chain:
        reachable = any(
            not any(b.handle(c) for b in chain[:chain.index(target)]) and target.handle(c)
            for c in probes)
        if not reachable:
            dead.append(target.name)
    return dead
```

3. **Side effects before decline.** A rung that reserves capacity, logs a decision, or writes a row and
   then declines has changed the world for a request it did not answer. Split "does this match?" from
   "do the work", and only the answerer acts.
4. **No terminal rung.** The chain returns `None` and the caller treats it as falsy-but-fine. Force the
   terminal rung structurally: build the chain with `chain_of(*rungs, terminal=...)`.
5. **Cycles.** A delegated-to rung delegates back. Keep a visited set of rung names plus a depth limit,
   and report the limit as an outcome, not an exception.
6. **Order-by-accident** in DI containers: registration order becomes ladder order. Make registration
   order explicit (an ordered list, a `Step` interface with `priority`) rather than discovered.

## Seen in

HTTP middleware and framework filters, message-bus handlers, GUI event bubbling, logging filters, IDE
quick-fix providers, agent tool-permission pipelines, Drools agenda groups (`setFocus` chooses which
rule set is consulted first - an explicit scope chain), and the GoF pattern this is named after.
