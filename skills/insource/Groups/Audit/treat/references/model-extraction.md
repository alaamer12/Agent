# Extracting a Tool's Model

Goal: recover the concepts and usage patterns the tool itself expects, for the version actually installed — not the
lowest-level functions it exports, and not the previous major's habits.

## Which version's model

1. Resolve the installed version from the lockfile (not the range in the manifest). No lockfile → use the manifest
   range, say so, and lower the confidence of the findings that depend on it.
2. Read documentation for that version, or for its major. Never from memory, and never from docs of a different major.
3. Docs for the installed version unfindable → say so, lower confidence, do not silently fall back to memory.
4. When a major changed the tool's **model** (not just its API surface), that is the highest-value finding of the
   review. In Physical mode, code still following the previous major's idioms is a finding.

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
Installed version: <from the lockfile, or the manifest range if there is none>
Docs source and version used: <page/site and version>
Core concepts: …
Paradigm: …
Natural boundaries: …
Result/error model: …
Official guidance on structure: …
```

This list becomes the left-hand side of the later comparison, and its version lines carry straight into the report.
