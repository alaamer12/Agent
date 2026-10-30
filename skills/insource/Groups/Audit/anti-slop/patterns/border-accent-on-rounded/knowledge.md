# Border accent on rounded element

**ID:** `border-accent-on-rounded`  
**Catalog section:** Visual Details  
**Official modality:** Source

## Definition and empirical evidence

This source rule calls attention to a prominent border/accent around a rounded surface. A boundary can help group content or signal that a card is interactive, but an unexplained decorative accent may instead compete with the content or imply status/interaction that is not present.

## Underlying principle and potential harm

Assess what the boundary communicates, when it appears, and whether that meaning is intentional. Unnecessary accents can create competing emphasis and inconsistent component treatments; status communicated only through color can also be inaccessible. WCAG non-text contrast applies when visual information is needed to identify a UI component or state, not to every decorative border.

## Recognition signals

- A strong colored outline is applied to many unrelated rounded cards or elements without communicating a state, grouping, or interaction.
- Similar component roles use inconsistent accent treatments.
- The border appears in a default state but resembles a warning, selection, focus, or clickable affordance.
- Contrast is insufficient for a border that is needed to identify a component or state.

## Causes to investigate

Possible causes include one-off emphasis, a copied template style, an undocumented validation/state treatment, a third-party component default, or an approved brand update not reflected in the system.

## Exceptions and false positives

- Status/error/warning/success borders can be semantic and useful.
- A boundary may indicate selection, keyboard focus, grouping, or card clickability.
- A documented brand or component variant may intentionally use an accent.
- A border’s color alone does not determine whether it is decorative, functional, or accessible; inspect behavior and state.

## Correction guidance

Confirm the intended role with the design/component owner and inspect default, hover, focus, selected, error, and warning states. Remove an accidental accent or replace it with the semantic token and component state that communicates the intended meaning. For intentional status, selection, or focus, document the scope and retain redundant cues such as text, icon, shape, or behavior. Verify required non-text contrast and visible focus in the rendered interface.

## Independent research references

- [Nielsen Norman Group — Cards](https://www.nngroup.com/articles/cards-component) — card boundaries can group related content and signal clickability, but are not universally needed.
- [USWDS state color tokens](https://designsystem.digital.gov/design-tokens/color/state-tokens) — semantic status colors and border uses.
- [Atlassian design tokens](https://atlassian.design/components/tokens/all-tokens) — border tokens for selection, critical/caution states, and brand.
- [W3C WAI WCAG 2.2 non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) — 3:1 applies to visual information needed to identify UI components/states.
- [W3C WAI WCAG 2.2 use of color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) — color cannot be the sole visual cue for information/actions.