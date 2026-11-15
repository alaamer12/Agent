# Transform: tier 1 → tier 2

> **Applies when the project adopts the tiered system** (Mode B in `../SKILL.md`). For general type enhancement without the tiers, use `core-workflow.md`.

Goal: every value with a domain meaning gets a brand with one creation point. A signature then says what the value *is*, not just which raw type it is made of.

*Standing note: options in `[brackets]` are illustrative, not exhaustive; adapt to the language.*

Identifiers in examples (`PlainX`, `toX`, `parseX`, `…Schema`) are illustrative role names, not conventions: follow the project's and ecosystem's own names and types ([naming](./tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). Prefer a type the compiler already provides ([compiler first](./wrong-type-errors.md)).

## Steps

```
1. List       find tier 1 types used for domain values (parameters, fields)
2. Name       <Domain><Meaning>: UserEmail, WorkerCount, OrderId
3. Choose     the most specific tier 1 type that is always true for the meaning
4. Define     the brand type
5. Create     one creation point; pick the policy
6. Replace    swap each occurrence of the tier 1 type for the brand
7. Delete     remove duplicated regexes, ranges and normalizations at call sites
```

## Questions that find missing brands

| Symptom | Brand to create |
|---------|-----------------|
| The same regex in several files | the brand for what it validates |
| The same range check twice | a brand with that range |
| A function takes several parameters of one raw type (`send(a, b)`) | a brand per meaning, so they cannot be swapped |
| A comment says "must be …" | the comment becomes the creation point |
| Two names for one idea (`uid`, `userId`, `user_id`) | one brand |
| An implied unit (`ms`, `cents`, `px`) | a brand carrying the unit |

## Choosing the base

| Meaning | Base | Why |
|---------|------|-----|
| `UserEmail` | `LowercaseString` | compared lowercase; the creation point also trims before it checks |
| `WorkerCount` | `PositiveIntNumber` | positive integer |
| `Port` | `PositiveIntNumber` | integer, bounded by the brand |
| `Price` | `IntNumber` | minor units, never floats |
| `Token` | `NonEmptyString` | never empty |

First look for an existing type ([golden rule](./reuse-before-create.md)). If no tier 1 type fits, add the refinement to tier 1 first. Never build a brand from a raw type.

## Before and after: swap-proof signatures

Two parameters of one raw type can be swapped silently; two brands cannot. A different function in each language:

```ts
function charge(account: string, amount: number) {}                    // before
function charge(account: AccountId, amount: MinorUnits) {}             // after
charge("acct_1", 500);   // error: the literal 500 is a number, not MinorUnits
```
```python
def schedule(delay: float, retries: int) -> None: ...                  # before
def schedule(delay: Seconds, retries: RetryCount) -> None: ...         # after
schedule(RetryCount(3), Seconds(1.5))   # mypy: swapped arguments
```
```go
func Connect(host string, port int) {}                                 // before
func Connect(host HostName, port Port) {}                              // after
```
```rust
fn resize(width: u32, height: u32) {}                                  // before
fn resize(width: Width, height: Height) {}                             // after
```

With `(string, string)` or `(u32, u32)` the old signature accepted swapped arguments; the branded one rejects them. The validation formerly repeated at call sites moves into the brand's single creation point (see [tier 2](../tiers/tier-2-brands.md)).

## Policy: normalize or reject

| Policy | Creation point returns | Use when |
|--------|--------------------|----------|
| `[normalize]` | the brand, always | any input can be repaired safely (trim and uppercase an ISO code) |
| `[normalize then reject]` | brand or failure | repair first, then check (an email) |
| `[reject]` | brand or failure | input must already be correct (a port) |

Decide once per group of sibling brands and record it in the catalog. These are example policies; a hybrid is fine if it is stated and consistent.

## A value with no rule

Still define the brand; its creation point accepts anything, and the brand records that the choice was made. One free-text brand per language:

```ts
export type UserBio = PlainString & Brand<"UserBio">;
```
```python
Remark = NewType("Remark", PlainString)
```
```go
type Comment struct{ v PlainString }
```
```rust
pub struct Nickname(PlainString);
```

## Placement

A brand lives with the feature that owns its meaning (`features/<owner>/types/brands/`); when two or more features need it, move it once to `shared/types/brands/`. See [tier 2](../tiers/tier-2-brands.md) and [structure](./tier-principles.md#structure-where-the-tier-folders-go).

## Done when

- [ ] No domain value is a bare tier 1 type in a public signature
- [ ] Each meaning has one brand and one creation point
- [ ] Duplicated validation at call sites is deleted
- [ ] Catalog lists the brand, its base, and its policy

Next: [tier 2 → tier 3](./transform-tier-2-to-tier-3.md).
