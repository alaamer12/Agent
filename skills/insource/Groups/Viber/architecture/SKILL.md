---
name: architecture
description: Orchestrates and drafts an application's complete technical architecture documentation suite across its core pillars (language conventions, error handling, visual UI/interaction, relational/SQL data modeling, plugin and settings extensibility under the Open/Closed Principle, cross-platform multi-device mechanics, accessibility/sensory adaptation, and display/notation architecture (how values are expressed - precision levels, container fit, locale display, voice-typeface pairings)), invoking each specialized sub-pillar to author binding specifications into the project's documentation suite (<docs>/ or <docs>/architecture/).
argument-hint: "<project root or app name>"
---

# Architecture Skill

## Overview

The **architecture** skill provides a unified, production-grade framework for establishing an application's technical architecture across 8 specialized pillars: **Language**, **Error**, **UI**, **Accessibility**, **Display**, **Database**, **Plugin & Settings**, and **Cross-Platform**.

Rather than dividing into fragmented independent tools, **architecture** serves as the single unified authority. Its internal sub-directories (`language/`, `error/`, `ui/`, `accessibility/`, `display/`, `db/`, `plugin/`, and `cross-platform/`) provide modular, self-contained reference guides, templates, and polyglot examples that are invoked selectively based on project needs.

---

## The 8 Internal Pillars

```
architecture/
├── SKILL.md                 # Single entry point, interview workflow, and routing doctrine
├── language/                # Coding standards, compiler flags, typing rigor, nullability
├── error/                   # Failure contracts (Result vs exceptions), payload shapes, boundaries
├── ui/                      # Layout stability (CLS), responsive reflow, skeletons, bidi/RTL
├── accessibility/           # Contrast/eye-comfort presets, multi-font, cognitive density, permission hygiene
├── display/                 # Notation levels, container budgets, locale display, voice-typeface pairings
├── db/                      # Dumb-store rules, entity lifecycles, ANSI DDL, table references
├── plugin/                  # Settings-as-plugins, OCP growth gate, build-time vs runtime, composition
└── cross-platform/          # View Barrels, #if & idiom bans, capability tokens, multi-axis isolation
```

| Pillar | Internal Directory | Artifact Generated | Scope & Authority |
| :--- | :--- | :--- | :--- |
| **Language** | `language/` | `<docs>/language-architecture.md` | Target runtime versions, strict compiler flags, typing tiers, defensive boundary collections. |
| **Error** | `error/` | `<docs>/error-architecture.md` | Result vs exceptions, error payload schemas, factory discipline, information security gates. |
| **UI** | `ui/` | `<docs>/ui-architecture.md` | Layout stability (zero CLS via skeletons), responsive reflow, typography, bidi/RTL localization. |
| **Accessibility** | `accessibility/` | `<docs>/accessibility-architecture.md` | Contrast tiers, eye-comfort presets, multi-font selection, cognitive density, permission autonomy. |
| **Display** | `display/` | `<docs>/display-architecture.md` | Notation spectrum (exact/grouped/compact/prose) per surface class, container budgets with fallback ladders, Intl/ICU locale display, voice-typeface-notation pairing table. |
| **Database** | `db/` | `<docs>/db-architecture.md` | Dumb-store invariant, entity lifecycles, ANSI DDL schemas, column specs, table reference. |
| **Plugin & Settings** | `plugin/` | `<docs>/plugin-architecture.md` or `<docs>/settings-architecture.md` | Settings-as-plugins, OCP growth gate, descriptor catalogs, contribution registries, layering, scope/storage, build-time vs runtime, trust and isolation. |
| **Cross-Platform** | `cross-platform/` | `<docs>/cross-platform.md` | PlatformComponents vs Concepts, View Barrels, #if & idiom bans, multi-axis layer resolution. |

---

## 2. Methodology & Conversational Interview Workflow

Execution operates across 4 structured phases:

