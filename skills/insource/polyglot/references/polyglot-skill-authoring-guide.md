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
| **Hardcoded Option Lists** | Presenting decision menus as a closed, numbered, exhaustive set (e.g. "pick Option 1, 2, or 3") that an agent reads as the full space of valid answers rather than a starting point. | Mark each choice as illustrative — `[bracket notation]` or an explicit "Example Option" prefix — and state once, near the top of the file, that a hybrid or unlisted answer is always acceptable. See §4 below. |

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

---

## 4. Notation for Illustrative (Non-Hardcoded) Options

Section 1's "Rigid Fixed Lists" anti-pattern is about *content* — forcing the agent's actual decision into one of a small set. This section is about *notation* — even a well-designed, genuinely open-ended trade-off spectrum can still read as mandatory to an agent if it's formatted like a form to fill out rather than a set of examples. The two problems compound: a numbered list ("Option 1, Option 2, Option 3") is both rigid in content and rigid-looking in notation, but a skill can accidentally have the second problem even after fixing the first — e.g. a genuinely well-reasoned trade-off spectrum that still gets typeset as a flat numbered list, which an agent then treats as exhaustive purely from the formatting.

**The fix has two parts, and both matter:**

1. **Mark each option as illustrative at the point of use** — either `[bracket notation]`, e.g. `[strict 3NF]` vs `[pragmatic denormalization]` vs `[hybrid relational-document]`, or an explicit "Example Option:" / "e.g." prefix where brackets would be visually noisy around a longer clause.
2. **State the escape hatch once, near the top of the file** — a short standing note that these are examples to reason from, not a closed set, and that a hybrid or an option not listed at all is always an acceptable answer. Repeating this after every single choice is noise; stating it once and trusting the notation to carry it thereafter is enough.

### Before / After

**Before (reads as a mandate — the classic "Rigid Fixed Lists" failure, made worse by numbered notation):**
```markdown
Which normalization strategy should be used? Choose one:
1. Strict 3NF
2. Pragmatic denormalization
3. Hybrid relational-document model
```

**After (reads as an illustrative menu, in prose, with the escape hatch already established once elsewhere in the file):**
```markdown
Which normalization strategy fits this workload — `[strict 3NF/BCNF, zero redundancy, high consistency]`
vs `[pragmatic denormalization, selective pre-aggregated columns for high-throughput reads]`
vs `[a hybrid relational-document model, structured relational core with JSON metadata]`?
These are illustrative starting points, not an exhaustive set — the right answer may be a
different variant of one of these or a combination the workload actually calls for.
```

The "After" version is not longer because it adds more caveats per line — it's the same information, typeset so an agent reads "these are examples" from the punctuation itself, with the standing escape-hatch sentence doing the rest of the work once rather than being repeated at every decision point.
