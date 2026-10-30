# 15 — Testing a ladder: shadows, totality, audit, and the metrics that catch the rest

A ladder is not verified by "it returned the right verdict twice". Four properties carry the whole
safety story, and three of them are checkable mechanically before any user sees a wrong answer.

## The six properties

Reachability and totality are the pair people skip; `scripts/ladder_audit.py` checks all six, including
**severity inversion** - a permissive rule ordered before a strict one whose conditions can co-hold,
which is the flat-list deny bug of `13` found mechanically.

| Property | Statement | How to check |
|---|---|---|
| **Totality** | every input produces a verdict, including malformed ones | cross-product the fact space; assert no exception and no `None` |
| **Reachability** | every rung can win for some input | probe: for each rule, find an input where it wins; report the ones with none |
| **Determinism** | same facts, same winner | shuffle the rule list, sort by the documented key, compare; run twice |
| **Order-independence where claimed** | in strictest/most-permissive modes, position must not matter | same as above, asserted per mode |
| **Non-contradiction** | no permissive rung is evaluated before a strict rung whose conditions can co-hold with it | for each pair, try to satisfy both; if possible and the earlier verdict is the looser one, flag it |
| **Purity** | predicates are replayable | a condition that reads the clock, RNG, stdin or the network can change the winner between the check and the action |

```python
def probe(rules, facts_space, default):
    winners = {}
    for facts in facts_space:
        r = decide(rules, facts)
        winners.setdefault(r["rule"], 0)
        winners[r["rule"]] += 1
    dead = [x["id"] for x in rules if x["id"] not in winners and x["id"] != default]
    return dead          # empty, or the shadow bug list
```

For structured facts, replace the hand-written space with a product over the domains, or a solver if
conditions are inequalities. Then assert the **count of reachable rules equals the count of rules**,
and make that assertion part of CI so a new broad rule that shadows an old one fails the build.

## Golden matrix: the highest-value ladder test

Enumerate a small representative fact set, run it through every mode you support, and commit the
result as a table.

```python
GOLDEN = [
    # facts                          first        strictest      permissive
    ({"tool":"bash","cmd":"rm -rf"},  ("allow","any-write"), ("deny","rm-rf"),  ("allow","any-write")),
    ({"tool":"bash","cmd":"git push"},("ask","git-push"),    ("ask","git-push"), ("ask","git-push")),
    ({"tool":"read","cmd":"cat"},     ("allow","read-safe"), ("allow","read-safe"),("allow","read-safe")),
    ({"tool":"zzz"},                  ("ask","default"),     ("ask","default"),  ("deny","default")),
]
```

Any change to a rule, an order, or a mode shows up as a diff in a committed table. That diff is the
review artifact a human can actually read, and it is the only thing that catches "the reordering you
did at 2am for the incident".

## Mutation checks worth running

- **Swap two adjacent rungs** and confirm the golden matrix changes where you expect. If swapping
  changes nothing, one of the rungs is unreachable.
- **Delete a rung** and confirm some input changes verdict. If nothing changes, the rung is dead code.
- **Narrow a rule** (add one field to the condition) and confirm it stays reachable.
- **Break totality on purpose** (remove the terminal rule) and confirm the tests fail loudly rather
  than returning a zero value.

## Audit trail: what every result should carry

```python
{"verdict": "deny",
 "rule": "rm-rf",                       # the winner's stable id
 "scope": "global",                     # which ladder it came from
 "tier": "deny",                        # which class of verdict
 "matched_count": 3,                    # how many rungs matched (shadow signal)
 "candidates": ["any-write","rm-rf","default"],   # optional, behind a debug flag
 "facts_hash": "sha256:...",            # so you can replay the exact decision
 "engine_version": "2.1.0", "rules_source": "policies/safety.yaml@4f2c1a9"}
```

`matched_count > 1` under a first-match mode is your shadow metric; graph it. `candidates` behind a
flag costs nothing and turns a support ticket into a reproduction. Log the source revision so a
"why did this get denied" question has an answer after the fact.

## User-facing failure modes are not stack traces

- **Ambiguous**: tell the user what changed and what to do, never "2 rules matched".
- **Denied**: name the owning policy area, not the internal rule id, and give an appeal path.
- **Malformed rule at load**: fail closed and report which rule id failed - the ladder must not fall
  open because a config typo.
