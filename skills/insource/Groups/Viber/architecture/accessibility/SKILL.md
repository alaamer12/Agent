---
name: accessibility
description: Orchestrates and authors an application's Accessibility Architecture specification into <docs>/architecture/accessibility-architecture.md. Moves beyond compliance checklists to design a comprehensive system spanning visual adaptation (high-contrast mode, eye-comfort presets like warm-cream/slate, user-tunable themes), typographic flexibility (multi-font selection, dyslexia-friendly fonts like Lexend/OpenDyslexic, fluid rem scaling without clipping), cognitive density tiers (compact vs standard vs spacious/verbose), comfort-reading modes, user autonomy and permission hygiene (contextual permissions, zero unexpected modals or popups), reduced motion, and assistive operability.
argument-hint: "[project root or app name]"
---

# Accessibility Architecture Skill

## 1. Overview & Philosophy

The **accessibility** skill defines the comprehensive sensory, cognitive, autonomy, and reading architecture for applications.

Accessibility is treated not merely as an automated markup audit (WCAG/ARIA), but as an **architectural user empowerment system**:
- Giving users control over **visual contrast and eye comfort** (high contrast, warm-cream, low blue-light, slate dark modes).
- Empowering users with **typographic choices** (dyslexia-optimized fonts like Lexend/Atkinson Hyperlegible, scalable rem units up to 200% without clipping).
- Modulating **cognitive load and information density** (compact power-user view vs verbose/spacious guided view, distraction-free comfort reading).
- Enforcing **user autonomy and permission hygiene** (contextual prompts only, zero unprompted popups or sudden modals).
- Honoring **sensory sensitivities** (root `prefers-reduced-motion`, opt-in audio/haptics, zero autoplay).

---

## 2. Directory Structure & Assets

```text
accessibility/
├── SKILL.md                                                # Entry point, doctrine, and workflow
├── assets/
│   └── templates/
│       └── accessibility-architecture-template.md          # Binding document template
├── references/
│   ├── accessibility-architecture-principles.md            # Deep dive into the 6 dimensions
│   └── discovery-interview.md                              # Targeted questions for the user
└── examples/
    └── accessibility-walkthrough.md                        # Clinical / operational portal walkthrough
```

---

## 3. Workflow & Conversational Discovery

When invoked (either standalone or via the parent `architecture` skill):

1. **Pre-Analysis**: Inspect the codebase, styling system, component libraries, and target user personas.
2. **Contextual Interview** (`references/discovery-interview.md`):
   - **Visual Adaptation & Eye Comfort**: High-contrast tier, eye-comfort presets (warm-cream, slate, paper), user theme customization.
   - **Typographic Flexibility**: Multi-font switcher (System vs Dyslexia-friendly vs Monospace), 200% zoom tolerance.
   - **Cognitive Density**: Compact vs Standard vs Spacious/Verbose tiers, distraction-free reading mode.
   - **Autonomy & Permissions**: Strict rule against cold permissions (notifications, sound, geolocation), popup/modal governance.
   - **Sensory & Motion**: Reduced-motion enforcement, zero autoplay, haptic toggles.
   - **Assistive Navigation**: Focus rings (`:focus-visible`), touch targets (≥44px), RTL reflow.
3. **Live Web Research**: Search for stack-specific accessibility implementations (e.g., `"CSS custom properties high contrast theme"`, `"Tailwind fluid typography rem clamp"`, `"Radix accessible font switcher"`).
4. **Author Specification**: Draft `<docs>/architecture/accessibility-architecture.md` using `assets/templates/accessibility-architecture-template.md`.
5. **Register in System Docs**: Cross-link from `AGENTS.md` or `UNITS.md` under design/accessibility guidelines.
