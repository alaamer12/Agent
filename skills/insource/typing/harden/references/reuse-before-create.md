# Golden Rule: Do Not Reinvent the Wheel

Before defining any plain type, refinement, brand or shape, look for one that already exists in the language, its standard library, or a dependency already in the project. Use it. Never write a custom `PositiveInt` just to follow the tiers.

*Library and type names are illustrative; the project's own names win ([naming](./principles.md#3-naming--describe-the-role-follow-the-ecosystem)). Verified by running: Pydantic 2.13.5 (`PositiveInt`, `NonNegativeInt`, `PositiveFloat`, `FiniteFloat`, `EmailStr`, `HttpUrl`, `FilePath` exist; Pandas 3.0.2 has no `PositiveInt`), `mypy` strict, TypeScript 7.0.2, Zod 4.6.5. Standard-library items for Python, Rust and Go are named from their documentation and were not run here.*

## 1. The tiers are roles, not code to write

The tiers say what each group of types is **for**. A role can be filled by an existing type. A custom class is justified only when nothing existing expresses the rule.

| Role | Fill it with an existing type when one exists | Create only if |
|------|-----------------------------------------------|----------------|
| Refinement (tier 1) | a built-in or library type for the state | none expresses it |
| Brand (tier 2) | a library or standard-library type for the meaning, plus a thin nominal marker if the compiler must tell it apart | no type carries the domain rule |
| Shape (tier 3) | the library's model: a Pydantic `BaseModel`, a Zod object, a serde struct | the project has no model type |

**How an existing type enters the code depends on the mode:**

- **General practice:** import the existing type where it is used.
- **Under the `tiers` level:** follow the hierarchy. **Only tier 1 knows the existing type.** The tier 1 file re-exports it under the project's name (a one-line file is complete), and tiers 2 and 3 import it from tier 1, never from the library. This is the same law as for raw types: the library's name appears in one place, so swapping the library touches only tier 1. Lint: library value types are imported only in tier 1 files.
- A **shape container** the library provides (a Pydantic `BaseModel`, a Zod object) is a tier 3 tool, not a value type, so tier 3 may import it.

## 2. Search order

1. **The language's built-in types**: TypeScript `Uppercase<string>`, template literal types, `URL`; Python `Literal`.
2. **The standard library**: Python `pathlib.Path`, `ipaddress`, `uuid.UUID`, `enum`; Rust `NonZeroU32`; Go `net/netip.Addr`, `net/url.URL`, `time.Duration`.
3. **A dependency already in the project**: Pydantic `PositiveInt`, `EmailStr`, `HttpUrl`; Zod `z.number().int().positive()`, `z.email()`; a refined-type library (Scala Iron).
4. **Create**, only after 1 to 3 come up empty, and as small as possible (for the tiered architecture, the `tiers` level says how).

## 3. Check what the existing type actually guarantees

An existing type may give the rule at runtime only, at compile time only, or both. Verified with Pydantic, in general practice (imported where used):

```python
from pydantic import PositiveInt
def retry(times: PositiveInt) -> None: ...
retry(-1)        # mypy: no error, the checker sees plain int
# at runtime the rule holds: TypeAdapter(PositiveInt) accepts 3, rejects 0, -1 and 1.5
```

So a reused type is not always a complete answer. **Add only the part that is missing**, usually the nominal marker. Under the `tiers` level the library type enters through tier 1, and everything above imports from there (verified with a real module layout under `mypy --strict`):

```python
# primitives/number.py      tier 1: the only module that imports the library's type
from pydantic import PositiveInt
PositiveIntNumber = PositiveInt          # re-exported under the project's name

# brands/network.py         tier 2: imports tier 1 only, never pydantic
from typing import NewType
from primitives.number import PositiveIntNumber
Port = NewType("Port", PositiveIntNumber)     # reuse the rule, add the compile-time distinction

# app.py                    a consumer: imports from the tiers
def connect(port: Port) -> None: ...
connect(8080)    # mypy: Argument 1 to "connect" has incompatible type "int"; expected "Port"
```

Only `primitives/number.py` imports Pydantic. Replacing the library later touches that one file.

| Existing type gives | Missing | Add |
|---------------------|---------|-----|
| runtime rule only (`PositiveInt`, `z.number().positive()`) | compile-time distinction | a nominal marker (`NewType`, brand), in tier 2 |
| compile-time state only (`Uppercase<string>`) | runtime check for dynamic values | a boundary check or type guard |
| compile-time and runtime (Rust `NonZeroU32`) | nothing | re-export it from tier 1 as is |
| nothing for the domain rule | the whole brand | create it (tier 2) |

## 4. Do not copy what a library already maintains

| Avoid | Prefer |
|-------|--------|
| A custom `PositiveInt` class beside Pydantic's | `PositiveInt`, plus `NewType` only if the checker must tell it apart |
| A hand-written email regex when `EmailStr` or `z.email()` exists | the library type |
| A wrapper around `uuid.UUID`, `Path` or `URL` | the standard type, plus a brand if two ids must not be swapped |
| Reimplementing non-zero integers in Rust | `NonZeroU32` |
| Copying a library's constraints into your own code | referencing them: copies drift |

## 5. When reuse is not enough

- **The library's rule differs from yours.** A library email check may accept or reject a different set than a database constraint. Compare with [shared vectors](./database-constraints.md) and write a brand only for the difference.
- **The dependency is not in the project yet.** Do not add a dependency for one type; weigh it, and ask ([use the project's tools](./tooling-adaptation.md)).
- **The library's normalization is its own.** Pydantic's `strip_whitespace` and Python's `str.strip()` disagree on `"\x1f"`; test idempotence instead of assuming equality.
