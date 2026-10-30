# Extracting a Tool's Model

Goal: recover the concepts and usage patterns the tool itself expects, not the lowest-level functions it exports.

## Primary sources (prefer in order)

1. Official documentation and "Getting Started" / "Concepts" pages
2. The library's own README and design notes
3. Official examples and recipes in the repository
4. Type definitions and public API surface (for TypeScript libraries)
5. Author or maintainer commentary that explains intent

Secondary blogs and "how I use X" posts are supporting evidence only.

## What to extract

Record only what the tool actually introduces or strongly implies:

| Category | Questions to answer |
|----------|---------------------|
| **Concepts & terminology** | What nouns and verbs does the docs use repeatedly? (Schema, Effect, Decoder, Program, Left/Right, Layer, …) |
| **Paradigm / execution model** | Imperative? Functional? Effect system? Schema-first? Pipeline? Explicit decoding? |
| **Natural boundaries** | Does the tool encourage separating schema from decoder, definition from usage, pure from effectful? |
| **Required abstractions** | Are there types or values the tool expects you to name and pass around? |
| **Error / result model** | How does the tool represent success and failure? Does it expect callers to handle that shape? |
| **File / module expectations** | Do official examples keep related concepts together or split them? |
| **Anti-patterns the tool warns against** | Any explicit "don't do this" guidance? |

## Extraction discipline

- Quote or paraphrase the tool's own language; do not translate everything into the project's existing vocabulary first.
- Distinguish "the tool provides a helper" from "the tool's model requires this concept to be first-class".
- If two tools solve similar problems (e.g. Zod vs Effect vs io-ts), extract each model independently. Overlap in capability does not imply identical structure.

## Output of this step

A short, explicit list:

```
Tool: <name>
Core concepts: …
Paradigm: …
Natural boundaries: …
Result/error model: …
Official guidance on structure: …
```

This list becomes the left-hand side of the later comparison.
