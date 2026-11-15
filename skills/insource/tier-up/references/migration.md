# Migration — converting an existing codebase to the tiered system

> For existing code. What the tiers *are* and their laws: [tiers](tiers.md); this file is only the sequence of steps from where the code stands to where the system says it should be. Identifiers are illustrative roles (the naming rules: `/type-up`).

```
raw types ──► tier 1 ──► tier 2 ──► tier 3 ──► boundary
   (§1)        (§2)        (§3)        (§4)
```

Run the stages in order; each is independently shippable. Before defining anything at any stage, apply the golden rule — the rule you just found may be one import away (the how: `/type-up`).

## 1. Raw types → tier 1

Goal: every raw `string`, `number`, `boolean` disappears except inside the primitive-family files, and generic rules applied by hand become refinements.

```
1. Inventory  every raw type on public and shared surfaces
2. Create     one file per primitive family under shared/types/primitives/
3. Name       each raw type by what the code means — plain only for "any value"
4. Find rules hand-applied generic rules (table below)
5. Refine     one refinement + creation point per rule, in the family file
6. Migrate    replace every hand-applied rule with its creation point
7. Lock       lint: raw types outside the primitives folder are errors
```

Steps 1-2 change no behavior. In step 3, a plain type is a neutral alias, but a kind or refinement is nominal: changing a parameter type makes the checker list every caller still passing an unrefined value — that list is step 6's work plan. Count the leftover `PlainX`: each must be a deliberate "any value is fine" (text to shout, an opaque note); one where you cannot say that is a missing refinement.

| The code accepts | Name it | Example |
|------------------|---------|---------|
| any value of the raw type, deliberately | the plain type | text to shout |
| any integer or any float (kind matters, not range) | `IntNumber`, `FloatNumber` | a count, a coordinate |
| a sign or range the domain gives | `PositiveIntNumber`, `NonEmptyString`… | a width, a name that must not be empty |

Where a language separates integers from floats (Python, Go, Rust), the raw type already told you the kind: an `int` parameter is at least `IntNumber`, never `PlainNumber`.

```ts
function greet(name: string, times: number) {}                 // before
function greet(name: PlainString, times: PositiveIntNumber) {} // after: any text; a repeat count is a positive int
```
```go
func Scale(factor float64) {}                                 // before
func Scale(factor PositiveFloatNumber) {}                     // after: a scale factor is a positive float
```

**Finding hand-applied rules** — search for the same operations in any language:

| Operation found | Generic rule | Refinement |
|-----------------|--------------|------------|
| lower/upper-casing | case | `LowercaseString`, `UppercaseString` |
| empty / null-or-empty check | emptiness | `NonEmptyString` |
| integer test | integer | `IntNumber` |
| NaN / infinity / finite test | finite | `FloatNumber` |
| `> 0`, `>= 0` | sign | `PositiveIntNumber`, `NonNegativeIntNumber`… |
| date validity | valid instant | `ValidDate` |

