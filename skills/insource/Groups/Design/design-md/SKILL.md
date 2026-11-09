---
name: design-md
description: "Authors and maintains a project-wide, binding DESIGN.md specification following Google Labs design.md and Stitch conventions. Bridges system architecture and visual UI design: combines machine-readable YAML design tokens (OKLCH color scales, fluid typography, 4/8pt spacing, elevation, radius, component tokens) with prescriptive, human-readable UI rationale and explicit Do's and Don'ts. Use when bootstrapping a project's visual system, formalizing design rules for AI coding agents, auditing UI consistency, or authoring a canonical DESIGN.md. Triggers: design.md, create design.md, design doc, visual design system, brand identity spec, design tokens, ui spec."
metadata:
  version: "1.0"
  valid-as-of: "2026-11-09"
---

# design-md — Canonical Visual Design & Token Specification

`design-md` authors and maintains a repository's canonical `DESIGN.md`. A `DESIGN.md` file is the persistent contract between human designers, software engineers, and AI coding agents. It prevents agents from defaulting to generic, cookie-cutter "AI templates" (rounded pastel gradients, ungrounded shadows, arbitrary spacing) by grounding every UI decision in machine-parseable tokens and opinionated product principles.

## The Dual-Layer Architecture of DESIGN.md

A compliant `DESIGN.md` combines two complementary layers:
1. **Machine-Readable YAML Tokens**: Normative tokens (OKLCH colors, typography ladders, spacing scales, border radii, shadows, and component specs) defined either in the top-level frontmatter or in fenced ````yaml code blocks within each section.
2. **Human-Readable Design Rationale**: Narrative guidelines, psychological registers, layout composition rules, and explicit **Do's and Don'ts** guarding against design slop.

```
┌────────────────────────────────────────────────────────┐
│                   DESIGN.md File                       │
├────────────────────────────────────────────────────────┤
│  Layer 1: Machine-Readable Tokens (YAML)              │
│  - colors (OKLCH perceptual palette + semantic roles) │
│  - typography (fluid rem ladder, font families, line) │
│  - spacing (4px / 8px incremental scale)              │
│  - elevation & surfaces (shadow tiers, borders)       │
│  - components (buttons, cards, inputs, dialogs)       │
├────────────────────────────────────────────────────────┤
│  Layer 2: Product Rationale & Rules (Markdown)         │
│  - 1. Overview & Product Feel (semantic register)     │
│  - 2. Color Language & Accessibility (WCAG / APCA)    │
│  - 3. Typography & Hierarchy (display vs body rules)  │
│  - 4. Layout & Surface Architecture (density, grid)   │
│  - 5. Elevation, Shapes & Corners                     │
│  - 6. Component Property Contracts                    │
│  - 7. Explicit Do's and Don'ts (the slop guardrails)  │
└────────────────────────────────────────────────────────┘
```

## Quick Reference & Procedure

| Step | Focus | Reference | Deliverable |
|---|---|---|---|
| **1. Discovery & Register** | Product feel, audience, brand adjectives | `references/product-feel-and-brand.md` | §1 Overview & Feel |
| **2. Perceptual Palette** | OKLCH color spaces, contrast, dark mode | `references/color-and-oklch.md` | §2 Colors & Tokens |
| **3. Typography Hierarchy** | Font pairings, fluid scales, line heights | `references/typography-and-spacing.md` | §3 Typography |
| **4. Layout & Surfaces** | Container max-widths, grids, spacing | `references/layout-and-surfaces.md` | §4 Layout & Spacing |
| **5. Component Specs** | Contract property tokens for UI primitives | `references/component-contracts.md` | §5-6 Components |
| **6. Slop Defense** | Explicit anti-patterns, Do's and Don'ts | `references/anti-patterns-and-donts.md` | §7 Do's and Don'ts |

Full start-to-finish template: `templates/canonical-design-md.md`.

---

## The Six Invariants of design-md

### 1. OKLCH Color Standards (No Raw Hex / HSL)
Every color palette must be specified in perceptual **OKLCH** (`oklch(L C H)`), optionally paired with RGB/Hex fallback mappings:
- **Perceptual uniformity**: Lightness (L) is physically uniform across all hues, guaranteeing accurate contrast and dark-mode inversion.
- **Predictable shades**: `L=50%` + `20%` = `L=70%` looks visually balanced without hue shifting.
- **WCAG / APCA Compliance**: Normal text must maintain at least 4.5:1 (or APCA Lc 60+) against its surface background.

### 2. Predictable File Structure
Agents scan `DESIGN.md` sequentially. Always maintain the canonical section order:
1. `## Overview & Product Feel`
2. `## Colors & Semantic Tokens`
3. `## Typography & Hierarchy`
4. `## Layout & Spacing System`
5. `## Elevation, Depth & Shapes`
6. `## Component Contracts`
7. `## Do's and Don'ts`

### 3. Opinionated Product Feel (No Generic SaaS Defaults)
Never write vague placeholders ("modern, clean, and intuitive"). State the concrete emotional and operational posture:
- *"This is a high-density financial execution terminal for portfolio managers. It must feel surgical, tabular, and calm — zero decorative animations, maximum data density, dark-slate background, and hairline 1px borders."*

### 4. Explicit Do's and Don'ts
Negative constraints contain the highest signal for AI coding agents. Every `DESIGN.md` must list at least 5 explicit **Don'ts** that eliminate typical agent slop (e.g. no mid-sentence bolding, no pastel background blobs, no floating cards on nested modals, no pure-black shadows).

### 5. Strict Separation of Design from Implementation
Keep `DESIGN.md` focused on visual tokens, layout rules, and component property contracts:
- **Allowed**: CSS variable mappings, token scales, container max-widths, elevation definitions, component anatomy.
- **Forbidden**: Framework setup code (e.g. `npm install`), API endpoint logic, database queries, deployment scripts.

### 6. Single Source of Truth in Repository
The generated `DESIGN.md` belongs at the repository root (`./DESIGN.md`) or in `docs/DESIGN.md`. All future UI generation, frontend agents, and code reviews must cite it directly.

---

## When to Invoke

- **Bootstrapping a new frontend**: Before writing components or styling, author `DESIGN.md` to define the project's visual system.
- **Auditing UI consistency**: When an existing app feels disconnected, disorganized, or "AI-generated".
- **Handoff to coding agents**: To ensure agentic tools (Claude Code, Cursor, Devin, OpenCode) adhere strictly to your brand tokens instead of default editor preferences.
