# Radius outside DESIGN.md

**ID:** `design-system-radius`  
**Catalog section:** Your design system  
**Official modality:** Source

## Definition and empirical evidence

The Impeccable catalog flags corner radii outside the scale documented in `DESIGN.md`; its suggested responses are to use a documented radius or add an intentional new shape to the system. The local source describes this as a consistency prompt, not a ban on exceptions.

## Underlying principle and potential harm

Maintain a coherent shape language while allowing component roles and variants that the system deliberately supports. Unreviewed one-off values can make equivalent surfaces look inconsistent and make broad shape changes harder. Large radii can also encroach on a component’s content or alter its silhouette; that is a rendered effect to assess, not a conclusion available from a number alone.

A radius is not itself an accessibility test. Interactive target-size and spacing criteria evaluate the rendered clickable area, including how rounded or clipped targets are treated.

## Recognition signals

- A CSS/custom-property/component radius value is absent from the documented scale.
- Similar component roles use multiple near-miss values that do not map to documented tokens.
- The computed radius materially changes a component’s shape or available content area across sizes/states.
- A radius interacts with clipping, focus outlines, or hit areas in a way that needs rendered inspection.

## Causes to investigate

Possible causes include an approved redesign not yet reflected in `DESIGN.md`; a hard-coded value bypassing an existing token; an absent component/size variant; a third-party component default; or an intentional but undocumented exception.

## Exceptions and false positives

- Component-specific settings can coexist with a shared scale; USWDS documents general radius utilities and component-level settings.
- Pills, circular controls, compact badges, and large surfaces may intentionally use different forms.
- A radius can be intentional brand language before documentation catches up.
- A value outside the scale does not prove visual harm, a smaller target, or failed accessibility. Conversely, a listed value does not guarantee good behavior in every component.

## Correction guidance

Confirm the current shape decision and compare `DESIGN.md`, component guidance, and the rendered component. For accidental drift, use the existing token or component setting appropriate to the role. For an intentional exception, document its role, scope, and variants and prefer a reusable token or component setting over repeated unexplained literals. Inspect content clipping, interactive hit area, and keyboard-focus visibility across relevant states and sizes.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — definition and suggested action for `Radius outside DESIGN.md`.
- [USWDS border utilities](https://designsystem.digital.gov/utilities/border) — shared radius utilities alongside component-specific settings.
- [Utah Design System shape guidance](https://designsystem.utah.gov/guidelinesStandards/designGuidelines/shapeRoundedCorners) — shape scale, aesthetic flexibility, and content-encroachment concern.
- [W3C WAI WCAG 2.2 target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — rendered target-size/spacing evaluation, including rounded or clipped targets.
- [Contentful design tokens](https://www.contentful.com/blog/design-token-system) — component-level tokens and reusable brand customization.