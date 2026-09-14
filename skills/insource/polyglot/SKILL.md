---
name: polyglot
description: Teaches AI agents how to design and author universal, general, and language-agnostic agent skills, and how to write balanced, representative polyglot code examples. Use when creating or refactoring agent skills, coding standards, templates, or architectural specifications.
---

# Polyglot: Universal & Language-Agnostic Skill Design

`polyglot` provides principles, workflows, and conventions to ensure that newly authored agent skills and architectural specifications never trap users into a single language, framework, database engine, or prescriptive convention.

---

## 1. The Core Universal Invariants

When creating any new skill or engineering guide:

1. **Principle Over Syntax:** Anchor every standard in architectural principles (e.g. boundary encapsulation, immutability, fail-fast vs resilient recovery) rather than single-language keywords (`readonly`, `final`, `const`).
2. **Never Mandate a Single Technology:** A skill must never force C#, TypeScript, Python, Go, or Rust unless the skill's explicit title is language-bound (e.g. `csharp-conventions`).
3. **Conversational Strategy Formulation:** When options exist (e.g. 3NF vs denormalized SQL, Monadic Result vs Domain Exceptions, Centralized vs Per-module files), formulate the choices dynamically with pros and cons, letting the user decide.
4. **Balanced Polyglot Representation:** When illustrating concepts with code snippets, provide multi-language comparative examples spanning different paradigm families (static vs dynamic, compiled vs interpreted, OOP vs functional).

---

## 2. Directory Layout for a Polyglot Skill

Follow the progressive disclosure model:

```text
.junie/skills/<skill-name>/
├── SKILL.md                          # Lean workflow & trigger rules (< 120 lines)
├── references/                       # Conceptual deep-dives & architecture
│   └── <topic>-principles.md
├── assets/templates/                 # Universal copyable templates with placeholders
│   └── <topic>-template.md
└── examples/                         # Polyglot comparative walkthroughs
    └── <topic>-polyglot-walkthrough.md
```

---

## 3. Polyglot Code Snippet Authoring Rules

When writing code examples inside examples or reference guides:

- **The Multi-Language Rule:** Never show only one language snippet. Show at least 2–4 representative languages across different paradigms (e.g. TypeScript, Go, Python, C# or Rust).
- **The "Before vs After" Pattern:** Demonstrate the anti-pattern (lossy, leaky, unsafe) followed by the disciplined implementation (encapsulated, typed, safe).
- **No Pseudo-Code Without Concrete Semantics:** Avoid fake syntax. Use idiomatic, modern syntax for each chosen language (e.g. Python 3.10+ type hints & `collections.abc`, TypeScript strict mode, Go `context.Context`, C# `IReadOnlyList` / records).

For detailed techniques and checklist, see `references/polyglot-skill-authoring-guide.md`.
For concrete comparative patterns, see `examples/universal-walkthrough-examples.md`.
