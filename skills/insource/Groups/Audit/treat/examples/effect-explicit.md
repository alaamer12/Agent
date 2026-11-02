# Example — Effect (Physical)

Illustrates a case where the tool's model introduces richer concepts that often benefit from explicit representation.

## Tool model (extracted)

- Tool: effect · installed version from the lockfile · docs for that major (illustrative; the model is
  version-scoped and evolves between majors)
- Core concepts: Effect, Schema, Decode / encode, Layer, Context, Program
- Paradigm: effect system with explicit success/failure, dependencies, and decoding
- Natural boundaries: schema definition is distinct from the decoding operation that produces an Effect
- Result model: Effect<A, E, R> — success, typed error, and requirements are all first-class
- Official guidance: keep decoding explicit; compose programs; do not treat Effect as a hidden implementation detail

## Diagnosis pattern (Physical)

Inspect existing code for:

- Whether `Schema` and decoding are collapsed into a single "validate" call that returns a plain value
- Whether Effects are immediately run and the Effect type never appears at module boundaries
- Whether error channels are widened to `unknown` or swallowed

## Typical respectful adjustments

When the project currently has only:

```
User/
└── User.schema.ts   # everything mixed
```

and Effect's decoding model is in use, a proportional recommendation may be:

```
User/
├── User.schema.ts   # schema definition
├── User.decode.ts   # explicit decode that returns Effect
└── User.api.ts
```

or an equivalent boundary that keeps "schema" and "decode-to-Effect" visible.

## Decision reminder

Only recommend the extra file or module if the project is actually using Effect's decoding / Effect model. If Effect is used merely as a Promise alternative with no schema/decode involvement, do not invent decode modules.
