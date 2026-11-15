# Transform: boundary input ↔ tier 3, and variants

> **Applies when the project adopts the tiered system** (Mode B in `../SKILL.md`). For general type enhancement without the tiers, use `core-workflow.md`.

Goal: outside data enters through one boundary check, and only validated shapes circulate inside. A shape that exists in more than one variant gets a name per variant.

*Standing note: options in `[brackets]` are illustrative, not exhaustive; adapt to the language.*

Identifiers in examples (`PlainX`, `toX`, `parseX`, `…Schema`) are illustrative role names, not conventions: follow the project's and ecosystem's own names and types ([naming](./tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). Prefer a type the compiler already provides ([compiler first](./wrong-type-errors.md)).

## The boundary

A boundary is anywhere data arrives that the type system did not create: network responses, storage, environment variables, URL parameters, form input, CLI arguments, files, message queues.

```
untrusted input  →  parse<Name>()  →  <Name>Schema  →  rest of the app
(unknown / PlainX)   creation points   (tier 3)
```

`PlainX` and the language's "unknown" type are allowed in boundary files and as creation point inputs; nowhere else outside tier 1.

## Steps

```
1. List boundaries    every place external data arrives
2. Type the input     the language's unknown/any-input type, or a PlainX-field shape
3. Write the check    call each field's brand creation point; collect failures
4. Return a result    the shape, or an error naming the failing field
5. Route everything   internal code accepts only shapes
6. Mirror outward     one toWire per output, from shape to serializable form
```

## Boundary-check example

The check holds no rules of its own; each rule lives in a brand's creation point. Whether it is a function at all (a library schema, `TryFrom`, a decoder, a type guard), how it is named, and its failure carrier (`Either`, `Result`, `(T, error)`, an exception) follow the project and ecosystem. A different boundary in each language:

```ts
// TypeScript: an HTTP body becomes an Invoice; the carrier here is an exception
function readInvoice(raw: unknown): Invoice {
  const r = (typeof raw === "object" && raw !== null ? raw : {}) as Record<string, unknown>;
  if (typeof r.id !== "string" || !isOrderId(r.id)) throw new BoundaryError("id", "expected ord_…");
  if (typeof r.amount !== "number" || !isMinorUnits(r.amount)) throw new BoundaryError("amount", "expected whole minor units");
  return { id: r.id, amount: r.amount };
}
```
```python
# Python: a parsed JSON dict becomes an Order; the carrier is an exception
def read_order(raw: dict[str, object]) -> Order:
    order_id = raw.get("id")
    if not isinstance(order_id, str) or not order_id.startswith("o-"):
        raise ValueError("id: expected o-…")
    return Order(id=OrderId(order_id), lines=())
```
```go
// Go: a decoded request map becomes a SearchRequest; the carrier is (value, error)
func ReadRequest(raw map[string]any) (SearchRequest, error) {
    q, _ := raw["query"].(string)
    query, err := NewSearchQuery(q)
    if err != nil { return SearchRequest{}, fmt.Errorf("query: %w", err) }
    l, _ := raw["limit"].(float64)
    limit, err := NewPageSize(l)
    if err != nil { return SearchRequest{}, fmt.Errorf("limit: %w", err) }
    return SearchRequest{Query: query, Limit: limit}, nil
}
```
```rust
// Rust: a wire struct with plain-type fields becomes a Payment; the carrier is Result
impl TryFrom<RawPayment> for Payment {
    type Error = PaymentError;
    fn try_from(r: RawPayment) -> Result<Self, Self::Error> {
        Ok(Self {
            account: AccountId::try_from(r.account).map_err(|e| PaymentError::field("account", e))?,
            amount: MinorUnits::try_from(r.amount).map_err(|e| PaymentError::field("amount", e))?,
        })
    }
}
```

If a validation library is used (Zod, Pydantic, serde, validator tags…), derive it from the creation points or test it against them, so a rule never exists in the library and not in the creation point.

## Variants

When a shape has more than one variant, name each variant instead of loosening one type:

| Variant | What it is | Fields |
|---------|-----------|--------|
| **Raw** (boundary input) | what the user or outside system provides | unknown / plain-type fields |
| **Patch** (overrides) | what a CLI or API call may change | brands, all optional |
| **Resolved** | after defaults, merge and validation | brands, required ones present |

A different shape in each language:

```ts
type ScanPatch    = { mode?: ScanMode; workers?: WorkerCount };
type ResolvedScan = { root: PathValue; mode: ScanMode; workers: WorkerCount };
const resolveScan = (file: ScanPatch, cli: ScanPatch): ResolvedScan => ({ ...DEFAULTS, ...file, ...cli });
```
```python
@dataclass(frozen=True)
class ExportPatch:
    format: ExportFormat | None = None
    compression: Compression | None = None

@dataclass(frozen=True)
class ResolvedExport:
    path: PathValue
    format: ExportFormat
    compression: Compression
```
```go
type ServerPatch struct{ Port *Port; Workers *WorkerCount }
type ResolvedServer struct{ Host HostName; Port Port; Workers WorkerCount }
func Resolve(file, cli ServerPatch) ResolvedServer { /* defaults, then file, then cli */ }
```
```rust
struct BuildPatch { target: Option<Target>, jobs: Option<JobCount> }
struct ResolvedBuild { target: Target, jobs: JobCount, out_dir: PathValue }
fn resolve(file: BuildPatch, cli: BuildPatch) -> ResolvedBuild { /* defaults ← file ← cli */ }
```

Only the resolved variant circulates in the app.

## Callers without static checking

Plain-JavaScript callers, scripts and other processes cannot be stopped by a compiler. Give them the **runtime** path: export the creation points and boundary checks, and check at the public boundary. Types document the contract; creation points enforce it.

## Failure handling (example options)

`[return a result naming the failing field]` is a good default; `[throw a typed error]` suits process startup where failing fast is correct; `[collect all errors]` suits forms and bulk imports. Pick one default per project and keep it for every boundary.

## Done when

- [ ] Every boundary has one boundary check
- [ ] Boundary checks contain no rules, only creation point calls
- [ ] Internal code takes only shapes
- [ ] Each variant of a shape has its own named type
- [ ] Each output has one `toWire`
