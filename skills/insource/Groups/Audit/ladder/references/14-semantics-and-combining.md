# 14 — Semantics: how many rungs may match, and how their answers combine

Same rungs, different combining rule, different answers. This is the axis people forget to specify,
and it is the one that changes behavior without changing a single condition.

## The four modes

| Mode | Contract | Order matters? | Standard name |
|---|---|---|---|
| first match | stop at the first true rung | yes, totally | XACML `first-applicable`, DMN `FIRST` |
| all matches, strictest | evaluate everything, take the most restrictive | no | `deny-overrides`, DMN `PRIORITY` with a restrictive ranking |
| all matches, most permissive | evaluate everything, take the most permissive | no | `permit-overrides`, DMN `ANY` (all must agree) |
| exactly one match | more than one is an error | irrelevant, by construction | `only-one-applicable`, DMN `UNIQUE` |

Plus two less-common ones: **collect** (return the set, caller combines - DMN `COLLECT`), and
**last match wins** (inverse of first; rewrite as first-match over a reversed list and say so).

## The divergence, computed

```python
RULES = [
    Rule("any-write", "allow", when=lambda f: f.write),      # broad, listed first
    Rule("git-push", "ask", when=lambda f: f.cmd.startswith("git push")),
    Rule("rm-rf", "deny", when=lambda f: f.cmd.startswith("rm -rf")),
]
```

| Fact | first-match | strictest | most-permissive | only-one |
|---|---|---|---|---|
| `rm -rf /`, write=True | allow (any-write) | **deny** (rm-rf) | allow | error: 2 match |
| `git push`, write=True | allow | ask | allow | error: 2 match |
| `ls`, write=False | allow (read-safe) | allow | allow | ok |
| `python -c hi`, write=False | **ask** (default) | ask | **deny** (no allow) | ok |

Rows 1 and 2 are the argument for tiers (`13`); row 4 shows that "no rule matched" also needs a policy,
and that the policy differs by mode.

## Choosing without guessing

| Question | Answer | Mode |
|---|---|---|
| Can a rule author's list position be trusted to encode safety? | no | strictest (or tiers + first-match) |
| Must the engine be fast on common cases? | yes | first-match, ordered by hit frequency after specificity |
| Do authors need to know their overlap breaks something? | yes | only-one: the error is the feature |
| Is the result a set, not a verdict (tags, labels, reasons)? | yes | collect |
| Is every rule meant to be independent and complete? | yes | unique, validated by the engine |

Safety-critical: prefer **fail-closed combining** (deny/strictest) plus a default that refuses. In
Cedar's words: default deny with deny-overrides, so "applications never have to enforce it by
convention". Preference/config: first-match with nearest-scope wins (`03`).

## Chaining and re-entry

