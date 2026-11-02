# Example — Zod (Empirical)

Illustrates a case where the tool's model is lightweight and additional structure is usually unnecessary.

## Tool model (extracted)

- Tool: zod · installed version from the lockfile · docs for that major (illustrative; a v3 review must not read
  v4 docs, and v3 idioms found in a v4 project are the review's most valuable finding)
- Core concepts: Schema, parse / safeParse, inferred types
- Paradigm: schema-first runtime validation + static inference
- Natural boundaries: a schema can live next to the domain type it validates
- Result model: success value or ZodError; safeParse returns a discriminated result
- Official guidance: define schemas, export them, use them directly for validation and type inference

## Typical respectful shape

```
User/
├── User.schema.ts   # Zod schema + inferred type
├── User.api.ts
└── …
```

No separate "decoder" or "validator service" layer is required by Zod's model.

## Diagnosis pattern

If a project already co-locates `User.schema.ts` with its consumers, Treat should report:

- Respectful aspects: schema is first-class, types are inferred, validation uses the schema directly
- Gaps: none (or only naming/style)
- Recommendations: none required

If a project hides the schema behind a generic `validate(input)` helper that erases the schema identity, flag the loss of the schema-as-concept and recommend making the schema visible again.