```text
┌────────────────────────────────────────────────────────┐
│            architecture Orchestration Flow             │
└────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────────┐
 │ Phase 1: Contextual Discovery & Relevance Interview  │
 │ • Analyze codebase, dependencies & project context   │
 │ • Present tailored questions to determine scope:     │
 │   - Language stack & target versions (e.g. .NET 10,  │
 │     Python 3.12, TS 5.6, Go 1.23)?                   │
 │   - Error philosophy & consumer requirements?        │
 │   - Does this app have a visual frontend UI?         │
 │   - Does this app interface with a database?         │
 │   - Does it target multiple platforms/form factors?  │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 2: Live Ecosystem & Version Web Research       │
 │ • For each confirmed technology, target version, and │
 │   runtime, perform live web search before authoring: │
 │   - "<language/runtime> <version> new features"      │
 │   - "<language/runtime> <version> breaking changes"  │
 │   - "<framework> best practices idiom tricks"        │
 │ • Cross-reference documentation to prevent applying  │
 │   obsolete paradigms or hallucinated legacy idioms.  │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 3: Sequential Pillar Execution                 │
 │ • Author specifications using the researched data    │
 │   and polyglot guidelines:                           │
 │   1. Language Architecture ➔ Draft conventions       │
 │   2. Error Architecture ➔ Agree on contracts         │
 │   3. UI Architecture (if visual UI confirmed)        │
 │   4. Accessibility (if visual UI confirmed)          │
 │   5. Display (if visual UI confirmed)                │
 │   6. Database Architecture (if DB confirmed)         │
 │   7. Plugin & Settings (if settings exist)           │
 │   8. Cross-Platform (if multi-target confirmed)      │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 4: Consolidation & UNITS.md Cross-Check        │
 │ • Validate all generated documents for consistency   │
 │ • Verify zero conflicting rules across pillars       │
 │ • Register shared structural units in UNITS.md       │
 └──────────────────────────────────────────────────────┘
```

---

## 3. The Discovery Interview & Web Research Guide

When invoked, the agent starts by inspecting the repository to formulate an initial hypothesis, engages the user with targeted questions, and runs targeted web searches for the chosen versions:

### Step 1: Language & Compiler Hygiene
> *"I detect [e.g. TypeScript / C# / Python / Go]. Which target runtime version are we building for (e.g. .NET 10, Python 3.12, TypeScript 5.6)? Would you like to establish binding compiler flags (zero-warnings), typing rigor tiers, and defensive collection boundaries for this application?"*
- If confirmed:
  1. **Mandatory Live Research:** Perform search queries:
     - `"<language> <version> new language features and best practices"`
     - `"<language> <version> breaking changes compiler strict flags"`
  2. Consult `architecture/language/` to draft the specification.

### Step 2: Error Architecture & Failure Contracts
> *"How should failure contracts and diagnostics be shaped across this application (e.g. monadic Result types, typed domain exceptions, or hybrid contracts)? Who consumes them (end-user UI, APM logs, REST clients)?"*
- If confirmed:
  1. Consult `architecture/error/` to agree on contracts and payload structures.

### Step 3: Visual UI & Design Contracts (Activation Gate)
> *"Does this application feature a visual user interface (Web, Mobile, Desktop GUI)? Or is it a headless service / CLI / daemon?"*
- If visual UI:
  1. **Live Research:** Search for latest idioms in the UI framework (e.g. `"Next.js 15 layout server components"`, `"MAUI 9 desktop responsiveness"`).
  2. Consult `architecture/ui/` to draft layout stability, zero CLS skeletons, and bidi/RTL rules.
  3. Consult `architecture/accessibility/` to establish visual adaptation tiers (high contrast, warm-cream/slate presets), typographic personalization (multi-font, dyslexia-friendly fonts), cognitive density controls, and permission hygiene.
  4. Consult `architecture/display/` to set the surface-class pairing table - notation level (exact / grouped / compact / prose) per reader question, container budgets with fallback ladders, the Intl/ICU locale pipeline (numerals, separators, calendars, Arabic plurals, bidi isolation), and the voice-typeface coherence roster. Accessibility user-choices always override its defaults.
