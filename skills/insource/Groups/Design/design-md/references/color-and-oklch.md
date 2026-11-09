# Color Architecture & OKLCH Token Standards

The `## Colors & Semantic Tokens` section defines the repository's color system. `design-md` mandates **OKLCH** (`oklch(L C H)`) as the primary definition format.

---

## 1. Why OKLCH Over Hex / HSL

- **Perceptual Uniformity**: In sRGB and HSL, yellow (`hsl(60, 100%, 50%)`) looks blindingly bright while blue (`hsl(240, 100%, 50%)`) looks dark. In OKLCH, lightness `L=0.6` has the exact same perceived brightness across every single hue.
- **Predictable Dark/Light Scaling**: Inverting lightness (`1.0 - L` or stepping down by `0.15`) reliably preserves contrast without altering hue or chroma.
- **Wider Gamut**: OKLCH natively accesses Display P3 colors available on modern displays while gracefully falling back in sRGB.

---

## 2. Token Structure & Taxonomy

A compliant DESIGN.md defines colors across three distinct tiers:
1. **Palette Scales (Raw Primitives)**: Numbered steps from `50` to `950`.
2. **Semantic Roles (Contextual)**: Brand primary, accent, surface, text, and border.
3. **Feedback / Status**: Success, warning, danger, and info.

```yaml
colors:
  # Primary Brand Palette (e.g. Precision Indigo)
  primary:
    50: "oklch(97% 0.02 265)"
    100: "oklch(93% 0.05 265)"
    200: "oklch(85% 0.09 265)"
    300: "oklch(75% 0.14 265)"
    400: "oklch(65% 0.18 265)"
    500: "oklch(55% 0.22 265)"  # Primary CTA / Brand anchor
    600: "oklch(48% 0.20 265)"
    700: "oklch(40% 0.16 265)"
    800: "oklch(32% 0.12 265)"
    900: "oklch(24% 0.08 265)"
    950: "oklch(16% 0.05 265)"

  # Neutral Slate Scale (Subtle cool chromatic undertone)
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

  # Semantic Surfaces & Roles
  semantic:
    bg-app: "var(--neutral-50)"
    bg-surface: "oklch(100% 0 0)"
    bg-surface-raised: "var(--neutral-100)"
    text-primary: "var(--neutral-950)"
    text-secondary: "var(--neutral-600)"
    text-muted: "var(--neutral-400)"
    border-subtle: "var(--neutral-200)"
    border-strong: "var(--neutral-400)"

  # Status Tokens
  status:
    success: "oklch(62% 0.17 145)"
    warning: "oklch(76% 0.16 75)"
    danger: "oklch(58% 0.22 25)"
    info: "oklch(60% 0.18 240)"
```

---

## 3. Contrast & Accessibility Guidelines

- **WCAG 2.1 AA**: Normal text (< 18pt / 24px) requires **4.5:1** contrast ratio against the background. Large text (≥ 18pt / 24px or bold ≥ 14pt) requires **3:1**.
- **Interactive Controls**: Form inputs, focus rings, and action borders must maintain **3:1** against adjacent surfaces.
- **Never rely on color alone**: Error states must pair red with an icon or explicit text label.
