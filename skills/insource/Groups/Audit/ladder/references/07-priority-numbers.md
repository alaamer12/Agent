# 06 — Priority numbers (the engine sorts, the author does not)

Each rung carries a number; the engine sorts by it before evaluating. Order detaches from position,
which is the whole point as soon as rules arrive from several files, teams, tables, or plugins.

## Shape

**Python**

```python
def decide(facts):
    ordered = sorted(RULES, key=lambda r: (r["priority"], r["id"]))  # tie-break: total order
    hit = next((r for r in ordered if r["when"](facts)), None)
    return (hit["then"], hit["id"]) if hit else ("ask", "default")
```

**TypeScript** — sort a copy; sorting in place makes the module's meaning depend on call history.

```ts
const ordered = [...rules].sort((a, b) => a.priority - b.priority || a.id.localeCompare(b.id));
const hit = ordered.find((r) => r.when(facts));
```

**Java** — `Comparator` chain, explicit that identity is the last tie-break.

```java
List<Rule> ordered = rules.stream()
    .sorted(Comparator.comparingInt(Rule::priority).thenComparing(Rule::id))
    .toList();
```

**SQL** — ordering key in the query, so the table's insertion order is irrelevant.

```sql
SELECT id, verdict FROM rules
 WHERE <matching condition>
 ORDER BY priority ASC, id ASC
 LIMIT 1;
```

**YAML config** — the number is data, so the diff shows intent.

```yaml
rules:
  - id: over-budget
    priority: 10          # lower evaluates first
    when: { field: budget, op: gt, value: 80 }
    then: ask
```

## Naming conventions you will meet

| Name | Where | Direction |
|---|---|---|
| priority | routing/gateway engines | usually **ascending**: 0 before 10 |
| salience | Drools | **descending**: higher fires first |
| rank | DMN `PRIORITY` hit policy | output precedence list, highest = most restrictive |
| weight / cost | CLIPS-style engines | engine-dependent |
| administrative distance | network routing | lower = more trusted |

Two directions exist. Write yours next to the field in the schema doc, and if you ingest rules from
elsewhere, **convert at the boundary** and assert the converted order with a test.

## Pick it when

- Rules come from multiple sources and position is meaningless or hostile.
- Non-authors insert rules between existing ones (gaps like 10/20/30 exist for that).
- You must be able to say "why did this win" as a number in a log line.
- The set is a merge of scopes/tenants and you need one global ranking (`03` composes with this).

Do not pick it when one file owns the whole ladder and a reviewer can read the order directly — then
position is simpler and honest (`02`).

## Failure modes

1. **Sort on priority alone.** With duplicates, the winner is whatever the sort's stability plus
   insertion order produced — different database, different answer. Tie-break on identity.
2. **Property-based proof, not vibes**: shuffle the rule list, sort, evaluate; the winner must be
   identical. That test *is* the point of this shape:

```python
def test_order_independence(facts, expected):
    for _ in range(50):
        shuffled = RULES[:]
        random.shuffle(shuffled)
        assert decide(facts, shuffled)[0] == expected
```

3. **Number collisions across teams.** Two owners both use 10. Fix: namespace the number (tier/scope
   first, priority inside), or allocate from a registry.
4. **Negative/large values** used to mean "urgent" while the engine sorts ascending — the urgent rule
   fires last. Say which end is urgent.
5. **Gaps that nobody fills** calcify into a fake ordering convention; document the numbering scheme or
   use a sequence with an "insert before" field instead of raw numbers.
6. **Priority as the only key in a safety ladder** — a lower number cannot outvote a deny tier. Use
   `13` for verdict classes, priority inside them.

## Seen in

Drools `salience` ("rules with a higher salience value are given higher priority when ordered in the
agenda"), Bifrost routing (rules sorted by priority ascending inside each scope), CLIPS conflict
resolution (`salience`, then LIFO, plus named strategies like complexity/simplicity/lex), network
routing administrative distance, CSS specificity as a computed priority number, DMN `PRIORITY` hit
policy.
