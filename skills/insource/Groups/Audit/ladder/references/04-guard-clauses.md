# 04 — Guard clauses (the vertical ladder)

An if-chain rotated 90°: reject or short-circuit on every bad case first, then the happy path runs
with no indentation left over. Same semantics as `01`, radically different reading order.

## Shape

```ts
async function submit(req: Request): Promise<Result> {
  if (!req.body)               return bad("empty body");
  if (req.idempotency?.stale)  return conflict("idempotency key reused");
  if (await isBlocked(req.user)) return forbidden("user blocked");
  if (!schema.safeParse(req.body).success) return unprocessable();
  if (req.dryRun)              return preview();
  return await persist(req);                         // flat, readable tail
}
```

## Why the order here is load-bearing

Guards are ordered **cheapest and most certain first, most expensive and least certain last**. That
is the opposite of the "most specific first" instinct from `01`, and it is deliberate:

1. Static/shape checks (no I/O, always right or wrong).
2. Local state checks (a cache read, a version compare).
3. Remote checks (auth service, quota, risk engine).
4. Mutating checks (reserve capacity, then release if a later guard rejects).

Get this wrong and every malformed request costs you three network calls. Get it wrong in the
other direction — a mutating guard early — and you leak reservations on rejection.

## Pick it when

Entering a function with several independent preconditions, especially handlers, commands, and
state-transition triggers. Use `02`/`06` when the same precondition set must be applied in several
places with the same message, or shown to users.

## Pitfalls

1. **Duplicated checks across siblings.** Five handlers each re-check "user is active" with slightly
   different error text, and one forgets. Fix: a shared `guards` list run by a wrapper — which is
   `10` (chain of responsibility) in disguise.
2. **Ordering by history instead of cost.** Guards get inserted where the last bug was, not where
   they belong. Annotate each guard with its cost class (`free` / `cache` / `remote` / `mutating`).
3. **A guard that only logs.** Then the ladder silently fails open. Either it returns, or it is not
   a guard.
4. **The happy path is unreachable in tests.** Every guard is a rung; if you never test a specific
   one, it may be dead (`req.idempotency?.stale` after a schema change) and still "working".
5. **Errors that leak topology.** Return a correlation id and a user-safe reason; keep the internal
   rule name in the log, not in the response body.

## Difference from a validation ladder

A validator collects **all** failures (`all-matches` semantics, `14`); a
guard ladder reports the **first** failure. Users hate a form that reports one error per submit. So
input *shape* validation uses all-matches, and *authorization/preconditions* use first-match —
because you do not want to tell an attacker which check they failed.

## The same guards in other stacks

**Go** - error-first returns, where the release pair makes the mutating-guard hazard visible.

```go
func Submit(w http.ResponseWriter, r *http.Request) error {
    if err := parseBody(r); err != nil { return badRequest(err) }
    if err := validateSchema(r.Body); err != nil { return unprocessable(err) }
    res, err := quota.Reserve(r)                    // mutating: cheapest-first rule broken? no,
    if err != nil { return forbidden(err) }         // but it must be last-but-one and reversible
    defer func() { if !committed { quota.Release(res) } }()
    if err := authz.Check(r); err != nil { return needsInput(err) }
    committed = true
    return persist(r)
}
```

**Rust** - `?` is a guard ladder the compiler checks; each `?` returns early on `Err`, so the happy
path is the only fallthrough.

```rust
fn submit(req: Request) -> Result<Ok, Error> {
    let body = parse(&req).ok_or(Error::EmptyBody)?;
    validate(&body)?;                     // free
    let user = authz::current(&req)?;     // remote
    risk::check(&user, &body)?;           // remote, expensive
    persist(body, user)
}
```

**Python** - the cost class belongs in the annotation, because guard order is a performance decision.

```python
def submit(req):
    if not req.body:                        # cost: free
        raise BadRequest("empty body")
    if not schema.is_valid(req.body):       # cost: free
        raise Unprocessable()
    if user_service.is_blocked(req.user):   # cost: remote
        raise Forbidden("account suspended")
    return persist(req)
```

**Elixir** - `with` is a guard ladder with one else-branch, the cleanest form of "every rung returns,
and the tail runs only if none did".

```elixir
with {:ok, body} <- parse(req),
     :ok <- validate(body),
     :ok <- authorize(user, body),
     {:ok, result} <- persist(body) do
  {:ok, result}
else
  {:error, reason} -> {:error, reason}
end
```

**C# / ASP.NET Core** - filters are guard clauses promoted to a ladder with explicit order numbers,
i.e. `07` rather than `01`: authorization (0), anti-forgery (10), caching (20), then the action. The
lesson is the one about duplicated checks: five controllers each re-checking "user is active" with
different messages is why the framework moved the guard into the pipeline.

**SQL / server-side validation** - a `CHECK` constraint is a guard the database enforces on every
write path, including the ones you forgot to write.

```sql
ALTER TABLE orders ADD CONSTRAINT orders_state_guard
  CHECK (state IN ('draft','paid','shipped','cancelled')) NOT VALID;
```

## Seen in

Middleware and interceptor pipelines, framework route guards, CLI command preconditions, compiler
passes ("is this syntax valid? is this name bound? is this type legal?"), statechart entry guards.
