# Walkthrough — one derivation, six stacks, five platforms

Comparative material only. Read it when you need the resolver *shape* in the stack in front of you,
or when the target isn't a web screen and you're unsure which states survive.

The screen under test, deliberately boring: **a list the viewer opens, refreshes, and can add to.**
Reads a provider, keeps a local cache, has one write.

---

## 1. The condition value — naive vs hardened

Six stacks, chosen to span the paradigm quadrants rather than to give six flavours of the same one:
systems-compiled (Go, Rust), managed (TypeScript, C#), dynamic-functional (Elixir), dynamic-scripted
(Python). Same eight variants, same precedence, same guarantee — only the mechanism that enforces it differs.

### TypeScript (managed, structural, discriminated unions)

```ts
// BEFORE — representable nonsense: 8 combinations, 1 considered
const loading = ref(false), error = ref<string | null>(null), items = ref<Item[]>([])
const show = computed(() => !loading.value && !error.value && items.value.length > 0)

// AFTER — impossible states are unrepresentable; the else branch is a named state
type Outcome = 'unreachable' | 'timed-out' | 'provider' | 'refused' | 'absent' | 'integrity'
type Condition =
  | { kind: 'blocked'; why: 'incompatible' | 'maintenance' | 'incident' }
  | { kind: 'gate'; why: 'signed-out' | 'expired' | 'entitlement' | 'consent' }
  | { kind: 'failed'; outcome: Outcome; retryable: boolean; correlationId: string }
  | { kind: 'unexpected'; what: string }                       // ← the mandatory else
  | { kind: 'pending'; stage: 'first' | 'retry'; elapsedMs: number }
  | { kind: 'empty'; why: 'never' | 'filtered' | 'unreachable' }
  | { kind: 'loaded'; items: Item[]; freshness: 'current' | 'stale' | 'refreshing' }
  | { kind: 'partial'; ok: Region[]; failed: Region[] }

function assertNever(c: never): never {
  throw new Error(`unhandled screen state: ${String(c)}`)      // never log payloads
}

function render(c: Condition) {
  switch (c.kind) {
    case 'pending':   return c.stage === 'first' ? placeholder() : keepWithBusy(c.elapsedMs)
    case 'empty':     return c.why === 'unreachable' ? noConnection() : emptyFor(c.why)
    case 'failed':    return c.outcome === 'refused' ? gate() : retryable(c)   // never a retry loop
    case 'unexpected':return unknownState(c.what)               // fail closed, disclose nothing
    case 'loaded':    return list(c.items, c.freshness)
    case 'partial':   return regions(c)
    case 'blocked':   return takeover(c.why)
    case 'gate':      return gate(c.why)
    default:          return assertNever(c)                     // compile error if a variant is missed
  }
}
```

### C# (managed, nominal, OO — a visitor interface carries the exhaustiveness check)

```csharp
// BEFORE — three flags reconciled at render time; the false-empty is one of the unconsidered combinations
if (IsLoading) ShowSpinner();
else if (Error is not null) ShowError();
else if (Items.Count == 0) ShowEmpty();      // offline-with-no-cache lands here
else ShowList(Items);

// AFTER — closed record hierarchy. C# cannot check a switch over a type hierarchy,
// so the guarantee moves into the visitor interface: one method per variant.
abstract record Condition
{
    public abstract T Accept<T>(IConditionVisitor<T> visitor);

    public sealed record Blocked(BlockedWhy Why) : Condition
    { public override T Accept<T>(IConditionVisitor<T> v) => v.Visit(this); }

    public sealed record Unexpected(string What) : Condition      // ← the mandatory else
    { public override T Accept<T>(IConditionVisitor<T> v) => v.Visit(this); }

    public sealed record Empty(EmptyWhy Why) : Condition
    { public override T Accept<T>(IConditionVisitor<T> v) => v.Visit(this); }

    public sealed record Failed(Outcome Result, bool Retryable, string CorrelationId) : Condition
    { public override T Accept<T>(IConditionVisitor<T> v) => v.Visit(this); }

    // …Pending, Gate, Loaded, Partial — each with the same one-line Accept
}

interface IConditionVisitor<out T>
{
    T Visit(Condition.Blocked c);     T Visit(Condition.Unexpected c);  T Visit(Condition.Empty c);
    T Visit(Condition.Failed c);      T Visit(Condition.Pending c);     T Visit(Condition.Gate c);
    T Visit(Condition.Loaded c);      T Visit(Condition.Partial c);
}

sealed class ScreenRenderer : IConditionVisitor<string>
{
    public string Visit(Condition.Empty c)      => c.Why == EmptyWhy.Unreachable ? NoConnection() : EmptyFor(c.Why);
    public string Visit(Condition.Failed c)     => c.Result == Outcome.Refused ? Gate()
                                                : c.Retryable ? Retry(c.CorrelationId) : HardFailure();
    public string Visit(Condition.Unexpected c) => UnknownState(c.What);   // fail closed, disclose nothing
    // …remaining arms: the interface makes omitting one a compile error, everywhere at once
}
```

Add a variant to `Condition` without adding it to `IConditionVisitor<T>`, and every renderer in the
solution breaks the build. The OO stack buys the same property the match buys, for slightly more ceremony —
and unlike the reflection trick people reach for, it is checked at compile time rather than at test time.

### Go (compiled, explicit, no sum types — an interface makes the set closed)

```go
// BEFORE — three booleans; "err != nil && len(items) > 0" silently drops the user's data
if err != nil { view.showError() } else if len(items) == 0 { view.showEmpty() } else { view.showList(items) }

// AFTER — private marker method seals the set outside this package
type Condition interface{ isCondition() }

type Blocked struct{ Why string }
type Failed struct{ Outcome string; Retryable bool; CorrelationID string }
type Unexpected struct{ What string }
type Pending struct{ Stage string; Elapsed time.Duration }
type Empty struct{ Why string }
type Loaded struct{ Items []Item; Freshness string }

func (Blocked) isCondition()    {}
func (Failed) isCondition()     {}
func (Unexpected) isCondition() {}
func (Pending) isCondition()    {}
func (Empty) isCondition()      {}
func (Loaded) isCondition()     {}

func (v *View) Render(c Condition) {
    switch c := c.(type) {
    case Pending:    if c.Stage == "first" { v.placeholder() } else { v.keepWithBusy(c.Elapsed) }
    case Empty:      if c.Why == "unreachable" { v.noConnection() } else { v.emptyFor(c.Why) }
    case Failed:     if c.Outcome == "refused" { v.gate() } else { v.retryable(c) }
    case Unexpected: v.unknownState(c.What)          // fail closed; log What, never the payload
    case Loaded:     v.list(c.Items, c.Freshness)
    case Blocked:    v.takeover(c.Why)
    default:         v.unknownState(fmt.Sprintf("%T", c)) // a new variant can't be forgotten silently
    }
}
```

### Rust (compiled, ownership, compiler-enforced exhaustiveness)

```rust
// BEFORE — Option<Vec<Item>> + bool + bool: four states spelled, six exist
if !loading && error.is_none() && !items.is_empty() { render(&items) }

// AFTER — the enum IS the state machine; a missed arm is a build failure
enum Condition {
    Blocked { why: BlockedWhy },
    Gate { why: GateWhy },
    Failed { outcome: Outcome, retryable: bool, correlation_id: CorrelationId },
    Unexpected { what: &'static str },
    Pending { stage: Stage, elapsed: Duration },
    Empty { why: EmptyWhy },
    Loaded { items: Vec<Item>, freshness: Freshness },
    Partial { ok: Vec<Region>, failed: Vec<Region> },
}

fn render(c: &Condition, v: &mut View) {
    match c {
        Condition::Pending { stage: Stage::First, .. }        => v.placeholder(),
        Condition::Pending { elapsed, .. }                     => v.keep_with_busy(elapsed),
        Condition::Empty { why: EmptyWhy::Unreachable }        => v.no_connection(),
        Condition::Empty { why }                               => v.empty_for(why),
        Condition::Failed { outcome: Outcome::Refused, .. }    => v.gate(),
        Condition::Failed { retryable: true, correlation_id, .. } => v.retry(correlation_id),
        Condition::Failed { .. }                               => v.hard_failure(),
        Condition::Unexpected { what }                         => v.unknown_state(what), // fail closed
        Condition::Loaded { items, freshness }                 => v.list(items, freshness),
        Condition::Partial { ok, failed }                      => v.regions(ok, failed),
        Condition::Blocked { why }                             => v.takeover(why),
        Condition::Gate { why }                                => v.gate_for(why),
    }   // ← no `_ =>` arm: a variant added to the enum breaks the build until it is handled
}
```

### Python (dynamic, dataclasses, `match` with no static exhaustiveness — so assert it)

```python
# BEFORE
if loading: show_spinner()
elif error: show_error()
elif not items: show_empty()          # unreachable-with-no-cache reaches here: the false-empty
else: show_list(items)

# AFTER
@dataclass(frozen=True)
class Blocked:    why: str
@dataclass(frozen=True)
class Gate:       why: str
@dataclass(frozen=True)
class Pending:    stage: str; elapsed: float
@dataclass(frozen=True)
class Empty:      why: str
@dataclass(frozen=True)
class Failed:     outcome: str; retryable: bool; correlation_id: str
@dataclass(frozen=True)
class Unexpected: what: str
@dataclass(frozen=True)
class Loaded:     items: Sequence[Item]; freshness: str
@dataclass(frozen=True)
class Partial:    ok: Sequence[Region]; failed: Sequence[Region]

Condition = Blocked | Gate | Failed | Unexpected | Pending | Empty | Loaded | Partial

def render(c: Condition, v: View) -> None:
    match c:
        case Pending(stage="first"):                      v.placeholder()
        case Pending(elapsed=e):                          v.keep_with_busy(e)
        case Empty(why="unreachable"):                    v.no_connection()
        case Empty(why=w):                                v.empty_for(w)
        case Failed(outcome="refused"):                   v.gate()
        case Failed(retryable=True, correlation_id=i):     v.retry(i)
        case Failed():                                    v.hard_failure()
        case Unexpected(what=w):                          v.unknown_state(w)  # never a default fallthrough
        case Loaded(items=items, freshness=f):            v.list(items, f)
        case Partial(ok=ok, failed=failed):               v.regions(ok, failed)
        case Blocked(why=w):                              v.takeover(w)
        case Gate(why=w):                                 v.gate_for(w)
        case other:
            # No compiler here: assert loudly in every debug build, fail closed in shipped ones.
            assert __debug__, f"unhandled screen state: {type(other).__name__}"
            v.unknown_state(repr(other))
```

### Elixir (dynamic, functional, clause heads — precedence as ordering, checked by tooling not the compiler)

```elixir
# BEFORE — one map, three keys, clauses tried in source order
def render(%{loading: true}),  do: :spinner
def render(%{error: e}) when not is_nil(e), do: :error
def render(%{items: []}),      do: :empty      # unreachable-with-no-cache lands here: the false-empty
def render(%{items: items}),   do: {:list, items}

# AFTER — tagged tuples are the sum type; the typespec states the closed set, Dialyzer checks it.
# Clause order is precedence *where patterns overlap* — {:failed, _} must sit below the two specific failed
# clauses. Disjoint tags cannot shadow each other, but keep them in ladder order anyway so the file reads
# as the decision instead of a lookup table.
@type condition ::
        {:blocked, BlockedWhy.t()}
      | {:gate, GateWhy.t()}
      | {:failed, %{result: atom(), retryable: boolean(), correlation_id: String.t()}}
      | {:unexpected, String.t()}                                    # ← the mandatory else
      | {:pending, %{stage: :first | :retry, elapsed: non_neg_integer()}}
      | {:empty, :never | :filtered | :paged | :policy | :entitlement | :unreachable}
      | {:loaded, %{items: [Item.t()], freshness: :current | :stale | :refreshing}}
      | {:partial, %{ok: [Region.t()], failed: [Region.t()]}}

def render({:pending, %{stage: :first}}, v),                 do: View.placeholder(v)
def render({:pending, %{elapsed: ms}}, v),                   do: View.keep_with_busy(v, ms)
def render({:empty, :unreachable}, v),                       do: View.no_connection(v)
def render({:empty, why}, v),                                do: View.empty_for(v, why)
def render({:failed, %{result: :refused}}, v),               do: View.gate(v)
def render({:failed, %{retryable: true, correlation_id: id}}, v), do: View.retry(v, id)
def render({:failed, _}, v),                                 do: View.hard_failure(v)
def render({:unexpected, what}, v),                          do: View.unknown_state(v, what)
def render({:loaded, %{items: i, freshness: f}}, v),         do: View.list(v, i, f)
def render({:partial, %{ok: ok, failed: bad}}, v),           do: View.regions(v, ok, bad)
def render({:blocked, why}, v),                              do: View.takeover(v, why)
def render({:gate, why}, v),                                 do: View.gate_for(v, why)

def render(other, v) do
  # The catch-all is the one clause that must exist and must never be reached.
  # Log the *shape* only — the payload may hold someone else's data.
  tag =
    case other do
      {name, _} when is_atom(name) -> name
      {name} when is_atom(name) -> name
      _ -> :not_a_condition
    end

  require Logger
  Logger.error("unhandled screen state: #{inspect(tag)}")
  View.unknown_state(v, "unclassified")
end
```

Nothing here fails the build when a variant is missed — a dynamic stack cannot. So the guarantee is
outsourced, and you must say which of the three you are paying for: a **Dialyzer** typespec over
`condition` (catches producer mistakes, not missing clauses), **a test per variant** driven off the typespec
list, or **the catch-all alerting loudly in every non-prod build** and rendering unknown in prod. Pick at
least two, and name them in the report: on a dynamic stack, "exhaustive" is a claim you have to instrument.

View method names (`placeholder`, `keep_with_busy`, …) stand for the project's own rendering calls;
the syntax around them is what's real.

**What all six buy you, in any stack:** `Loaded` cannot coexist with `Failed`; `Empty` must carry *why*;
`Unexpected` cannot be forgotten; adding a state is a build error, a startup failure or a test failure
rather than a runtime surprise for one viewer on a bad link.

What differs is only **where the guarantee is enforced** — and that is the one thing to copy deliberately,
because it is what "all states handled" stops being an aspiration:

| Stack | The mechanism that makes an unhandled variant impossible to miss | Fails at |
|---|---|---|
| TypeScript | `assertNever(c)` against a discriminated union | build |
| C# | one `IConditionVisitor<T>` method per variant | build |
| Rust | a `match` with no `_` arm | build |
| Go | `default` in the type switch, plus a sealed private marker method | runtime, loudly |
| Python | `assert __debug__` in the final `case` | debug run / test |
| Elixir | catch-all clause + Dialyzer typespec + a test per variant | type-check, test |

Two of the six cannot check it statically, and say so in the code. That admission — *this stack needs a test
where that one needs a compiler* — belongs in the report (`precedence-resolution.md` §exhaustiveness).

---

## 2. The same 11 rows, five platforms

Which states survive changes with the platform posture (`inventory.md`). Coverage stays the axis
walk; the vocabulary of *carriers* is what moves.

| State (row) | browser web | mobile (offline-first) | desktop | CLI / TUI | embedded / field link |
|---|---|---|---|---|---|
| pending, first | structure placeholder | pull-to-refresh + placeholder | window content placeholder, cancel in the toolbar | braille/spinner line, or count-so-far | elapsed timer, decision point at budget |
| high-latency-but-working | elapsed + cancel | same, plus data-saver path | progress with `N of M`, cancellable | streaming lines | **the normal case** — resumable, never a frozen frame |
| no-connection-at-entry | full-screen honest block | serve cache; else block | block + "open offline copy" | exit-with-message or degraded read-only | queue-and-wait mode |
| no-connection-with-cache | keep + stale line | **the primary mode** | keep + offline title bar | `(cached HH:MM)` suffix per line | keep; suppress write affordances |
| failed (retryable) | retry, backoff | auto-retry on radio edge | retry + "why" detail behind a disclosure | re-run hint on the next line | jittered backoff, don't drain battery |
| unexpected / unknown shape | render "unknown", don't crash | same, and refuse the write | same, plus log bundle with correlation id only | exit code + one line, no traceback | **halt the action**, keep last known good |
| empty-filtered | clear-filter action | same | same + a filter-state chip | a "clear filters" key binding, not a link | same |
| write in flight / queued | disable + inline busy | **queue UI is first-class**, unsent marker | modal-or-tray, app can quit with queue | job id + status command | durable outbox, survives reboot |
| lost-in-transit | "not confirmed — check" | same, plus resend-with-idempotency-key | same | non-zero exit, "verify before retry" | never auto-resend an unconfirmed action |
| device/host (suspend, kill, low power, storage full) | tab hidden / bfcache restore | OS kill + state restore; thermal defers sync | lock, display change, another process holds the file | terminal resized/closed; SIGPIPE | radio off, thermal throttle, clock skew |
| perception & operability | focus + live region | VoiceOver / TalkBack, touch target size | UIA / NSAccessibility peers, full keyboard | screen-reader-safe text, `NO_COLOR`, narrow-width reflow | no audio, high-contrast sunlight, gloved hands |

**Two rows only exist off-web** and are the ones a web-trained agent misses: *another process holds
the lock* (desktop) and *the link is slow by design, so resumption and outbox durability are the
happy path* (field/embedded). **Two rows only exist on web and are over-applied elsewhere:** URL
forcing (`?state=`) and hover-only affordances.

---

## 3. Where each decision belongs (the trade-off, restated per stack)

| Concern | Options | Pick by |
|---|---|---|
| Where the resolver lives | in-screen · transport wrapper · app shell · producer side (headless) | how many screens share the mechanism; see `precedence-resolution.md` |
| How exhaustiveness is enforced | compiler · startup assertion · test per variant · the matrix as checklist | what the language can check; when it can't, say so in the report |
| How state survives the host | memory · serialize on suspend · durable outbox · refetch on resume | whether the viewer can lose work; offline-first demands the outbox |
| Progress vocabulary | placeholder · indeterminate · determinate-with-number · elapsed+cancel | whether a real numerator exists and how long the wait can run |
| Forcing hook | query param · launch arg · env var · dev menu · key binding · fixture payload | whatever the platform offers without shipping a prod backdoor |
