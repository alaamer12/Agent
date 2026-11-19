# Weak-type holes: where the wall leaks

A type wall is only as strong as its weakest annotation. Agents build the wall well in the places
they are thinking about — the boundary, the brand, the config — and leave characteristic holes
elsewhere: a bare container here, an `any` there, a narrowed value handed back through a wide
callback. This file owns the hole census: what each one looks like, why the checker stays silent,
and the fix.

*Names and `[bracketed]` options are illustrative, not exhaustive. Checker behaviors are documented
semantics of the named tools; verify on the project's versions. Related but distinct: the relation
family (overloads/overrides/dispatch/wrappers) in
[overloads-overrides-dispatch](./overloads-overrides-dispatch.md); casting law in
[wrong-type-errors §4](./wrong-type-errors.md).*

## 1. `Any` is a hole, in every costume

An `any` / `Any` / `interface{}` / `object` on a public signature means: no type here. Worse, it
contagions — TypeScript flows `any` both directions (one `any` in a chain silently unchecks its
neighbors); Python annotating a container's elements as `Any` unchecks everything stored in it.

- Prefer the strong default: TS [unknown] at boundaries (forces a narrow before use) over any;
  Python `[object]` or a precise union over bare `Any`; Go `any` only at true edges and converted
  immediately.
- **Bare container annotations are implicit Any wearing a disguise** — the single most common
  leftover once a codebase is "typed": `list`, `dict`, `set`, `Callable`, `Map`, `Array`, `Function`
  written without parameters. Annotate the parts: `list[Port]`, `dict[CountryCode, Email]`,
  `Callable[[Port], ScanResult]`, TS `Map<Key, Value>`. A sweep task ("type-up this module") that
  leaves bare containers has not type-upped it.
- Generic `T` unconstrained, where the actual set is closed, is the same hole spelled
  pretentiously: constrain it to the union/protocol the code can actually handle.

## 2. Variance is the hole that bites on assign, not on use

`Container<Port>` vs `Container<PlainNumber>` interchangeability is decided by the *generic's role*,
not its name. Producer positions covary, consumer positions contravary; arrays are the unsound
classic (covariant arrays in TS/Java accept writes that break at runtime; Rust/Go reject the
pattern outright). Ecosystem spellings: TS [`in`/`out` annotations — but also notice TS infers
structure, so "the checker accepted it" is not proof of soundness], Kotlin/Swift [`in`/`out`],
Python [`Protocol` declared covariant/contravariant only where correct — checkers default
invariant], Java [`extends`/`super` wildcards]. Rule of thumb when a substitution the code should
refuse compiles: the generic signature is wrong — fix the declaration; do not cast the caller.

## 3. Narrowing lost between the check and the call

The checker narrowed the value; the agent re-widened it at the seam:
- **Callback seam** — `if isinstance(x, A): run(x)` where `run` is typed `(x: Parent)`. The
  narrowed fact evaporates into the parent. Type the callback on the narrow side, or pass the
  narrow value only into narrow-typed parameters.
- **Attribute vs local** — `isinstance(self.cfg, Ready)` narrows until anything could have mutated
  the attribute (both mypy and tsc distrust member narrowing across calls/assignments). Copy to a
  local, narrow the local — then keep the attribute's type honest.
- **Python runtime truth**: annotations never reject at runtime; `x: A` after a check is
  documentation. A value that crosses a process/API/file boundary needs the creation point (rung
  5), not a remembered narrowing.

## 4. The two meanings of absent

`Optional[T]` / `T | undefined` / nullable columns conflate **"not provided"** with **"explicitly
none"** — the classic destroyed PATCH: the client means "clear the field", the server sees `None`
and stores it. Shape-level answer: the **patch variant** ([principles §variants](./principles.md))
keeps absent-vs-null explicit. At the function level: a module-level `[MISSING]` sentinel as the
default (Python idiom stdlib itself uses), TS `in`/optional-chain awareness of key presence, not
just value; never a mutable default argument (`def f(x: list = [])` is a binding bug dressed as a
type).

## 5. Flags and unnamed positions

`render(true, false, true)` — after the third boolean nobody (no checker, no reader) knows what
could be legal pairs. Patterns: **boolean blindness** (a `bool` that is really a two-member closed
set → name it; prefer the literal spelling per the [tie-breaker](./wrong-type-errors.md#within-rung-2-literal-or-enum-the-tie-breaker)); **flag pairs that always travel together** → one state
type; **bare tuples carrying roles** (`tuple[int, int]` where position 0 means offset) → a small
named struct/dataclass/record so the compiler can label positions, and reordering becomes an error
instead of a story.

## 6. Growing a set in silence

Today the closed set is five members and every switch handles five. Tomorrow a sixth member joins —
and every switch that does not handle it **still compiles** and takes the silent default. Make the
growth a compiler task: TS default branch `const _never: never = x` (a new arm fails the build);
Python `match` with a `case _:` calling `typing.assert_never(x)` (3.11+, verified present);
Rust / Swift / Kotlin match are exhaustive by construction; Go — the checker cannot, so the guard
is an [`exhaustive`-style lint or a table-driven test that enumerates the set]. A "type-up" pass
that adds sets without a guard planted has scheduled the next silent bug.

## 7. Test fixtures fabricating domain values

The wall holds, the tests pass — because the fixture built its branded value with the escape hatch:
`email("just a string") as Email`, `UserEmail(...)  # type: ignore[arg-type]`, TS `as` casts on raw
objects feeding branded shapes. A fixture that bypasses the creation point tests a world the
boundary rejects. Build fixtures **through the creation points** (they normalize and reject — same
path production takes); when a test genuinely needs an invalid value, that is the *point* of the
test: name it (`invalid_email_raw()`) and assert the rejection. Weakening the fixture to green the
test is the same anti-pattern the deck's testing law already bans.
