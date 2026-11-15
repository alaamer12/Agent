# Tier 2: Brands

> **Applies when the project adopts the tiered system** (Mode B in `../SKILL.md`). For general type enhancement without the tiers, use `../references/core-workflow.md`.

> A brand gives a refined primitive a **domain meaning**. It is the unit where micro-decisions live.

*Standing note: layouts, names and `[bracketed]` options are illustrative examples, not a closed set; a hybrid or different answer is always acceptable. Adapt identifiers and file extensions to the language.*

Identifiers in examples (`PlainX`, `toX`, `parseX`, `…Schema`) are illustrative role names, not conventions: follow the project's and ecosystem's own names and types ([naming](../references/tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). Prefer a type the compiler already provides ([compiler first](../references/wrong-type-errors.md)).

Creation points may be hand-written (shown here) or built with the project's validation library: see [use the project's tools](../references/tooling-adaptation.md).

## Purpose

Answer "what does this value mean here?" and attach every rule that follows from the meaning: format, range, unit, normalization. A module receiving a `UserEmail` knows the rules were already applied.

## Rules (language-independent)

1. **Build only from tier 1.** A brand derives from a refined primitive, never from a raw type or directly from `PlainX`.
2. **Define each meaning once.** Two modules needing one meaning import one brand.
3. **One creation point per brand for runtime values**, the only place the brand value is created. A brand fed only by compile-time-verified literals needs none. Any functions are named in the project's idiom, never mandated as `toX` / `parseX`.
4. **State the policy** per group of sibling brands: `[normalize]`, `[normalize then reject]`, or `[reject]`. Record it in the catalog. Error styles and compile-time literal checks: [wrong-type errors](../references/wrong-type-errors.md).
5. **Closed sets are brands too.** Modes and statuses are enums or unions of literals, not free strings.
6. **No rule is still a decision.** A free-text field gets a brand (`UserBio`) whose creation point accepts any `PlainString`; the brand records that none applies.
7. **Operations are steps, not types.** A creation point may trim, truncate, collapse or decode before it validates; none of these becomes a tier 1 type or a brand of its own ([distinguishability test](./tier-1-primitives.md#what-qualifies-as-a-refinement-the-distinguishability-test)). A guarantee that follows from them ("at most 40 characters") is a rule of the brand.
8. **Secrets are brands** (`Token`, `Secret`), so logging and serialization can exclude them by type.

9. **Reuse before you create** (golden rule). Fill a brand with an existing type (`EmailStr`, `uuid.UUID`, `HttpUrl`) that tier 1 has re-exported, never one imported from the library, and add a nominal marker only if the compiler must tell it apart ([reuse-before-create](../references/reuse-before-create.md)).

## Project structure and placement
*Folder names are example names: this skill prefers `primitives/`, `brands/` and `shapes/`, but the project's own convention wins, and for brands the ecosystem's own word is fine (`newtypes/`, `opaque/`). Source folders unrelated to types are hidden below. Full layout and rules: [structure](../references/tier-principles.md#structure-where-the-tier-folders-go).*

Tier 2 follows **ownership**: a brand lives with the feature that owns its meaning, or in shared when two or more features need it.

```
src/
├── …                                (app, ui, and every other source folder: hidden)
├── shared/
│   └── types/
│       ├── primitives/              tier 1 (see tier 1)
│       └── brands/                  tier 2 used by two or more features
│           ├── network.<ext>        Port, HostName
│           └── identity.<ext>       EntityId, Token
└── features/
    ├── user/
    │   ├── …                        (views, components, hooks, services: hidden)
    │   └── types/
    │       └── brands/              tier 2 owned by user
    │           └── user.<ext>       UserIso, UserEmail, UserAge
    └── order/
        └── types/brands/ …          tier 2 owned by order
```

Placement test: *who owns this meaning?* One owner keeps it. Two or more features need it: move it to `shared/types/brands/` once, and everyone imports it. A feature never imports another feature's private brand; promote it first. Without feature folders, one `types/brands/` holds them all.

## Example: brands in ordinary function signatures

An ordinary function takes brands directly; the compiler rejects a plain value and a swapped argument. Each language shows a different scenario.

**TypeScript** (an id is a pattern type, so literals are checked with no function; a quantity is a number, so it is a brand):

```ts
type OrderId  = `ord_${string}`;
type Quantity = PositiveIntNumber & Brand<"Quantity">;

function placeOrder(id: OrderId, qty: Quantity) { /* … */ }
placeOrder("ord_42", qty);   // ok
placeOrder("42", qty);       // error: '"42"' is not assignable to parameter of type '`ord_${string}`'
placeOrder(qty, "ord_42");   // error: swapped arguments
```

**Python** (two brands over the same raw type, so a swap is catchable):

```python
PathValue   = NewType("PathValue", str)
GlobPattern = NewType("GlobPattern", str)

def scan(root: PathValue, pattern: GlobPattern) -> None: ...
scan("src", "*.py")                           # mypy: "str" is not "PathValue"
scan(GlobPattern("*.py"), PathValue("src"))   # mypy: swapped arguments
```

**Go:**

```go
type HostName struct{ v LowercaseString }
type Port struct{ v PositiveIntNumber }

func Connect(host HostName, port Port) { /* … */ }
// Connect("db.local", 5432)  → compile error: untyped constants are not HostName or Port
```

**Rust:**

```rust
pub struct UserEmail(LowercaseString);     // private field

pub fn send(to: &UserEmail, subject: &str) { /* … */ }
// send("a@b.co", "hi")  → compile error: expected `&UserEmail`, found `&str`
```

### Where brand values come from

The same three sources as tier 1: a literal the compiler verifies (`placeOrder("ord_42", qty)` above), a more refined value, or one creation point where a runtime value enters. That creation point applies the brand's policy (normalize, reject, or both) and is not a mandated `toX` function:

```ts
function isOrderId(s: string): s is OrderId { return /^ord_[A-Za-z0-9]+$/.test(s); }   // TypeScript: a type guard
if (isOrderId(input)) placeOrder(input, qty);
```
```python
def read_root(raw: str) -> PathValue:        # Python: the one place a runtime string becomes a PathValue
    if not raw:
        raise ValueError("root: must not be empty")
    return PathValue(raw)
```
```go
func NewHostName(s PlainString) (HostName, error) { /* lowercase, then check */ }   // Go: (value, error)
```
```rust
impl TryFrom<PlainString> for UserEmail { /* trim, lowercase, check; Result is the carrier */ }   // Rust: TryFrom
```

A closed set, in the idiom of each language: TypeScript union of literals, Python `Literal` or `Enum`, Go typed constants behind a validating creation point, Rust `enum`. Example values: `[full]`, `[changed]`, `[staged]`.

## Brand catalog (starting names, illustrative)

| Intent | Name | Built from | Constraint |
|--------|------|-----------|------------|
| File-system path | `PathValue` | `NonEmptyString` | non-empty |
| Glob pattern | `GlobPattern` | `NonEmptyString` | non-empty |
| File extension | `FileExtension` | `LowercaseString` | starts with `.` |
| Relative path | `RelativePath` | `NonEmptyString` | no drive or leading root |
| Domain id | `UserId`, `OrderId` | `NonEmptyString` | prefix + charset / UUID / ULID |
| Count / workers | `WorkerCount` | `PositiveIntNumber` | upper bound |
| Port | `Port` | `PositiveIntNumber` | 1 to 65535 |
| Money amount | `MinorUnits` | `IntNumber` | currency minor units |
| Secret | `Token` | `NonEmptyString` | never logged |

## How tier 2 differs from the others

| | Tier 1 | Tier 2 | Tier 3 |
|---|--------|--------|--------|
| Question | what rule is generic? | what does it mean here? | which values travel together? |
| Typical name | `LowercaseString` | `UserEmail` | `UserSchema` |
| Creation point | generic, normalize or reject | domain rules on top of tier 1 | `parse`, composing brand creation points |
| Changes when | a generic rule changes | a domain rule changes | the shape changes |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Brand built straight from a raw type | Build from a tier 1 refinement |
| Same regex in two files | One brand, one creation point |
| Casting to the brand in business code | Call the creation point |
| One brand throws, a sibling returns failure | Decide the policy per group of sibling brands |
| Cross-feature import of a private brand | Promote it to `shared/types/brands/` |
| Brand with no creation point | Add one; a brand nobody can validly create is dead |
| `TrimmedEmail`, `TruncatedName` as brands | Trimming and truncating are creation point steps; the brand is `UserEmail`, `DisplayName` |

See also: [tier 1 to tier 2](../references/transform-tier-1-to-tier-2.md) and [database constraints](../references/database-constraints.md) (a brand becomes a domain or `CHECK`).
