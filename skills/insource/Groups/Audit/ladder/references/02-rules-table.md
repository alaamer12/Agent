# 02 — The rules table (list of rung records)

The same traversal, but rungs are data in a list, so order becomes an explicit, reviewable artifact
and the set can be printed, diffed, and tested as a whole.

## Shape

```ts
type Rule = { id: string; when: (f: Facts) => boolean; then: (f: Facts) => Result };

const RULES: Rule[] = [                       // ordered: this array IS the ladder
  { id: "cancelled",  when: f => f.status === "cancelled",   then: () => ("refund-hold") },
  { id: "vip-auto",   when: f => f.tier === "vip" && f.amount > 100, then: () => ("fast-track") },
  { id: "default",    when: () => true,                      then: () => ("standard") },
];

export function decide(f: Facts): { result: Result; rule: string } {
  for (const r of RULES) if (r.when(f)) return { result: r.then(f), rule: r.id };
  throw new Error("unreachable: table must end in a total rule");
}
```

Two properties the if-chain does not have: every rung has an **id**, and totality is checkable
(the last rule's `when` is `() => true`).

## Pick it when

- Rules live in one language and one repo, but you need them visible as a set (review, diff, docs).
- You want per-rung tests keyed by rule id.
- The engine is "first match wins" and you want that stated in the type, not in a comment.

## Pitfalls

1. **Insertion by append.** New rules go at the bottom to be "safe", then nobody deletes the
   generalized rule that now shadows nothing. Result: dead rules that still cost a test. Fix: make
   insertion position a reviewed decision — see `07` for priority numbers when authors cannot be
   trusted with order.
2. **Predicate duplication.** Three rules repeat `f.tier === "vip"`; a change to the tier definition
   misses one. Fix: extract named predicates (`isVip(f)`), and consider `05` (tree) if prefixes
   repeat a lot.
3. **Mutable order at runtime.** Sorting the array in place inside `decide` mutates shared state. Fix:
   sort a copy, or sort once at module load and freeze.
4. **`then` doing I/O.** Table rules must return a value; effects go in the caller after the winner
   is known, so a replay of `decide` is harmless.
5. **Silent non-totality.** "There is always a default" is a belief, not a property. Assert at import
   time: `if (RULES[RULES.length - 1].id !== "default") throw`.

## Testing

- **Completeness**: a table-driven test with one input per rule id plus one input that must fall to
  `default`.
- **No shadowing**: for each rule, an input that a naive broad rule above would also match, but which
  must return the *narrow* id. (If it returns the broad id, the broad rule is above it and wrong.)
- **Stability**: build the table from a set (unordered) then sort; assert the sorted order is
  identical across runs and across platforms (see `07` tie-break).

## The same table in other stacks

**Python** - with the import-time totality assertion that makes "there is always a default" a fact.

```python
ALWAYS = lambda f: True
RULES = [
    {"id": "cancelled", "when": lambda f: f["cancelled"], "then": "refund-hold"},
    {"id": "vip-auto",  "when": lambda f: f["tier"] == "vip" and f["amount"] > 100,
     "then": "fast-track"},
    {"id": "default",   "when": ALWAYS, "then": "standard"},
]
assert RULES[-1]["when"] is ALWAYS, "table must end in a total rule"

def decide(f):
    hit = next((r for r in RULES if r["when"](f)), None)
    return (hit["then"], hit["id"]) if hit else ("standard", "engine-default")
```

**Go** - a slice of structs, never a map: Go randomizes map iteration order deliberately, so a
map-keyed ladder is nondeterministic by construction.

```go
type Rule struct {
	ID   string
	When func(Call) bool
	Then string
}

var rules = []Rule{
	{"rm-rf", func(c Call) bool { return strings.HasPrefix(c.Cmd, "rm -rf") }, "deny"},
	{"any-bash", func(c Call) bool { return c.Tool == "bash" }, "allow"},
	{"default", func(Call) bool { return true }, "ask"},
}

func decide(c Call) (string, string) {
	for _, r := range rules {
		if r.When(c) {
			return r.Then, r.ID
		}
	}
	return "ask", "engine-default" // reachable only if the table lost its terminal rule
}
```

**Java** - records plus `findFirst`, so the winner's identity is part of the result type, not a side
channel.

```java
record Rule(String id, Predicate<Call> when, String then) {}

Optional<Rule> hit = rules.stream().filter(r -> r.when().test(call)).findFirst();
String verdict = hit.map(Rule::then).orElse("ask");
String winner  = hit.map(Rule::id).orElse("engine-default");
```

**Rust** - iterators, with the found arm carrying its own id.

```rust
let hit = rules.iter().find(|r| (r.when)(facts));
let (verdict, winner) = match hit {
    Some(r) => (r.then.clone(), r.id.clone()),
    None => ("ask".into(), "engine-default".into()),
};
```

**SQL** - here the table really is a table, and ordering is a query clause rather than a storage
accident.

```sql
SELECT id, verdict FROM rules r
 WHERE (r.pattern IS NULL OR :cmd LIKE r.pattern || '%')
 ORDER BY r.tier_rank, r.id
 LIMIT 1;
```

**DMN-flavored YAML** - the same shape with the hit policy stated, because a table without a declared
policy is a table with an undeclared engine.

```yaml
table: order-triage
hit_policy: FIRST          # UNIQUE | FIRST | ANY | COLLECT | PRIORITY
inputs: [cancelled, refunded, paid, shipped]
output: state
rules:
  - { when: [true, -, -, -], out: cancelled }
  - { when: [_, true, -, -], out: refunded }
  - { when: [_, _, false, -], out: awaiting_payment }
  - { when: [_, _, true, true], out: shipped }
  - { when: [_, _, true, false], out: processing }
```

## Seen in

Bifrost routing rules (scope → priority → first match), permission engines that convert last-match
rule sets into first-match at import time, error-to-classification maps, linter rule lists.
