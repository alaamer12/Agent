# Polyglot Skill Authoring Guide

This reference provides actionable methodologies for creating AI agent skills that remain universal, unopinionated toward specific vendors, and adaptable to any software engineering ecosystem.

---

## 1. The Anti-Patterns of Skill Authoring

| Anti-Pattern | Description | Polyglot Remedy |
|--------------|-------------|-----------------|
| **Monoculture Bias** | Writing all examples, templates, or instructions in one language (e.g. C# only or JS only). | Present language-agnostic concepts and provide parallel snippets in at least 2–4 languages. |
| **Forced Constraints** | Hardcoding arbitrary requirements as mandates (e.g. "All tables must be in 3NF", "All errors must have fix messages"). | Frame constraints as architectural trade-offs; prompt the agent to ask and agree with the user. |
| **Rigid Fixed Lists** | Restricting choices to fixed options: "You must choose Option 1, Option 2, or Option 3". | Teach the agent to analyze the domain and dynamically formulate tailored solutions with trade-offs. |
| **Vendor Coupling** | Tying relational design to Postgres/MySQL, UI to React/Tailwind, or errors to HTTP status codes. | Use engine-agnostic concepts (Dumb Store, Relational Invariants, UI Component Boundaries, Domain Result contracts). |

---

## 2. Methodology for Polyglot Concept Design

### Step 1: Extract the Abstract Principle
Ask: *"What is the universal engineering problem this skill solves?"*
- Not: *"How to use `CancellationToken` in C#"*
- But: *"How to manage cooperative cancellation and unbounded I/O across asynchronous runtimes"*

### Step 2: Formulate the Trade-off Spectrum
Map the spectrum of valid engineering choices rather than declaring a single "correct" answer:
- **Typing Rigor:** Untyped / Dynamic ↔ Lossy Primitive Types ↔ Abstract Collections ↔ Branded Types / NewType ↔ Refinement / Dependent Types.
- **Error Handling:** Unchecked Runtime Panics ↔ Checked Exceptions ↔ Monadic Results (`Result<T, E>`) ↔ Three-tier Hybrid.
- **Relational Normalization:** 1NF / Flat Document ↔ Pragmatic 3NF ↔ Strict BCNF/4NF.
- **UI Architecture:** Monolithic Server Rendered ↔ Hydrated SPA ↔ Native Platform Swap ↔ Headless Micro-Frontend.

### Step 3: Progressive Disclosure Structure
Keep the main skill lean and modular:
1. `SKILL.md`: Metadata, triggers, workflow phases, and key questions to ask.
2. `references/`: Detailed architectural explanations, trade-off analysis, and spectrum breakdowns.
3. `assets/templates/`: Reusable markdown steering templates with generic placeholders (`<app-name>`, `<module>`, `<contract-model>`).
4. `examples/`: Comparative multi-language walkthroughs showing concrete application.

---

## 3. Polyglot Code Snippet Authoring Standards

### The Representative 4-Quadrant Matrix
When illustrating a concept, select languages that span the four quadrants of modern software development:

```text
               Static Typing
                     ▲
                     │
      Go / Rust      │   TypeScript / C#
  (Systems/Compiled) │ (Managed/Enterprise)
                     │
◄────────────────────┼────────────────────►
Functional / Pragmatic│ Object-Oriented / Class
                     │
      Elixir / Clojure│ Python / Ruby
                     │  (Dynamic/Scripted)
                     ▼
               Dynamic Typing
```

### The "Before vs After" Comparison Rule
Always show:
1. **The Vulnerable / Naive Pattern:** Showing how teams inadvertently leak details or sacrifice safety.
2. **The Hardened / Polyglot Pattern:** Showing how the universal standard applies in that specific language's idioms.

### Language-Specific Idioms to Respect
- **TypeScript:** Use `readonly`, strict property checks, utility types, and discriminated unions.
- **Python:** Use `collections.abc` (e.g. `Sequence`, `Mapping`), `typing.NewType`, dataclasses, and strict mypy/ruff settings.
- **Go:** Use explicit error returns, `context.Context` as first parameter, unexported struct fields, and interfaces at consumer sites.
- **C#:** Use records, `IReadOnlyList<T>`, nullable reference types (`?`), and `CancellationToken`.
- **Rust:** Use `Result<T, E>`, ownership/borrowing semantics, newtype structs, and explicit trait bounds.
