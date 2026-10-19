# Hairline border with wide shadow

**ID:** `gpt-thin-border-wide-shadow`  
**Catalog section:** Visual Details  
**Official modality:** Source

## Definition and empirical evidence

The catalog describes a thin border and a broad shadow both defining the same card. It suggests choosing the edge or shadow so the surface has a clearer shape. These cues can coexist when they express different roles; their mere presence is not proof of redundancy.

## Underlying principle and potential harm

Use each visual boundary/elevation cue for a purpose. A border can mark a crisp edge, while a shadow can communicate lift, overlap, or separation. If both repeat the same perimeter without added meaning, their combined weight may make the surface look heavy and compete with content. Removing a cue without checking context can instead make an edge disappear.

WCAG non-text contrast concerns the actual visual component boundary when that boundary is needed for identification; an exterior shadow/glow is not automatically the contrast-bearing edge.

## Recognition signals

- Both a visible border and a broad shadow appear to trace the same card perimeter.
- Their combined prominence makes surfaces feel more elevated/heavy than neighboring components.
- Nested or closely packed cards gain duplicate outlines and shadows.
- The border is required to distinguish a component, but only the exterior shadow makes its edge perceptible.

## Causes to investigate

Possible causes include a default border retained after adding elevation; styles copied from a component/theme with different surface assumptions; a theme/token change that increased a formerly subtle cue; or separate authors adding edge and elevation without coordinating intent.

## Exceptions and false positives

- A border can preserve a crisp edge on variable/low-contrast backgrounds while a shadow communicates lift.
- Layered or dense surfaces may need both cues for separation.
- Focus or selected-state borders have a distinct state role and should be assessed separately.
- One CSS declaration may be imperceptible in context; source coincidence does not prove redundant visual emphasis.

## Correction guidance

Confirm the surface’s role and intended elevation, then inspect it alongside similar components and backgrounds. If both only trace the same edge, retain the more appropriate cue: a border for a defined perimeter, or a shadow for elevation, and tune/remove the other. If both are intentional, reduce their combined prominence and document their separate roles. Recheck rendered separation and applicable boundary contrast; do not rely on an exterior shadow where a visible component edge is needed.

## Independent research references

- [Material Design — Elevation](https://m2.material.io/design/environment/elevation.html) — shadow’s role in expressing edges, overlap, and elevation.
- [USWDS Card](https://designsystem.digital.gov/components/card) — cards are usually distinguished with a border or a shadow.
- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — grouping cues can help, but excess borders/backgrounds can clutter.
- [W3C WAI WCAG 2.1 non-text contrast](https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html) — scope of component-boundary contrast and treatment of exterior shadows/glows.