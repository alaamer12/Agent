# Accessibility Architecture Principles & Holistic Spectrum

> **What this owns:** The foundational philosophy and engineering principles for Accessibility Architecture. Beyond checklist compliance (WCAG/ARIA), accessibility is an architectural pillar of **sensory, cognitive, autonomy, and reading comfort adaptation**.

---

## 1. The 6 Dimensions of Modern Accessibility Architecture

Accessibility is not just "screen readers and high contrast". A modern accessible system architecture empowers every user to adapt the sensory and cognitive load of the application to their individual needs:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   Accessibility Architecture Spectrum                  │
└────────────────────────────────────────────────────────────────────────┘

 1. Visual & Contrast Adaptation
    • Not just Light vs Dark: High-contrast mode (deepened secondary text, solid borders).
    • Eye-comfort presets: Warm-creamy, Sepia, E-ink low-stimulation, Midnight OLED.
    • User-tunable base tint/hue adjustments.

 2. Typography & Legibility Controls
    • Dynamic type scaling (rem/em boundaries without layout breaks).
    • Accessible font choices: Dyslexic-friendly (OpenDyslexic, Lexend), High-legibility sans (Atkinson Hyperlegible), system monospaced.
    • Line-height, letter-spacing, and reading measure (max-width ch) controls.

 3. Cognitive Load & Content Density
    • Information density tiers: Compact (power user / high density) vs Normal vs Verbose / Spacious (step-by-step guidance).
    • Distraction-free / Focused-reading mode: collapsible sidebars, dimmed secondary chrome.
    • Plain-language / explainer toggles for complex domain terms.

 4. User Autonomy & Permission Hygiene
    • Explicit consent before disruption: notifications, location, microphone, sound effects.
    • Predictable modal dialogs: zero unprompted popups, marketing takeovers, or layout jumps.
    • Reversible decisions: clear undo buffers, confirmation on destructive actions.

 5. Motion, Audio & Sensory Sensitivity
    • Respect `prefers-reduced-motion` at root token level.
    • Zero auto-playing video/audio; independent toggle for interface sounds/haptics.
    • Photosensitivity protections: strict ban on high-frequency strobing or flickering.

 6. Navigation, Focus & Interaction Diversity
    • 100% Keyboard operability with clear, persistent focus indicators.
    • Robust bidi/RTL support and touch target floors (minimum 44x44px / 48x48px).
    • Semantic markup, predictable heading hierarchies, and standard ARIA roles.
```

---

## 2. In-Depth Architectural Domains

### Dimension A: Visual Adaptation & Eye-Comfort Palettes
- **High-Contrast Layering**: Does not require changing brand personality. In high-contrast mode:
  - Secondary and tertiary muted text are promoted to higher luminance contrast ratios (minimum 7:1 for body text, 4.5:1 for secondary).
  - Subtle 1px borders are darkened or thickened to clearly delineate container boundaries.
  - Interactive element states (hover, focus, active) gain unmistakable high-contrast rings.
- **Eye-Comfort & Custom Presets**:
  - Theming is tokenized (`--bg-primary`, `--bg-surface`, `--text-main`, `--text-muted`, `--border-dim`).
  - Pre-engineered presets reduce eye fatigue:
    - *Warm Cream / Paper*: Low blue-light, soft off-white background with charcoal text.
    - *Midnight / Solarized*: Subdued dark mode avoiding pure #000000 contrast glare.
    - *User-Defined Accent/Background*: Allows users with specific light sensitivities to pick their preferred base tone.

### Dimension B: Typographic Flexibility
- **Multi-Font Family Selection**:
  - Allow users to switch font families across 3 primary categories:
    1. *Standard System*: Clean, modern sans-serif (Inter, Roboto, SF Pro).
    2. *Dyslexia-Optimized*: Weighted baselines and distinct letter shapes (OpenDyslexic, Lexend, Atkinson Hyperlegible).
    3. *Monospaced / Clean Serif*: Fixed character widths for unambiguous code/financial numbers or editorial reading.
- **Fluid & Scalable Sizing**:
  - Layouts must be built with relative units (`rem`, `em`, `clamp()`).
  - Container heights must never be fixed with `overflow: hidden` on text wrappers. Scaling up to 200% must wrap cleanly without text clipping.

### Dimension C: Cognitive Density & Reading Comfort Modes
- **Density Tiers**:
  - *Compact*: For operators and power users scanning hundreds of table rows.
  - *Standard*: Balanced padding and default whitespace.
  - *Spacious / Verbose*: Generous line heights, visible helper text, explicit step indicators, and simplified cards.
- **Comfort-Reading Mode**:
  - Dedicated toggle for long-form content: strips away rails, ads, floating action buttons, and secondary stats. Sets line length to an optimal 60-75 characters (`max-width: 68ch`).

### Dimension D: Autonomy & Permission Architecture
- **Informed Consent Over Aggression**:
  - Notifications, push alerts, sound cues, and browser permissions must never be triggered on initial page load.
  - Contextual triggering: Ask for notification permission only when the user explicitly triggers an action that warrants a notification (e.g. "Notify me when this batch export completes").
  - Zero surprise popups: modal dialogs are reserved for direct user-initiated flows or critical safety confirmations.
