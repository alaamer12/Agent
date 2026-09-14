---
name: ui-rules
description: Establishes visual design contracts, responsiveness standards, skeleton loading rules, typography slots, RTL localization, and icon systems for frontend applications. Triggers only when an application possesses a visual user interface.
---

# UI Rules Skill

The **ui-rules** skill defines and standardizes visual, interaction, and design system contracts for frontend applications (Web, Mobile, Desktop). It enforces layout stability (CLS prevention via skeletons), responsive reflow and block swapping, typography and slot systems, tiered icon architecture, and bidirectional/RTL localization.

---

## 1. When to Use & Activation Gate

- **Activation Gate:** Execute this skill **only** when the target application has a confirmed visual UI (Web, Mobile, Desktop GUI, Admin).
- **Skip Condition:** If the application is a headless backend, CLI tool, or background service daemon, bypass this skill entirely.
- As the optional frontend technical conventions step in the `like-a-pro` meta-skill lifecycle.

---

## 2. Methodology & Workflow

For the targeted frontend application, execute the following 9-phase conversational discovery and design analysis:

```text
┌────────────────────────────────────────────────────────┐
│                   ui-rules Workflow                    │
└────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────────┐
 │ Phase 1: Tech-Stack & Framework Ecosystem Discovery  │
 │ • Identify application UI environment & target OS    │
 │ • Investigate latest tools & libraries for that stack │
 │   (using web search or documentation tools)          │
 │ • Check major version conventions & breakdown traps  │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 2: Data Fetching, Preservation & Invalidation  │
 │ • State cache lifecycle (stale-while-revalidate)     │
 │ • Preservation across navigation & app backgrounding │
 │ • Targeted cache invalidation & mutation re-fetching │
 │ • Offline persistence & optimistic updates           │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 3: Responsiveness & Form Factor Geometry       │
 │ • No fixed heights on text-bearing elements          │
 │ • Fluid row/grid sizing & overflow-safe wrapping     │
 │ • Density-independent tokens (dp/rem, safe-area)     │
 │ • Screen breakpoints & block layout swapping         │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 4: Skeleton Loading & Shimmer Pairing System   │
 │ • The Pairing Rule (1 content container = 1 skeleton)│
 │ • Zero Cumulative Layout Shift (CLS) footprint match │
 │ • Shimmer sweep animation standards & color tokens   │
 │ • Loading precedence: skeleton vs inline vs optimist │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 5: Text Display & Smart Truncation Rules       │
 │ • Two modes: WordWrap (main) vs Truncation (chips)   │
 │ • Character/line cap thresholds (TruncatingLabel)    │
 │ • Safe handling for long unbroken tokens (URLs/IDs)  │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 6: Sub-Text Slot & Error Binding System        │
 │ • Standard sub-text slot on primary text components  │
 │ • Binding point for DomainError (External & Fix)     │
 │ • Zero-space footprint when unpopulated              │
 │ • Multi-level compound component slots (cards/feeds) │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 7: Icon System (Three-Tier Architecture)       │
 │ • Tier 1 (Neutral): inactive/secondary actions       │
 │ • Tier 2 (Brand / Positive): primary action/success  │
 │ • Tier 3 (Conceptual): distinct semantic row hues    │
 │ • Visual states: Normal, PointerOver/Hover, Disabled │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 8: Illustrations & Letterbox Panels            │
 │ • Full-width letterbox panels on fixed canvas        │
 │ • Inline stickers (empty states, search, dialogs)    │
 │ • Vector-first rule (SVG/font glyphs over bitmaps)   │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 9: i18n, Localization & Directionality Strategy│
 │ • Inquire about application locale requirements      │
 │   (Single-locale LTR vs Multi-lingual vs RTL/Bidi)   │
 │ • If multi-direction: logical properties, bidi      │
 │   isolation, and font fallbacks                      │
 │ • If single-locale: standard directional baseline    │
 │ ➔ Output: .repertoire/.steering/<app>/tech/ui-rules.md│
 └──────────────────────────────────────────────────────┘
```

---

## 3. Core Universal Invariants

1. **Frontend Gatekeeping:** Never generate UI rules for headless, background, or CLI applications.
2. **Ecosystem & Tooling Grounding:** Before establishing UI conventions, the agent researches the target stack's latest ecosystem conventions and version-specific capabilities (via documentation or search tools) to ensure standards align with current idioms and avoid obsolete patterns.
3. **Data Preservation & Invalidation:** UI screens must specify clear data lifecycles—preserving cached state across navigation and tab switches to eliminate blank screen flicker, while defining deterministic invalidation triggers for mutations and background returns.
4. **Text Container Elasticity:** Fixed heights on text-bearing elements are strictly prohibited to prevent clipping in internationalized languages or dynamic text sizing.
5. **The Skeleton Pairing Rule:** Content containers must have a sibling skeleton component matching its exact geometry, aspect ratio, and padding to guarantee zero Cumulative Layout Shift (CLS).
6. **Sub-Text Slot Integration:** Primary text components provide an empty-safe sub-text slot for user-facing error messages, fix instructions, and contextual metadata.
7. **Three-Tier Icon Architecture:** Icons adhere to explicit semantic tiers (Neutral, Brand/Positive, Conceptual) with defined interaction states (Normal, Hover, Disabled).
8. **Contextual i18n & Directionality:** The internationalization and bidirectional strategy is agreed conversationally. Logical spacing properties and bidi isolation are enforced when multi-direction or RTL support is required by the project.

---

## 4. References & Assets

- **UI Principles Reference:** See [references/ui-principles-reference.md](references/ui-principles-reference.md) for full descriptions of design contracts and interaction invariants.
- **Output Template:** See [assets/templates/ui-contracts-template.md](assets/templates/ui-contracts-template.md) for the copyable application steering skeleton.
- **Cross-Platform Walkthrough:** See [examples/ui-walkthrough.md](examples/ui-walkthrough.md) for step-by-step examples across Web and Native platforms.
