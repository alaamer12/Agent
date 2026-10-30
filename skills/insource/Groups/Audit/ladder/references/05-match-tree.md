# 05 — The match tree (nested conditions)

Conditions arranged as a tree instead of a list: each node tests one observable, dispatches on its
value, and leaves hold decisions. Used wherever many rules share a first test.

## Shape

```
                       ┌ "bash" ── cmd ──┬ "rm -rf*" ──── DENY
        tool ──────────┤                 ├ "git push*" ── ASK
                       │                 └ * ──────────── ALLOW
                       ├ "read" ───────────────────────── ALLOW
                       └ * ────────────────────────────── ASK
```

**Python** — exact child first, wildcard as fallback; the path and node count come free.

```python
def observe(node, facts, path):
    value = facts.get(node.test)
    if value is None:
        return None
    child = node.children.get(value) or node.children.get(WILDCARD)
    if child is None:
        return None
    path.append(f"{node.test}={value}")
    return (child, path) if isinstance(child, Leaf) else observe(child, facts, path)
```

**Go** — a map of children, so the wildcard is an explicit second lookup rather than a loop order.

```go
func observe(n *Node, facts Facts, path *[]string) (*Leaf, bool) {
	v, ok := facts[n.Test]
	if !ok {
		return nil, false
	}
	child, found := n.Children[v]
	if !found {
		child, found = n.Children["*"]
	}
	if !found {
		return nil, false
	}
	*path = append(*path, n.Test+"="+v)
	if leaf, isLeaf := child.(*Leaf); isLeaf {
		return leaf, true
	}
	return observe(child.(*Node), facts, path)
}
```

**SQL** — a tree is just a self-referencing table; recursive CTE walks it to a leaf.

```sql
WITH RECURSIVE walk AS (
  SELECT id, parent_id, test, decision, 1 AS depth
    FROM nodes WHERE parent_id IS NULL
  UNION ALL
  SELECT n.id, n.parent_id, n.test, n.decision, w.depth + 1
    FROM nodes n JOIN walk w ON n.parent_id = w.id
   WHERE n.edge = (SELECT v FROM facts WHERE facts.node = w.id) OR n.edge = '*'
)
SELECT decision FROM walk WHERE decision IS NOT NULL ORDER BY depth DESC LIMIT 1;
```

## Pick it when

- Many rungs share a prefix test ("is this bash?") and you evaluate it once instead of per rule.
- Rules are naturally hierarchical: file paths, IP prefixes, taxonomies, DOM/AST node types.
- Latency matters and the list is long: cost becomes O(depth) instead of O(rules).
- You want specificity to be **structural** (exact child beats wildcard) instead of positional.

Do not pick it when the logic is genuinely linear (a validation sequence), when authors must read the
rules in order (use `02`/`06`), or when a flat list is under ~10 rungs.

## The one rule that decides whether the tree is safe

**Exact before wildcard, always.** If children are consulted in declaration order and the wildcard is
declared first, every specific branch below it is dead code — the same shadow defect as a flat list,
now hidden inside a data structure. Two mitigations, both cheap:

```python
def dead_children(node):
    """A wildcard declared before its siblings shadows them under a positional walk."""
    if WILDCARD in node.children and next(iter(node.children)) == WILDCARD:
        return [f"{node.test}={k}" for k in node.children if k != WILDCARD]
    return []
```

- Resolve by lookup (exact, then wildcard) — order in the file becomes a lint, not a bug.
- Keep the flat rule list as the source of truth and **compile** the tree from it. The tree is a build
  artifact; a hand-edited tree is unauditable and undiffable.

## Failure modes

- **Leaf-less branch**: a node whose every child misses. Decide: return no match (fall through to the
  next structure) or error. Silently returning `None` and letting the caller treat it as "allow" fails open.
- **Path explosion**: 32768 children under one node means the observable is not the right discriminator.
- **Two leaves through different paths**: no natural priority story. Resolve by longest path, by
  most-matched-fields, or refuse with an ambiguity error (XACML's `only-one-applicable`).
- **Predicate with effects in a node**: a node that mutates on the way down makes the walk
  non-replayable; trees are often walked twice (validation + execution).
- **Cost claim unverified**: measure nodes-visited against list comparisons on real data before
  claiming the win. In my own fixture the tree won at 3 rules and would win more as the table grows.

## Testing

For every leaf, assert a fact set that reaches it (reachability) **and** that the recorded path is the
expected path. Add one deliberate shadow case and assert the detector finds it, or the detector is
untested code.

## Seen in

Packet-classification and firewall engines (the `tcv` family of algorithms), IP routing tries and
longest-prefix-match tables, URL routers (trie per path segment), CSS selector matching, ML decision
trees, contract/permission wildcard rules, and policy engines that store "condition nodes with an
observed value, a pattern, and child nodes ending in a decision leaf".
