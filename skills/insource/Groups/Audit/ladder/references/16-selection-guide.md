# 16 — Selection guide: which ladder, which mode, which nesting

Everything in one table, then the questions that resolve the remaining ambiguity. Use this to narrow the
shape in a design doc — or, in Step 2 of the workflow, to pick the two or three options worth putting to
the user with their trade-offs (`20` finds the sites, `21` reports and records, `22` writes the code);
use `00` for the vocabulary the doc must state.

## Need to shape

| Need | Shape | Reference |
|---|---|---|
| Few rules, one file, one owner | if-chain | `01` |
| Reject bad input before doing work | guard clauses | `04` |
| Order must be reviewable, results auditable | rules table | `02` |
| Rules from several files, teams, or tenants | priority numbers | `07` |
| Different authorities may override each other | scope chain | `03` |
| A prohibition must not be overridable | fixed tiers | `13` |
| Non-developers edit the rules without a deploy | decision table in config | `06` |
| Many rules sharing a first test; long rule sets | match tree | `05` |
| Rungs have heavy, per-owner dependencies | chain of responsibility | `10` |
| Ordered fallbacks with cost, timeout, error class | attempt/escalation ladder | `11` |
| Discriminator is a closed set of states | state/dispatch matrix | `08` |
| Same, inside a typed language | pattern matching / switch | `09` |
| Transitions depend on context | statechart guards | `12` |
| Business users assemble decisions | visual branch builder | `12` |
| "Which rule fired?" is a product requirement | audit trail in every shape | `15` |

## Then set the mode

| Situation | Mode | Why |
|---|---|---|
| Safety, spend, compliance | all-strictest, or tiers + first-match | order cannot be a security control |
| Preferences, formatting, routing, config | first-match, nearest-scope-wins | users expect their own setting to win |
| Tagging, labeling, reason collection | collect | several rungs are correct at once |
| Rule authors must be told when they overlap | only-one / unique | the error is the feature |
| Latency-critical, huge rule count | first-match over a compiled tree | cost is O(depth), not O(rules) |

## The five questions that resolve the rest

1. **Who may reorder this?** If the answer includes anyone who is not a code reviewer, the ordering
   must be data with a schema (`06`, `07`) and a validation gate.
2. **Must a higher authority always win?** Then tiers (`13`) - and pick the loop order (`03`/`13`).
3. **Can two rungs be right at once?** Then collect or strictest; first-match will silently pick one.
4. **What happens on an input no rung knows?** Unknown must render as unknown (`08`, `15`). If your
   answer is "the happy path", you have chosen to fail open.
5. **What is the terminal rung?** If you cannot name it, the ladder is not finished.

## Migration paths (they are cheap in one direction)

```
if-chain -> rules table -> priority numbers -> fixed tiers -> decision table in config
        \                 (same semantics, more discipline)
         -> match tree    (only when rule count or latency forces it)
         -> scope chain    (only when ownership splits)
```

- Chain to table is mechanical and always worth it once you need an audit trail.
- Table to priority is one `sorted()` call plus a schema field; do it when a second team appears.
- Priority to tiers is the change that fixes safety-by-habit; do it **before** the incident.
- Tiers plus scopes is where behavior actually changes: see `03` for the loop-order decision table.
- Config plus grammar is the expensive one; it buys independent release cadence and costs a validator,
  a UI, and a support story.

## Anti-selections

| You are told | It is actually | Reach for |
|---|---|---|
| "make it a state machine" | the transitions have guards | `12` (and guards are a ladder) |
| "use a rules engine" | rules are per-tenant data | `06` |
| "add a priority field" | someone wants a tier they can't name | `13` |
| "just more `elif`s" | the set is closed | `08`/`09` |
| "we need a decision tree" | rules share prefixes | `05` |
| "cascade the config" | ownership is split | `03` |
| "fallback list" | attempts have cost and error classes | `11` |

## Worked picks, three real requests

- *"Do we have tiers between our config sources, and can a user override a platform deny?"* Two ladders
  nested, and the loop order answers it (`13`). Audit the real order first (`20`): config precedence bugs
  are usually an undeclared inner ladder, not a missing feature.
- *"Route model requests; teams can set defaults, users can pin one model; over-budget goes cheap."*
  Scope chain (user, team, global) with priority inside each scope, first-match, `chain_rule` off,
  terminal default route. Audit returns `(route, scope, rule, hops)`.
- *"Gate tool calls: never delete, always confirm writes, everything else allowed."*
  Fixed tiers (deny, ask, allow), tiers outside scopes so a user allow cannot beat a platform deny,
  default `ask`, `matched_count` logged. See `13`.
- *"Classify a fetch result for the UI: pending, loaded, empty, partial, stale, fault, cancelled, plus
  an unknown provider response."*
  State/dispatch matrix keyed on a closed type, with one extra `unknown` handler and a totality test
  enumerating the union. See `08`.
