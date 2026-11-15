# Component Property Contracts

The `## Component Contracts` section bridges tokens to concrete UI elements. It establishes strict property mappings so agents do not improvise button heights, input borders, or dialog padding.

---

## 1. Core Primitives

### 1.1 Buttons (`Button`)
Every button must have a clear hierarchy level:

```yaml
components:
  button:
    variants:
      primary:
        bg: "var(--primary-500)"
        text: "oklch(100% 0 0)"
        border: "none"
        hover-bg: "var(--primary-600)"
        active-bg: "var(--primary-700)"
      secondary:
        bg: "var(--semantic-bg-surface)"
        text: "var(--semantic-text-primary)"
        border: "1px solid var(--semantic-border-subtle)"
        hover-bg: "var(--neutral-100)"
      ghost:
        bg: "transparent"
        text: "var(--semantic-text-secondary)"
        border: "none"
        hover-bg: "var(--neutral-100)"
        hover-text: "var(--semantic-text-primary)"
      danger:
        bg: "var(--status-danger)"
        text: "oklch(100% 0 0)"
        hover-bg: "oklch(50% 0.22 25)"

    sizes:
      sm:
        height: "32px"
        padding: "0 12px"
        typography: "var(--typography-scale-sm)"
        radius: "var(--radius-md)"
      md:
        height: "40px"
        padding: "0 16px"
        typography: "var(--typography-scale-base)"
        radius: "var(--radius-md)"
      lg:
        height: "48px"
        padding: "0 24px"
        typography: "var(--typography-scale-lg)"
        radius: "var(--radius-lg)"
```

### 1.2 Form Inputs (`Input`)
```yaml
  input:
    height: "40px"
    padding: "0 12px"
    bg: "var(--semantic-bg-surface)"
    border: "1px solid var(--semantic-border-subtle)"
    radius: "var(--radius-md)"
    text: "var(--semantic-text-primary)"
    placeholder: "var(--semantic-text-muted)"
    focus-ring: "2px solid var(--primary-500)"
    focus-ring-offset: "1px"
    error-border: "1px solid var(--status-danger)"
```

### 1.3 Cards (`Card`)
```yaml
  card:
    bg: "var(--semantic-bg-surface)"
    border: "1px solid var(--semantic-border-subtle)"
    radius: "var(--radius-lg)"
    padding: "var(--spacing-6)"
    header-gap: "var(--spacing-4)"
    footer-border: "1px solid var(--semantic-border-subtle)"
```

### 1.4 Tables & Data Grids (`Table`)
- Row height: 40px (compact) or 48px (standard).
- Header row: Font-weight medium (500), uppercase, tracking `0.05em`, subtle bottom border.
- Alternating zebra stripes: Forbidden. Use clean hover highlighting (`bg-neutral-50` / `bg-neutral-900`) instead.

---

## 2. Interactive States Mandate

Every interactive component contract must explicitly declare four states:
1. **Default**: Rest state.
2. **Hover**: Visual affordance (subtle background shift, pointer cursor).
3. **Focus-Visible**: High-visibility 2px focus ring with 1px offset for keyboard accessibility.
4. **Disabled**: Opacity reduced to 50%, `cursor: not-allowed`, no hover events.
