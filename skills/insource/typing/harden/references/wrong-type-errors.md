# Compiler First: Rejecting Wrong Types

The goal is for the **compiler** to say "this is a string, not the uppercase string I expected" and refuse to build. Runtime checks exist only for values the compiler cannot know. No function per type is required.

*Verified by running: the TypeScript snippets (TypeScript 7.0.2, strict mode). Python, Go, Rust and Scala snippets follow documented behavior and should be run in the target project. Built-in type behavior varies by compiler version: verify on the project's. Identifiers are illustrative roles ([naming](./principles.md#3-naming--describe-the-role-follow-the-ecosystem)); `[bracketed]` options are examples, not a closed set.*

## 1. The ladder: prefer the highest rung that works

| Rung | Mechanism | Rejects at compile time | Needs a function? |
|------|-----------|-------------------------|-------------------|
| 1 | A **built-in or ecosystem type** that already expresses the rule | `Uppercase<string>`, `` `${number}px` ``, refined-type libraries | no |
| 2 | **Closed set**: literal union, enum | `"fulll"` where `"full" \| "changed"` is expected | no |
| 3 | **Nominal type**: brand, NewType, opaque type, newtype | a plain value where a named meaning is expected | only where runtime values must enter the type |
| 4 | **Conditional / const evaluation on literals** | a bad literal, with a custom readable message | no |
| 5 | **Runtime check** at the point dynamic data enters | nothing at compile time; throws or returns failure | yes, one boundary check |

Persisted data adds a last line of defense in the database ([database constraints](./database-constraints.md)). Rungs 1 to 4 are the compiler's work. Rung 5 is used only for data that exists at runtime (input, files, network, computed strings). Do not add rung 5 functions to values the compiler can already judge.

## 2. Rung 1 in TypeScript (verified)

```ts
function f(s: Uppercase<string>) {}
f("HELLO");               // ok
f("hello");               // error: Argument of type 'string' is not assignable to parameter of type 'Uppercase<string>'
f("Hello");               // error
declare const dyn: string;
f(dyn);                   // error: a general string is not provably uppercase
declare const u: Uppercase<string>;
f(u.toLowerCase());       // error: the result of toLowerCase() is a plain string
const widened: string = u;   // ok: a refined value is usable wherever its parent is (up is free)

type Px = `${number}px`;
const w: Px = "12px";     // ok
const bad: Px = "12em";   // error: '"12em"' is not assignable to type '`${number}px`'
```

No brand, no creation point, and the compiler names the mismatch. For a **dynamic** string, narrow with a type guard written in the language's idiom (a runtime check at the one place the data enters):

```ts
function isUppercase(s: string): s is Uppercase<string> { return s === s.toUpperCase(); }
if (isUppercase(input)) f(input);   // narrowed: ok
```

## 3. Rung 4: when no built-in expresses the rule

A conditional type evaluates to `never` for a bad literal; `never` is not itself an error, the error appears where a value is used against it. Return a message type instead of `never` for a readable error:

```ts
type Err<M extends string> = `Type error: ${M}`;
type TwoUppercaseLetters<S extends string> =
  string extends S ? Err<"literal required">
  : S extends `${infer A}${infer B}${infer R}` ? (R extends "" ? (S extends Uppercase<S> ? S : Err<"must be uppercase">) : Err<"must be 2 letters">)
  : Err<"must be 2 letters">;

declare function setCountry<S extends string>(code: TwoUppercaseLetters<S>): void;
setCountry("US");     // ok
setCountry("us");     // error: '"us"' is not assignable to parameter of type '"Type error: must be uppercase"'
setCountry("USA");    // error: ... '"Type error: must be 2 letters"'
```

The `string extends S` branch is the guard for a general `string`. Whether a bare `UppercaseOnly<string>` evaluates to `never` or to `string` differs between compiler versions (it is `never` on the version used here), so never rely on either: test it.

A standalone helper like this is the general-practice answer. Under the `tiers` level the same rule already lives in the tiers (a tier 1 state and a tier 2 brand), and the literal route is optional, added only for values written in source.

## 4. Rung 3: nominal types

