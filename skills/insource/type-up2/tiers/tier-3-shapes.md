# Tier 3: Shapes

> **Applies when the project adopts the tiered system** (Mode B in `../SKILL.md`). For general type enhancement without the tiers, use `../references/core-workflow.md`.

> A shape assembles brands into a record, a configuration, a contract, or a tagged union.

*Standing note: layouts, names and `[bracketed]` options are illustrative examples, not a closed set; a hybrid or different answer is always acceptable. Adapt identifiers and file extensions to the language.*

Identifiers in examples (`PlainX`, `toX`, `parseX`, `…Schema`) are illustrative role names, not conventions: follow the project's and ecosystem's own names and types ([naming](../references/tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). Prefer a type the compiler already provides ([compiler first](../references/wrong-type-errors.md)).

Creation points may be hand-written (shown here) or built with the project's validation library: see [use the project's tools](../references/tooling-adaptation.md).

## Purpose

Answer "which values travel together, and which are optional?" A shape adds no value rules (those live in tier 2). It adds **structure**.

## Rules (language-independent)

1. **Fields are brands or other shapes.** No raw types, no `PlainX` fields.
2. **Build only from tier 2 and tier 3.** A shape reaching into tier 1 skips a tier; give the field a brand.
3. **Mark optional and required explicitly.**
4. **Use tagged unions (sum types) for anything with cases**, so each case carries exactly its own data.
5. **Keep variants separate** when a shape exists in more than one variant: raw (boundary input), patch, resolved. Never loosen one shape to serve all three.
6. **Document every public shape**: one-sentence purpose, a real example, the constraints its brands enforce.
7. **Opaque bags are named.** Per-item extension options may be a named opaque type; an anonymous `Record<string, unknown>` / `dict[str, Any]` / `map[string]any` is a raw type in disguise.

8. **Reuse before you create** (golden rule). A shape may be the project's own model type (a Pydantic `BaseModel`, a Zod object, a serde struct) instead of a custom class; its fields still use brands imported from tier 2, never library value types ([reuse-before-create](../references/reuse-before-create.md)).

## Project structure and placement
*Folder names are example names: this skill prefers `primitives/`, `brands/` and `shapes/`, but the project's own convention wins, and for brands the ecosystem's own word is fine (`newtypes/`, `opaque/`). Source folders unrelated to types are hidden below. Full layout and rules: [structure](../references/tier-principles.md#structure-where-the-tier-folders-go).*

Tier 3 follows **the owner of the shape**: with the feature that defines and evolves it, or in shared when two or more features use it.

```
src/
├── …                                (app, ui, and every other source folder: hidden)
├── shared/
│   └── types/
│       ├── primitives/              tier 1
│       ├── brands/                  tier 2 used by two or more features
│       └── shapes/                  tier 3 used by two or more features
│           └── config.<ext>         ConfigShape, ResolvedConfig
└── features/
    ├── search/
    │   ├── …                        (views, components, decorations, hooks, services: hidden)
    │   └── types/
    │       ├── brands/              tier 2 owned by search
    │       └── shapes/              tier 3 owned by search
    │           └── search.<ext>     SearchState, SearchQuery
    └── profile/
        └── types/shapes/ …          tier 3 owned by profile
```

Placement test: a shape used by one feature lives in that feature's `types/shapes/`; one used by several lives in `shared/types/shapes/`. Its fields' brands are imported from wherever they are owned. The boundary check that produces a shape lives next to it, or beside the service that receives the data (`[next to the shape]`, `[with the service]`); the project decides.

## Example: shapes consumed by ordinary functions

A shape is used in ordinary function signatures too. Each language shows a different shape.

**TypeScript** (a tagged union; data exists only in the case that has it, and a missing case is a compile error):

```ts
type SearchState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; results: ResultItem[] }
  | { kind: "error"; message: ErrorMessage };

function describe(s: SearchState): string {
  switch (s.kind) {
    case "idle":    return "waiting";
    case "loading": return "loading";
    case "success": return `${s.results.length} results`;     // results exists only here
    case "error":   return s.message;
    default: { const unhandled: never = s; return unhandled; } // a missing case fails to compile
  }
}
```

**Python** (a record of brands):

```python
@dataclass(frozen=True)
class OrderLine:
    sku: Sku
    qty: Quantity

@dataclass(frozen=True)
class Order:
    id: OrderId
    lines: tuple[OrderLine, ...]

def total_quantity(order: Order) -> int:
    return sum(line.qty for line in order.lines)

Order(id="o-1", lines=())      # mypy: Argument "id" has incompatible type "str"; expected "OrderId"
```

**Go** (no sum types, so a sealed interface):

```go
type Job interface{ isJob() }               // sealed: unexported method
type Queued struct{ Position PositiveIntNumber }
type Running struct{ Progress Percent }
type Finished struct{ Output PathValue }
func (Queued) isJob()   {}
func (Running) isJob()  {}
func (Finished) isJob() {}

func Describe(j Job) string {
    switch v := j.(type) {
    case Queued:   return "queued"
    case Running:  return "running"
    case Finished: return "done: " + v.Output.String()
    }
    return ""   // the Go compiler does not check exhaustiveness; a linter such as `exhaustive` does
}
```

**Rust** (an enum; omitting a case is a compile error):

```rust
pub enum Upload {
    Idle,
    Sending { progress: Percent },
    Done { url: Url },
    Failed { reason: ErrorMessage },
}

pub fn label(u: &Upload) -> String {
    match u {
        Upload::Idle => "idle".into(),
        Upload::Sending { progress } => format!("{}%", progress.get()),
        Upload::Done { url } => url.to_string(),
        Upload::Failed { reason } => reason.to_string(),
    }
}
```

**Variants kept separate** (shown as names only, since the idea is the same everywhere): `RawConfig` (unvalidated input), `ConfigPatch` (brand fields, all optional), `ResolvedConfig` (brand fields, required ones present). Only the resolved variant circulates inside the app.

## How tier 3 differs from the others

| | Tier 1 | Tier 2 | Tier 3 |
|---|--------|--------|--------|
| Adds | a generic rule | a domain meaning | structure |
| Contains | one plain or refined type | one refined value | many values |
| Creation | validates a value | validates a meaning | the boundary check composes brand creation points (library schema, `TryFrom`, decoder, `parse`) |
| Placement | `shared/types/primitives/` only | owner, or shared if used by 2+ features | owner, or shared if used by 2+ features |
| Typical name | `PositiveIntNumber` | `WorkerCount` | `ResolvedConfig` |
| Unit of change | a rule | a rule in a domain | a field list |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `PlainX` in a field | Define a brand in tier 2 |
| One shape loosened to serve raw, patch and resolved | Three named variants |
| Boolean flags for cases (`isLoading`, `hasError`) | Tagged union |
| A shape defining validation rules | Move the rule into the brand's creation point |
| Undocumented public shape | Add purpose, example, constraints |

See also: [database constraints](../references/database-constraints.md) (a record becomes a table, a tagged union a `kind` column with a `CHECK`), [tier 2 to tier 3](../references/transform-tier-2-to-tier-3.md) and [boundary and variants](../references/transform-boundary-and-variants.md).
