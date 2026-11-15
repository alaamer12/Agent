# Tiered Types Template

> **For the tiered system** (this skill). For general type enhancement without the tiers, use `/type-up`.

Skeleton for introducing the three-tier type system to a new surface. Names below are illustrative roles: use the project's and ecosystem's own names and types, and prefer a type the compiler already provides.

## Structure (example names; the project's convention wins)

```
shared/types/primitives/    tier 1, only here
shared/types/brands/        tier 2 used by two or more features
shared/types/shapes/        tier 3 used by two or more features
features/<owner>/types/brands/   tier 2 owned by one feature
features/<owner>/types/shapes/   tier 3 owned by one feature
```

See [structure](../../references/tiers.md#2-structure--where-the-tier-folders-go).

## Tier 1: primitives (one file per primitive family)

```
primitives/string.<ext>
  PlainString
  UppercaseString  LowercaseString  NonEmptyString      (visible states only; trim/truncate are creation point steps)

primitives/number.<ext>
  PlainNumber
  IntNumber  FloatNumber (finite)
  PositiveIntNumber  PositiveFloatNumber  NonNegativeIntNumber …

primitives/boolean.<ext>
  PlainBoolean
```

Each refinement gets one creation point and a stated policy (normalize / reject).

## Tier 2: brands (one file per domain area)

```
<Domain><Meaning> = <refinement> + brand
```

Examples: `UserIso`, `UserEmail`, `UserDisplayName`, `UserAge`, `Port`, `OrderId`.
Closed sets: unions / enums of literals (`ScanMode`, `StepStatus`).

## Tier 3: shapes

```
<Name>Schema     fields = tier 2 brands
<Name>State      tagged union: each case carries only its own data
<Name>Patch      overrides, kept separate from the main shape
```

## Boundary check (placed next to the shape, or beside the service)

```
parse<Name>(raw: unknown | PlainX…): Result<<Name>Schema>
```

One per boundary (network, storage, env, forms, CLI).

## Catalog (update in the same commit as the code)

| Name | Tier | Built from | Creation point | Policy | Used by |
|------|------|-----------|-------------|--------|---------|
| ...  | ...  | ...       | ...         | normalize / reject | ... |

## Checks

- [ ] Lint: raw types only in tier 1 files
- [ ] Lint: brand casts only inside creation points
- [ ] Lint: `PlainX` only in tier 1 and in boundary check files
- [ ] Property tests for every creation point
