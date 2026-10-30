---
name: treat
description: Evaluate how adopted tools and libraries want to be used and recommend project structure or implementation adaptations that respect their models, concepts, patterns, and constraints. Operates empirically from documentation or physically on existing code. Produces a TREAT.md report only — never edits code. Use when adopting a library, reviewing tool integration, checking whether a project forces a tool into an unnatural shape, or asking how to structure around Zod, Effect, io-ts, or similar. Triggers include treat, respect the tool, tool-aware structure, library model, adapt project to library.
---

# Treat

Respect the way a tool wants to be used. Do not force libraries into the project's existing shape. Produce a diagnostic report only; never edit source files.

## Core Principle

```
Using the same capability ≠ Using the same structure
```

A library is more than APIs. It may introduce concepts, terminology, patterns, file structures, execution models, programming paradigms, and supporting abstractions. Identify those and recommend where (if anywhere) the project should adapt.

## Operating Modes

Choose exactly one mode at the start. State it in the report.

| Mode | When | Primary evidence |
|------|------|------------------|
| **Empirical** | No (or incomplete) existing code for the tool | Official docs, guides, examples, API surface, design notes |
| **Physical** | Code already uses the tool | Actual project files + docs for intended model |

Empirical answers "how should we structure around this tool?". Physical answers "does the current structure respect the tool's model?".

## Mandatory Workflow

### 1. Capture scope
- Identify the tool(s) under review.
- Identify the relevant project area (feature, module, whole codebase).
- Note current project conventions only as secondary context — they do not override the tool's model.

### 2. Extract the tool's model
Read primary sources (docs, README, design docs, official examples). Extract:
- Core concepts and terminology the tool expects developers to use
- Recommended or natural file / module boundaries
- Programming paradigm or execution model
- Required or strongly suggested abstractions (schemas vs decoders, Effects, Left/Right, etc.)
- Constraints on data flow, error handling, type definitions, or runtime validation

Do not invent concepts the tool does not actually introduce. See `references/model-extraction.md`.

### 3. Inspect the project side
- **Empirical**: map the tool model onto the project's existing organization and naming.
- **Physical**: locate every place the tool is imported or used; note how concepts are named, grouped, or hidden.

### 4. Compare and diagnose
For each extracted concept or pattern ask:
- Is it represented in the project?
- Is it forced into an alien shape?
- Is the tool reduced to isolated helper calls while its model is ignored?
- Would additional structure help, or would it be bureaucracy?

Apply the anti-over-structuring rule: introduce structure only when the tool's model requires it.

### 5. Produce TREAT.md
Write the report to `TREAT.md` at the project root (or a path the user specifies). Never modify application source. Use the exact template in `references/report-template.md`.

## Progressive disclosure

| Need | Load |
|------|------|
| How to extract a tool's model | `references/model-extraction.md` |
| Report structure and required sections | `references/report-template.md` |
| Worked examples (Zod / Effect / io-ts style) | `examples/zod-simple.md`, `examples/effect-explicit.md` |
| Decision rules for "add structure or not" | `references/structure-decision.md` |

## Hard constraints

- **Never edit** project source, configs, or package files. Report only.
- Prefer official documentation and the tool's own examples over secondary blogs.
- Prefer the tool's native terminology over project-local aliases when diagnosing.
- If the tool's model fits the existing structure cleanly, say so and recommend no change.
- Keep recommendations proportional: respect, not bureaucracy.
