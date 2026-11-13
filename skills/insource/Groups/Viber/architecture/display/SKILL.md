---
name: display
description: Orchestrates and authors an application's Display Architecture specification into <docs>/architecture/display-architecture.md — how values and text are EXPRESSED to users. Owns the notation spectrum (exact 4,982,317 vs grouped 5,000,000 vs compact 5M vs prose "nearly 5 million"; 500_000 stays source-side) and assigns a precision level per surface class; container-fit discipline (every display slot declares a character/width budget; overflow is a defect - fixed-width cards must never let a plain number strike through; fallback ladders and tabular figures); locale display rules via Intl/ICU (separators, Arabic-Indic vs Western numerals, calendars, Arabic plural categories, bidi isolation inside RTL text); and the voice-medium-typeface pairing — not every voice matches every typeface and vice versa, so each surface class declares its (voice register, typeface + figure style, notation level) triple coherently, always under the accessibility pillar's user-override precedence.
argument-hint: "[project root or app name]"
---

# Display Architecture Skill

## 1. Overview & Philosophy

Every value the app puts on screen is a **claim with three coupled decisions**: how precise it
is, which notation expresses it, and in which medium (typeface + container) it renders. Choosing
one decision and improvising the other two is how `5,000,000` strikes through a fixed-width card,
how a friendly marketing number renders in audit-grade tabular monospace, and how an Arabic
sentence eats its own digits. This pillar decides all three, once, per surface class.

The pillar's doctrine:

- **Precision is a property of the reader's question, not of the widget.** "About how many?"
  earns `5M`; "what exactly do I owe?" earns the full `4,982,317`. The level is assigned by the
  architecture, not re-guessed per screen by the implementer.
- **Compression may hide precision, never destroy it.** A compact display keeps the exact value
  reachable (tooltip, detail view, screen-reader text).
- **The container is part of the message.** A display slot without a declared width budget and
  fallback ladder is an unfinished contract; worst-case-magnitude × worst-case-locale test
  strings prove it holds.
- **Voice, medium, and notation must corroborate each other.** They are declared as one triple
  per surface class; mismatch (playful display face on legal figures, prose rounding in a
  reconciliation table) is a defect, not a style choice.
- **Boundaries held against sibling pillars:** `ui` owns layout stability and mirroring; this
  pillar owns what string fills the slot. `accessibility` owns the user's overrides (fonts,
  density, zoom); this pillar defines the defaults those overrides replace, and always yields.

## 2. Directory Structure & Assets

```text
display/
├── SKILL.md                                              # Entry point, doctrine, workflow
├── assets/
│   └── templates/
│       └── display-architecture-template.md              # Binding document template
├── references/
│   ├── display-principles.md                             # Deep dive: spectrum, containers, i18n, voice-triple
│   └── discovery-interview.md                            # Targeted questions for the user
└── examples/
    └── display-walkthrough.md                            # Ops-console stat-card overflow + RTL locale pass
```

## 3. Workflow & Conversational Discovery

When invoked (standalone or via the parent `architecture` skill):

1. **Pre-Analysis**: inspect UI surfaces, design tokens (`--font`, type scale), locale setup
   (`Intl` usage, RTL support, message files), data-heavy components (cards, tables, charts),
   and the project's declared voice register (AGENTS.md voice section when present).
2. **Contextual Interview** (`references/discovery-interview.md`): which surfaces carry
   quantities, the reader's question per surface, tight containers, regulatory exactness
   needs, target locales (RTL? numeral system? calendar?), the typeface roster and each
   surface's voice.
3. **Live Web Research** before authoring: current `Intl` / ICU plural and numeral behavior in
   the confirmed stack, framework formatting idioms, Arabic-Indic digit rendering notes.
4. **Author Specification**: draft `<docs>/architecture/display-architecture.md` using
   `assets/templates/display-architecture-template.md` — surface-class table with the full
   triple (voice, typeface + figures, notation level), budgets, fallback ladders, locale
   pipeline, pairing roster, acceptance test strings.
5. **Register & cross-check**: cross-link from the ui/accessibility architecture docs (declare
   the boundary rules there too); sync points (theme tokens, voice section, locale files)
   recorded so an edit to one side lands on all rows in the same c