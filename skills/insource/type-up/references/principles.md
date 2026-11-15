# Principles — the doctrine, both modes

The rules every type-up task runs on, stated once here. Mechanism choice lives in [wrong-type-errors](wrong-type-errors.md); the golden rule's how in [reuse-before-create](reuse-before-create.md); the opt-in tiered architecture is its own skill (`/tier-up`); words in [terminology](terminology.md).

Turn raw-type fields into a documented, validated type system that helps editors, authors, runtime safety and CI — while staying practical for consumers. Use it for configuration shapes, public APIs, domain contracts, CLI patches, and any shared surface where intent is lost behind `string` / `int` / `bool`. **Not for:** pure internal implementation details with no shared surface — keep those lightweight.

## 1. The one-line rule per law

- **Compiler first, runtime last.** Say it with: a built-in or ecosystem type → a closed set → a nominal type → a literal check; a runtime check only where data originates at runtime. The ladder and per-language proof: [wrong-type-errors](wrong-type-errors.md). No function per type is required.
- **Ordinary functions take brands in their signatures.** The compiler rejects a plain value or a swapped argument. A creation point exists only where a runtime value must enter, in the ecosystem's idiom (type guard, library parse, `TryFrom`), never as a mandatory `toX` per type.
- **Make each micro-decision once.** Module A lowercasing and module B not lowercasing is a bug review cannot see. Whenever you catch yourself making a small choice about a value (case, range, unit, sign, timezone, trimming, truncating), promote it into a named rule.
- **Multiple checks, one rule.** Static types (authoring) → runtime creation points (production) → schema / property tests (dev/CI) enforce the same rule without each restating it; keep them synchronized (§7).
- **Zero or minimal runtime cost in the core.** Brands are type-only; creation points are lightweight; heavy validation libraries stay optional and, when the project uses one, are the implementation ([tooling](tooling-adaptation.md)).
- **Document with examples.** Every public type or config field shows real usage: one-sentence purpose, a real example in the consumer's language, the constraints its creation points enforce (JSDoc / docstring / godoc / rustdoc form).
- **Adopt per surface, fully.** A half-branded struct teaches developers which fields "really" need care; partial adoption is worse than none on that surface.

## 2. The three checks

```
┌────────────────────────────────────────────────────────────┐
│  Check 1: Static / authoring types                         │
│  (aliases, interfaces, structs, records, NewTypes)         │
├────────────────────────────────────────────────────────────┤
│  Check 2: Runtime (creation points, boundary checks)       │
│  (lightweight checks shipped with the library / engine)    │
├────────────────────────────────────────────────────────────┤
│  Check 3: Schema & property tests                          │
│  (dev/CI only — Zod, Pydantic, QuickCheck, Hypothesis…)    │
└────────────────────────────────────────────────────────────┘
```

Check 1 improves editor experience and documentation; check 2 protects production paths without heavy dependencies; check 3 catches drift and provides generative confidence. CLI / programmatic patches deserve their own shape so file-based config types remain honest.

## 3. Naming — describe the role, follow the ecosystem

These docs describe **roles**; the identifiers in examples (`PlainString`, `UserEmail`, `toX`, `parseX`, `…Schema`) are illustrative, not conventions to copy.

1. **Name what it is**, descriptively. Do not import a prefix or suffix scheme (`Plain…`, `to…`, `parse…`, `…Lit`, `…Schema`) because these docs used one.
2. **The project's existing names win**; then the ecosystem's idioms, casing and file-naming (`snake_case` in Python and Rust files, `PascalCase` types in TypeScript, exported-capital rules in Go).
3. **Reuse the ecosystem's own types** for failure and absence (`Either`, `Result`, `Option`, `Maybe`); never define a parallel one.
4. **`PlainX` in these files is shorthand** for "the plain type of raw type X" — a deliberate "any value" marker, not a naming scheme to adopt.
5. **One naming scheme per project**, written in the catalog.

## 4. Representation strategies

Prefer the lightest representation that communicates intent and catches mistakes.

| Approach | Best when | Languages / idioms |
|----------|-----------|--------------------|
| **Built-in / library type** | the language or ecosystem already expresses the rule | TS `Uppercase<string>`, template literals, `URL`; Python `Literal`, `pathlib.Path`; Rust `NonZeroU32`; see [reuse-before-create](reuse-before-create.md) |
| **Type alias** | zero runtime cost, documentation only ("any value" visible) | TS `type`, Go alias, Python `TypeAlias` |
| **NewType / opaque** | nominal distinction at type-check time | Python `NewType`, Haskell newtype, Scala `opaque`, Kotlin value class |
| **Brand / phantom** | nominal typing without a runtime wrapper | TS branded intersection, Rust newtype struct |
| **Refinement / dependent** | encode a generic state in the type | TS template literals, refined-type libraries (Scala Iron) |
| **Enum / union** | closed sets of allowed values | all modern languages |
| **Tagged union** | cases carrying different data | TS discriminated union, Rust `enum`, Go sealed interface, Python `Literal` + dataclasses |

