# Transform: raw types → tier 1

> **Applies when the project adopts the tiered system** (Mode B in `../SKILL.md`). For general type enhancement without the tiers, use `core-workflow.md`.

Goal: every raw `string`, `number`, `boolean` disappears except inside the tier 1 primitive-family files, and generic rules that modules apply by hand become refinements.

*Standing note: options in `[brackets]` are illustrative, not exhaustive; adapt to the language.*

Identifiers in examples (`PlainX`, `toX`, `parseX`, `…Schema`) are illustrative role names, not conventions: follow the project's and ecosystem's own names and types ([naming](./tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). Prefer a type the compiler already provides ([compiler first](./wrong-type-errors.md)).

## Steps

```
1. Inventory   find every raw type in public and shared surfaces
2. Create      one file per primitive family in shared/types/primitives/: string, number, boolean …
3. Name        each raw type by what the code means: a plain type only for "any value", otherwise a kind or refinement
4. Find rules  search for hand-applied generic rules (table below)
5. Refine      add a refinement + creation point per rule, in the primitive-family file
6. Migrate     replace each hand-applied rule with its creation point
7. Lock        lint: raw types outside shared/types/primitives/ are errors
```

Steps 1 and 2 change no behavior. In step 3 a plain type is also a neutral alias, but a kind or refinement is nominal: the compiler lists every caller that passes an unrefined value, which is intended (step 6). Every `PlainX` left after step 3 must be a deliberate "any value" choice; count them to see what is still undecided.

## Step 3: name each raw type by what the code means

A plain type (`PlainNumber`, `PlainString`) says "any value of this raw type is acceptable". Use it only when that is true. When the code needs more, name it.

| The code accepts | Name it | Example |
|------------------|---------|---------|
| any value of the raw type, deliberately | the plain type | text to shout, an opaque note |
| any integer, or any float (the kind matters, not the range) | `IntNumber`, `FloatNumber` | a count of anything, a coordinate |
| a sign or range the domain gives | `PositiveIntNumber`, `PositiveFloatNumber`, `NonEmptyString`… | a width, a scale factor, a name that must not be empty |

Where a language already separates integers from floats (Python, Go, Rust), the raw type has already told you the kind: an `int` parameter is at least `IntNumber`, a `float64` at least `FloatNumber`, never `PlainNumber`. A different function in each language:

```ts
function greet(name: string, times: number) {}                       // before
function greet(name: PlainString, times: PositiveIntNumber) {}       // after: any text is fine; a repeat count is a positive integer
```
```python
def resize(width: int, height: int) -> None: ...                     # before
def resize(width: PositiveIntNumber, height: PositiveIntNumber) -> None: ...   # after: sizes are positive integers
```
```go
func Scale(factor float64) {}                                        // before
func Scale(factor PositiveFloatNumber) {}                            // after: a scale factor is a positive float
```
```rust
fn shout(text: String) {}                                            // before
fn shout(text: PlainString) {}                                       // after: any text is acceptable
```

Only `shout` and the `name` in `greet` keep a plain type, and they do so on purpose. If a plain type appears where you would be unable to say "any value is fine", it is a missing refinement or brand.

## Step 4: find hand-applied generic rules

Before adding any refinement, check for an existing type ([golden rule](./reuse-before-create.md)): the rule you found may already be one import away.

Search any language for the same operations:

| Operation found (any language) | Generic rule | Refinement to add |
|--------------------------------|--------------|-------------------|
| lower / upper-casing a string | case | `LowercaseString`, `UppercaseString` |
| empty-string / null-or-empty check | emptiness | `NonEmptyString` |
| integer test | integer | `IntNumber` |
| NaN / infinity / finite test | finite | `FloatNumber` |
| `> 0`, `>= 0` | sign | `PositiveIntNumber`, `NonNegativeIntNumber` … |
| date validity check | valid instant | `ValidDate` |

**Operations are not refinements.** Trimming, truncating, collapsing spaces, escaping, decoding and Unicode normalization leave no trace in the result (a trimmed `"hello-world"` looks like any other string), so they never become tier 1 types. Move them into the creation point of the brand that needs them ([distinguishability test](../tiers/tier-1-primitives.md#what-qualifies-as-a-refinement-the-distinguishability-test)).

A rule that appears in **two or more modules** is the signal. A rule that appears once is still worth a refinement if it is a known bug source (case, sign, NaN).

## Steps 5 and 6: refine, then migrate

Before, the decision is scattered and invisible to review:

```
module A:  key = slug.lower()        module B:  key = slug        ← the bug
```

After, one refinement exists and the function that needs it says so in its signature. Changing the parameter type makes the compiler or type checker list every caller still passing an unrefined value. A different function in each language:

```ts
function lookupSlug(slug: LowercaseString) {}       // LowercaseString = Lowercase<string>, built in
lookupSlug(typed);        // error: 'string' is not assignable to 'Lowercase<string>'
```
```python
def retry(times: PositiveIntNumber) -> None: ...
retry(count)              # mypy: "int" is not "PositiveIntNumber"
```
```go
func Mean(xs []FiniteNumber) FiniteNumber { /* … */ }
Mean(raw)                 // compile error: []float64 is not []FiniteNumber
```
```rust
fn set_title(title: &NonEmptyString) { /* … */ }
set_title("");            // compile error: expected `&NonEmptyString`, found `&str`
```

The refinement's value comes from one of three sources ([tier 1](../tiers/tier-1-primitives.md#where-the-values-come-from)): a literal the compiler verifies, a more refined value, or a single creation point where a runtime value enters. No function per type is added to every call site. In a dynamically checked language with no checker, that creation point is the guard: make the function call it, or check at the public boundary.

## Edge cases to decide once

| Question | Where decided | Example decision |
|----------|---------------|------------------|
| Is `NaN` a number? | `FloatNumber` | `[no: FloatNumber is finite]` |
| What counts as an empty string? | `NonEmptyString` | `[length zero]` or `[no non-whitespace character]` |
| Is lowercasing locale-dependent? | `LowercaseString` | `[locale-independent]` |
| What is `-0`? | sign refinements | `[treat as 0]` |
| Are numeric strings numbers? | boundary, not tier 1 | parse at the boundary |

## Done when

- [ ] No raw type outside the primitive-family files
- [ ] Every hand-applied generic rule has one refinement and one creation point
- [ ] Lint enforces it

Next: [tier 1 → tier 2](./transform-tier-1-to-tier-2.md).
