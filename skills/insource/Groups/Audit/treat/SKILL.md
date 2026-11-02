---
name: treat
description: 'Evaluate how adopted tools and libraries want to be used and recommend structure or adaptations that respect their model - concepts, patterns, constraints. Reviews a named tool, or discovers model-heavy candidates from the dependency manifests when none is named. Version-aware: the model comes from docs for the installed version, and previous-major idioms are findings. Produces a diagnostic report (in chat by default, as TREAT.md on request) and never edits code. Use when adopting a library or checking whether a project forces a tool into an unnatural shape (Zod, Effect, io-ts). Triggers include treat, respect the tool, tool-aware structure, library model, adapt project to library, zod v3 vs v4, library migration, are we using this library correctly.'
---

# Treat

Respect the way a tool wants to be used. Do not force libraries into the project's existing shape. Produce a diagnostic report — in chat by default, as `TREAT.md` only if asked; never edit source files.

## Core Principle

```
Using the same capability ≠ Using the same structure
```

A library is more than APIs. It may introduce concepts, terminology, patterns, file structures, execution models, programming paradigms, and supporting abstractions. Identify those and recommend where (if anywhere) the project should adapt.

## Operating Modes

Choose exactly one mode at the start. State it, and the reviewed version, in the report.

| Mode | When | Primary evidence |
|------|------|------------------|
| **Empirical** | No (or incomplete) existing code for the tool | Official docs, guides, examples, API surface, design notes |
| **Physical** | Code already uses the tool | Actual project files + docs for intended model |

Empirical answers "how should we structure around this tool?". Physical answers "does the current structure respect the tool's model?".

## Version rules

A library's model is version-specific, so version is part of the evidence, not metadata:

- Resolve the **installed** version from the lockfile, not the range in the manifest. No lockfile → use the manifest range and lower the confidence of affected findings.
- Extract the model only from documentation for that version (or its major). Never from memory, and never from docs of a different major.
- State the reviewed version(s) and the docs source and version used, per tool, in the report.
- In Physical mode, code still following a previous major's idioms is a finding (for example Zod v3 patterns in a v4 project, or a deprecated API still in use).
- Mixed versions installed, or partial adoption of new APIs, is itself a finding: report the migration as unfinished rather than picking a side.
- If docs for the installed version cannot be found, say so, lower the confidence of the affected findings, and never fall back to memory silently.
- When a major changed the tool's **model** — not merely its API surface — call that out as the highest-value finding category.

## Mandatory Workflow

### 1. Capture scope

No formal argument syntax exists: whatever follows `/treat` is free text to interpret.

| Invocation | Meaning |
|---|---|
| `/treat zod` | review that tool |
| `/treat zod in src/api` | review that tool in that area |
| `/treat zod and effect` | review several named tools |
| `/treat` | run discovery, then review |

**Bare `/treat` discovery:**

1. Read the dependency manifest(s) (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, …) and the lockfile.
2. Shortlist **model-heavy** candidates: libraries that bring their own concepts, paradigm, or required abstractions, and that are easy to under-use, half-use, or misuse — validation/schema (Zod, io-ts, Valibot), effect systems (Effect), data fetching and caching (TanStack Query), ORMs and query builders (Drizzle, Prisma), RPC (tRPC), state machines (XState).
3. Strong signals for inclusion: the tool is optional enough that a team can forget it or reduce it to shallow helper functions; or it has had a breaking major version, so old habits can survive silently.
4. Exclude: foundational frameworks the project cannot avoid (React, Next.js, Django, Rails) — misuse surfaces immediately and the framework dictates structure; utility libraries with no distinct model (lodash, date-fns, clsx, uuid); tooling/build/lint dependencies unless the user named them.
5. Present the shortlist with one line of reason per candidate. Three or fewer → review them all without asking. More than three → ask one concise question about priority and recommend a top 3.
6. Nothing qualifies → say so plainly and stop. Do not invent work.

**Scope notes:**

- Identify the area under review (feature, module, whole codebase); default to the whole codebase.
- Current project conventions are secondary context only; they never override the tool's model.
- Resolve the installed version per tool now, per **Version rules**.

### 2. Extract the tool's model
Read primary sources (docs, README, design docs, official examples) **for the installed version**. Extract:
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
- Is it using the **previous major's** model while the installed version moved on (Version rules)?
- Would additional structure help, or would it be bureaucracy?

Apply the anti-over-structuring rule: introduce structure only when the tool's model requires it.

Then give each tool a verdict: **fits cleanly** / **partial mismatch** / **significant mismatch**.

### 5. Report

**Default: deliver the report in chat.** Write `TREAT.md` (project root, or a path the user gives) only when asked — "save it", "export", "write TREAT.md", or a named path. That file is the **only** write this skill may ever perform, in either mode.

Both outputs use the same structure from `references/report-template.md`. In chat, keep it compact: verdict per tool first, then findings, then recommendations — omit sections that would be empty instead of pasting the skeleton.

Per tool, the report must include:

- reviewed **version** (from the lockfile) and the **docs source and version** used
- **mode** (Empirical or Physical)
- **verdict** (fits cleanly / partial mismatch / significant mismatch)
- **findings**, each with a confidence, and lowered confidence wherever the version evidence was indirect
- **recommendations**, proportional to the finding

If the structure already respects the tool's model, say so and recommend no change — that is a valid and encouraged outcome, not a failed review. `references/report-template.md` must carry these same fields (per-tool version, docs source, mode, verdict, findings with confidence, recommendations); update it if it does not.

## Progressive disclosure

| Need | Load |
|------|------|
| Which candidates are worth reviewing, for bare `/treat` | this file, step 1 |
| How to extract a tool's model, and for which version | `references/model-extraction.md` |
| Report structure and required sections (chat and file) | `references/report-template.md` |
| Worked examples (Zod / Effect / io-ts style) | `examples/zod-simple.md`, `examples/effect-explicit.md` |
| Decision rules for "add structure or not" | `references/structure-decision.md` |

## Hard constraints

- **Never edit** project source, configs, lockfiles, or package files. Report only; `TREAT.md` on request is the sole permitted write.
- Model extraction and findings are tied to the **installed version**; a different major's documentation is not evidence.
- Prefer official documentation and the tool's own examples over secondary blogs.
- Prefer the tool's native terminology over project-local aliases when diagnosing.
- If the tool's model fits the existing structure cleanly, say so and recommend no change.
- Keep recommendations proportional: respect, not bureaucracy.
- Interrupt the user only once, and only where step 1 says: the prioritization question when bare `/treat` finds more than three candidates.
