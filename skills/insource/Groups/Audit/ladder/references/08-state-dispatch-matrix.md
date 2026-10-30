# 08 — State/dispatch matrix (the closed-set ladder)

When the discriminator is a **closed set** - an enum, a tagged union, a status field - a ladder over
it should be exhaustive by construction. This is the shape where the compiler, not a test, tells you
that a new state was not handled.

## Shape

**TypeScript** - `Record<Kind, Handler>` makes a missing state a type error; the `Unexpected` variant
catches values that arrive from outside the type.

```ts
type State = "idle" | "loading" | "ready" | "empty" | "partial" | "stale" | "error" | "cancelled";

const HANDLERS: Record<State, (v: View) => View> = {
  idle: (v) => v.prompt(),
  loading: (v) => v.pending(),
  ready: (v) => v.content(),
  empty: (v) => v.emptyState(),
  partial: (v) => v.content().withNotice("partial"),
  stale: (v) => v.content().withNotice("stale"),
  error: (v) => v.failure(),
  cancelled: (v) => v.idle().withReason("cancelled"),
};

function render(state: string, v: View): View {
  const h = (HANDLERS as Record<string, Handler | undefined>)[state];
  return h ? h(v) : v.unknown(state);   // unknown renders as unknown, never as the happy path
}
```

**Rust** - `match` on an enum is checked for exhaustiveness; guards add the ordered-rung behavior.

```rust
match fetch {
    Fetch::Ok(n) if n > 1000 => View::loaded_heavy(n),
    Fetch::Ok(n) => View::loaded(n),
    Fetch::Stale(0) => View::fault(),      // guard reorders the ladder inside one variant
    Fetch::Stale(n) => View::stale(n),
    Fetch::Empty => View::empty(),
    Fetch::Pending => View::pending(),
    Fetch::Cancelled => View::cancelled(),
    Fetch::Fault => View::fault(),
}
```

**Python** - no exhaustiveness check, so make the fallback explicit and enumerate in a test.

```python
HANDLERS = {"pending": show_pending, "loaded": show_loaded, "empty": show_empty,
            "stale": show_stale, "fault": show_fault, "cancelled": show_cancelled}

def render(state, view):
    handler = HANDLERS.get(state)
    return handler(view) if handler else show_unknown(view, state)

def test_handler_set_is_total():
    assert set(HANDLERS) == set(STATES), sorted(set(STATES) - set(HANDLERS))
```

**C#** - switch expressions with a discard arm; `_ =>` is the mandatory terminal rung.

```csharp
string Describe(Fetch f) => f switch
{
    Fetch.Ok(var n) when n > 1000 => "loaded-heavy",
    Fetch.Ok(_) => "loaded",
    Fetch.Stale(0) => "fault",
    Fetch.Stale(_) => "stale",
    Fetch.Empty => "empty",
    Fetch.Cancelled => "cancelled",
    _ => "unknown",
};
```

**Java** - `switch` over a sealed interface: with pattern labels the compiler flags a non-exhaustive
switch (and `-Xlint:fallthrough` keeps the C-style hole visible).

```java
String describe(Fetch f) {
    return switch (f) {
        case Fetch.Ok ok when ok.n() > 1000 -> "loaded-heavy";
        case Fetch.Ok ok -> "loaded";
        case Fetch.Stale s when s.n() == 0 -> "fault";
        case Fetch.Stale s -> "stale";
        case Fetch.Empty e -> "empty";
        case Fetch.Cancelled c -> "cancelled";
        case Fetch.Fault x -> "fault";
        case Fetch.Pending p -> "pending";
    };
}
```

**Go** - no exhaustiveness for string kinds, so the total map is the pattern and the zero value is the bug.

```go
var handlers = map[State]func(View) View{
	StateIdle: showPrompt, StateLoading: showPending, StateReady: showContent,
	StateEmpty: showEmpty, StateStale: showStale, StateError: showFailure,
}

func render(s State, v View) View {
	if h, ok := handlers[s]; ok {
		return h(v)
	}
	return showUnknown(v, s) // a zero-value State lands here: that is a bug, and now it is visible
}
```

## Pick it when

- The set of inputs is **closed and named** (statuses, event types, verdict classes, entity states).
- The decision is one lookup per value - no ranges, no cross-field conditions.
- Adding a state must break the build in every language that can check it.
- You are tempted to write an `if` chain over `status === ...`: that chain is this ladder, unenforced.

Do not pick it when the discriminator is open-ended (numbers, strings from users), when conditions
combine several fields, or when the ordering across states is a policy (that is `13`/`14`).

## Failure modes

- **Default arm that renders the happy path.** `default: return success` makes every new state look
  fine. Unknown renders as unknown, with the value in the message.
- **Zero-value ingress.** In Go/Java/C# an uninitialized enum hits `default` - so `default` must be a
  diagnosis, not a treatment.
- **Two matrices for one concept**: a status map for the UI, a status map for the log, drifting apart.
  One source, projected.
- **Matrix keyed on the wrong thing**: `state x role` tables that are really two ladders composed -
  split them before the table becomes 40 cells.
- **Stringly-typed keys**: `map[string]Handler` with a typo silently loses a rung. Bind keys to the
  enum/constants the type system knows.
- **The map is the ordering too**: if handler order matters, a map is the wrong structure - use `02`.

## Testing

A totality test that enumerates the domain (assert the key sets are equal), a distinctness assertion
when states must not collapse to the same label, and one case per handler. Where the compiler can
check exhaustiveness, prefer a compile-time test: adding a variant to the enum should fail the build.

## Seen in

UI state renderers (see the `stateful` skill's precedence ladder), event dispatch in state machines,
error-code → message maps, verdict → UI treatment in permission engines, protocol message handlers,
`Result`/`ExitCode` rendering in CLIs, and every reducer that switches on an action type.
