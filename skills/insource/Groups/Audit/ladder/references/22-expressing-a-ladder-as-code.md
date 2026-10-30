# 22 — Expressing a ladder as code without the nest

The chosen ladder is a spec (`21`); this file is how to write it so the shape survives contact with the
repo's clean-code rules. Nested conditionals are the default form and usually the rejected form: depth
hides the order, and the order **is** the policy.

## The split that makes everything else easy

Separate three things that an `if`-tree fuses:

```
facts -> [decide] -> verdict(+"why")      pure, total, testable, no I/O
          [interpret] verdict -> effects  the only place anything happens
```

`decide` is the ladder. It takes a value and returns a value, never a promise, never a mutation, never a
log line. Everything the audit wants — totality, reachability, determinism, order-independence — is
free once the ladder is a pure function over data (`15`), and `scripts/ladder_audit.py` can read its
rules because they are data.

Once that split exists, the nesting problem mostly solves itself: the tree becomes a lookup, a fold, or
a match over a closed type, and the effects move to one `interpret`.

## Idioms, by what the ladder actually is

**Closed set of inputs → match over a sum type, dispatch table for the behaviour.** Exhaustive by
construction, no default arm to hide in.

```ts
type Verdict = RefundDecision;                       // discriminated union, not strings
const DECISIONS: Record<Verdict["kind"], (v: Verdict) => Outcome> = {
  overLimit:   v => ({ kind: "review", reason: v.limit }),
  vipFast:     () => ({ kind: "approve" }),
  needsProof:  () => ({ kind: "reject", reason: "proof-required" }),
};
const decide = (v: Verdict): Outcome => DECISIONS[v.kind](v);   // total: the type says so
```

```rust
match verdict {                                     // non-exhaustive here is a compile error
    Refund::OverLimit { limit } => Outcome::Review(limit),
    Refund::VipFast             => Outcome::Approve,
    Refund::NeedsProof          => Outcome::Reject(Reason::Proof),
}
```

```python
match decision:                                     # 3.10+; guard the ranges, keep it flat
    case OverLimit(limit=lim): return Review(lim)
    case VipFast():              return Approve()
    case NeedsProof():           return Reject(Reason.PROOF)
```

```go
switch v := decision.(type) {                       // no exhaustiveness: default must be loud
default: return Outcome{}, fmt.Errorf("unhandled decision %T", v)
}
```

**Conditions, not kinds → table of named predicates.** The order becomes a list you can read, sort,
shuffle and audit.

```ts
const rules = [
  { id: "over-limit",  when: isOverLimit,    then: () => review("limit") },
  { id: "vip-fast",    when: and(isVip, not(isFraudFlag)), then: () => approve() },
  { id: "terminal",    when: () => true,     then: () => manualReview() },
] as const;
const firstMatch = <F>(fs: F, rs: readonly Rule[]) => rs.find(r => r.when(fs));   // the engine
```

```python
from functools import reduce
decide = lambda facts: next((r.then(facts) for r in RULES if r.when(facts)), ESCALATE)
```

**Escalation of severity → fold with a lattice, not a chain of branches.** All-strictest is one
`min`, and it is order-free by construction (`14`).

```ts
const STRICTEST = { deny: 0, ask: 1, allow: 2 } as const;
const combine = (vs: Verdict[]) => vs.reduce((a, b) => (STRICTEST[a] <= STRICTEST[b] ? a : b), "allow");
const decide = (f: Facts) => combine(RULES.filter(r => r.when(f)).map(r => r.verdict));
```

**Ordered attempts → a loop with a policy, not a chain of `try`/`catch`.** `??`-chains and nested
`try`s drop the reason and the budget (`11`).

```ts
for (const [i, a] of ATTEMPTS.entries()) {
  if (spent + a.cost > budget) { log.push({ attempt: a.name, outcome: "skipped", why: "budget" }); break; }
  const r = await a.run(signal);                      // never swallow: classify, then decide
  if (r.ok) return { value: r.value, witnesses: log };
  log.push({ attempt: a.name, outcome: r.error.kind });
  if (r.error.kind !== "transient") continue;         // escalate
  await sleep(backoff(i));
}
return { error: new Exhausted(log) };                 // the ladder's terminal rung, carrying why
```

**Guards on entry → early returns, one clause per rule, flat tail.** Cost-ascending, and no `else`
ladder (`04`).

```ts
async function submit(req: Request): Promise<Result> {
  const shape = parseShape(req);        if (shape.err)  return badRequest(shape.err);
  const auth  = await authorize(req);   if (auth.denied) return forbidden(auth, req.correlationId);
  const risk  = await score(req);       if (risk.needsConfirmation) return confirm(risk);
  return ok(await persist(req));
}
```

## Clean-code rules that shape the choice

- **No boolean-flag parameters.** `decide(facts, strict)` hides a tier in an argument; make the mode a
  named value or two functions.
- **Nesting depth ≤ 2, functions single-purpose.** If a rung needs three conditions, name the
  conjunction (`isVipFastTrack`) rather than indenting it.
- **No side effects in predicates** — a predicate that logs or mutates cannot be shuffled, re-run or
  property-tested (`14`, `15`).
- **The order lives in data, the interpretation lives in code.** Sorting is the engine's job, and it
  says which direction wins (`07`).
- **Every rung has a name, every result says who answered** (`02`, `15`).
- **Unknown is a value, not a crash and not a pass.** Exhaustive match or loud default (`08`).
- **Small files, one concern per file**: the rules, the predicates, the engine, the interpreter, and the
  tests get their own place if the project has places.

## Fit the repo's existing paradigm, whatever it is

Read the neighbours before choosing an idiom above. The tell is what the code already imports and how it
names things:

| Repo signal | Express the ladder as |
|---|---|
| Result/Either/Option types, `?`, `map/or_else`, fp-ts, ZIO, Vavr, Arrow | combinators over values, errors as values, one `interpret` at the boundary |
| Exceptions, typed error classes, middleware | guard clauses plus a tier list; map exception to verdict once, at the boundary |
| Heavy generics, interfaces, DI containers | chain of responsibility with an ordered registration list (`10`) |
| Data-driven services, config tables, rules from a DB | decision table in config with a validated grammar (`06`) |
| Reducers, state machines, event handlers | state-transition guards, ordered, with a terminal no-op (`12`) |
| Pipelines, streams, iterator chains | `filter`/`find`/`reduce` over rule data — the same fold the STRICTEST example shows |

Importing a functional library into an OO service (or the reverse) to place one ladder is the mistake,
not the fix. A table of named predicates is functional enough for a codebase of classes; a strategy
object is table-driven enough for a codebase of functions. The ladder's properties — total, ordered,
auditable, pure predicates — are the requirement; the syntax is the repo's.

## If the repo forbids it

Some projects ban what this file recommends: no maps of functions, no sum types, no data-driven rules,
nesting enforced by an old lint. Then implement the ladder in the allowed form and keep the properties by
other means — a single function with early returns still has an order, add the audit as tests where the
linter won't run it, and record the constraint in the decision doc (`21`) so the next reader knows the
shape was chosen under protest.
