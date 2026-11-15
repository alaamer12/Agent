# Tier 1: Primitives

> **Applies when the project adopts the tiered system** (Mode B in `../SKILL.md`). For general type enhancement without the tiers, use `../references/core-workflow.md`.

> The only tier that names a raw language type. Everything above is built from what is defined here.

*Standing note: names, file extensions and layouts below are illustrative. Adapt identifiers to the language's conventions (`PlainString` / `plain_string`), and any `[bracketed]` option is an example, not a closed set; a hybrid or different answer is always acceptable.*

Identifiers in examples (`PlainX`, `toX`, `parseX`, `…Schema`) are illustrative role names, not conventions: follow the project's and ecosystem's own names and types ([naming](../references/tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). Prefer a type the compiler already provides ([compiler first](../references/wrong-type-errors.md)).

Creation points may be hand-written (shown here) or built with the project's validation library: see [use the project's tools](../references/tooling-adaptation.md).

## Purpose

Own the **generic visible states** a value can be in: case, integer-ness, sign, finiteness, emptiness. A rule that mentions a domain noun (user, order, port) belongs in [tier 2](./tier-2-brands.md).

## Rules (language-independent)

1. **One file per primitive family** (string, number, boolean, bigint, date). The raw type is named in its own file and nowhere else.
2. **First export is the plain type** (`PlainX` here), a plain rename. A one-line file is complete; add no logic to justify it. If the project already names it, or the language's own type serves, use that. **Use a plain type in a signature only when any value of the raw type is acceptable**; if the code needs an integer, a float, a sign or a range, name that refinement (`IntNumber`, `FloatNumber`, `PositiveFloatNumber`).
3. **Refinements form chains.** Each step narrows the previous one and adds one rule.
4. **Up is free, down is a checked step.** A refined value is usable wherever its parent is; the reverse goes through the refinement's creation point (or a compile-time-verified literal).
   - Languages with structural / intersection typing: up is implicit.
   - Languages with nominal wrappers: up is an explicit, total, zero-cost conversion (`as_int()`, `From`).
5. **Prefer a type the compiler already provides** (`Uppercase<string>`, a template literal type, a refined-type library type). Define a wrapper only when nothing built-in expresses the state.
6. **One creation point per refinement for runtime values**, the only place a cast or wrapper is created. A refinement fed only by literals or built-in types needs none.
7. **Hard edge cases are decided here, once** (`NaN`, `±Infinity`, `-0`, what counts as an empty string).
8. **Chains may be linear or stacked.** (TypeScript note: the brand marker must hold a *set* of names, as in the helper below; a marker holding one literal per brand makes any stacked brand collapse to `never`.) Where the type system supports intersections, shared markers let rules stack independently (`Int` + `Positive`); where it does not, use a linear chain (`PlainNumber → IntNumber → PositiveIntNumber`) and add named steps as needed.H. **Reuse before you create** (golden rule). If the language, standard library or a project dependency already provides the refinement (`Uppercase<string>`, Pydantic `PositiveInt`, Rust `NonZeroU32`), use it and add only what it lacks. Tier 1 is the only tier that names the existing type: re-export it here under the project's name, and tiers 2 and 3 import it from tier 1, never from the library ([reuse-before-create](../references/reuse-before-create.md)).

## What qualifies as a refinement: the distinguishability test

A tier 1 refinement names a **state the value shows**, not an **operation that was applied to it**.

Look at one value on its own and ask: can you tell from the value alone which side it is on, and do the two sides look different?

| Candidate | Can you tell by looking? | Verdict |
|-----------|-------------------------|---------|
| `"hello-world"` vs `"HELLO-WORLD"` | yes: the case is in the content | `LowercaseString`, `UppercaseString` are real |
| `""` vs `"hello"` | yes | `NonEmptyString` is real |
| `1.5` vs `1` | yes | `IntNumber` is real |
| `-5` vs `5` | yes | `PositiveIntNumber` is real |
| `NaN` vs `3.2` | yes | finite `FloatNumber` is real |
| `"hello-world"` as plain, **trimmed** or **truncated** | no: nothing in the result records what was done to it | not a thing |

