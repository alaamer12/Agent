---
name: architecture
version: 2.5.0
author: Amr
specialized: none
description: Orchestrates and drafts an application's complete technical architecture documentation suite across 12 pillars - language conventions, error handling contracts, visual UI/interaction, accessibility and sensory adaptation, display/notation architecture, relational/SQL data modeling, plugin and settings extensibility under the Open/Closed Principle, cross-platform multi-device mechanics, seams and third-party boundaries (the date-don't-marry doctrine - vendor sealing, utility/usability taxonomy, composition ladders, the two walls, component ownership transfer), media handling, testing architecture (lanes, fixtures, No-String Rule, conformance tests), and gates architecture (enforcement ladder, tier budgets, baselines, agent-proof checks); interviews for scope, mandates live version research, and invokes each sub-pillar to author binding specifications into <docs>/ or <docs>/architecture/.
argument-hint: "<project root or app name>"
---

# Architecture Skill

## Overview

The **architecture** skill provides a unified, production-grade framework for establishing an application's technical architecture across 12 specialized pillars: **Language**, **Error**, **UI**, **Accessibility**, **Display**, **Database**, **Plugin & Settings**, **Cross-Platform**, **Seams**, **Media (imgery)**, **Testing**, and **Gates**.

Rather than dividing into fragmented independent tools, **architecture** serves as the single unified authority. Its internal sub-directories (`language/`, `error/`, `ui/`, `accessibility/`, `display/`, `db/`, `plugin/`, `cross-platform/`, `seams/`, `media/`, `testing/`, and `gates/`) provide modular, self-contained reference guides, templates, and polyglot examples that are invoked selectively based on project needs.

The pillars are internal modules, not independent skills. `accessibility/`, `display/`, `plugin/`, `media/`, `seams/`, `testing/`, and `gates/` each carry a `method.md` with that pillar's workflow; read it first when routing there. The other pillars are driven directly from this file through their `references/`, `assets/`, and `examples/`. The full discovery-interview scripts live in `references/discovery-interview.md`; consult it whenever a step's questions fire.

---

## The 12 Internal Pillars

```
architecture/
├── SKILL.md                 # Single entry point, interview workflow, and routing doctrine
├── references/              # discovery-interview.md — full question scripts per step
├── language/                # Coding standards, compiler flags, typing rigor, nullability
├── error/                   # Failure contracts (Result vs exceptions), payload shapes, boundaries
├── ui/                      # Layout stability (CLS), responsive reflow, skeletons, bidi/RTL
├── accessibility/           # Contrast/eye-comfort presets, multi-font, cognitive density, permission hygiene
├── display/                 # Notation levels, container budgets, locale display, voice-typeface pairings
├── db/                      # Dumb-store rules, entity lifecycles, ANSI DDL, table references
├── plugin/                  # Settings-as-plugins, OCP growth gate, build-time vs runtime, composition
├── cross-platform/          # View Barrels, #if & idiom bans, capability tokens, axis naming
├── seams/                   # Vendor sealing, seam taxonomy & ladders, two walls, ownership transfer
├── media/                   # Asset sourcing & brand marks, formats, loading posture, fonts, embed facades
├── testing/                 # Test ladder, fixtures & generators, No-String Rule, conformance tests
└── gates/                   # Enforcement ladder, tier budgets, register, baselines, agent-proof checks
```

| Pillar | Internal Directory | Artifact Generated | Scope & Authority |
| :--- | :--- | :--- | :--- |
| **Language** | `language/` | `<docs>/language-architecture.md` | Target runtime versions, strict compiler flags, typing tiers, defensive boundary collections. |
| **Error** | `error/` | `<docs>/error-architecture.md` | Result vs exceptions, error payload schemas, factory discipline, information security gates. |
| **UI** | `ui/` | `<docs>/ui-architecture.md` | Layout stability (zero CLS via skeletons), responsive reflow, typography, bidi/RTL localization. |
| **Accessibility** | `accessibility/` | `<docs>/accessibility-architecture.md` | Contrast tiers, eye-comfort presets, multi-font selection, cognitive density, permission autonomy. |
| **Display** | `display/` | `<docs>/display-architecture.md` | Notation spectrum (exact/grouped/compact/prose) per surface class, container budgets with fallback ladders, Intl/ICU locale display, voice-typeface-notation pairing table. |
| **Database** | `db/` | `<docs>/db-architecture.md` + `table-reference.md` | Dumb-store invariant, entity lifecycles, ANSI DDL schemas, column specs, table reference. |
| **Plugin & Settings** | `plugin/` | `<docs>/plugin-architecture.md` or `<docs>/settings-architecture.md` | Settings-as-plugins, OCP growth gate, descriptor catalogs, contribution registries, layering, scope/storage, build-time vs runtime, trust and isolation. |
| **Cross-Platform** | `cross-platform/` | `<docs>/cross-platform-architecture.md` | PlatformComponents vs Concepts, View Barrels, #if & idiom bans, axis filename law and multi-axis dispatch. Who may *know* the platform SDK is a Seams question, not this pillar's. |
| **Seams** | `seams/` | `<docs>/seams-architecture.md` | Date-don't-marry doctrine: one seam per capability, utility/usability taxonomy, composition ladders, import & markup walls, hard-zero vs ratcheted severity, migration batches, adopted-component ownership. |
| **Media (imgery)** | `media/` | `<docs>/media-architecture.md` | Asset sourcing & brand-mark ledger, format pipeline, responsive/latency posture (LCP rule, space reservation), icon system grammar, fonts delivery, embed facades & consent, media caching and budgets. |
| **Testing** | `testing/` | `<docs>/testing-architecture.md` | Test ladder and lane budgets, fixture lifecycle and isolation, generator registry with derived identity, the No-String Rule for test data, conformance tests that make documentation executable. |
| **Gates** | `gates/` | `<docs>/gates-architecture.md` | Enforcement ladder and rung per rule class, tier table with p95 budgets, gate register, fail-closed and exit-code contract, baselines and ratchets, suppressions and exceptions, agent completion contract, inventory and governance. |

