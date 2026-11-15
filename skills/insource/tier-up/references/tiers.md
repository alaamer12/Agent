# The tiered system — the laws

> This skill's single owner for the tier system. General typing craft — the checks, naming, rigor, the brand catalog of starting names — belongs to `/type-up`; converting existing code is [migration](migration.md).

Three ordered groups of types, each built only from the tier below: **tier 1 primitives** (generic visible states, the only place a raw type is named) → **tier 2 brands** (domain meanings, one creation point each) → **tier 3 shapes** (records and tagged unions assembled from brands).

## 1. The laws

1. **Raw type named in one file per primitive family.** Tier 1 owns the language's types; everything above speaks tier names. A library-provided type enters through tier 1 too: tier 1 re-exports it, tiers 2 and 3 import from there, so swapping the library touches one file (the golden rule's how: `/type-up`).
2. **Imports follow tier order and never skip.** Shapes import brands, brands import primitives, same scope or shared; a shape reaching into tier 1 skips a tier — give that field a brand. A feature never imports another feature's private brand; promote it first.
3. **Every brand is defined once.** Two modules needing one meaning import one brand.
4. **Casts happen only at a brand's creation point.** Anywhere else, an escape hatch that breaks the guarantee.
5. **Values flow up freely, down through a creation point.** Every narrowing is one checkable function.
6. **One policy per primitive family, one per group of sibling brands** (§4) — mixing normalize and reject across siblings is itself a micro-decision left unmade.
7. **A refinement is a visible state, never an operation** (§3); operations are steps inside creation points.
8. **`PlainX` is a deliberate "any value" choice only** — as a chain base, a creation-point/boundary input, or genuinely any value; never where the code needs a kind, sign, or range (`IntNumber`, `PositiveFloatNumber`, a brand for those).
9. **No rule is still a decision.** A free-text field gets a brand (`UserBio`) whose creation point accepts anything; the brand records that none applies.
10. **Promote every micro-decision you catch** (case, range, unit, sign, timezone, trimming, truncating):

```
generic visible state (case, sign, integer, finite, empty) → tier 1 refinement
operation (trim, truncate, decode)                         → a step inside the owning brand's creation point
domain choice                                              → tier 2 brand
group of values                                            → tier 3 shape
```

## 2. Structure — where the tier folders go

*Folder names are example names (the project's convention wins; for brands the ecosystem's word — `newtypes/`, `opaque/` — is fine). Type-free source folders are hidden.*

```
src/
├── …                                    (app, ui, services…: hidden)
├── shared/
│   └── types/
│       ├── primitives/                  tier 1 — only ever here
│       │   ├── string.<ext>             PlainString + string refinements + their creation points
│       │   ├── number.<ext>             PlainNumber + Int/Float chains + creation points
│       │   ├── boolean.<ext>            …one file per primitive family
│       │   └── index.<ext>              the public surface for tiers 2 and 3
│       ├── brands/                      tier 2 used by two or more features
│       └── shapes/                      tier 3 used by two or more features
└── features/
    └── <owner>/
        └── types/
            ├── brands/                  tier 2 owned by this feature
            └── shapes/                  tier 3 owned by this feature
```

Placement test: *who owns this meaning / shape?* One owner keeps it local; two or more take it to `shared/`, once. Tier 1 never lives inside a feature (a `primitives/` folder under `features/` is a lint error). No feature folders → one `types/` with the same three subfolders. Boundary checks sit next to the shape they produce or beside the receiving service; tests sit next to what they test; migrations follow the project's own tool (the `CHECK`/domain mirroring: `/type-up`).

## 3. The distinguishability test (what qualifies as a refinement)

A tier 1 refinement names a **state the value shows**, not an **operation that was applied to it**. Look at one value alone and ask: can you tell from the value which side it is on, and do the two sides look different?

| Candidate | Tell by looking? | Verdict |
|-----------|------------------|---------|
| `"hello"` vs `"HELLO"` | yes — the case is in the content | `LowercaseString` / `UppercaseString` are real |
| `""` vs `"hello"` | yes | `NonEmptyString` is real |
| `1.5` vs `1`, `-5` vs `5`, `NaN` vs `3.2` | yes | `IntNumber`, sign, finite-`FloatNumber` are real |
| `"hello-world"` as plain, **trimmed** or **truncated** | no — nothing in the result records what was done | not a thing |

