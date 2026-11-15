# Use the Project's Tools

Applies to **both modes**. The concepts in this skill (rules written once, creation points that reject, shapes assembled from named meanings, a boundary that parses outside data) do not depend on any library. **How they are implemented should follow what the project already uses**, not the plain-language examples in the other files.

*Standing note: library names and `[bracketed]` options are illustrative, not exhaustive; a hybrid or different answer is always acceptable. Verified by running: Zod 4.6.5, Valibot 1.5.0, Pydantic 2.13.5, Hypothesis 6.168.5. Not run here: ArkType, io-ts, and everything for Go and Rust. Check the project's installed version, since APIs and message formats change between major versions.*

Identifiers in examples (`PlainX`, `toX`, `parseX`, `…Schema`) are illustrative role names, not conventions: follow the project's and ecosystem's own names and types ([naming](./tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). Prefer a type the compiler already provides ([compiler first](./wrong-type-errors.md)).

## 1. Pick the implementation

```
1. The project already uses a validation library      → express creation points and shapes with it
2. The user names one                                  → use it, and say it adds a dependency
3. Neither                                             → hand-written creation points (the other files)
4. A mix is fine                                       → e.g. hand-written creation points + a library at the boundary
```

Whatever the library, look first for a type the compiler already provides for the static part (for example `Uppercase<string>`), and use the library for the runtime part. Never add a dependency just to follow this skill, and never write a type a dependency already provides ([golden rule](./reuse-before-create.md)). Detect first:

| Ecosystem | Look in | Signals |
|-----------|---------|---------|
| JavaScript / TypeScript | `package.json` | `zod`, `valibot`, `arktype`, `io-ts`, `yup`, `joi`, `@sinclair/typebox` |
| Python | `pyproject.toml`, `requirements*` | `pydantic`, `attrs` + `cattrs`, `marshmallow`, `beartype`; tests: `hypothesis` |
| Go | `go.mod` | `go-playground/validator`; tests: `rapid`, `testing/quick` |
| Rust | `Cargo.toml` | `serde`, `validator`, `garde`; tests: `proptest` |
| Others | build manifest | the ecosystem's validation / property-testing libraries |

## 2. Concept to library feature

| Concept | Zod | Valibot | Pydantic | Go / Rust (typical) |
|---------|-----|---------|----------|---------------------|
| Generic state (tier 1) | `z.string().toLowerCase()`, `z.number().int()` | `v.pipe(v.string(), v.toLowerCase())` | `StringConstraints(to_lower=True)`, `Field(ge=1)` | validator tags / `TryFrom` |
| Brand (nominal marker) | `.brand<"Name">()` | `v.brand("Name")` | `NewType("Name", base)` for static distinction | unexported field / newtype |
| Creation point (normalize or reject) | `schema.parse` / `schema.safeParse` | `v.parse` / `v.safeParse` | `TypeAdapter(T).validate_python`, `Model.model_validate` | `New…` / `TryFrom` |
| Shape (tier 3) | `z.object({...})`, `z.discriminatedUnion` | `v.object`, `v.variant` | `BaseModel`, tagged unions | structs / `enum` |
| Type derived from the rule | `z.infer<typeof S>` | `v.InferOutput<typeof S>` | the annotation itself | the struct itself |
| Property test of a creation point | any property tester | any property tester | Hypothesis `@given` | `rapid`, `proptest` |

The library schema is the **single source of truth**: derive the static type from it and do not hand-write a second type that can drift.

## 3. Zod example (the tiers, in the library)

```ts
// tier 1: shared/types/primitives/*.ts   ← the only files that call z.string() / z.number()
export const LowercaseString = z.string().toLowerCase().brand<"Lowercase">();   // a visible state
export const IntNumber       = z.number().int().brand<"Int">();
export const PositiveInt     = IntNumber.positive().brand<"Positive">();

// tier 2: brands, built only from tier 1 schemas
export const OrderId  = LowercaseString.startsWith("ord_").brand<"OrderId">();
export const Sku      = LowercaseString.regex(/^[a-z0-9-]+$/).brand<"Sku">();
export const Quantity = PositiveInt.max(1000).brand<"Quantity">();

// tier 3: a shape
export const OrderLine = z.object({ sku: Sku, qty: Quantity });
export const Order     = z.object({ id: OrderId, lines: z.array(OrderLine).min(1) });
export type Order      = z.infer<typeof Order>;

// an ordinary function takes the shape; the compiler rejects plain values
function totalQuantity(order: Order): number { return order.lines.reduce((sum, l) => sum + l.qty, 0); }

// boundary
Order.parse({ id: "ORD_7", lines: [{ sku: "AB-1", qty: 2 }] });     // id "ord_7", sku "ab-1": normalized, then checked
Order.safeParse({ id: "7", lines: [{ sku: "bad sku", qty: 0 }] });  // success: false; issues name each path and rule
```

Checked: brands stack and a derived type carries every brand; a refined value flows up; calling `totalQuantity` with plain values, or building an `Order` from a plain string or number, is a compile error; invalid runtime data returns issues with the field path (`id`, `lines.0.sku`, `lines.0.qty`).

**Library caveats (Zod, verified):**

- `refine` alone does **not** change the TypeScript type: `z.infer` is still `string`. Add `.brand<"Name">()` to get the nominal type.
- The rule runs at **runtime only**. For literals that should fail the build, keep a compile-time check beside the schema ([wrong-type errors](./wrong-type-errors.md)); closed sets use `z.enum` / `z.literal`, which are checked statically.
- Normalizing schemas have different input and output types; use `z.input<>` for what callers send and `z.infer<>` (output) for what circulates inside.
- Mode B keeps its law: `z.string()` and `z.number()` are raw types, so they appear only in tier 1 files.

## 4. Valibot differences (verified)

Valibot's validation actions are typed against the pipe's current output, so apply them **before** `v.brand`, or continue a branded pipe with `v.check`:

```ts
const IntNumber = v.pipe(v.number(), v.integer(), v.brand("Int"));
const Percent   = v.pipe(IntNumber, v.check(n => n >= 0 && n <= 100, "must be 0..100"), v.brand("Percent"));

function label(p: v.InferOutput<typeof Percent>): string { return `${p}%`; }
label(v.parse(Percent, 40));           // "40%"
v.safeParse(Percent, 140).success;     // false
v.safeParse(Percent, 4.5).success;     // false (not an integer)
```

ArkType and io-ts offer the same idea (a typed schema that infers the static type); the exact syntax was not run here, so consult the project's installed version.

## 5. Pydantic and Hypothesis (verified)

```python
PathValue   = NewType("PathValue", str)                        # static nominal distinction
WorkerCount = NewType("WorkerCount", int)
PathField   = Annotated[PathValue, StringConstraints(strip_whitespace=True, min_length=1)]
WorkerField = Annotated[WorkerCount, Field(ge=1, le=64)]

class Job(BaseModel):                                          # a shape
    model_config = {"frozen": True}
    source: PathField
    workers: WorkerField

Job.model_validate({"source": "  data/in ", "workers": 8})     # source='data/in' workers=8
Job.model_validate({"source": "   ", "workers": 100})          # ValidationError: source too short, workers <= 64
```

Pydantic validates at runtime; a static checker still needs `NewType` (or an equivalent) for the nominal part. A property test pins the creation point's contract (validating twice changes nothing):

```python
adapter = TypeAdapter(PathField)
@given(st.text())
def test_stable(s):
    try: once = adapter.validate_python(s)
    except ValidationError: return                  # rejected inputs may stay rejected
    assert adapter.validate_python(once) == once
```

**A library's normalization is its own.** Hypothesis found that Pydantic's `strip_whitespace` leaves `"\x1f"` unchanged while Python's `str.strip()` removes it. Test idempotence and use shared vectors; never assume a library's normalization equals the language function's ([database constraints](./database-constraints.md) shows the same kind of gap).

## 6. How the modes use libraries

- **Mode A (general):** use the library's own features directly (`.refine`, `Field`, constraints) to tighten what is already there. Branding, tier files and the tier laws are not required.
- **Mode B (tiered):** the library implements the creation points, and only tier 1 imports its value types (tiers 2 and 3 import from tier 1). Tier files become library-schema files in the same folders (`primitives/`, `brands/`, `shapes/`, see [structure](./tier-principles.md#structure-where-the-tier-folders-go)); tier order and the one-file-per-family law still hold, because schemas import only the schemas of the tier below.

If a library is used only at the boundary and creation points are hand-written inside, keep the library schema derived from or tested against the creation points, so a rule never exists in only one of them.

Database constraints belong in the project's own migration or schema tool; generate or test them against the same rules ([database constraints](./database-constraints.md)).

## 7. Done when

- [ ] The implementation uses what the project already depends on, or the user approved a new dependency
- [ ] Static types are derived from the library schemas, not duplicated
- [ ] Brands (or the language's equivalent) make wrong kinds a check-time error
- [ ] Rules that the library cannot check statically have a compile-time or runtime guard of their own
- [ ] Creation points have property or table tests, with the project's test tooling
