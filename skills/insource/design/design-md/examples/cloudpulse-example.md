# Worked Example: CloudPulse Operational Monitoring Platform

Here is a complete, production-grade `DESIGN.md` created for an operational observability platform:

```markdown
---
version: "alpha"
name: "CloudPulse Visual Design Specification"
description: "Binding design tokens, component contracts, and UI guidelines for CloudPulse."

tokens:
  colors:
    primary:
      500: "oklch(56% 0.20 250)"
      600: "oklch(48% 0.18 250)"
    neutral:
      50: "oklch(98% 0.005 250)"
      100: "oklch(95% 0.008 250)"
      200: "oklch(90% 0.010 250)"
      800: "oklch(24% 0.012 250)"
      900: "oklch(18% 0.010 250)"
      950: "oklch(12% 0.008 250)"
    semantic:
      bg-app: "var(--neutral-950)"
      bg-surface: "var(--neutral-900)"
      bg-surface-raised: "var(--neutral-800)"
      text-primary: "oklch(98% 0 0)"
      text-secondary: "oklch(75% 0.01 250)"
      border-subtle: "oklch(28% 0.01 250)"
      border-strong: "oklch(42% 0.02 250)"
    status:
      success: "oklch(62% 0.18 145)"
      warning: "oklch(76% 0.16 75)"
      danger: "oklch(58% 0.22 25)"

  typography:
    fonts:
      body: "'Geist', -apple-system, sans-serif"
      mono: "'Geist Mono', monospace"
    scale:
      xs: { fontSize: "0.75rem", lineHeight: 1.4 }
      sm: { fontSize: "0.875rem", lineHeight: 1.45 }
      base: { fontSize: "1rem", lineHeight: 1.5 }
      lg: { fontSize: "1.125rem", lineHeight: 1.4 }
      xl: { fontSize: "1.25rem", lineHeight: 1.35 }
      "2xl": { fontSize: "1.5rem", lineHeight: 1.25 }

  spacing:
    "1": "0.25rem"
    "2": "0.5rem"
    "3": "0.75rem"
    "4": "1rem"
    "6": "1.5rem"
    "8": "2rem"

  radius:
    sm: "2px"
    md: "4px"
    lg: "6px"

  elevation:
    shadows:
      none: "none"
      sm: "0 1px 2px 0 oklch(0% 0 0 / 0.2)"
---

# CloudPulse Design System

## Overview & Product Feel
CloudPulse is an operational observability console built for reliability engineers. It must feel like a precision flight instrument: dark-first, dense, immediate, and zero-distraction.

### Personality Statement
- **Tone**: Surgical, calm, and high-density.
- **Posture**: Hairline 1px borders (`border-subtle`), monospaced telemetry, and 4px radii.
- **Anti-Identity**: Never a bubbly SaaS template. No bouncy CSS keyframe animations, no floating modal stacks, and no pastel status pills.

## Colors & Semantic Tokens
Specified in OKLCH for consistent contrast in dark mode.
- **Primary Blue (`oklch(56% 0.20 250)`)**: Reserved for live filter activation and runbook executions.
- **Surface Contrast**: Slate black canvas (`neutral-950`) with dark graphite cards (`neutral-900`) separated by hairline 1px borders.

## Typography & Hierarchy
- **Body & Controls**: Geist sans with tight tracking.
- **Metrics & Timestamps**: Geist Mono with `tabular-nums` ensuring column numbers never jitter during live polling.

## Layout & Spacing System
- **Sidebar**: Fixed 220px, collapsible to 48px icon rail.
- **Metric Grid**: 4-column auto-fit with 16px gap (`spacing.4`).

## Elevation, Depth & Shapes
- No drop shadows on standard dashboard cards; separation is achieved purely via borders.
- Floating command palette uses `shadow-sm` and a 1px border.

## Component Contracts
- **Live Badges**: 20px height, 1px border, filled status dot.
- **Buttons**: 32px height (compact), 4px radius, 12px padding.
- **Log Stream**: Monospaced 12px type, 24px line height, alternating row highlight on hover.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Use tabular figures (`tabular-nums`) for all live metric displays. | Don't allow metric numbers to jitter horizontally on data refresh. |
| Use 1px borders with `border-subtle` to divide metric panels. | Don't use box shadows to separate dark-mode panels. |
| Reserve green/red status colors exclusively for system health. | Don't use green or red for arbitrary decorative UI accents. |
| Keep button heights at a compact 32px or 36px in operational views. | Don't use oversized 48px+ consumer touch targets in data views. |
| Maintain strict 4.5:1 contrast against dark background. | Don't use low-contrast charcoal text on black surfaces. |
```