A brand, NewType, opaque type or newtype makes a plain value an error where a named meaning is required. In TypeScript, the brand marker must hold a set of names so stacked brands merge (the marker shape: the `tiers` level's tier 1):

```ts
declare const t: unique symbol;
type Brand<N extends string> = { readonly [t]: { readonly [K in N]: true } };
type UserIso = Uppercase<string> & Brand<"UserIso">;     // built-in state + domain meaning
const x: UserIso = "US";                                   // error: a raw value is not UserIso
```

A value can enter such a type from a compile-time-verified literal route (rung 4) or from the single creation point for runtime values (rung 5). Casts exist only at the creation point.

## 5. Other ecosystems (illustrative; verify in the project)

A different rule in each language:

```python
ScanMode = Literal["full", "changed", "staged"]         # rung 2: the checker rejects "fulll"
PathValue = NewType("PathValue", str)                    # rung 3: a plain str is rejected where a PathValue is required
```
```scala
// Scala 3: an opaque type is rung 3; failure is carried by the ecosystem's own Either
opaque type Port = Int
object Port:
  def from(n: Int): Either[String, Port] = Either.cond(n >= 1 && n <= 65535, n, "port must be 1..65535")
// refined-type libraries (for example Iron) can check literals statically: use one if the project has it
def connect(host: HostName, port: Port): Unit = ???
```
```rust
// rung 3 + 4: a newtype with a const fn; a bad literal in a const context fails the build
impl UserIso {
    pub const fn from_static(s: &'static str) -> Self {
        let b = s.as_bytes();
        assert!(b.len() == 2, "UserIso must be 2 letters");
        let mut i = 0;
        while i < b.len() { assert!(b[i].is_ascii_uppercase(), "UserIso must be uppercase"); i += 1; }
        Self(s)
    }
}
const DEFAULT_COUNTRY: UserIso = UserIso::from_static("US");   // "us" here is a compile error
```
```go
// Go: typed constants give a closed set (rung 2); rules still need a runtime check (rung 5)
type ScanMode int
const (
    ScanFull ScanMode = iota
    ScanChanged
    ScanStaged
)
```

## 6. Rung 5: runtime rejection, only for dynamic data

Use the **failure carrier the ecosystem already has**; do not invent one:

| Ecosystem | Typical carrier |
|-----------|-----------------|
| Rust | `Result`, `TryFrom`, `FromStr` |
| Scala | `Either`, `Option`, `Try` |
| Haskell | `Either`, `Maybe` |
| Go | `(T, error)` |
| Python | exception, or `Optional` for expected absence |
| TypeScript | exception, a discriminated union, the project's fp library (`Either`, `Result`) or validation library issues |
| Kotlin / Swift / Java | `Result`, `throws`, `Optional` |

Style options (`[return the carrier]`, `[throw]`, `[assert in development only]`) follow the project: return at boundaries and forms, throw for startup configuration, assert only where upstream already validated. An error names the rule and the field, includes a safe excerpt, and never includes secrets.

One boundary check per source of dynamic data is enough (a library `parse` call, a type guard, a `TryFrom`). Per-type functions such as `parse_X` are **not required**; add a creation point only when runtime values must become the type. If the project uses a validation library, that call is the boundary check ([use the project's tools](./tooling-adaptation.md)).

## 7. Callers that bypass the compiler

Plain-JavaScript callers, `any` / `Any`, reflection and other processes skip static checks. Check at the public boundary, so the error is raised there rather than later.

## 8. Test that the compiler really rejects

Negative tests prove the rule fails when it should:

| Language | Check-time negative test | Runtime test |
|----------|--------------------------|--------------|
| TypeScript | `// @ts-expect-error` above the bad call (the test fails if it compiles) | assert the boundary check throws or returns failure |
| Python | the type checker in CI; `assert_type` / expected-error comments | `pytest.raises` |
| Go | none for rules; keep typed constants for sets | table test of the boundary check |
| Rust | `compile_fail` doctests or the `trybuild` crate | assert on `Err(_)` |
| Scala | compile-error assertion in the test framework | assert on `Left(_)` |

Include the general-`string` case, since compilers differ on it.