- If headless: skip UI, accessibility, and display architectures.

### Step 4: Relational Data & Database Standards
> *"Does this service interact with a database (PostgreSQL, SQLite, MySQL)? Would you like to establish Dumb-Store conventions, relational modeling strategies, and an application table reference?"*
- If confirmed:
  1. **Live Research:** Search for engine-specific best practices (e.g. `"PostgreSQL 17 performance UUIDv7 indexing"`).
  2. Consult `architecture/db/` to establish schemas and DDL standards.

### Step 5: Plugin & Settings Extensibility
> *"Does this application have a settings screen, configuration catalog, feature flags, per-tenant or per-platform preferences, or any extension modules? Should settings and plugins share one extension contract so adding the Nth item never edits shared code? Must extensions load at build time or after release?"*
- If confirmed:
  1. **Live Research:** Search for stack-specific patterns (e.g. `"<framework> plugin architecture dynamic loading"`, `"<platform> app store downloadable code policy"`, `"<framework> configuration descriptor pattern"`).
  2. Consult `architecture/plugin/` to run the Open/Closed growth gate, choose build-time versus runtime per axis, and draft descriptors, contributions, composition, scope and storage.
  3. When the product has settings but no third-party plugins, author `settings-architecture.md`; otherwise author `plugin-architecture.md`.

### Step 6: Multi-Platform & Multi-Form-Factor Scope
> *"Does this application target multiple operating systems (iOS, Android, Windows, macOS, Web) or form factors (phone, tablet, desktop)? Should we enforce View Barrels, zero `#if` conditionals in shared code, and multi-axis isolation?"*
- If confirmed:
  1. Consult `architecture/cross-platform/` to author decoupling and isolation specifications.

---

## 4. Documentation Placement

The generated artifacts are written to the project's documentation root as confirmed with the user:
- **Unified Single Folder:** `<docs>/architecture/` containing:
  - `language-conventions.md`
  - `error-architecture.md`
  - `ui-architecture.md` (if applicable)
  - `accessibility-architecture.md` (if applicable)
  - `display-architecture.md` (if applicable)
  - `sql-architecture.md` & `table-reference.md` (if applicable)
  - `plugin-architecture.md` or `settings-architecture.md` (if applicable)
  - `cross-platform-architecture.md` (if applicable)
- **Or Standalone Root Documents:** e.g. `<docs>/error-architecture.md`, `<docs>/accessibility-architecture.md`, `<docs>/display-architecture.md`, `<docs>/plugin-architecture.md, `<docs>/cross-platform-architecture.md`.

---

## 5. Core Invariants

1. **Context-First & Mandatory Live Research:** Never generate rules from static memory alone. Once the user confirms the tech stack and version (e.g. .NET 10, Python 3.12, TS 5.6), execute live searches for current breaking changes, new idioms, and strict compiler flags before authoring documentation.
2. **Context-First, Never Force:** Never generate UI rules for a CLI or database rules for an app with no database.
3. **Unified Vocabulary:** Ensure naming and architectural roles match across all generated documentation.
4. **No Hardcoded Paths:** Always use relative or user-configured `<docs>/` paths.
5. **UNITS.md Integration:** Any architectural unit or visual control identified during the interview must be cross-checked against `UNITS.md`.
6. **Polyglot Universality:** Keep all reference guides, examples, and rules framework-agnostic and balanced across different languages.
7. **Open/Closed Growth Gate:** Any settings or plugin design must pass the four extensions in `plugin/SKILL.md` — add an item, add a module, add a shape, add a scope — without editing shared code beyond the declared extension point. Name the files each extension changes; if shared code appears, the seam is wrong.
8. **Build-Time by Default:** Prefer build-time code and contracts. Move an axis to runtime only for a written reason and only on a platform that permits it. Never propose downloadable executable code on a mobile app-store target.
