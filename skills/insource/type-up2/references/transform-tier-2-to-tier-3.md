# Transform: tier 2 → tier 3

> **Applies when the project adopts the tiered system** (Mode B in `../SKILL.md`). For general type enhancement without the tiers, use `core-workflow.md`.

Goal: values that travel together become one named shape, so no function takes a loose list of brands and no shape is described only in a comment.

*Standing note: options in `[brackets]` are illustrative, not exhaustive; adapt to the language.*

Identifiers in examples (`PlainX`, `toX`, `parseX`, `…Schema`) are illustrative role names, not conventions: follow the project's and ecosystem's own names and types ([naming](./tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). Prefer a type the compiler already provides ([compiler first](./wrong-type-errors.md)).

## Steps

```
1. Group      find brands that always appear together (parameter lists, literals, DTOs)
2. Name       <Name>Schema / <Name>State / <Name>Patch
3. Mark       required vs optional per field
4. Find cases if the shape has modes, model a tagged union
5. Define     the shape, from brands only
6. Replace    swap parameter lists and anonymous objects for it
7. Split      separate raw, patch and resolved variants when they differ
8. Document   purpose, example, constraints
```

## Finding groups

| Symptom | Shape |
|---------|--------------|
| A function with 3+ related brand parameters | one shape parameter |
| The same object shape built in several places | a shape |
| An interface / struct / dataclass with raw fields | a shape, after each field gets a brand |
| Flags like `isLoading`, `hasError`, `data?` | a tagged union |
| Fields valid only in some modes | a tagged union, one case per mode |
| Config read from a file, overridden by CLI, then defaulted | three variants ([boundary and variants](./transform-boundary-and-variants.md)) |

Order matters: a field cannot enter a shape until its brand exists, so run [tier 1 → tier 2](./transform-tier-1-to-tier-2.md) per field first.

## Before and after: raw record

A different record in each language; every field becomes a brand (tier 2 first), then the record is assembled:

```ts
interface Invoice { id: string; amount: number; note?: string }                          // before
type Invoice = { id: OrderId; amount: MinorUnits; note?: Remark }                        // after
```
```python
@dataclass
class Address: street: str; city: str; postcode: str                                     # before
@dataclass(frozen=True)
class Address: street: Street; city: City; postcode: PostCode                            # after
```
```go
type ServerConfig struct{ Host string; Port int; Workers int }                           // before
type ServerConfig struct{ Host HostName; Port Port; Workers WorkerCount }                // after
```
```rust
struct Shipment { weight: f64, destination: String, priority: u8 }                       // before
struct Shipment { weight: Kilograms, destination: CountryCode, priority: Priority }      // after
```

## Before and after: flags to a tagged union

Before, impossible states are representable (loading with a result set, an error and a result together). A different shape in each language:

```ts
type Download = { isLoading: boolean; error?: string; file?: FileRef };                   // before
type Download =                                                                           // after
  | { kind: "idle" } | { kind: "running"; percent: Percent }
  | { kind: "done"; file: FileRef } | { kind: "failed"; reason: ErrorMessage };
```
```python
@dataclass
class Payment: paid: bool; failure: str | None; receipt: str | None                      # before
Payment = Pending | Paid | Declined      # frozen dataclasses: Paid(receipt: ReceiptId), Declined(reason: ErrorMessage)
```
```go
type Connection struct{ Up bool; Err string; Session string }                            // before
type Connection interface{ isConnection() }   // sealed: Down{}, Up{Session SessionId}, Failed{Reason ErrorMessage}
```
```rust
struct Sync { running: bool, error: Option<String>, last_run: Option<String> }             // before
enum Sync { Idle, Running { since: Timestamp }, Failed { reason: ErrorMessage } }          // after
```

After, each case carries only its own data, and handling is checked for coverage: a discriminated union with a `never` check in TypeScript, `match` with a type checker in Python, a sealed interface plus an exhaustiveness linter in Go, an `enum` in Rust (full examples in [tier 3](../tiers/tier-3-shapes.md)).

## Nesting and opaque bags

A shape may contain others (`OrderSchema { customer: UserSchema, lines: [OrderLineSchema], total: MinorUnits }`); never inline raw fields into the nested shape.

Where a shape must allow per-item extension without coupling the core to every extension, name the bag (`ExtensionOptions`) and document it; an anonymous map type is a raw type in disguise.

## Documentation pattern

Every public shape states: a one-sentence purpose, a real example in the consumer's language, and the constraints its brands enforce, using the language's doc-comment form (JSDoc, docstring, godoc, rustdoc).

## Placement

A shape lives with the owner of the shape (`features/<owner>/types/shapes/`, or `shared/types/shapes/` when two or more features use it); its brands are imported from wherever they are owned. See [tier 3](../tiers/tier-3-shapes.md) and [structure](./tier-principles.md#structure-where-the-tier-folders-go).

## Done when

- [ ] No public function takes an unnamed group of related brands
- [ ] No shape field is a raw type or `PlainX`
- [ ] Cases are tagged unions, not flag combinations
- [ ] Every public shape is documented
- [ ] Raw, patch and resolved variants are separate where they differ