A trimmed or truncated string is an ordinary string; the same holds for sanitized, escaped, decoded, collapsed, Unicode-normalized, deduplicated. Operations live inside creation points (`toUserEmail` trims, lowercases, then validates; the brand states only the outcome). A guarantee that follows from an operation ("at most 40 characters", "no edge whitespace") is stated as a rule of the owning **tier 2 brand** — never as `TrimmedString`. Quick check before adding a refinement: write one value inside and one outside; if they cannot look different without describing history, it is an operation.

## 4. Creation point policy

| Policy | Returns | Use when |
|--------|---------|----------|
| **Normalize** | the type, always | any input can be repaired safely (trim + lowercase an ISO code) |
| **Normalize then reject** | type or failure | repair, then check (an email) |
| **Reject** | type or failure | input must already be correct (a port) |

Decide once per primitive family (tier 1) and per group of sibling brands (tier 2), write it in the catalog, keep siblings consistent. Rejection mechanics and error styles: the compiler-first ladder in `/type-up`.

## 5. Tier 1 — primitives

Own the **generic visible states**: case, integer-ness, sign, finiteness, emptiness. A rule mentioning a domain noun (user, order, port) belongs to tier 2.

1. One file per primitive family (string, number, boolean, bigint, date); the raw type appears in its own file and nowhere else.
2. The first export is the plain type — a plain rename. **A one-line file is complete; add no logic to justify it.** If the language's own type serves or the project already named it, use that.
3. Refinements form chains: each step narrows the previous one and adds one rule. Chains may be linear (`PlainNumber → IntNumber → PositiveIntNumber`) or stacked where the type system intersects types.
4. Up is free, down is a checked step (languages with nominal wrappers make "up" an explicit, total, zero-cost conversion).
5. Prefer a built-in or library state the compiler already checks (§ principles §1 ladder); define a wrapper only when nothing expresses it.
6. One creation point per refinement for runtime values — the only place a cast or wrapper is created. A refinement fed only by literals or built-ins needs none.
7. **Hard edge cases are decided here, once:** is `NaN` a number (`FloatNumber` is finite: no NaN, no ±Infinity)? what counts as empty? is lowercasing locale-dependent? what is `-0`? numeric strings are parsed at the boundary, not tier 1.
8. *TypeScript note: the brand marker must hold a **set** of names (`Brand<N extends string> = { readonly [t]: { readonly [K in N]: true } }`) so stacked brands merge; a one-literal marker makes every stacked brand collapse to `never`.*

Ordinary signatures take the refined type — that is what makes the compiler say "this is a string, not a lowercase string":

```ts
// primitives/string.ts — the only file that names `string`
export type PlainString     = string;
export type LowercaseString = Lowercase<string>;          // built-in: no brand, no function
function lookupSlug(slug: LowercaseString) {}
lookupSlug("my-post");      // ok
lookupSlug("My-Post");      // error: 'string' is not assignable to 'Lowercase<string>'

// primitives/number.ts — no built-in state, so the chain uses brands
export type IntNumber         = number & Brand<"Int">;
export type PositiveIntNumber = IntNumber & Brand<"Positive">;
function retry(times: PositiveIntNumber) {}
retry(3);                   // error: the literal is a number, not PositiveIntNumber
```
```python
# primitives/number.py
PlainNumber = float
IntNumber = NewType("IntNumber", int)
PositiveIntNumber = NewType("PositiveIntNumber", IntNumber)
def retry(times: PositiveIntNumber) -> None: ...          # mypy rejects a plain int
```
```go
// primitives/string.go — an unexported field blocks conversion from a plain string
type PlainString = string
type NonEmptyString struct{ v PlainString }
func Greet(name NonEmptyString) {}
```

**Where values come from** (the three sources, every tier): a literal the compiler verifies — no function; a more refined value — up is free; a runtime value — one creation point, in the ecosystem's idiom: a type guard (`n is PositiveIntNumber`), a Python function returning `T | None`, Go's `NewNonEmptyString(s) (NonEmptyString, error)`, Rust's `TryFrom`. Name and shape them as the project does; they are a mechanism, not a naming scheme.

## 6. Tier 2 — brands

Answer *"what does this value mean here?"* and attach every rule that follows from the meaning — format, range, unit, normalization. A module receiving a `UserEmail` knows the rules were already applied. Brand values come from the same three sources; closed sets (modes, statuses) are brands too, as enums or literal unions, never free strings; **secrets are brands** (`Token`, `Secret`) so logging and serialization can exclude them by type. Starting names: the brand catalog in `/type-up`.

