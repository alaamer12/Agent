# Dark mode with glowing accents

**ID:** `dark-glow`  
**Catalog section:** Color & Contrast  
**Official modality:** Source

## Definition and empirical evidence

The catalog flags a dark interface whose vivid luminous accents/glows are so broad or strong that the screen becomes a wall of neon. Dark surfaces and bright accents are not inherently problematic. Color should have a purposeful role such as primary action, meaningful state, selection, or data series.

## Underlying principle and potential harm

Use theme-aware semantic colors to establish hierarchy and maintain legibility in the dark appearance. If many elements glow, they can compete for attention, flatten primary/secondary distinctions, or make text and controls uncomfortable to view. Contrast must be evaluated in the rendered dark theme; a bright hue/glow does not guarantee it.

## Recognition signals

- Glow/bright accents repeat across unrelated surfaces without consistent semantic roles.
- Decorative effects compete with the primary action or meaningful states.
- Text, icons, or control boundaries lose distinction against dark surfaces.
- Source clues include repeated high-saturation tokens, glow effects, and animated brightness; these are investigation leads, not proof.

## Causes to investigate

Possible causes include a default “futuristic” style; making every component appear interactive; copying neon campaign styling; or insufficiently distinct semantic color roles.

## Exceptions and false positives

- Vivid accents can communicate focus, selection, error, or another consistent semantic state.
- Data/monitoring displays may use saturated colors for series/status when their mapping is clear and perceptible.
- A luminous dark identity may fit gaming, low-light, or established brand contexts.
- Static glow is not the same as flashing content; assess animated flashing against the relevant criterion separately.
- Dark mode itself is not a violation; review actual contrast and user context.

## Correction guidance

Identify focal point and semantic color roles before changing the palette. If decorative glow competes with content, soften/remove it or reserve it for the highest-priority action/state. Preserve meaningful accents but make mappings consistent, test text and component contrast in each theme/state, and provide non-color cues when needed. Evaluate animation as rendered rather than from a still image.

## Independent research references

- [Apple Human Interface Guidelines — Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode) — dark-theme adaptation, contrast, and low-light context.
- [Material Design 3 — Color system](https://m3.material.io/styles/color/system/how-the-system-works) — semantic theme-aware roles and contrast relationships.
- [GOV.UK Design System — Colour](https://design-system.service.gov.uk/styles/colour) — semantic focus/error/success roles.
- [W3C WAI WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — rendered text/background contrast.
- [W3C WAI WCAG 2.2 flashing](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) — flashing criterion for animated effects, not static glow.