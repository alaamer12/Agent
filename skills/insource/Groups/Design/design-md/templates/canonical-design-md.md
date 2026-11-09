# CANONICAL DESIGN.md TEMPLATE

```markdown
---
version: "alpha"
name: "{{PROJECT_NAME}} Visual Identity"
description: "Canonical design tokens, component contracts, and UI principles for {{PROJECT_NAME}}."

tokens:
  colors:
    primary:
      50: "oklch(97% 0.02 265)"
      100: "oklch(93% 0.05 265)"
      200: "oklch(85% 0.09 265)"
      300: "oklch(75% 0.14 265)"
      400: "oklch(65% 0.18 265)"
      500: "oklch(55% 0.22 265)"
      600: "oklch(48% 0.20 265)"
      700: "oklch(40% 0.16 265)"
      800: "oklch(32% 0.12 265)"
      900: "oklch(24% 0.08 265)"
      950: "oklch(16% 0.05 265)"

    neutral:
      50: "oklch(98% 0.005 260)"
      100: "oklch(95% 0.008 260)"
      200: "oklch(90% 0.010 260)"
      300: "oklch(82% 0.012 260)"
      400: "oklch(70% 0.015 260)"
      500: "oklch(56% 0.018 260)"
      600: "oklch(44% 0.018 260)"
      700: "oklch(34% 0.015 260)"
      800: "oklch(24% 0.012 260)"
      900: "oklch(18% 0.010 260)"
      950: "oklch(12% 0.008 260)"

    semantic:
      bg-app: "var(--neutral-50)"
      bg-surface: "oklch(100% 0 0)"
      bg-surface-raised: "var(--neutral-100)"
      text-primary: "var(--neutral-950)"
      text-secondary: "var(--neutral-600)"
      text-muted: "var(--neutral-400)"
      border-subtle: "var(--neutral-200)"
      border-strong: "var(--neutral-400)"

    status:
      success: "oklch(62% 0.17 145)"
      warning: "oklch(76% 0.16 75)"
      danger: "oklch(58% 0.22 25)"
      info: "oklch(60% 0.18 240)"

  typography:
    fonts:
      body: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
      heading: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
      mono: "'JetBrains Mono', ui-monospace, monospace"
    scale:
      xs: { fontSize: "0.75rem", lineHeight: 1.4, letterSpacing: "0.01em" }
      sm: { fontSize: "0.875rem", lineHeight: 1.5, letterSpacing: "0em" }
      base: { fontSize: "1rem", lineHeight: 1.6, letterSpacing: "-0.01em" }
      lg: { fontSize: "1.125rem", lineHeight: 1.5, letterSpacing: "-0.015em" }
      xl: { fontSize: "1.25rem", lineHeight: 1.4, letterSpacing: "-0.02em" }
      "2xl": { fontSize: "1.5rem", lineHeight: 1.3, letterSpacing: "-0.025em" }
      "3xl": { fontSize: "2rem", lineHeight: 1.2, letterSpacing: "-0.03em" }

  spacing:
    "1": "0.25rem"
    "2": "0.5rem"
    "3": "0.75rem"
    "4": "1rem"
    "6": "1.5rem"
    "8": "2rem"
    "12": "3rem"
    "16": "4rem"

  radius:
    none: "0px"
    sm: "0.25rem"
    md: "0.5rem"
    lg: "0.75rem"
    full: "9999px"

  elevation:
    shadows:
      none: "none"
      sm: "0 1px 2px 0 oklch(0% 0 0 / 0.05)"
      md: "0 4px 6px -1px oklch(0% 0 0 / 0.08)"
      lg: "0 10px 15px -3px oklch(0% 0 0 / 0.10)"

  components:
    button:
      height: "40px"
      padding: "0 16px"
      radius: "var(--radius-md)"
    input:
      height: "40px"
      padding: "0 12px"
      radius: "var(--radius-md)"
      border: "1px solid var(--border-subtle)"
    card:
      padding: "var(--spacing-6)"
      radius: "var(--radius-lg)"
      border: "1px solid var(--border-subtle)"
---

# {{PROJECT_NAME}} Design System

## Overview & Product Feel
{{PROJECT_NAME}} is an engineered, high-performance web application designed for {{TARGET_AUDIENCE}} to {{CORE_USER_GOAL}}.

### Personality Statement
The interface embodies **calm, surgical efficiency**. We reject gratuitous decoration, bouncing spring physics, and multi-colored floating gradients. Every element exists to clarify data hierarchy and streamline user action.
- **Tone**: Professional, focused, and crisp.
- **Visual Posture**: Clean hairline borders, high text legibility, and tabular data alignment.
- **Anti-Identity**: Never a generic marketing template, never toy-like, and never cluttered.

## Colors & Semantic Tokens
Colors follow the **OKLCH** color model for perceptual uniformity and accurate contrast.

### Palette Rationale
- **Primary Indigo (`oklch(55% 0.22 265)`)**: Reserved for high-value actions (primary CTAs, active selection tabs).
- **Neutral Slate**: Cool chromatic gray scale preventing eye fatigue during extended operational sessions.
- **Status Accents**: Pure single-purpose signifiers for state (Green = online/success, Red = alert/error, Amber = pending/warning).

## Typography & Hierarchy
Typography prioritizes reading speed and information density.
- **Prose**: Kept strictly within `65ch` line width.
- **Headings**: Tight negative letter-spacing with clean sentence casing.
- **Numbers**: Always rendered with `tabular-nums` in tables and metric cards.

## Layout & Spacing System
Layouts follow an incremental 4px / 8px baseline grid.
- **Dashboard Grid**: Main canvas max-width `1280px` (`xl`).
- **Sidebar**: Fixed width `240px` with 36px item height.
- **Internal Card Gaps**: Standard `1.5rem` (`spacing.6`).

## Elevation, Depth & Shapes
We build depth through **hairline 1px borders and surface lightness stepping** rather than muddy drop shadows.
- Cards sit on `var(--semantic-bg-surface)` with a `1px solid var(--semantic-border-subtle)` outline.
- Corners are unified at `8px` (`radius.md`) for controls and `12px` (`radius.lg`) for containers.

## Component Contracts
- **Primary Buttons**: Solid fill, bold label, 40px height, 1px active push state.
- **Secondary Buttons**: Outlined with `1px solid var(--border-subtle)`, surface background, hover to `neutral-100`.
- **Form Inputs**: Crisp 40px height, 12px horizontal padding, 2px focus ring on focus-visible.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Use 1px hairline borders to define cards and sections. | Don't use heavy black box shadows to separate cards. |
| Limit primary brand color to the key action per view. | Don't use primary accent color on multiple competing buttons. |
| Maintain 4.5:1 WCAG contrast for all text. | Don't use muted low-contrast gray text on light backgrounds. |
| Right-align numeric columns in tables. | Don't center-align numbers or metrics. |
| Use sentence case for all buttons, menus, and headings. | Don't use Title Case or ALL CAPS for standard body labels. |
| Follow the 4px / 8px spacing token scale strictly. | Don't invent arbitrary pixel margins (`margin: 17px`). |
| Include explicit focus rings for keyboard navigation. | Don't remove focus outlines (`outline: none`) without replacement. |
```