```ts
type OrderId  = `ord_${string}`;                              // pattern type: literals checked, no function
type Quantity = PositiveIntNumber & Brand<"Quantity">;
function placeOrder(id: OrderId, qty: Quantity) {}
placeOrder("42", qty);          // error: '"42"' is not '`ord_${string}`'
placeOrder(qty, "ord_42");      // error: swapped arguments — the point of two brands
```
```python
PathValue   = NewType("PathValue", str)                       # two brands over one raw type:
GlobPattern = NewType("GlobPattern", str)                     # a swap is now catchable
def scan(root: PathValue, pattern: GlobPattern) -> None: ...
```
```rust
pub struct UserEmail(LowercaseString);                        // private field
pub fn send(to: &UserEmail, subject: &str) {}                 // a &str is simply not accepted
```

## 7. Tier 3 — shapes

Answer *"which values travel together, and which are optional?"* A shape adds no value rules (those live in tier 2) — it adds **structure**: fields are brands or other shapes (never raw, never `PlainX`); optional and required are explicit; anything with cases is a **tagged union** so each case carries exactly its own data; variants (raw / patch / resolved) stay separate names, never one loosened shape; public shapes carry the documentation pattern.

```ts
type SearchState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; results: ResultItem[] }        // results exists only here
  | { kind: "error"; message: ErrorMessage };
function describe(s: SearchState): string {
  switch (s.kind) {
    case "idle":    return "waiting";
    case "loading": return "loading";
    case "success": return `${s.results.length} results`;
    case "error":   return s.message;
    default: { const unhandled: never = s; return unhandled; }   // a missing case fails to compile
  }
}
```
```rust
pub enum Upload { Idle, Sending { progress: Percent }, Done { url: Url }, Failed { reason: ErrorMessage } }
// match is exhaustive by construction — omitting a case is a compile error
```

Python: `Literal`-tagged frozen dataclasses with `match`; Go: no sum types, so a sealed interface (unexported marker method) plus an exhaustiveness linter (`exhaustive`) — the compiler itself does not check.

## 8. The tiers at a glance

| | Tier 1 | Tier 2 | Tier 3 |
|---|--------|--------|--------|
| Question | what rule is generic? | what does it mean here? | which values travel together? |
| Adds | a generic rule | a domain meaning | structure |
| Built from | the raw type | tier 1 only | tier 2 and tier 3 |
| Files | one per primitive family | one per domain | one per group of shapes |
| Creation | validates a value | validates a meaning | the boundary check composes brand creation points |
| Typical name | `LowercaseString` | `UserEmail` | `ResolvedConfig` |
| Changes when | a generic rule changes | a domain rule changes | the field list changes |

## 9. Checks and lint

The three checks (defined in `/type-up`) gain teeth here — four lint rules enforce almost the whole system mechanically: raw types and library value types imported only in tier 1 family files; `PlainX` only in tier 1 and boundary files; brand casts only at creation points; imports follow tier order. Property tests per creation point: normalizers idempotent, outputs satisfy the refinement, rejected inputs stay rejected, `toWire`→`parse` round-trips.

**The catalog** (extends the sync table): every type — name, tier, built from, creation point, policy, users — updated in the same commit as the code. A validation library never defines a rule the creation point lacks (the library discipline: `/type-up`).

## 10. Mistakes

| Mistake | Fix |
|---------|-----|
| Domain noun in a tier 1 name (`UserLowercase`) | move to tier 2 |
| Operation as a type (`TrimmedString`, `TruncatedString`) | a creation point step; keep only visible states |
| Logic added to `PlainX` | a rename; logic belongs to refinements |
| Raw type appearing outside tier 1 | use `PlainX`; lint it |
| `PlainNumber` where a kind/sign/range is needed; `PlainX` in a shape field | name the refinement or brand; shapes take tier 2 |
| Two creation points for one refinement; the same regex in two files | one creation point, one brand |
| Casting to a brand in business code | call the creation point |
| Mixed policies across siblings; one brand throws while a sibling returns failure | one policy per family / sibling group (§4) |
| Brand built straight from a raw type | build from a tier 1 type |
| Brand nobody can validly create | add its creation point |
| Cross-feature import of a private brand | promote it to shared |
| One giant `types.ts` | one file per family (1), per domain (2), per group of shapes (3) |
| Flags instead of cases (`isLoading`, `hasError`, `data?`) | tagged union — impossible states stop being representable |
| One shape loosened for raw, patch and resolved | three named variants |
| Anonymous `Record<string, unknown>` | a named opaque type |
| A shape defining validation rules | move the rule into the brand's creation point |
| Undocumented public shape | purpose, example, constraints |
