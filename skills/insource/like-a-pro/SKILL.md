---
name: like-a-pro
description: "Root meta-skill orchestrator reproducing production-grade engineering standards across applications. Lifecycle: Idea -> detailsup (topic-by-topic specification) -> app-boundary confirmation -> per-application standards and system docs, dispatching the standalone skills it calls: language-handling, sql-handling, error-handling, ui-handling, system-md (SYSTEM-COMPONENTS.md), units-md (UNITS.md), and optionally agents-md for AGENTS.md. This file routes: it sequences phases, confirms application boundaries, and reports what each phase produced. It never does a child skill's work and writes no project files itself."
argument-hint: '[project root or application path]'
when_to_use: 'The user wants production-grade standards applied across an application or monorepo, asks to run the like-a-pro lifecycle, or needs the phases ordered: idea, specification, app-boundary confirmation, standards, then system and units docs.'
---

# Like-a-Pro Meta-Skill

The **like-a-pro** meta-skill is a modular orchestration engine designed to reproduce production-grade technical standards, schemas, error architectures, and system documentation across any software project. It bridges the journey from initial idea to robust, consistent implementation standards across 3 canonical phases.

---

## 1. The Core Lifecycle

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Like-a-Pro Lifecycle                            │
└────────────────────────────────────────────────────────────────────────┘

 Phase 1: Idea (including Phase 1.5 Product Definition)
 ├─ Clarify raw vision, features, target platforms
 └─ In-scope vs out-of-scope, user experience (DESIGN.md / README.md)
       │
       ▼
 Phase 2: Technical Specification  ->  detailsup
 ├─ Topic-by-topic conversational discovery of how the system works
 └─ Scrapers, workers, pipelines, caching, data models documented in docs/
       │
       ▼
 Phase 3: Standards and System Definition
 ├─ Step 3.1: Mandatory App Boundary Discovery & User Confirmation (this skill's own step)
 └─ Step 3.2: Per-Application Standards Application (each a standalone skill)
     ├─ language-handling : Polyglot coding, strict compiler flags, typing spectrum
     ├─ sql-handling      : Stage 1 SQL rules + Stage 2 table references
     ├─ error-handling    : Failure contracts, structured payloads, file layout
     ├─ ui-handling       : Skeletons, responsiveness, data caching, i18n (UI apps only)
     ├─ system-md         : SYSTEM-COMPONENTS.md - the architectural inventory
     └─ units-md          : UNITS.md - the reusable-unit catalog (UI builder profile included there)
```

---

## 2. Invariants & Guardrails

1. **Application-Centric Scope:** Standards are applied per confirmed application, not globally across a repository. Monorepos with multiple apps receive tailored standards for each app.
2. **Mandatory App Boundary Confirmation:** The agent must **never** assume application boundaries from directory trees alone. It scans candidate apps and prompts the user for verification before invoking child skills.
3. **Conversational Tailoring:** Child skills do not force rigid single-vendor choices (e.g. no forced C#, no forced 3NF, no forced Result monads, no forced RTL). They present options and trade-offs.
4. **UI Gatekeeping:** The `ui-handling` skill executes only when an application possesses a visual user interface.
5. **One owner per document:** `system-md` writes `SYSTEM-COMPONENTS.md` (the functional building blocks); **`units-md`** writes `UNITS.md`, including the UI builder-block catalog that used to live here as system-creator "Mode B" — see [units-md's UI profile](../Groups/Viber/units-md/references/03-ui-units-profile.md). Never two inventories of the same thing.
6. **This skill writes nothing.** It sequences phases, confirms the application boundary, and reports what each phase produced.

---

## 3. Skill Catalog & Navigation

Every child is a standalone skill now — `details-up` and `system-creator` were extracted as `detailsup` and
`system-md`, and the `UNITS.md` half of `system-creator` became `units-md`. Invoke any of them directly, with or
without the lifecycle. Paths are relative to this file (`skills/insource/like-a-pro/`).

| Skill | Where | Purpose |
|---|---|---|
| **[`language-handling`](../Groups/Pro/language-handling/SKILL.md)** | `Groups/Pro/` | Establishes language standards, typing rigor, and compiler flags. |
| **[`sql-handling`](../Groups/Pro/sql-handling/SKILL.md)** | `Groups/Pro/` | Establishes dumb-store SQL rules and application table references. |
| **[`error-handling`](../Groups/Pro/error-handling/SKILL.md)** | `Groups/Pro/` | Establishes failure contracts, error codes, and payload formats. |
| **[`ui-handling`](../Groups/Pro/ui-handling/SKILL.md)** | `Groups/Pro/` | Establishes visual contracts, skeletons, caching, and i18n (UI apps only). |
| **[`detailsup`](../Groups/Pro/detailsup/SKILL.md)** | `Groups/Pro/` | Phase 2: conversational topic-by-topic technical specification. |
| **[`system-md`](../Groups/Pro/system-md/SKILL.md)** | `Groups/Pro/` | Phase 3: `SYSTEM-COMPONENTS.md`, the architectural inventory. |
| **[`units-md`](../Groups/Viber/units-md/SKILL.md)** | `Groups/Viber/` | `UNITS.md`: the reusable units consulted before building, incl. the UI profile. |
| **[`agents-md`](../Groups/Viber/agents-md/SKILL.md)** | `Groups/Viber/` | Optional finale: records the obligations and pointers in `AGENTS.md`. |

## 3.5 Running the lifecycle

1. **Phase 1** — clarify the idea and product definition with the user; write down scope in and out.
2. **Phase 2** — run [`detailsup`](../Groups/Pro/detailsup/SKILL.md): one topic at a time until the open design questions are closed and documented.
3. **Phase 3.1** — confirm the app boundary (invariant 2). Nothing downstream runs on an assumed boundary.
4. **Phase 3.2** — for each confirmed application, run the standards skills that apply (`language-handling`, `sql-handling`, `error-handling`, plus `ui-handling` only when there is a UI), then [`system-md`](../Groups/Pro/system-md/SKILL.md) for the component inventory, and [`units-md`](../Groups/Viber/units-md/SKILL.md) when a reusable-unit catalog is wanted or `AGENTS.md` §4 points at one.
5. **Optional finale** — [`agents-md`](../Groups/Viber/agents-md/SKILL.md) turns the agreed standards into obligations and pointers. It owns `AGENTS.md`; this lifecycle only says what to point at.

Report per phase: what was decided, which documents now exist, what stayed pending, and what was not covered.

---

## 4. References & Walkthroughs

- **App Boundary Protocol:** See [references/app-boundary-discovery.md](references/app-boundary-discovery.md) for structural discovery and user confirmation rules.
- **End-to-End Walkthrough:** See [examples/meta-skill-lifecycle-walkthrough.md](examples/meta-skill-lifecycle-walkthrough.md) for a complete scenario from raw idea to conventions. It predates the extraction: where it names `details-up` read `detailsup`, where it names `system-creator` read `system-md`, and anything producing `UNITS.md` runs through `units-md`.
