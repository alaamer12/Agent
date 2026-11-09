# Accessibility Architecture Specification Template

<!-- 
This document defines the binding Accessibility & Sensory Adaptation Architecture for the application.
Author: Generated via the architecture/accessibility skill
Placement: <docs>/architecture/accessibility-architecture.md
-->

# {Project Name} — Accessibility Architecture Specification

## 1. Executive Summary & Philosophy
This application treats accessibility as a foundational architectural system spanning visual adaptation, typographic personalization, cognitive density management, user autonomy, sensory protection, and assistive navigation.

| Dimension | Architectural Contract | Implementation Strategy |
| :--- | :--- | :--- |
| **Visual Adaptation** | High-contrast tier, eye-comfort palettes, tokenized themes | CSS Variables / Theme Tokens |
| **Typography** | Multi-font selection, dynamic rem scaling, no text clipping | Fluid type scale + font switcher |
| **Cognitive Density** | Compact vs Standard vs Verbose modes, Comfort Reading | Data attributes on layout root |
| **Autonomy & Permissions** | Contextual-only permissions, zero unprompted modals | Permission boundary gates |
| **Sensory Sensitivity** | Root reduced-motion token, zero autoplay, haptic toggles | Media query listeners + settings |
| **Navigation & Operability** | 100% keyboard navigable, persistent focus ring, 44px floor | Semantic DOM + focus-visible |

---

## 2. Visual Adaptation & Eye-Comfort Theming

### 2.1 Theme & Preset Matrix
The interface provides tokenized visual themes accessible via user preferences:

- **Standard Modes**: Light Mode and Dark Mode.
- **High-Contrast Layering**:
  - Secondary/muted text elevated to ≥ 7:1 contrast ratio.
  - Structural container borders reinforced with 1.5px solid lines.
  - Active elements wear a high-visibility 2px focus ring (`--focus-ring`).
- **Eye-Comfort Presets**:
  - `Warm Cream`: Low blue-light, paper-tinted background (`#fbf8f2`) with deep charcoal ink (`#2c2a29`).
  - `Subdued Slate`: Low-glare dark mode avoiding stark black (`#161b22`).
  - `Custom Tint`: Allows user tuning of base hue/saturation without breaking contrast minimums.

### 2.2 Token Contracts (CSS Custom Properties)
```css
:root {
  --bg-app: #ffffff;
  --bg-surface: #f6f8fa;
  --text-primary: #1f2328;
  --text-secondary: #656d76;
  --border-subtle: #d0d7de;
  --focus-ring: #0969da;
}

[data-contrast="high"] {
  --text-secondary: #1f2328; /* Elevated to primary contrast */
  --border-subtle: #1f2328; /* Reinforced borders */
  --focus-ring: #000000;
}

[data-preset="warm-cream"] {
  --bg-app: #fbf8f2;
  --bg-surface: #f3eee3;
  --text-primary: #2c2a29;
  --text-secondary: #57534e;
  --border-subtle: #d6cebf;
}
```

---

## 3. Typographic Personalization & Fluid Scaling

### 3.1 Font Family Selection
The user may choose from three accessible font stacks:
1. **System Default**: Modern high-legibility sans-serif (`system-ui, -apple-system, Inter, sans-serif`).
2. **Dyslexia-Optimized**: Enhanced character distinction and baseline weighting (e.g. `Lexend`, `OpenDyslexic`, or `Atkinson Hyperlegible`).
3. **Monospaced / Data**: Equal-width characters for financial and technical clarity (`ui-monospace, SFMono-Regular, monospace`).

### 3.2 Zoom & Layout Tolerance
- All typography and spatial padding must use relative units (`rem`, `em`, `ch`).
- The interface must remain fully functional and unclipped at up to **200% browser zoom**.
- Fixed `height` with `overflow: hidden` on text containers is strictly forbidden.

---

## 4. Cognitive Density & Reading Comfort Modes

### 4.1 Density Tiers
Controlled via `data-density="compact|standard|spacious"`:
- **Compact**: Tighter row heights (32px), condensed padding (6px), optimized for high-volume data tables and dashboard grids.
- **Standard**: Balanced default layout.
- **Spacious / Verbose**: Generous line heights (1.75), expanded tap targets, step-by-step onboarding banners, and inline plain-language helpers.

### 4.2 Distraction-Free Comfort-Reading Mode
When activated on articles, documentation, or long-form records:
- Collapses sidebars, navigation rails, and non-essential floating widgets into a minimized drawer.
- Constrains reading measure to `max-width: 68ch` centered on screen.
- Increases body font size by +15% and enforces `line-height: 1.8`.

---

## 5. User Autonomy, Permissions & Disruption Hygiene

### 5.1 Permission Invariants
- **No Cold Permissions**: Never request browser notifications, audio, microphone, or geolocation on landing or authentication.
- **Contextual Justification**: A permission dialog must only appear immediately following an explicit user action (e.g. clicking "Enable Delivery Alerts").
- **Graceful Rejection**: The application must remain 100% functional if any permission is denied.

### 5.2 Modal & Interruption Governance
- **Zero Unprompted Takeovers**: No promotional overlays, countdown timers, or sudden popup modals.
- **Non-Modal Toasts**: Transient feedback is delivered through passive aria-live status regions that do not steal keyboard focus.
- **Confirmation Floors**: Destructive actions (deletes, resets) require explicit two-step confirmation with undo buffers where feasible.

---

## 6. Motion, Sensory Protection & Audio Control

- **Reduced Motion**: All animations and transitions listen to `prefers-reduced-motion: reduce`:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
  ```
- **Zero Autoplay**: Audio and video media never play without direct user interaction.
- **Sound & Haptic Toggle**: App-level setting to mute interface sounds and haptic feedback independently of system volume.

---

## 7. Assistive Navigation, Focus & RTL Verification

- **Keyboard Focus Ring**: Always visible on `:focus-visible` with minimum 2px width and 2px outline offset.
- **Touch Targets**: Minimum hit area of 44×44 CSS pixels for all interactive controls.
- **Bidirectional Reflow**: All horizontal layouts utilize CSS Logical Properties (`margin-inline`, `padding-inline`, `inset-inline-start`) to guarantee seamless RTL language reflow.