A trimmed or truncated string is an ordinary string. `"hello-world"` could have been typed that way, trimmed, or cut to length, and no one can tell, so there is nothing for a type to represent. The same holds for any operation: sanitized, escaped, decoded, collapsed, Unicode-normalized, deduplicated.

Rules that follow:

- **Operations are steps inside a creation point**, never types. `toUserEmail` trims, lowercases, then validates; the brand `UserEmail` states only the outcome (a valid, lowercase email).
- If a domain needs "no edge whitespace" or "at most N characters" as a **guarantee**, state it as a rule of a **tier 2 brand** (`DisplayName` rejects over-long input); do not create `TrimmedString` or `TruncatedString`.
- Quick check before adding a refinement: write two example values, one inside and one outside. If you cannot make them look different without describing their history, it is an operation.

## Project structure and placement
*Folder names are example names: this skill prefers `primitives/`, `brands/` and `shapes/`, but the project's own convention wins, and for brands the ecosystem's own word is fine (`newtypes/`, `opaque/`). Source folders unrelated to types are hidden below. Full layout and rules: [structure](../references/tier-principles.md#structure-where-the-tier-folders-go).*

Tier 1 lives in **one place only**: the shared types folder, even when the rest of the project is organized by feature.

```
src/
├── …                                (app, ui, features, and every other source folder: hidden)
└── shared/
    └── types/
        └── primitives/              tier 1: only ever here
            ├── string.<ext>         PlainString + string refinements + creation points
            ├── number.<ext>         PlainNumber + number refinements + creation points
            ├── boolean.<ext>        PlainBoolean
            ├── bigint.<ext>         only if the project uses it
            └── index.<ext>          the public surface for tiers 2 and 3
```

Why one place: a refinement is generic by definition. A rule that only makes sense in one domain is a tier 2 brand and lives with its owner. Lint: a `primitives/` folder under `features/` is an error.

## Example: ordinary functions take the refined type

No function per type is required. The consumer is an ordinary function whose signature names the refined type; that is what makes the compiler say "this is a string, not a lowercase string" or "this is an int, not a positive int". Each language below shows a different primitive family.

**TypeScript, string family** (the compiler already has the state, so there is no brand and no function):

```ts
// primitives/string.ts   ← only file that names `string`
export type PlainString     = string;
export type LowercaseString = Lowercase<string>;

function lookupSlug(slug: LowercaseString) { /* … */ }
lookupSlug("my-post");   // ok
lookupSlug("My-Post");   // error: Argument of type 'string' is not assignable to parameter of type 'Lowercase<string>'
```

**TypeScript, number family** (no built-in exists, so the chain uses brands):

```ts
// primitives/number.ts   ← only file that names `number`
declare const tag: unique symbol;
export type Brand<N extends string> = { readonly [tag]: { readonly [K in N]: true } };   // a set of names, so stacked brands merge
export type PlainNumber       = number;
export type IntNumber         = PlainNumber & Brand<"Int">;
export type PositiveIntNumber = IntNumber & Brand<"Positive">;
export type FloatNumber         = PlainNumber & Brand<"Float">;     // finite: no NaN, no ±Infinity
export type PositiveFloatNumber = FloatNumber & Brand<"Positive">;

function retry(times: PositiveIntNumber) { /* … */ }
retry(3);   // error: Argument of type 'number' is not assignable to parameter of type 'PositiveIntNumber'
```

**Python, number family:**

```python
# primitives/number.py   ← only module that names `int` / `float`
PlainNumber = float
IntNumber = NewType("IntNumber", int)
PositiveIntNumber = NewType("PositiveIntNumber", IntNumber)

def retry(times: PositiveIntNumber) -> None: ...
retry(3)   # mypy: Argument 1 to "retry" has incompatible type "int"; expected "PositiveIntNumber"
```

**Go, string family** (a struct with an unexported field blocks conversion from a plain string):

```go
// primitives/string.go   ← only file that names `string`
type PlainString = string
type NonEmptyString struct{ v PlainString }

func Greet(name NonEmptyString) { /* … */ }
// Greet("")  → compile error: a string constant is not a NonEmptyString
```

**Rust, number family:**

```rust
// primitives/number.rs   ← only file that names `f64`
pub type PlainNumber = f64;
pub struct FiniteNumber(PlainNumber);     // private field

pub fn mean(values: &[FiniteNumber]) -> FiniteNumber { /* … */ }
// mean(&[1.5, 2.0])  → compile error: expected `FiniteNumber`, found a floating-point literal
```

## Where the values come from

A refined value has exactly three possible sources. Only the third needs code, and that code is not a mandated function-per-type:

| Source | Needs a function? | Examples |
|--------|-------------------|----------|
| A literal the compiler verifies | no | `lookupSlug("my-post")`; a template literal type, `Literal`, a `const fn` |
| A more refined value (up is free) | no | a `PositiveIntNumber` passed where an `IntNumber` is expected |
| A runtime value entering | one creation point, in the ecosystem's own idiom | below |

```ts
function isPositiveInt(n: PlainNumber): n is PositiveIntNumber { return Number.isInteger(n) && n > 0; }
if (isPositiveInt(input)) retry(input);          // TypeScript: a type guard narrows
```
```python
def positive_int(n: int) -> PositiveIntNumber | None:      # Python: the one place a runtime int enters
    return PositiveIntNumber(IntNumber(n)) if n > 0 else None
```
```go
func NewNonEmptyString(s PlainString) (NonEmptyString, error) { /* … */ }   // Go: (value, error)
```
```rust
impl TryFrom<PlainNumber> for FiniteNumber { /* Err for NaN and ±Infinity */ }   // Rust: TryFrom
```

Name and shape them as the project and ecosystem do; they are a mechanism, not a naming scheme.

## Creation point policy

Decide once per primitive family: `[normalize]` (always succeeds, `to_lowercase`), `[reject]` (returns failure, `to_positive_int`), or `[normalize then reject]`. Mixing policies across sibling refinements is itself a micro-decision. How rejection becomes a compile-time or runtime error: [wrong-type errors](../references/wrong-type-errors.md).

## How tier 1 differs from the others

| | Tier 1 | Tier 2 | Tier 3 |
|---|--------|--------|--------|
| Knows | the raw type | a domain meaning | a shape |
| Rule source | generic | domain | which brands travel together |
| Built from | the raw type | tier 1 only | tier 2 and tier 3 |
| Files | one per primitive family | one per domain | one per group of shapes |
| Placement | `shared/types/primitives/` only | owner; `shared/types/brands/` if used by 2+ features | owner; `shared/types/shapes/` if used by 2+ features |
| Names | `IntNumber`, `LowercaseString` | `UserAge`, `UserEmail` | `UserSchema`, `SearchState` |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Domain noun in a tier 1 name (`UserLowercase`) | Move to tier 2 |
| An operation named as a type (`TrimmedString`, `TruncatedString`) | Make it a step inside a creation point; keep only visible states |
| Logic added to `PlainX` | Keep it a rename; logic goes in refinements |
| Raw type appearing in another file | Use `PlainX`; lint it |
| Two creation points for one refinement | One creation point, in the primitive-family file |
| Treating `PlainX` as a safety type | It is an alias, an audit marker; safety starts at refinements |
| `PlainNumber` where the code needs an integer, a float or a sign | Name the kind or refinement (`IntNumber`, `PositiveFloatNumber`); plain means "any value" |

See also: [raw to tier 1](../references/transform-raw-type-to-tier-1.md).
