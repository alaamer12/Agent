# Accessibility Architecture Interview Guide

> **What this owns:** The discovery interview conducted by the `architecture` skill (or invoked standalone) to design the project's `<docs>/architecture/accessibility-architecture.md` specification.

---

## 1. Contextual Pre-Analysis

Before asking questions, inspect the repository:
1. **Frontend Stack**: React, Vue, Svelte, Angular, iOS/SwiftUI, Android/Compose, plain HTML/CSS.
2. **Current Theming & CSS System**: Tailwind, CSS Variables/Tokens, CSS-in-JS, Material UI, Shadcn/Radix.
3. **Target Audience**: Consumer public, enterprise operators, reading/editorial, data-dense financial/trading, healthcare, education.

---

## 2. The 6 Architectural Discovery Rounds

### Round 1: Visual Adaptation, Eye-Comfort & Contrast
> *"How should visual adaptation be structured for your users? Beyond standard light/dark modes, should we architect:
> 1. A dedicated **High-Contrast mode** (darkening secondary text, solidifying container outlines)?
> 2. **Eye-comfort presets** (e.g. warm cream / paper, low blue-light sepia, solarized dark)?
> 3. User-customizable theme/accent color palettes?"*

### Round 2: Typography & Multi-Font Flexibility
> *"Do your users require typographic personalization?
> 1. Should the interface support selectable font families (e.g. standard sans, dyslexia-friendly fonts like Lexend/OpenDyslexic, or high-legibility serif/mono)?
> 2. What scaling range should layouts tolerate without breaking or clipping (e.g. up to 200% zoom with relative `rem`/`em` scaling)?"*

### Round 3: Cognitive Density & Reading Comfort Modes
> *"How should information density and cognitive load adapt to different user needs?
> 1. Should we architect **Density Tiers** (e.g., Compact for data power users vs Spacious/Verbose with guided explanations)?
> 2. Is there a need for a **Distraction-Free / Comfort-Reading Mode** (collapsing side rails, setting a strict 65ch reading measure)?"*

### Round 4: Autonomy, Permissions & Disruption Hygiene
> *"What rules should govern permissions and interruptions?
> 1. How should browser permissions (notifications, sound, geolocation) be handled (e.g., strictly contextual on user trigger, never on first load)?
> 2. How are popups, modals, and toasts constrained to prevent cognitive disruption or accidental loss of focus?"*

### Round 5: Motion, Audio & Sensory Sensitivity
> *"How does the app respond to sensory and vestibular sensitivities?
> 1. How are animations bound to the operating system's `prefers-reduced-motion` token?
> 2. Are sound cues, video autoplay, and ambient animations strictly opt-in?"*

### Round 6: Keyboard, Screen Reader & Navigation Hygiene
> *"What are the baseline navigation contracts?
> 1. What are the touch-target floors (e.g., 44×44px minimum) and keyboard focus indicator conventions (unambiguous 2px outline rings)?
> 2. What are the bidi / RTL and internationalization support requirements?"*
