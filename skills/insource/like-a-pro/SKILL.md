---
name: like-a-pro
description: Root meta-skill orchestrator that reproduces production-grade engineering standards and conventions across applications. Guides the complete lifecycle from Idea -> Details-Up -> App Boundary Confirmation -> Child Skills (language-conventional, sql-conventional, errors-handling, ui-rules, system-creator).
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
 Phase 2: Technical Specification (via details-up)
 ├─ Topic-by-topic conversational discovery of how the system works
 └─ Scrapers, workers, pipelines, caching, data models documented in docs/
       │
       ▼
 Phase 3: Standards and System Definition (Like-a-Pro & Child Skills)
 ├─ Step 3.1: Mandatory App Boundary Discovery & User Confirmation
 └─ Step 3.2: Per-Application Standards Application (Child Skills)
     ├─ language-conventional : Polyglot coding, strict compiler flags, typing spectrum
     ├─ sql-conventional      : Stage 1 SQL rules + Stage 2 table references
     ├─ errors-handling        : Failure contracts, structured payloads, file layout
     ├─ ui-rules (Optional)    : Skeletons, responsiveness, data caching, i18n
     └─ system-creator         : SYSTEM-COMPONENTS.md (Mode A) + UNITS.md (Mode B)
```

---

## 2. Invariants & Guardrails

1. **Application-Centric Scope:** Standards are applied per confirmed application, not globally across a repository. Monorepos with multiple apps receive tailored standards for each app.
2. **Mandatory App Boundary Confirmation:** The agent must **never** assume application boundaries from directory trees alone. It scans candidate apps and prompts the user for verification before invoking child skills.
3. **Conversational Tailoring:** Child skills do not force rigid single-vendor choices (e.g. no forced C#, no forced 3NF, no forced Result monads, no forced RTL). They present options and trade-offs.
4. **UI Gatekeeping:** The `ui-rules` skill executes only when an application possesses a visual user interface.
5. **Living System Inventory:** `system-creator` documents functional building blocks (`SYSTEM-COMPONENTS.md`) and catalogs reusable UI builder units (`UNITS.md`).

---

## 3. Child Skills Catalog & Navigation

| Child Skill | Directory | Purpose |
|---|---|---|
| **`language-conventional`** | `language-conventional/` | Establishes language standards, typing rigor, and compiler flags. |
| **`sql-conventional`** | `sql-conventional/` | Establishes dumb-store SQL rules and application table references. |
| **`errors-handling`** | `errors-handling/` | Establishes failure contracts, error codes, and payload formats. |
| **`ui-rules`** | `ui-rules/` | Establishes visual contracts, skeletons, caching, and i18n (UI apps only). |
| **`details-up`** | `details-up/` | Conversational topic-by-topic technical specification engine. |
| **`system-creator`** | `system-creator/` | Documents system architecture and catalogs UI builder blocks. |

---

## 4. References & Walkthroughs

- **App Boundary Protocol:** See [references/app-boundary-discovery.md](references/app-boundary-discovery.md) for structural discovery and user confirmation rules.
- **End-to-End Walkthrough:** See [examples/meta-skill-lifecycle-walkthrough.md](examples/meta-skill-lifecycle-walkthrough.md) for a complete scenario from raw idea to conventions.