Heavy branding that forces casts on every dynamic consumer is usually worse than a well-documented alias plus a runtime creation point. (When the project adopted the tiered architecture, its laws fix which representation goes where — `/tier-up`.)

## 5. Composing surfaces and variants

Keep public shapes composed from named types, never raw fields:

```
Config / Contract
  ├── path fields, identifier fields, closed-set fields   (brands)
  ├── nested item configs composed the same way
  └── optional vs required clearly marked
```

When one shape lives in more than one version, name the **variants** instead of loosening one type: `RawConfig` (unvalidated input), `ConfigPatch` (CLI/API overrides, all optional), `ResolvedConfig` (after defaults + validation). Only the resolved variant circulates inside the app; the boundary mechanics: the boundary stage of `/tier-up`'s migration path.

## 6. Brand catalog — starting names, illustrative

Adapt to the domain; verify the constraint against the project before reusing a row.

| Intent | Suggested name | Built from | Constraint |
|--------|----------------|-----------|------------|
| File-system path | `PathValue` / `PathLike` | non-empty text | non-empty |
| Glob pattern | `GlobPattern` | non-empty text | non-empty |
| File extension | `FileExtension` | lowercase text | starts with `.` |
| Relative path | `RelativePath` | non-empty text | no drive or leading root |
| Domain id | `UserId`, `OrderId`, `CheckId` | non-empty text | prefix + charset / UUID / ULID |
| Count / workers | `WorkerCount` | positive int | upper bound |
| Port | `Port` | positive int | 1–65535 |
| Money amount | `MinorUnits` | int | currency minor units, never floats |
| Non-empty text | `NonEmptyString` | text | length ≥ 1 |
| Mode / strategy | `ScanMode`, `ReporterType` | closed set | enum / literal union |
| Status | `StepStatus` | closed set | pass \| fail \| skip |
| Opaque token / secret | `Token`, `Secret` | non-empty text | never logged |

Opaque bags for per-item extension options (`Record<string, unknown>`, `dict[str, Any]`, `map[string]any`) get a **name** (`ExtensionOptions`) — an anonymous bag is a raw type in disguise.

## 7. Keeping the checks synchronized

One change to a rule updates types, creation points, and schema together. Keep a small sync table (docs or comments):

| Field | Static type | Runtime check | Schema / test |
|-------|-------------|---------------|---------------|
| checksDir | `PathValue` | non-empty | `min_length=1` |
| steps[].id | `CheckId` | prefix regex | pattern match |
| scanMode | `ScanMode` | enum membership | enum |
| concurrency | `WorkerCount` | int ≥ 1 | `int().positive()` |

When a field changes, update every column in one commit/PR. (The tiered architecture keeps this table as its **catalog** — `/tier-up` extends it with built-from, policy and users.)

## 8. Workflow — definition of done

```
- [ ] 1. Inventory   every property, current type, real-world constraint and invariant
- [ ] 2. Name        the brand or existing type for each meaning (§6, golden rule first)
- [ ] 3. Represent   choose the lightest strategy per language (§4)
- [ ] 4. Compose     public shapes from named types; mark optional/required; variants if needed (§5)
- [ ] 5. Mirror      creation points enforce the same constraints, production-light (§1, ladder)
- [ ] 6. Test        schema / property / negative tests for each rule (§2, check 3)
- [ ] 7. Sync        document usage; the §7 table or catalog is current — one change, one commit
```

Typical layout: one `types/` or `contracts/` folder per surface — public type definitions, shared brands, the validation schema, lightweight checks, and their tests. The tiered architecture's folder law: `/tier-up`.

**Done means:** no unvalidated outside data flows inward; each rule lives in one place; the three checks cover it; no raw types on public fields where a domain meaning exists; consumers use the types without friction (no mandatory casts in common cases).

## 9. Anti-patterns — master list

| Avoid | Prefer |
|-------|--------|
| Bare `string` / `int` / `bool` on public surfaces | a named type that carries the rule |
| Only static types, no runtime enforcement | creation points at boundaries + schema tests |
| Heavy branded types that break dynamic consumers | alias + documentation + runtime check at the boundary |
| Duplicated magic strings / enums across files | one constant, enum, or brand |
| Validation only inside the heaviest schema library | production-light checks; library derived from or tested against them |
| Forcing one language's typing style on all consumers | per-ecosystem representation (§4) |
| A rule in a comment ("must be lowercase") | the rule in a creation point the compiler enforces |
| Partial adoption across a surface | adopt it fully or leave it (§1) |

Tier-architecture mistakes live with that skill (`/tier-up`).

## 10. The rigor spectrum

```
Untyped / dynamic
  → visible raw-type names        audit marker, no safety yet
    → brands + creation points    rules enforced at boundaries        (this skill)
      → nominal + refinement      kinds, signs and ranges in the type
        → the tiered architecture raw types confined, meanings branded,
                                  structures shaped                   (/tier-up)
        → refinement/dependent types, formal verification
```

Most production systems land productively in the middle bands. Pay for as much rigor as the cost of a mistake, the lifespan of the code, and the number of modules sharing the data justify; skip it for throwaway scripts. The cost is more code to write, manage and remember; the return is the micro-decision bugs that never reach production.