---

## 2. Methodology & Conversational Interview Workflow

Execution operates across 4 structured phases:

1. **Phase 1 — Contextual Discovery & Relevance Interview.** Analyze the codebase, dependencies and project context; present the tailored §3 questions to determine scope: language stack & target versions, error philosophy, visual UI, database, plugin/settings surfaces, multi-platform targets, and which third-party capabilities the app consumes.
2. **Phase 2 — Live Ecosystem & Version Web Research.** For each confirmed technology, target version and runtime, perform live web search before authoring (`"<language> <version> new features"`, `"<language> <version> breaking changes"`, `"<framework> best practices idiom tricks"`); cross-reference documentation to prevent applying obsolete paradigms or hallucinated legacy idioms.
3. **Phase 3 — Sequential Pillar Execution.** Author specifications using the researched data and polyglot guidelines, in dependency order: Language → Error → UI → Accessibility → Display → Database → Plugin & Settings → Cross-Platform → **Seams** → Media → Testing (every app has tests) → Gates (every app has delivery). Conditional pillars are skipped only when their §3 gate is answered in the negative, and the skip is recorded as an open decision.
4. **Phase 4 — Consolidation & UNITS.md Cross-Check.** Validate all generated documents for consistency; verify zero conflicting rules across pillars; register shared structural units in `UNITS.md`.

---

## 3. The Discovery Interview & Web Research Guide

Ask the step questions in order; verbatim scripts, live-research queries and per-step reconciliation duties live in [`references/discovery-interview.md`](references/discovery-interview.md) — open it whenever a step fires. The agent starts by inspecting the repository to formulate an initial hypothesis before asking anything.

| Step | Question domain | Fires when | Pillar consulted |
| :--- | :--- | :--- | :--- |
| 1 | Language & compiler hygiene | always | `language/` |
| 2 | Error contracts & failure payloads | always | `error/` |
| 3 | Visual UI contracts — a11y, display and media ride this gate | visual UI confirmed | `ui/`, `accessibility/`, `display/`, `media/` |
| 4 | Relational data & DDL standards | database confirmed | `db/` |
| 5 | Plugin & settings extensibility | settings or extensions exist | `plugin/` |
| 6 | Multi-platform & form-factor scope | multi-target confirmed | `cross-platform/` |
| 7 | **Seams & third-party boundaries** | third-party capabilities exist | `seams/` (read its `method.md` first) |
| 8 | Testing & test data architecture | always | `testing/` |
| 9 | Gates & enforcement architecture | always | `gates/` |

---

## 4. Documentation Placement

The generated artifacts are written to the project's documentation root as confirmed with the user:
- **Unified Single Folder:** `<docs>/architecture/` containing:
  - `language-architecture.md`
  - `error-architecture.md`
  - `ui-architecture.md` (if applicable)
  - `accessibility-architecture.md` (if applicable)
  - `display-architecture.md` (if applicable)
  - `media-architecture.md` (if applicable)
  - `db-architecture.md` & `table-reference.md` (if applicable)
  - `plugin-architecture.md` or `settings-architecture.md` (if applicable)
  - `cross-platform-architecture.md` (if applicable)
  - `seams-architecture.md` (if third-party capabilities confirmed)
  - `testing-architecture.md` (always)
  - `gates-architecture.md` (always)
- **Or Standalone Root Documents:** the same filenames placed directly at `<docs>/` instead of `<docs>/architecture/`.

---

## 5. Core Invariants

1. **Context-First & Mandatory Live Research:** Never generate rules from static memory alone. Once the user confirms the tech stack and version (e.g. .NET 10, Python 3.12, TS 5.6), execute live searches for current breaking changes, new idioms, and strict compiler flags before authoring documentation.
2. **Context-First, Never Force:** Never generate UI rules for a CLI or database rules for an app with no database.
3. **Unified Vocabulary:** Ensure naming and architectural roles match across all generated documentation.
4. **No Hardcoded Paths:** Always use relative or user-configured `<docs>/` paths.
5. **UNITS.md Integration:** Any architectural unit or visual control identified during the interview must be cross-checked against `UNITS.md`.
6. **Polyglot Universality:** Keep all reference guides, examples, and rules framework-agnostic and balanced across different languages.
7. **Open/Closed Growth Gate:** Any settings or plugin design must pass the four extensions in `plugin/method.md` — add an item, add a module, add a shape, add a scope — without editing shared code beyond the declared extension point. Name the files each extension changes; if shared code appears, the seam is wrong.
8. **Build-Time by Default:** Prefer build-time code and contracts. Move an axis to runtime only for a written reason and only on a platform that permits it. Never propose downloadable executable code on a mobile app-store target.
9. **Tests Are Executable Architecture:** Every binding rule a compiler cannot enforce gets a conformance test, or it is a preference. Test data has one home and one vocabulary; a test body names intent, never a value (No-String Rule). Never present coverage as evidence of correctness — name the invariant or the mutation it catches.
10. **A Rule Without a Gate Is a Preference:** Every binding rule names its gate, tier, owner, and evidence, or is explicitly advisory. A gate the gated can edit is not a gate; a gate never observed failing is presumed broken; a gate that fails open on a missing report is worse than no gate at all.
11. **Date, Don't Marry:** Every external capability is reachable only through one seam you own, named in the project's own vocabulary. A boundary that fails the one-file swap test is not a seam; a wall no planted fixture has ever fired against is not a check; an adopted component without a ledger row is a component nobody owns.
