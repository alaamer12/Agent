# AI color palette

**ID:** `ai-color-palette`  
**Catalog section:** Color & Contrast  
**Official modality:** Source

## Definition and empirical evidence

The catalog calls out familiar purple/violet gradients and bright cyan on dark backgrounds as recognizable AI-interface defaults, and recommends building color around product identity and use. This is a review signal, not proof those hues are wrong.

## Underlying principle and potential harm

Choose colors to serve product identity, audience, tasks, and interface roles. An unconsidered default can make unrelated products feel interchangeable or create emphasis mismatched to the task. Any palette can also create inaccessible text/background pairings or ambiguous state cues. WCAG evaluates rendered contrast and whether color is the sole information channel; it does not ban particular colors.

## Recognition signals

- Purple/violet gradients and bright cyan accents recur without a product-specific rationale.
- Repeated accents do not correspond to clear surface/action/state/data roles.
- Unrelated screens use the same fashionable treatment, weakening product or page distinctions.
- Source clues include hard-coded colors, gradient declarations, and repeated accents, but these cannot establish brand fit, visual hierarchy, or accessibility on their own.

## Causes to investigate

Possible causes include a generic prompt/starter palette; copying familiar tech aesthetics without checking identity; choosing colors before defining semantic roles; or applying marketing colors to task-focused UI without testing contrast or meaning.

## Exceptions and false positives

- Purple, violet, or cyan may be established brand colors or useful for a product’s audience.
- Category conventions can support recognition; evaluate whether following/departing from them serves users.
- Role-based system colors and user-preference modes can intentionally reuse familiar hues.
- A purple/cyan palette may be coherent, accessible, and on-brand; a novel palette can still mismatch, flatten hierarchy, or fail contrast.
- Color association alone cannot establish intent or quality.

## Correction guidance

Confirm brand and task requirements before changing colors. If the palette is an unconsidered default, define a coherent, role-based set from product identity and user needs; compare representative screens rather than selecting for novelty. Document intentional roles and maintain consistency. Test rendered text contrast, applicable non-text contrast, and non-color cues for status/information.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — purple/violet and cyan as common signals, with identity/use as the basis for color.
- [USWDS color tokens overview](https://designsystem.digital.gov/design-tokens/color/overview) — role-based color tokens guided by project identity and user needs.
- [W3C WAI WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — rendered text/background contrast.
- [W3C WAI WCAG 2.2 use of color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) — color need not be avoided but cannot be the only cue.
- [Material Design 3 — Customizing Material](https://m3.material.io/foundations/customization) — brand, user preference, role-based schemes, and accessibility adjustments.