# 06 — Decision table in config (the ladder as data with a bounded grammar)

The rungs leave the codebase entirely: rules live in YAML, JSON, or a database row, conditions are
written in a small expression language, and a non-developer can edit the ladder without a deploy.

## Shape

```yaml
ladder:
  matching: first            # first | all | unique-error
  ordering_key: tier+priority
  terminal: ask              # the answer when nothing matches - never omit this key
  facts:                     # the schema rungs may read; unknown field = load-time error
    tool:   { type: enum, values: [bash, read, write, net] }
    cmd:    { type: string }
    budget: { type: integer, min: 0, max: 100 }
  tiers: [{ name: deny, rank: 1 }, { name: ask, rank: 2 }, { name: allow, rank: 3 }]
  rules:
    - id: rm-rf
      tier: deny
      when: { field: cmd, op: starts, value: "rm -rf" }
      then: { verdict: deny, message: "deletion needs an explicit yes" }
      owner: platform
      source: policies/safety.yaml
```

## The grammar is the safety property

**Bounded, pure, total. No host functions.** Field/op/value triples plus `all` / `any` / `not` cover
most needs and stay analyzable; a Turing-complete condition language does not.

```python
def eval_condition(node, facts):
    if isinstance(node, dict) and "all" in node:
        return all(eval_condition(c, facts) for c in node["all"])
    if isinstance(node, dict) and "any" in node:
        return any(eval_condition(c, facts) for c in node["any"])
    field, op, want = node["field"], node["op"], node["value"]
    if field not in facts:
        raise UnknownField(field)        # fail closed at load/eval, never a silent false
    return OPS[op](facts[field], want)   # OPS is a fixed dict: eq ne gt lt in starts matches
```

| Language | Reach for it when | What you inherit |
|---|---|---|
| field/op/value triples + all/any/not | few authors, simple facts | your own validator (that's fine, and cheap) |
| JSONLogic | rules exchanged between services | a spec, not a compiler |
| **CEL** (Common Expression Language) | policy in Kubernetes-ish infra, need typed totals | no loops, no side effects, error-tolerant evaluation |
| **Rego / OPA** | policies must be queried, explained, and tested at scale | a real language, a real learning curve |
| **Cedar** | authorization with `permit`/`forbid` and deny-overrides built in | default-deny semantics you do not have to write |
| SpEL / MVEL / DRL | you already run Spring/Drools | arbitrary host calls unless you lock the receiver down |

The last row is the trap: `when: "T(java.lang.Runtime).getRuntime()..."` is a valid SpEL expression.
If the grammar can call your process, the config file is a code-execution surface with a friendly UI.

## Validation, at load time

1. **Schema-validate** every rule (id pattern, known tier, known op for that field's type, verdict matches
   tier semantics). Unknown keys are errors, not warnings - a typo'd `prority` silently drops an ordering key.
2. **Field-validate** every `when` against the declared `facts` schema. An unreachable field means the
   rule can never fire: refuse the load or quarantine the rule and report it.
3. **Uniqueness** on `id`; **collisions** on `(tier, scope, priority)` reported, with the tie-break printed.
4. **Totality**: require a `terminal`/`default` key in the document, not an implied one.
5. **Owners**: `owner` and `source` per rule, because a rule you cannot attribute is a rule you cannot delete.
6. **Round-trip test**: load the production file in CI and assert the parsed rule count and the resolved
   verdict for a fixture set of facts. Config bugs then fail a build instead of failing a user.

## Pick it when

- Business, risk, support, or growth edit decisions; a deploy per rule change is the bottleneck.
- Rules are per-tenant rows in a database and are read at request time.
- You need the ladder to be diffable, exportable, and replayable as data.

Do not pick it when the conditions need the host language (awaits, sessions, domain methods) - a
grammar that grows methods is a programming language, and you will pay for it twice.

## Failure modes

- **Indentation-as-semantics**: a YAML block moved two spaces changes a rule's tier or scope and still
  parses. Parse with a schema; echo the parsed rule back to the author.
- **Versionless edits**: someone changes a rule and the audit says `rm-rf`, which now means something
  else. Keep `revision`/`updated_by` per rule and log the resolved revision in the audit.
- **Priority in a second file**: rules here, ordering there. One record, one diff.
- **Divergent evaluators**: the engine and the UI preview evaluate differently, so the preview lies.
  Share one evaluator, or make the preview call the engine.
- **Rules that outlive their incident**: `expires` on a temporary rule, or a scheduled report of rules
  that never fire.

## Seen in

DMN decision tables (OMG) with their **hit policies** - `UNIQUE`, `FIRST`, `ANY`, `COLLECT`,
`RULE ORDER`, `OUTPUT ORDER`, `PRIORITY` - which are exactly the semantics choices in `14`; Bifrost
rules carrying `priority`, `enabled`, `chain_rule`; XACML policy sets with combining algorithms;
Cedar and OPA policy files; feature-flag targeting rules; `rules_files`-style per-scope rule storage.