A rule may say "re-run the whole ladder with my output as the new facts" (Bifrost's `chain_rule`;
Drools' `setFocus` for agenda groups; routers that resolve then re-resolve). Effects:

- Termination is no longer structural. Bound it: `max_hops`, and a visited set of
  `(rule_id, fingerprint(facts))`.
- A rule whose output re-satisfies its own input is an infinite loop with extra steps. Detect it as a
  configuration error at load: simulate the rule against its own output.
- The audit trail becomes a **path**, not a rung: `[hop1/rule, hop2/rule, ...]`. Return it; a two-hop
  resolution that reports only the last hop is undebuggable.
- Idempotency: if the second pass has effects (billing, quota consumption), you are now double-charging.

## Failure modes

- **Undocumented mode**: the engine picks one and the config implies another. Name the mode in the
  document that defines the rules - and assert it in a test.
- **Combining rule per-tier vs global**: strictest across tiers but first-match inside a tier is a
  real design; strictest everywhere silently disables feature flags that return "off".
- **Last-match in a system imported from a first-match file**: some engines convert last-match rule
  sets into first-match at import time. If you do that conversion, log the converted list; otherwise
  the diff review is meaningless.
- **Ambiguity swallowed**: two matches collapse to the first without recording the collision. Report
  `matched_count` even when you short-circuit - shadowing bugs show up as `count > 1` counts in prod.
- **Tie-break by identity** silently reorders when names change. Prefer explicit in-tier order.
- **Testing only the happy mode**: write the table above as a test. The four columns on the same fixture
  are the clearest documentation of what you chose.

## Reference implementations of these names

DMN hit policies (OMG): `UNIQUE`, `FIRST`, `ANY`, `COLLECT`, `RULE ORDER`, `OUTPUT ORDER`, `PRIORITY`.
XACML 3.0 combining algorithms: `deny-overrides`, `permit-overrides`, `first-applicable`,
`only-one-applicable`. Cedar: `forbid` beats `permit`, default deny. CLIPS: named conflict-resolution
strategies (depth, breadth, simplicity, complexity, lex, mea, random) - order, specificity, and pattern
size as first-class choices. Drools: salience plus LIFO by default, agenda groups as scopes.

## The same modes, in more stacks

**Go** — strictest-wins without a sort: one pass, keep the most restrictive.

```go
var winner *Rule
best := -1
for i := range rules {
    r := &rules[i]
    if !r.When(f) {
        continue
    }
    if best == -1 || rank(r.Verdict) < best {
        best, winner = rank(r.Verdict), r
    }
}
if winner == nil {
    return Decision{Verdict: "ask", Rule: "default"}   // total, never a zero value
}
```

**Rust** — the combining rule as an explicit fold, so changing it is a one-line diff.

```rust
let winner = rules.iter()
    .filter(|r| r.when(facts))
    .min_by_key(|r| match r.verdict { Deny => 0, Ask => 1, Allow => 2 })
    .ok_or(Error::NoMatch)?;          // the caller must handle NoMatch: totality is its job
```

**TypeScript** — `ts-pattern` chains are first-match by construction; the all-match variant is a filter
plus a reduce, and the difference in the code is the difference in policy.

```ts
const firstWay = match(f)
  .with({ blocked: true }, () => "blocked")
  .with({ fault: true, rows: 0 }, () => "fault")
  .otherwise(() => "ready");

const strictestWay = RULES.filter((r) => r.when(f))
  .reduce((best, r) => (RANK[r.verdict] < RANK[best.verdict] ? r : best)).verdict;
```

**SQL** — both semantics from one scan; `rn = 1` is first-match, `MIN(tier_rank)` is strictest.

```sql
WITH m AS (
  SELECT f.id AS fact, r.id AS rule, r.tier_rank,
         ROW_NUMBER() OVER (PARTITION BY f.id ORDER BY r.tier_rank, r.id) AS rn
    FROM facts f JOIN rules r ON r.matches_f(f)
)
SELECT fact,
       MAX(CASE WHEN rn = 1 THEN rule END) AS first_match_rule,
       MIN(tier_rank)                       AS strictest_rank,
       COUNT(*)                             AS matched_count
  FROM m GROUP BY fact;
```

`matched_count > 1` under a first-match engine is the shadow signal from `15`, in one column.

**Elixir** — the mode as a case clause, which is the most honest form: the policy is in the head of the
function, not in a config file someone has to remember.

```elixir
def decide(mode, rules, facts) do
  hits = Enum.filter(rules, & &1.when.(facts))
  case {mode, hits} do
    {:first, [hit | _]}        -> hit.verdict
    {:strictest, []}           -> :ask
    {:strictest, hits}         -> hits |> Enum.min_by(&rank(&1.verdict)).verdict
    {:unique, [_] = [hit]}     -> hit.verdict
    {:unique, hits}            -> raise "ambiguous: #{Enum.map_join(hits, ", ", & &1.id)}"
    {:collect, hits}           -> Enum.map(hits, & &1.verdict)
  end
end
```

## Testing the mode, not just the verdict

```python
def test_modes_diverge_on_the_safety_case():
    facts = {"tool": "bash", "cmd": "rm -rf /", "write": True}
    assert decide("first", RULES, facts)[0] == "allow"        # the defect, pinned as a fact
    assert decide("all-strictest", RULES, facts)[0] == "deny"
    with pytest.raises(Ambiguous):
        decide("unique", RULES, facts)
```

If that table is not in your test suite, nobody on the team can say which mode the ladder is in — which
is the finding `15` calls `order-mode`.
