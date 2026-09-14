---
name: errors-handling
description: Establishes structural error handling conventions, customizable failure contracts, error payload shapes, and module error architecture for a confirmed application. Use when designing error handling rules or creating error steering documents.
---

# Errors Handling Skill

The **errors-handling** skill establishes production-grade error architectures for applications. Rather than imposing rigid, single-paradigm error structures, it guides the agent to explore and agree upon the application's **Error Contract Philosophy** (e.g. Result types vs exceptions vs hybrid contracts) and **Error Payload Shape** (e.g. simple codes, RFC 7807 Problem Details, or multi-part internal/external/fix payloads) based on real application requirements.

---

## 1. When to Use

- When defining an application's error handling conventions and failure taxonomy.
- When selecting an error contract paradigm (monadic Results, typed exceptions, or hybrid models).
- When agreeing upon the application's error payload structure (localized messages, diagnostics, codes).
- When establishing module error organization (per-module files vs centralized registries).
- As the third technical conventions step in the `like-a-pro` meta-skill lifecycle.

---

## 2. Methodology & Workflow

For the targeted application, execute the following 5-phase conversational discovery and design analysis:

```text
┌────────────────────────────────────────────────────────┐
│               errors-handling Workflow                 │
└────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────────┐
 │ Phase 1: Contextual Error Contract Discovery         │
 │ • Analyze application context, runtime & failure flow│
 │ • Synthesize relevant architectural options (with    │
 │   trade-offs, pros & cons tailored to this project)  │
 │ • Discuss and record the user's chosen contract model│
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 2: Error Payload & Consumer Needs Discovery    │
 │ • Inquire about error consumers (UI, APM, APIs, bots)│
 │ • Propose fitting payload structures (e.g. compact,  │
 │   standard RFC 7807, multi-part localized, or custom)│
 │ • Define machine-readable code format & metadata     │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 3: Error Organization & Distribution Strategy  │
 │ • Assess codebase size, team layout & modularity     │
 │ • Propose layout models (per-module, centralized,    │
 │   feature sliced, or domain bounded)                 │
 │ • Agree on factory architecture & ban ad-hoc strings │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 4: Observability, Logging & Security Gate      │
 │ • Define APM indexing, telemetry, and error levels   │
 │ • Prevent technical diagnostics leakage to users     │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 5: Aggregation & Batch Operations              │
 │ • Define behavior for batch / composite failures     │
 │ ➔ Output: .repertoire/.steering/<app>/tech/errors.md │
 └──────────────────────────────────────────────────────┘
```

---

## 3. Core Universal Invariants

1. **Context-Driven Proposal, Not Fixed Lists:** The agent never relies on a static, closed list of choices. It analyzes the application's specific domain and runtime, formulating tailored options with concrete trade-offs for user selection.
2. **Conversational Contract Agreement:** The error handling paradigm is agreed with the user based on project context, rather than assumed or forced.
3. **Conversational Payload Agreement:** The structure and fields of domain errors are tailored to who or what consumes them (end-user screens, external clients, internal logs).
4. **Conversational Organization Agreement:** The distribution of error files is chosen to match the project's modularity and team workflow.
5. **No Ad-Hoc String Errors:** Constructing bare error strings inside business logic is prohibited. All errors must be constructed via agreed error factories.
6. **Information Boundary Discipline:** Sensitive technical diagnostics (stack traces, SQL logs, raw connection strings) must never leak across public boundaries to end users.

---

## 4. References & Assets

- **Universal Principles:** See [references/error-architecture-principles.md](references/error-architecture-principles.md) for full descriptions of contract models, payload designs, and trade-offs.
- **Output Template:** See [assets/templates/error-architecture-template.md](assets/templates/error-architecture-template.md) for the customizable application steering skeleton.
- **Polyglot Walkthrough:** See [examples/errors-polyglot-walkthrough.md](examples/errors-polyglot-walkthrough.md) for step-by-step examples across different contract choices.
