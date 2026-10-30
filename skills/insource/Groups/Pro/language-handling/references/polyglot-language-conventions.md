# Language Conventions Reference Guide (Polyglot Principles)

This reference guide establishes the principles and polyglot mappings for generating language conventions across various programming languages.

---

## 1. Toolchain, Tooling & Code Hygiene Across Ecosystems

Application standards must mandate a complete automated code quality toolchain comprising:
1. **Compiler Strictness / Flag Enforcement:** Zero tolerance for warnings (`TreatWarningsAsErrors`, `strict: true`, `-Wall -Werror`).
2. **Linter:** Static analysis catching runtime footguns, concurrency traps, and dead code.
3. **Formatter:** Deterministic formatting tool enforcing uniform layout without stylistic debates.
4. **Docstyle:** Enforced conventions for public API documentation (parameter docs, return comments, example usage).

| Ecosystem | Strict Config | Linter | Formatter | Docstyle Standard |
|---|---|---|---|---|
| **TypeScript / JS** | `tsconfig.json` (`strict: true`) | `eslint` / `biome` | `prettier` / `biome` | TSDoc (`/** ... */`) |
| **Python** | `pyproject.toml` (`mypy --strict`) | `ruff check` / `flake8` | `ruff format` / `black` | Google / NumPy / PEP 257 (`pydocstyle`) |
| **Go** | `go.mod` / CI flags | `golangci-lint` | `gofmt` / `goimports` | GoDoc convention (`// Package ...`) |
| **Rust** | `Cargo.toml` (`clippy::all`) | `cargo clippy` | `rustfmt` | Rustdoc (`/// ...`) |
| **C# / .NET** | `*.csproj` (`<TreatWarningsAsErrors>`) | Roslyn Analyzers / `dotnet format` | `csharpier` / `dotnet format` | XML Documentation (`/// <summary>`) |

---

## 2. Typing Rigor Spectrum: From Untyped to Branded Types

For any language—whether dynamically typed (Python, JS) or statically typed (TypeScript, Go, C#)—the application conventions must define where domain concepts sit along the Typing Rigor Spectrum:

```text
Untyped / Any ───► Lossy / Primitive ───► Strict / Semantic ───► Lossless / Branded (NewType)
```

1. **Tier 0: Untyped / Dynamic (PROHIBITED for application core):**
   - E.g., `any` in TS, untyped `def foo(x):` in Python. Prohibited across all internal domain boundaries.
2. **Tier 1: Lossy Primitives (Permitted only for non-domain scalars):**
   - E.g., using `int` for an entity identifier, `string` for an email address, `int` for positive-only quantities. Prone to parameter-order bugs (`Transfer(fromId: int, toId: int)`).
3. **Tier 2: Strict Semantic / Abstract Types (Required for interfaces & collections):**
   - Python: Using `collections.abc.Sequence[T]`, `collections.abc.Mapping[K, V]`, `pydantic.PositiveInt`.
   - TypeScript: Using `ReadonlyMap<K, V>`, `readonly T[]`.
   - C#: Using `IReadOnlyList<T>`, `IReadOnlyDictionary<K, V>`.
4. **Tier 3: Lossless / Branded / NewType (Required for domain IDs & units):**
   - **Python:** `UserId = NewType('UserId', int)`
   - **TypeScript:** `type Brand<K, T> = K & { readonly __brand: T }; type UserId = Brand<string, 'UserId'>;`
   - **C#:** `public readonly record struct UserId(long Value);`
   - **Rust:** `struct UserId(u64);`
   - **Go:** `type UserID int64`

---

## 3. Type Hierarchy & Encapsulation Mapping

Different languages implement data modeling and encapsulation with different keywords, but the architectural intent remains identical:

| Architectural Role | C# | TypeScript | Go | Rust | Kotlin |
|---|---|---|---|---|---|
| **Immutable Value / DTO** | `record struct` / `record` | `type T = Readonly<{...}>` | `type T struct` (unexported fields) | `#[derive(Clone, PartialEq)] struct T` | `data class T(...)` |
| **Closed Service / Worker** | `sealed class` | `class T` (not exported for subclassing) | `type T struct` (pointer receiver) | `struct T` (implementing methods) | `class T` (final by default) |
| **Open Domain Base** | `abstract class` | `abstract class` | N/A (prefer composition) | Traits with default methods | `abstract class` |
| **Cross-Layer Contract** | `interface` | `interface` | `type Interface interface` | `trait` | `interface` |

---

## 3. Polyglot Public Boundary Contracts

Never leak internal mutable collections or unvalidated representations across public boundaries:

### Examples Across Languages:

#### C#
- **Leaky (Prohibited):** `public List<Order> GetOrders()`
- **Encapsulated (Required):** `public IReadOnlyList<Order> GetOrders()`

#### TypeScript
- **Leaky (Prohibited):** `getOrders(): Order[]`
- **Encapsulated (Required):** `getOrders(): readonly Order[]` (or `ReadonlyArray<Order>`)

#### Go
- **Leaky (Prohibited):** `func (s *Service) GetOrders() []Order` (caller can mutate the slice)
- **Encapsulated (Required):** Return cloned slices, or use accessor iterator functions `func (s *Service) Orders(yield func(Order) bool)`

#### Kotlin
- **Leaky (Prohibited):** `fun getOrders(): ArrayList<Order>`
- **Encapsulated (Required):** `fun getOrders(): List<Order>` (immutable Kotlin collection interface)

---

## 4. Nullability & Guard Disciplines Across Languages

| Language | Nullability Model | Safe Handling & Guard Idiom | Blind Force-Unwrapping (PROHIBITED) |
|---|---|---|---|
| **C#** | Nullable Reference Types (`T?`) | `ArgumentNullException.ThrowIfNull(arg)` | `arg!` |
| **TypeScript** | Strict Null Checks (`T \| null \| undefined`) | `if (!arg) throw new Error(...)` or type guards `assertIsDefined(arg)` | `arg!` |
| **Go** | Explicit `nil` & error returns | `if arg == nil { return ErrInvalidArgument }` | Blind pointer dereferencing without check |
| **Rust** | `Option<T>` & `Result<T, E>` | Pattern matching or `?` operator | `.unwrap()` in production code |
| **Kotlin** | First-class null safety (`T?`) | `requireNotNull(arg) { "..." }` | `arg!!` |

---

## 5. Async, Concurrency & Cancellation Across Languages

Every asynchronous operation must provide cooperative cancellation and avoid blocking:

- **C#:** Accept `CancellationToken ct = default` in every async method. Never call `.Result` or `.Wait()`.
- **TypeScript:** Accept `signal?: AbortSignal` for all async operations (fetch, worker loops). Never leave promises unhandled.
- **Go:** Accept `ctx context.Context` as the first parameter of any I/O or goroutine-spawning function. Propagate context down.
- **Rust:** Pass async futures through async runtimes (`tokio`), supporting cancellation tokens (`tokio_util::sync::CancellationToken`).
