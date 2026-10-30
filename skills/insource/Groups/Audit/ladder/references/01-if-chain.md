# 01 — The if-chain (one place, code only)

The plainest ladder: sequential `if / else if / else` in a single function. Nothing else is
promised — no data, no reorder safety, no audit beyond what you return.

## Shape

```python
def classify(order):
    if order.cancelled:        return "cancelled"     # most specific first
    if order.refunded:         return "refunded"
    if not order.paid:         return "awaiting_payment"
    if order.shipped:          return "shipped"
    return "processing"                              # the fallback IS the else
```

## Pick it when

- Fewer than ~5 rungs, one owner, and the rule will not be read by a non-programmer.
- The conditions need the full language (early returns, local variables, awaits) that no table can
  express.
- The order is a property of the *logic*, not a policy someone tunes.

Do not pick it when: rules come from config or another team, the list grows past ~7 rungs, more than
one place needs to read the same rule set, or you must report which rule fired. Use `02` or `06`.

## Pitfalls specific to this form

1. **Order coupling.** Moving a rung changes behavior in ways the reader cannot see. Fix: put a
   comment on each rung stating which rungs below it depend on its position ("cancelled before
   refunded: a cancelled refund order is cancelled, not refunded").
2. **Missing final else.** The chain returns `None` implicitly and the caller treats it as falsy-but-
   fine. Fix: always end with a value, and if the fallback is an error, return/raise an error type.
3. **Condition with effect.** `if save_and_check(x)` — evaluated possibly twice by tests or replays.
4. **Copy-paste divergence.** A near-identical chain in a second language or service, kept in sync by
   hope. That is the signal to move to `06` (shared config).
5. **Ordering by "natural reading"** instead of by specificity. The natural reading of the business
   rule is often the least safe order (broad rule first).

## Variants that are still an if-chain

- **Guard clauses** (`04`): same mechanism, but the rungs reject bad input and the tail is the happy
  path.
- **Chain of responsibility**: the same shape spread across objects; each link decides or delegates.
- **Nested ifs**: the degenerate form; flatten with early returns. If you cannot flatten because the
  structure is a tree of conditions, that is a hint you have `05` (match tree) instead.

## Testing

Test the seams: one case per rung, one case that proves each rung still shadows what it should not,
and one case that hits the fallback. For any rung that no test reaches, either delete it or document
why it is unreachable.

## The same chain in other stacks

**TypeScript** - plus the `never` trick that turns a missing terminal branch into a compile error.

```ts
function classify(o: Order): string {
  if (o.cancelled) return "cancelled";
  if (o.refunded)  return "refunded";
  if (!o.paid)     return "awaiting_payment";
  if (o.shipped)   return "shipped";
  return "processing";
}
function assertNever(x: never): never { throw new Error("unhandled: " + x); }
```

**Go** - expressionless `switch`. `default` is optional, which is exactly the hazard.

```go
func classify(o Order) string {
    switch {
    case o.Cancelled: return "cancelled"
    case o.Refunded:  return "refunded"
    case !o.Paid:    return "awaiting_payment"
    case o.Shipped:  return "shipped"
    }
    return "processing" // "" if you forget it: totality is on you, not on the compiler
}
```

**Rust** - the same early-return shape; with an enum instead, the compiler enforces the tail.

```rust
fn classify(o: &Order) -> &'static str {
    if o.cancelled { return "cancelled"; }
    if o.refunded  { return "refunded"; }
    if !o.paid     { return "awaiting_payment"; }
    if o.shipped   { return "shipped"; }
    "processing"
}
```

**Elixir** - `cond`, where the `true ->` arm is the mandatory else (omitting it raises
`CaseClauseError` rather than returning `nil`, which is the one kindness).

```elixir
def classify(o) do
  cond do
    o.cancelled -> :cancelled
    o.refunded  -> :refunded
    not o.paid  -> :awaiting_payment
    o.shipped   -> :shipped
    true        -> :processing
  end
end
```

**SQL** - searched `CASE`, evaluated in written order; a missing `ELSE` is NULL by the standard, so the
terminal rung is a syntax decision, not a style one.

```sql
SELECT CASE
         WHEN cancelled THEN 'cancelled'
         WHEN refunded  THEN 'refunded'
         WHEN NOT paid  THEN 'awaiting_payment'
         WHEN shipped   THEN 'shipped'
         ELSE 'processing'
       END AS state
FROM orders;
```

Note the divergence between stacks on the *same* decision: Go and Python silently produce a zero value,
Elixir raises, SQL yields NULL, TypeScript and Rust can be made to refuse to compile. Pick the language
whose failure mode you can actually test for.

## Seen in

Everywhere, including places that pretend otherwise: middleware pipelines (`10`), route handlers,
form validators. Its honest name in most codebases is "the thing we will replace next sprint".
