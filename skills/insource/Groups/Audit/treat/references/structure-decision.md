# Structure Decision Rules

Treat exists to prevent both under-respect and over-structuring.

## When to recommend additional structure

Recommend new files, folders, or named abstractions only when at least one of the following is true:

1. The tool's model treats a concept as first-class and the project currently hides or flattens it.
2. Official examples or docs consistently separate concerns that the project currently merges.
3. Mixing the tool's concepts into an existing generic file creates mixed responsibilities or awkward naming.
4. The tool's result/error model or execution model is being ignored, producing brittle call sites.

## When to recommend no additional structure

Do not invent organization when:

1. The tool's model is already expressible cleanly inside the existing module layout.
2. The only change needed is naming or a small usage adjustment, not new boundaries.
3. Adding files would merely restate the same concept under a new name (bureaucracy).
4. The tool is used as a simple utility and its own docs treat it that way.

## Decision test (apply to every candidate recommendation)

```
Does the tool's model require this concept to be visible and named?
  YES → recommend representing it (file, type, module, or explicit boundary)
  NO  → leave the existing structure; note that the current shape is already respectful
```

## Proportionality

- Prefer the smallest change that restores respect for the model.
- Prefer renaming or relocating over introducing parallel hierarchies.
- Prefer explicitness where the tool is explicit; prefer simplicity where the tool is simple.

## Common failure modes to flag

| Failure | Symptom |
|---------|---------|
| Tool-as-helpers | Only low-level functions are called; higher concepts never appear |
| Forced shape | Project conventions override the tool's natural boundaries |
| Hidden model | Left/Right, Effect, Decoder, etc. are wrapped away so callers never see them |
| Invented ceremony | Extra layers that the tool itself does not use or recommend |
