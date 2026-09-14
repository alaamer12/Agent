# Polyglot Language Conventions Template

Use this universal template when drafting language conventions for any target application. Replace placeholders (`<...>`) with the application's concrete language choices.

```markdown
# <Language> Implementation Conventions — <Application Name>

> **Runtime / Toolchain:** <e.g. .NET 10 / Node 22 / Go 1.23 / Rust 1.82 / Python 3.13>
> **Target Version:** <e.g. C# 14 / TypeScript 5.6 / Go 1.23>
> **Analysis & Strictness:** <Strict / Zero-warning tolerance>

---

## 1. Toolchain, Tooling & Code Hygiene

Directives and flags ensuring strict verification, eliminating warning debt and accidental behavior:

<!-- Specify toolchain flags (e.g. strict mode, treat warnings as errors) AND required tools (linter, formatter, docstyle) -->

### 1.1 Tooling Suite
- **Linter:** `<e.g. eslint / ruff / golangci-lint / clippy / dotnet-format>`
- **Formatter:** `<e.g. prettier / ruff format / gofmt / rustfmt / csharpier>`
- **Docstyle:** `<e.g. tsdoc / pydocstyle / godoc / rustdoc / xmldoc>`

### 1.2 Compiler Directives & Build Configuration
| Configuration Directive | Standard & Invariant Enforced |
|---|---|
| `<Strict / Null-check Flag>` | Explicit absence only; no implicit unchecked nulls/nils. |
| `<Warnings-As-Errors Flag>` | Zero compiler warning debt; warnings break build. |
| `<Modern Language Version>` | Enables contemporary idiomatic idioms and performance optimizations. |
| `<Module / Namespace Isolation>` | Enforces explicit import hygiene and boundary encapsulation. |

---

## 2. Typing Rigor Spectrum & Type Declaration Hierarchy

### 2.1 Typing Rigor Tier
Define the application's required typing rigor:
- **Tier 1 (Lossless / Branded / NewType):** Domain primitives wrapped in semantic branded types (e.g. `UserId`, `ProjectId`, `PositiveInt`).
- **Tier 2 (Strict Standard Typing):** Static types everywhere, full signatures, disallowing untyped `any` / dynamic types.
- **Tier 3 (Lossy / Basic Typing):** Primitive scalar types (`int`, `string`), discouraged for critical domain invariants.

### 2.2 Type Declaration Decision Hierarchy
Map application concepts into appropriate language constructs:

```text
Is it a pure data carrier with value equality semantics?
├── Yes, compact / stack-friendly → <record struct / readonly struct / value type / plain type>
├── Yes, heap-allocated / domain model → <record / immutable class / dataclass / struct>
└── No → continue ↓

Does it encapsulate state + operational behavior / service?
├── Yes, service worker / singleton → <sealed class / struct with unexported fields / final class>
├── Yes, extensible domain foundation → <abstract class / open trait>
└── No → continue ↓

Does it define a contract between application layers?
└── Yes → <interface / protocol / trait>
```

### Invariants:
1. **Closed by default:** Types are not inheritable unless designed explicitly for extension (`sealed` / `final`).
2. **Immutability by default:** Properties and members cannot be mutated after construction unless explicitly mutable by design.
3. **Canonical construction:** Constructors / factory functions must enforce domain invariants before returning the instance.

---

## 3. Public API Boundaries & Collection Contracts

Public application boundaries (controllers, service interfaces, public methods) must expose immutable, non-leaking contracts:

| Conceptual Structure | Allowed Public Return Type | Allowed Parameter Type | Prohibited Across Boundaries |
|---|---|---|---|
| Sequential list | `<Read-only sequence / immutable slice>` | `<Iterable / Collection abstraction>` | Mutable arrays, internal raw lists |
| Key-value dictionary | `<Read-only map>` | `<Read-only map>` | Mutable raw hash maps |
| Uniqueness set | `<Read-only set>` | `<Read-only set>` | Mutable sets |
| Stream / Generator | `<Async stream / Channel consumer>` | `<Async sequence abstraction>` | Unbounded eager collections |
| Optional value | `<Nullable type T? / Option<T>>` | `<Nullable type T? / Option<T>>` | Magic sentinels (`-1`, empty string) |

---

## 4. Nullability & Guard Clauses

1. Non-nullability is the default baseline for all types.
2. Every nullable or optional type must be explicitly checked before use; blind force-unwrapping is banned.
3. Validate invariants at method boundaries using standard assertions or guard helpers.

---

## 5. Async & Concurrency Discipline

1. **Non-blocking execution:** Never perform synchronous blocking on top of asynchronous tasks or futures.
2. **Cancellation propagation:** Every asynchronous operation accepts cooperative cancellation tokens or contexts (`CancellationToken`, `AbortSignal`, `context.Context`).
3. **Structured concurrency:** Tasks must have bounded lifecycles managed by scoped orchestrators, channels, or worker pools.

---

## 6. Naming & Organization

- Follow the target language's idiomatic casing conventions consistently.
- Organize types into predictable module or folder boundaries matching application layers.
```
