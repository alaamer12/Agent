# Isolation plan: <scope>

Use this template for big tasks only (whole project, several components, three or more axes, identity or build changes, or a decision the user must make). For a small task, isolate directly and give a short summary instead.

Scope: <project | module path | feature description>. Mode: <audit | plan | refactor>. Language and build system: <detected>.

Options named in `[brackets]` are examples, not a closed list.

## 1. Axis inventory

| Axis | Example values | Total or sparse | Binds at | Open or fixed values | Feeds identity | Evidence |
|---|---|---|---|---|---|---|
| `[axis]` | `[a, b]` | | build / runtime | | yes / no | file or requirement |

Not code (record and set aside): <promotion rings, value-only differences, identical binaries>.

## 2. Level decision

| Axis set | Level | Constraint reached | Reason |
|---|---|---|---|
| `[axis]` | 1 / 2 / 3 | <what forced the next level> | |

## 3. Seams

| Component | Seam (named for what varies) | Contract | Base implementation | Varies by |
|---|---|---|---|---|

## 4. Layout

```
<tree of base, platform files, family files, Layers/, Registration/>
```

Import direction: <one line per rule from layers.md, adapted to the project>.

## 5. Resolution policy

Ambiguity policy: `[strict | fixed precedence | priority numbers]`. Trade-off stated: <one sentence>. Decision: <chosen, by whom>.

## 6. Identity (only if variants coexist)

Identity source: <where>. Axes feeding identity: <list>. Collisions found: <list from the checklist>.

## 7. Verification

Checks added: <list>. Profiles checked in CI: <list>. Command: `<check_layers.py invocation>`.

## 8. Migration order

1. <smallest component first, with the reason>
2. <next>

## 9. Out of scope and open questions

- <what this plan deliberately does not do>
- <question for the user>
