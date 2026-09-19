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
5. **Illustrative, Non-Hardcoded Options:** When a skill lists choices for an AI agent to reason from (not code snippets, but decision menus like "which caching strategy" or "which matching algorithm"), mark them as examples, not a mandate — either bracket notation (`[LRU]` vs `[LFU]` vs `[TTL]`) or an explicit "Example Option:" prefix. Never phrase a choice set as if it were closed and exhaustive ("pick Option 1, 2, or 3") — the point is to give the agent a shape to reason from, not a menu it's confined to. See `references/polyglot-skill-authoring-guide.md` §4 and `examples/universal-walkthrough-examples.md` Pattern 4.

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

---

## 4. Illustrative Option Notation (Non-Hardcoded Choices)

Section 3 covers code snippets. This section covers the other thing polyglot skills constantly write: decision menus for an AI agent to reason from — "which eviction policy," "which consistency model," "which matching strategy." These are just as prone to monoculture bias as code, in a different way: phrasing them as a flat, numbered, closed list ("choose Option 1, 2, or 3") reads to an agent as a mandate, not a menu, and it will treat the real answer as forced into one of the listed items even when a hybrid or an unlisted alternative is actually correct.

- **Bracket notation:** wrap each illustrative choice in `[brackets]`, e.g. `[LRU]` vs `[LFU]` vs `[TTL-based expiry]`. Brackets visually signal "example," the same way code fences signal "this is code."
- **"Example Option" phrasing:** where bracket notation would be visually noisy (long options, nested clauses), prefix instead with the literal phrase "Example Option" or "e.g." before each choice, so the illustrative status is stated rather than only implied by punctuation.
- **State the escape hatch explicitly, once, near the top of the file:** a short standing note that options are illustrative, not exhaustive or mandatory, and that a hybrid or unlisted answer is always acceptable — so it doesn't need repeating after every single choice.
- **Never number options as if selecting an index** ("Option 1", "Option 2") without also naming what each one actually is inline — an agent (or a person) shouldn't have to cross-reference a numbered list elsewhere to know what "Option 2" means, and numbering alone reads more like a form to fill out than a set of examples.

See `examples/universal-walkthrough-examples.md` Pattern 4 for a full before/after conversion, and `references/polyglot-skill-authoring-guide.md` §4 for the anti-pattern table entry.

---

For detailed techniques and checklist, see `references/polyglot-skill-authoring-guide.md`.
For concrete comparative patterns, see `examples/universal-walkthrough-examples.md`.
