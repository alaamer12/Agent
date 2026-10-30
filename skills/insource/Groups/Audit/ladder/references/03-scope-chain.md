# 03 — The scope chain (ladder of ladders)

Two ladders nested: rungs inside a scope, and scopes ordered among themselves. The classic question
it answers is not "which rule matches" but "**who is allowed to override whom**".

## Shape

```python
SCOPES = ["user", "team", "customer", "global"]     # most specific first

def resolve(rules_by_scope, facts):
    for scope in SCOPES:                            # outer ladder
        for rule in sorted(rules_by_scope[scope], key=lambda r: r.priority):
            if rule.when(facts):                    # inner ladder
                return RuleHit(rule.id, scope=scope, priority=rule.priority)
    return FALLTHROUGH
```

An empty scope is skipped, not an error. A scope with a match **ends the walk** — that is the whole
semantic, and it is what makes "closest wins" different from "most restrictive wins" (`13`).

## Semantics, precisely

| Property | Value |
|---|---|
| Ordering key | scope position, then in-scope key (priority or position) |
| Matching | first match wins, within the first scope that has any match |
| Fallback | fallthrough to a system default |
| Override direction | narrower scope beats broader scope |
| Audit | rule id + scope + in-scope key. Cheap and worth returning |

## Pick it when

Rules have owners: user, team, tenant, repo, folder. Config that walks upward. Anything where a
person closest to the context must be able to beat a central default without asking permission.

Do **not** pick it for safety decisions: closest-wins means a user scope can beat a global `deny`.
For that, put the deny in a tier that is checked across all scopes (`13`) — see "Combining" below.

## Pitfalls

1. **Combining two ordering keys without stating precedence.** "Priority 1 in the team scope beats
   priority 99 in the user scope" surprises everyone. Decide: scopes-first (closest wins) or
   priority-first (global ranking). State it in a comment at the definition of the outer ladder.
2. **Inherited scope with no boundary marker.** Folder-based cascades (EditorConfig, ESLint,
   `.gitignore`) stop at the project root; if you keep walking to the filesystem root you inherit a
   developer's home-directory config into a CI build. Define the top of the walk explicitly.
3. **Two rungs in the same scope match and the tie-break is unspecified.** Same hazard as `07`; sort
   by a total order including identity.
4. **A scope that never has rules but exists in the list.** Harmless but misleading: it advertises a
   capability nobody uses. Either populate it or drop it and document where those rules live now.
5. **Deep chains become slow** when re-evaluated per request. Cache by (scope chain, facts fingerprint)
   and note the cache key in the audit output so a stale answer is diagnosable.

## Combining with tiers — the decision that changes behavior

With a global `deny rm -rf` and a user `allow bash`:

| Nesting | Winner | Right for |
|---|---|---|
| scopes outside, tiers inside | **allow** (user scope wins outright) | preferences, routing, formatting |
| tiers outside, scopes inside | **deny** (deny tier searched everywhere) | security, compliance, quotas |

Both loops are three lines. Choosing wrong is a policy bug that no test catches unless you wrote a
test specifically for the cross-scope conflict. Write that test.

## The same cascade in other stacks

**TypeScript** - scopes as a key list and a `Record`, so an unhandled scope is a type error.

```ts
const SCOPE_ORDER = ["user", "team", "customer", "global"] as const;
type Scope = (typeof SCOPE_ORDER)[number];

function resolve(sets: Record<Scope, Rule[]>, f: Facts) {
  for (const scope of SCOPE_ORDER) {
    const hit = sets[scope].find((r) => r.when(f));
    if (hit) return { ...hit, scope };               // audit: which authority answered
  }
  return { then: "default", name: "fallthrough", scope: "none" as const };
}
```

**Go** - a slice of scope structs; the zero value of a missing map entry is why the lookup is checked
instead of trusted.

```go
type Scope struct {
	Name  string
	Rules []Rule
}

func resolve(scopes []Scope, f Facts) (Decision, bool) {
	for _, s := range scopes {
		for _, r := range s.Rules {
			if r.When(f) {
				return Decision{Then: r.Then, Rule: r.ID, Scope: s.Name}, true
			}
		}
	}
	return Decision{Then: "default", Rule: "fallthrough"}, false
}
```

**Java** - sealed-ish records for scopes with an explicit `chain` flag; the hop limit lives in the
resolver, not in the rules.

```java
record Rule(String id, Predicate<Facts> when, String then, boolean chain) {}
record Scope(String name, List<Rule> rules) {}

static Decision resolve(List<Scope> scopes, Facts f, int maxHops) {
    for (Scope s : scopes) {
        for (Rule r : s.rules()) {
            if (r.when().test(f)) {
                if (!r.chain()) return new Decision(r.then(), r.id(), s.name());
                if (maxHops-- <= 0) return new Decision("error", r.id(), s.name());
                f = r.applyTo(f);
            }
        }
    }
    return new Decision("default", "fallthrough", "none");
}
```

**SQL** - one table, ordered by scope rank; the nearest-wins answer is `DISTINCT ON`.

```sql
SELECT DISTINCT ON (fact_id) fact_id, scope, rule, then
  FROM (SELECT f.id AS fact_id, s.name AS scope, r.rule, r.then,
               ROW_NUMBER() OVER (PARTITION BY f.id
                                  ORDER BY s.rank, r.priority, r.rule) AS rn
          FROM facts f
          JOIN rules r ON r.matches(f)
          JOIN scopes s ON s.name = r.scope) t
 WHERE rn = 1;
```

**Six shipped cascades, three different directions.** Read the direction column before reusing your
intuition:

| System | Outer ladder | Inner ladder | Direction |
|---|---|---|---|
| EditorConfig | directory walk to `root=true` | glob sections | nearest wins |
| ESLint flat config | config array entries | `files` matches | **last entry wins** |
| `.gitignore` | directory depth | pattern list, `!` negation | **last match wins** |
| nginx | `http` > `server` > `location` | exact > longest prefix > regex order | specificity first |
| Bifrost | VirtualKey > Team > Customer > Global | priority ascending | nearest wins |
| CSS | origin/importance > `@layer` > specificity > scope proximity > order | declarations within a layer | per stage |

Nearest-wins, last-wins and specificity-wins all exist in widely used tools. A cascade whose direction
is inherited from whatever tool the author used last is a policy accident - state it in the schema, in
the resolver comment, and in the audit field that names the winning scope.

## Seen in

Bifrost (VirtualKey → Team → Customer → Global), EditorConfig, ESLint/Stylelint cascading configs,
Kubernetes config precedence, nginx `http`/`server`/`location` blocks, feature-flag targeting rules,
CSS `@layer` + origin + specificity (a four-level cascade with fixed precedence).
