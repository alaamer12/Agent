# Semantic Types Template

Use this as a starting skeleton when introducing professional typing to a new public surface.

## 1. Primitive Aliases / NewTypes

```
PathLike          // non-empty path
GlobPattern       // non-empty glob
Identifier        // domain-specific ID with format constraint
PositiveInt       // integer ≥ 1
NonEmptyString    // length ≥ 1
Mode / Status     // closed enum or union
```

## 2. Public Shape

```
Config / Contract
  - fields using the semantic primitives above
  - nested item configs composed the same way
  - optional vs required clearly marked
```

## 3. Layered Variants (if needed)

- Raw / File config (what the user authors)
- Patch / Override (CLI or API mutations)
- Resolved (after defaults + validation)

## 4. Sync Table

| Field | Static Type | Runtime Check | Schema |
|-------|-------------|---------------|--------|
| ...   | ...         | ...           | ...    |

## 5. Documentation Snippet for Consumers

Show the idiomatic way to annotate or import the type in the consumer language(s).