A rule in **two or more modules** is the signal; a known bug source (case, sign, NaN) earns a refinement even once. Operations (trim, truncate, escape, decode…) never become types — [the distinguishability test](tiers.md#3-the-distinguishability-test-what-qualifies-as-a-refinement). Edge cases (`NaN`, `-0`, empty) are decided once here: [tiers §5 rule 7](tiers.md).

## 2. Tier 1 → tier 2

Goal: every value with a domain meaning gets a brand with one creation point, so a signature says what the value *is*, not which raw type it carries.

```
1. List    tier 1 types used for domain values (parameters, fields)
2. Name    <Domain><Meaning> — in the project's idiom, not necessarily this shape
3. Choose  the most specific tier 1 type always true for the meaning
4. Define  the brand
5. Create  one creation point; state its policy (tiers §4)
6. Replace every occurrence of the bare tier 1 type with the brand
7. Delete  the regexes, ranges and normalizations the call sites duplicated
```

| Symptom | Brand to create |
|---------|-----------------|
| The same regex in several files | the brand for what it validates |
| The same range check twice | a brand with that range |
| Several parameters of one raw type (`send(a, b)`) | a brand per meaning — swaps become compile errors |
| A comment saying "must be …" | the comment becomes the creation point |
| Two names for one idea (`uid`, `userId`) | one brand |
| An implied unit (`ms`, `cents`, `px`) | a brand carrying the unit |

Base selection: `UserEmail` from `LowercaseString` (creation point also trims before checking), `Port` from `PositiveIntNumber` (bounded by the brand), `Price` from `IntNumber` (minor units, never floats), `Token` from `NonEmptyString`. No tier 1 type fits? Add the refinement first; never build a brand from a raw type.

```ts
function charge(account: string, amount: number) {}            // before: swappable
function charge(account: AccountId, amount: MinorUnits) {}     // after
```
```python
def schedule(delay: float, retries: int) -> None: ...              # before
def schedule(delay: Seconds, retries: RetryCount) -> None: ...     # after: mypy rejects the swap
```

A value with no rule still gets the brand — its creation point accepts anything, and the brand records that the choice was made: `UserBio = PlainString & Brand<"UserBio">` (TS), `Remark = NewType("Remark", PlainString)` (Python), `pub struct Nickname(PlainString)` (Rust). Placement: [tiers §2](tiers.md#2-structure--where-the-tier-folders-go).

## 3. Tier 2 → tier 3

Goal: values that travel together become one named shape — no function takes a loose list of brands, no shape described only in a comment.

```
1. Group   brands that always appear together (parameter lists, literals, DTOs)
2. Name    in the project's style (record / state / patch)
3. Mark    required vs optional per field
4. Find cases — if the shape has modes, model a tagged union
5. Define  the shape, from brands only
6. Replace parameter lists and anonymous objects with it
7. Split   raw / patch / resolved variants where they differ (§4)
8. Document purpose, example, constraints
```

| Symptom | Shape |
|---------|-------|
| A function with 3+ related brand parameters | one shape parameter |
| The same object shape built in several places | a shape |
| A struct / dataclass / interface with raw fields | a shape, after each field gets its brand |
| Flags like `isLoading`, `hasError`, `data?` | a tagged union, one case per mode |
| Config read from a file, overridden by CLI, then defaulted | three variants (§4) |

Order matters: a field enters a shape only once its brand exists — run §2 per field first. Flags to cases:

```ts
type Download = { isLoading: boolean; error?: string; file?: FileRef };   // before: idle+error+file at once is legal
type Download =                                                            // after: each case carries only its data
  | { kind: "idle" } | { kind: "running"; percent: Percent }
  | { kind: "done"; file: FileRef } | { kind: "failed"; reason: ErrorMessage };
```
```rust
struct Sync { running: bool, error: Option<String>, last_run: Option<String> }   // before
enum Sync { Idle, Running { since: Timestamp }, Failed { reason: ErrorMessage } } // after: match is checked
```

Nesting: shapes contain shapes, never inlined raw fields; per-item extension gets a **named** opaque bag (`ExtensionOptions`) — an anonymous map is a raw type in disguise.

## 4. The boundary, and variants

Goal: outside data enters through one boundary check, only validated shapes circulate inside, and each output has one wire form.

A boundary is anywhere data arrives that the type system did not create: network, storage, env vars, URL params, forms, CLI args, files, queues.

```
untrusted input  →  parse<Name>()  →  <Name> shape  →  rest of the app
(unknown / plain)   creation points    (tier 3)
```

`PlainX` and the language's unknown type are allowed only in boundary files and as creation-point inputs.

```
1. List   every place external data arrives
2. Type   the input (unknown / any-input, or a plain-field raw shape)
3. Check  the boundary check calls each field's creation point and collects failures —
          it holds no rules of its own
4. Return the shape, or an error naming the failing field
5. Route  internal code accepts only shapes
6. Mirror one toWire per output, shape → serializable form
```

The check's form follows the project — a library `parse`, `TryFrom`, a decoder, a type guard — and its carrier too (`Result`, `(T, error)`, an exception):

```ts
function readInvoice(raw: unknown): Invoice {           // TS: rules live in the brands, not here
  const r = (typeof raw === "object" && raw !== null ? raw : {}) as Record<string, unknown>;
  if (typeof r.id !== "string" || !isOrderId(r.id)) throw new BoundaryError("id", "expected ord_…");
  if (typeof r.amount !== "number" || !isMinorUnits(r.amount)) throw new BoundaryError("amount", "expected whole minor units");
  return { id: r.id, amount: r.amount };
}
```
```go
func ReadRequest(raw map[string]any) (SearchRequest, error) {   // Go: (value, error)
    q, _ := raw["query"].(string)
    query, err := NewSearchQuery(q)
    if err != nil { return SearchRequest{}, fmt.Errorf("query: %w", err) }
    l, _ := raw["limit"].(float64)
    limit, err := NewPageSize(l)
    if err != nil { return SearchRequest{}, fmt.Errorf("limit: %w", err) }
    return SearchRequest{Query: query, Limit: limit}, nil
}
```

With a validation library, derive its schema from the creation points or test it against them — a rule never lives in the library only (the library discipline: `/type-up`). Callers that bypass the compiler (plain JS, scripts, other processes) get the runtime path: export the creation points and check at the public boundary. Failure handling, one project default: `[result naming the field]` (good default), `[typed throw]` (process startup), `[collect all errors]` (forms, bulk imports).

**Variants** — when one shape has more than one version, name each instead of loosening one type:

| Variant | What it is | Fields |
|---------|-----------|--------|
| **Raw** | what the user or outside system provides | unknown / plain fields |
| **Patch** | what a CLI or API may change | brands, all optional |
| **Resolved** | after defaults, merge and validation | brands, required present |

```ts
type ScanPatch    = { mode?: ScanMode; workers?: WorkerCount };
type ResolvedScan = { root: PathValue; mode: ScanMode; workers: WorkerCount };
const resolveScan = (file: ScanPatch, cli: ScanPatch): ResolvedScan =>
  ({ ...DEFAULTS, ...file, ...cli });     // precedence: defaults ← file ← cli
```

Only the resolved variant circulates inside the app.

## Done (whole migration)

- [ ] No raw type outside the primitive-family files; lint enforces it
- [ ] Every hand-applied generic rule is one refinement with one creation point and a stated policy
- [ ] No domain value is a bare tier 1 type in a public signature; call-site validation duplicates are deleted
- [ ] Every meaning has one brand; every group of traveling values one shape; cases are tagged unions, not flags
- [ ] Every boundary has one check holding no rules of its own; internal code takes only shapes; each output has one `toWire`
- [ ] Raw / patch / resolved separated where they differ; every public shape documented
- [ ] The catalog lists each type: tier, built from, creation point, policy, users — updated in the same commits as the code
