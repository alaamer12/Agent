---
name: language-conventional
description: Establishes idiomatic language-specific coding standards, type systems, collection boundaries, nullability, async discipline, and compiler flags for a confirmed application. Use when generating, standardizing, or auditing programming language conventions for an application.
---

# Language Conventional Skill

The **language-conventional** skill codifies and applies production-grade programming language standards for a specific application. Rather than applying generic advice, it inspects the application's actual tech stack (C#, TypeScript, Go, Kotlin, Swift, Rust, Python, etc.) and establishes binding conventions for type declarations, nullability, async/await concurrency, defensive guards, and project configuration.

---

## 1. When to Use

- When onboarding a newly confirmed application into the project's engineering standards.
- When drafting or refining an application's language steering document (e.g., `.repertoire/.steering/<app>/tech/<language>-conventions.md`).
- When performing a code quality or style alignment audit across an application codebase.
- As the first technical conventions step invoked by the `like-a-pro` meta-skill.

---

## 2. Methodology & Workflow

For the targeted application, execute the following 6-phase analysis:

```text
┌────────────────────────────────────────────────────────┐
│             Language Convention Workflow               │
└────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────────┐
 │ Phase 1: Toolchain, Tooling & Code Hygiene Inspection│
 │ • Identify language runtime & compiler target version│
 │ • Mandate tooling suite: linter, formatter, docstyle │
 │ • Check project compiler flags (strict mode, errors) │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 2: Typing Rigor Spectrum & Type System         │
 │ • Select typing level: Lossless/Branded vs Basic     │
 │ • Value vs Reference types vs Data carrier hierarchy │
 │ • Encapsulation defaults (closed/sealed by default)  │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 3: Nullability & Defensive Guard Discipline    │
 │ • Strict non-null guarantees / Option semantics      │
 │ • Standardized parameter validation & guard clauses  │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 4: Collection Selection & API Boundaries       │
 │ • Read-only contracts on public boundaries           │
 │ • Abstract collections (e.g. Sequence vs raw arrays) │
 │ • Concrete mutable collections confined to internals │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 5: Async & Concurrency Model                   │
 │ • Non-blocking discipline (no sync-over-async)       │
 │ • Cancellation / context propagation                 │
 │ • Concurrency primitives (Channels / Actors / Queues)│
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 6: Code Style, Formatting & Doc Conventions    │
 │ • Naming conventions (casing, file mapping)          │
 │ • Docstring & API documentation standards (docstyle) │
 └──────────────────────────────────────────────────────┘
```

---

## 3. Core Universal Invariants (Agnostic Rules)

Regardless of the target language, every generated convention must enforce these core invariants:

1. **Zero Warning Debt:** Compiler warnings must be treated as errors (`TreatWarningsAsErrors` in .NET, `strict: true` in TS, `-Wall -Werror` in C/Go).
2. **Defensive API Boundaries:** Public APIs must expose immutable or read-only interfaces (`IReadOnlyList<T>`, `ReadonlyArray<T>`, unmodifiable views). Never leak mutable collections across layer boundaries.
3. **Sealed by Default:** Classes/types must be closed for inheritance unless explicitly designed and documented as extension points.
4. **Explicit Nullability Intent:** Avoid implicit nullability. Make nullability an intentional, typed choice (`T?` or `Option<T>`). Banish unchecked null assertions / blind force-unwrapping.
5. **Pervasive Cancellation & Non-Blocking:** All asynchronous operations must support cooperative cancellation and must never block calling threads with synchronous waits.

---

## 4. Application Output Artifact

The output of this skill must be written to the target application's tech documentation steering path:
- File path: `.repertoire/.steering/<app-name>/tech/<language>-conventions.md` (or the application's equivalent tech conventions directory).

### Required Document Structure:
1. **Toolchain, Tooling & Code Hygiene:** Exact settings for compiler flags, linter configuration, automated formatter, and docstyle rules.
2. **Typing Rigor & Declaration Hierarchy:** Typing rigor tier (Untyped / Lossy / Strong Branded), plus decision tree mapping conceptual data/behavior to concrete language constructs.
3. **Public Boundary Types:** Table of input parameters vs return types, including abstract collections.
4. **Nullability & Validation:** Guard syntax, argument checking, prohibition of blind unwrapping.
5. **Async & Concurrency:** Threading rules, cancellation / context passing, event-loop/queue patterns.
6. **Code Style, Formatting & Docs:** Casing, file layout, helper encapsulation, docstyle requirements.

---

## 5. Polyglot References & Assets

- **Universal Guidelines & Multi-Language Mapping:** See [references/polyglot-language-conventions.md](references/polyglot-language-conventions.md) for conceptual comparisons across TypeScript, Python, Go, Rust, and C#, including typing rigor tiers and tooling standards.
- **Output Template:** See [assets/templates/language-conventions-template.md](assets/templates/language-conventions-template.md) for the universal application conventions skeleton.
- **Polyglot Walkthrough:** See [examples/polyglot-walkthrough.md](examples/polyglot-walkthrough.md) for step-by-step examples across TypeScript, Python, Go, and C#.