- **Unmatched**: never render as the happy path. "unknown" is a design, not a default.

## Review questions (ten, in order, before approving a ladder change)

1. What is the ordering key, and where is it declared?
2. Which mode are we in - first, all-strictest, all-permissive, only-one? Stated anywhere?
3. Is there a terminal rung, and does it produce a value for a fact with an unknown field?
4. Which rung did this fixture hit, and does the result prove it?
5. What new rule does this one shadow? Run the probe.
6. Does reordering the list change the answer? It should not, in all-match modes.
7. Where do side effects live - in the predicate or in the outcome? Predicates must be replayable.
8. If this ladder chains, what stops the loop?
9. What is the blast radius of a typo in this config file: fail-open or fail-closed?
10. What will we see in production when this ladder is wrong - which metric moves?

## The probes, in the stacks where the ladder lives

**TypeScript** — totality and reachability as one table test, with the dead list asserted rather than
eyeballed.

```ts
type Facts = Record<string, string | number | boolean>;

function sampleFacts(rules: Rule[], known: string[]): Facts[] {
  const out = rules.map((r) => {
    const f: Facts = {};
    for (const [field, op, value] of atoms(r.when)) {
      if (op === "eq") f[field] = value;
      else if (op === "in") f[field] = (value as never[])[0];
      else if (op === "starts") f[field] = `${value}-extra`;
      else if (op === "gt") f[field] = Number(value) + 1;
    }
    for (const k of known) f[k] ??= `probe-${String(k)}`;
    return f;
  });
  return [...out, Object.fromEntries(known.map((k) => [k, `probe-${k}`]))];
}

test("ladder is total and every rung is reachable", () => {
  const winners = new Set(sampleFacts(RULES, KNOWN).map((f) => decide(RULES, "first", f)?.id ?? null));
  expect(winners.has(null)).toBe(false);                       // totality
  const dead = RULES.filter((r) => !winners.has(r.id)).map((r) => r.id);
  expect(dead).toEqual([]);                                    // reachability
});
```

**Go** — the same two assertions as table tests, whose zero values make a missing verdict impossible to
miss.

```go
for _, tc := range cases {
	got, ok := decide(rules, tc.facts)
	if !ok {
		t.Errorf("no verdict for %+v: ladder is not total", tc.facts)
	}
	if got.Rule != tc.wantRule {
		t.Errorf("%+v: got %s want %s", tc.facts, got.Rule, tc.wantRule)
	}
}

seen := map[string]bool{}
for _, tc := range cases {
	if d, ok := decide(rules, tc.facts); ok {
		seen[d.Rule] = true
	}
}
for _, r := range rules {
	if !seen[r.ID] && !r.Terminal {
		t.Errorf("rule %s never won any probe: shadowed or dead", r.ID)
	}
}
```

**Rust** — the property that order-independence actually claims, over shuffled input.

```rust
let mut shuffled = rules.clone();
shuffled.rotate_left(1);
assert_eq!(
    decide(&rules, Mode::AllStrictest, &facts).rule,
    decide(&shuffled, Mode::AllStrictest, &facts).rule,
    "all-match mode must not depend on list order"
);
```

**pytest shape** — the golden matrix as a parametrized test, so a reordering fails with the fact that
caused it in the test name.

```python
@pytest.mark.parametrize("facts,winner", GOLDEN)
def test_golden(facts, winner):
    assert decide(RULES, "first", facts)[1] == winner
```

## What "covered" means here

Line coverage of a ladder is nearly worthless: a shadowed rule is executed on the way to never winning.
Track these instead, and put them in the same report as the audit:

- **rung coverage**: rules that won at least one probe / rules that exist. Target 100%, minus a
  documented exemption list.
- **verdict coverage**: each verdict value produced by at least one rule, including the terminal one.
- **conflict coverage**: pairs of rules that can both hold, and the test that says which one wins.
- **drift**: the number of rules nobody has touched in two quarters; expired incident rules (`06`).

## Seen in

Rule engines with test fixtures per rule (Drools' rule-unit tests), DMN model validation (hit policy +
decision-table coverage), CSS debugging tools that show the matched-declaration list with the winner
bolded (`matched_count` and `candidates`, in browser form), and permission engines that report the rule
that decided alongside the verdict.
