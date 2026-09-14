# type-up — Typing Principles & Reference

## 1. Layering Model (Universal)

```
┌────────────────────────────────────────────────────────────┐
│  Layer 1: Static / Authoring Types                         │
│  (type aliases, interfaces, structs, records, NewTypes)    │
├────────────────────────────────────────────────────────────┤
│  Layer 2: Runtime Validator                                │
│  (lightweight checks shipped with the library / engine)    │
├────────────────────────────────────────────────────────────┤
│  Layer 3: Schema & Property Tests                          │
│  (dev/CI only — Zod, Pydantic, QuickCheck, Hypothesis…)    │
└────────────────────────────────────────────────────────────┘
```

- **Layer 1** improves editor experience and documentation.
- **Layer 2** protects production paths without heavy dependencies.
- **Layer 3** catches drift and provides generative confidence.

CLI / programmatic patches often deserve their own shape so that file-based config types remain honest.

---

## 2. Semantic Primitive Catalog (Starting Point)

These names are conventions, not mandates. Adapt to the domain.

### Paths & Files

| Intent | Suggested Name | Typical Constraint |
|--------|----------------|--------------------|
| File-system path | `PathLike` | non-empty string |
| Optional ignore file | `GitignorePath` / `IgnorePath` | string or null/None |
| Glob pattern | `GlobPattern` | non-empty |
| File extension | `FileExtension` | starts with `.` |
| Relative path | `RelativePath` | no leading drive / absolute markers |

### Identifiers

| Intent | Suggested Name | Typical Constraint |
|--------|----------------|--------------------|
| Domain ID | `CheckId`, `UserId`, `OrderId` | prefix + charset / UUID / ULID |
| Non-empty text | `NonEmptyString` | length ≥ 1 |
| Opaque token | `Token` / `Secret` | non-empty, never logged |

### Numbers & Enums

| Intent | Suggested Name | Typical Constraint |
|--------|----------------|--------------------|
| Count / workers | `PositiveInt` | integer ≥ 1 |
| Port | `Port` | 1–65535 |
| Mode / strategy | `ScanMode`, `ReporterType` | closed union / enum |
| Status | `StepStatus` | "pass" \| "fail" \| "skip" |

### Opaque Bags

Use `Record<string, unknown>`, `dict[str, Any]`, `map[string]any`, etc. for per-item options that should not couple the core type to every possible extension.

---

## 3. Representation Strategies by Language Family

| Approach | Best when | Languages / Idioms |
|----------|-----------|--------------------|
| **Type alias** | Zero runtime cost, documentation only | Type `type PathLike = string`, Go type alias, Python `TypeAlias` |
| **NewType / Opaque** | Want nominal distinction at type-check time | Python `NewType`, Haskell newtype, Scala opaque |
| **Branded / Phantom** | Nominal typing without runtime wrapper | TS branded types, Rust newtype structs |
| **Refinement / Dependent** | Encode format or range in the type | TS template literals, refined types libraries |
| **Enum / Union** | Closed set of values | All modern languages |

**Trade-off guidance:** Prefer the lightest representation that still communicates intent and catches mistakes. Heavy branding that forces casts on every `.js` / dynamic consumer is usually worse than a well-documented alias.

---

## 4. Interface / Struct Composition Patterns

Keep public shapes composed from the semantic primitives:

```
Config
  ├── PathLike fields
  ├── Identifier fields
  ├── Enum / Mode fields
  └── Nested Step / Item configs (themselves composed)
```

Introduce distinct shapes when layers differ:

- `RawConfig` / `FileConfig` — what the user writes
- `CliPatch` / `Overrides` — what the CLI or API can change
- `ResolvedConfig` — after defaults + validation + merging

---

## 5. Documentation Patterns

Every public type should carry:

1. One-sentence purpose
2. Real-world example (in the language of the consumer)
3. Constraintants that the runtime validator will enforce

Example skeleton (language-agnostic):

```
/**
 * Loaded from <config-file> at project root.
 * Example:
 *   { checksDir: "./checks", scanMode: "changed" }
 */
```

---

## 6. Keeping Layers Synchronized

Maintain an explicit sync table (in docs or code comments):

| Field          | Static Type   | Runtime Check          | Schema / Test          |
|----------------|---------------|------------------------|------------------------|
| checksDir      | PathLike      | non-empty string       | min_length=1           |
| steps[].id     | CheckId       | regex / prefix check   | pattern matching       |
| scanMode       | ScanMode      | enum membership        | enum                   |
| concurrency    | PositiveInt   | integer ≥ 1            | int + positive         |

When a field changes, update all three columns in one commit/PR.

---

## 7. Anti-Patterns

| Avoid | Prefer |
|-------|--------|
| Bare `string` / `int` on public surfaces | Semantic alias or NewType |
| Only static types, no runtime enforcement | Lightweight validator + schema tests |
| Heavy branded types that break dynamic consumers | Alias + documentation + runtime checks |
| Duplicated magic strings / enums in many files | Single source of truth constant or enum |
| Validation only in the heaviest schema library | Production-safe lightweight checks + optional schema |
| Forcing one language’s typing style on all consumers | Polyglot-friendly representations |

---

## 8. Trade-off Spectrum: Typing Rigor

```
Untyped / Dynamic
    → Lossy primitives (string, int, bool)
        → Semantic aliases + docs
            → NewType / Branded / Opaque
                → Refinement / Dependent types
                    → Full formal verification
```

Most production systems land productively in the middle three bands. Choose the band that matches the cost of a mistake and the consumer mix (static vs dynamic languages).
