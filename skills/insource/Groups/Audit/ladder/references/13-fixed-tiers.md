# 13 — Fixed tiers: the engine owns the verdict order

A tier is a named class of verdict whose relative order is fixed by the engine. Authors order rules
*inside* a tier and never across tiers. The point is that safety does not depend on someone
remembering to put the deny above the allow.

## Shape

**Python**

```python
TIER_ORDER = ("deny", "ask", "allow")     # engine-owned

def evaluate(sets: dict[str, list[Rule]], f) -> tuple[str, str]:
    for tier in TIER_ORDER:
        hit = next((r for r in sets[tier] if r.when(f)), None)
        if hit:
            return tier, hit.name
    return "ask", "default"               # unknown is not free
```

**TypeScript** - `Record<Tier, Rule[]>` makes a missing tier a compile error; the tuple order stays data.

```ts
const TIER_ORDER = ["deny", "ask", "allow"] as const;
type Tier = (typeof TIER_ORDER)[number];
type RuleSet = Record<Tier, Rule[]>;

function tiersFirst(set: RuleSet, f: Facts): { verdict: Tier; rule: string } {
  for (const tier of TIER_ORDER) {
    const hit = set[tier].find((r) => r.when(f));
    if (hit) return { verdict: tier, rule: hit.name };
  }
  return { verdict: "ask", rule: "default" };
}
```

**C# / Java** - the tier set is closed by the enum, so totality is checkable at startup and a rule in an
unhandled tier cannot exist.

**SQL** - the order lives in a column you cannot typo, and the query shows both semantics side by side.

```sql
SELECT r.id, r.tier FROM rules r JOIN facts f ON <matches>
 WHERE f.id = :fact
 ORDER BY r.tier_rank, r.id
 FETCH FIRST 1 ROW ONLY;              -- tiersFirst
```

## Why a flat list is not equivalent

Same two rules, one flat list:

```python
flat = [
    {"name": "any-bash", "verdict": "allow", "when": lambda f: f.tool == "bash"},
    {"name": "rm-rf",    "verdict": "deny",  "when": lambda f: f.cmd.startswith("rm -rf")},
]
# flat[0] is consulted first -> "rm -rf /" is ALLOWED
```

Correct only because nobody reordered it. Tiers turn "remember the right order" into a structural
property: the deny tier is searched before any allow can win, no matter who appended what.

## Tiers plus scopes: the order of the loops is the policy

| Nesting | `global deny rm -rf` + `user allow any bash` | Right for |
|---|---|---|
| scopes outside, tiers inside | **allow** - nearest scope decides | overridable preferences: routing, formatting, config |
| tiers outside, scopes inside | **deny** - the deny tier is searched across every scope first | security, compliance, spend limits |

Both are three lines of code. Nothing but a test written specifically for the cross-scope conflict
will tell you which one you shipped.

## Standards that are tiers with names

| Name | Semantics |
|---|---|
| XACML `deny-overrides` | every rule evaluated; any Deny wins |
| XACML `permit-overrides` | mirror image; use only when allow must win |
| XACML `only-one-applicable` | more than one match is an error - a shadow detector by definition |
| Cedar / AWS Verified Permissions | `forbid` beats `permit`, plus default deny: the application never enforces it by convention |
| CSS cascade | origin/importance -> layers -> specificity -> scope proximity -> order of appearance; each stage is a tier, and only ties descend |
| Permission globs (sudoers, `.gitignore`, agent tool rules) | usually **last match wins** - the opposite default; check the manual, never assume |

## Failure modes

- **Tier-order drift**: a new tier ("warn", "review") appended to the list instead of placed. Keep the
  order in one constant and assert it in a test.
- **Empty tier**: compiles fine, silently converts "no rules" into "never wins". Startup check: every
  tier non-empty, or documented as intentionally reserved.
- **Tier-vs-priority confusion**: a lower priority number cannot outvote a tier. If authors expect it
  to, the tier is wrong, not the number.
- **Verdict leaking between tiers**: an `ask` that also grants (auto-approves after N tries) has moved a
  decision from the ask tier to allow without going through the allow tier.
- **Default that flips by accident**: returning `None`, `undefined`, or `True` when nothing matched.
  Return the restrictive value explicitly.
- **Shadow inside a tier**: tiers fix cross-class ordering only. Inside the allow tier, position or
  priority still decides - so `07` (in-tier order) and `15` (shadow probe) still apply.

## Testing

- A conflict test per pair of tiers: for each (higher tier rule, lower tier rule) that both match one
  fact, assert the higher tier wins. Generate it from the rule set; do not hand-write the two cases you
  thought of.
- An order-shuffle test inside each tier: the winner must be stable once the in-tier tie-break is defined.
- A totality test over a fact space: every fact yields a verdict and a rule name, never an exception.

## Seen in

Claude-style tool permission engines (deny/ask/allow with first match inside the tier), Cedar, IAM
policy evaluation (explicit deny beats allow), CSS, firewall rule groups, WAF phases, ESLint rule
severity plus ignore-directive precedence, and any "safety first, then preferences, then defaults"
engine you have been asked to write on whiteboard.
