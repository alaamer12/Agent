# Font size outside DESIGN.md

**ID:** `design-system-font-size`  
**Catalog section:** Your design system  
**Official modality:** Source

## Definition and empirical evidence

The catalog rule flags authored font sizes outside the typography declared in `DESIGN.md`. A documented scale is a consistency and routing guide for type roles, not a requirement that every computed size be a fixed literal; the local registry description should be retained as source provenance.

## Underlying principle and potential harm

Use a type scale for stable roles while keeping intentional additions and responsive behavior documented. Unexplained one-off values can flatten or fragment hierarchy and make coordinated typography changes harder. Scale membership does not itself establish accessibility: text must remain usable when users enlarge it or override spacing.

## Recognition signals

- An authored size is outside the documented role scale and is not explained by a component or responsive variant.
- A role has several inconsistent sizes that do not map to the design system.
- Fluid or relative declarations (`clamp()`, `em`, `rem`, media/container queries) compute sizes that need evaluation across viewports and user settings.
- Text or controls clip, overlap, or lose content/functionality under 200% resizing or text-spacing overrides.

## Causes to investigate

Possible causes include an approved scale update not yet documented; a hard-coded size bypassing a token; a missing role/size/responsive variant; legacy or third-party component styles; or an intentional exception with no recorded rationale.

## Exceptions and false positives

- Display, caption, label, and data-dense roles may need different values; a system scale can permit project-specific additions.
- Fluid `clamp()` and breakpoint values can compute intermediate sizes rather than use a single scale stop.
- Relative or user-adjustable sizing may intentionally differ from a static reference.
- A stale `DESIGN.md` can make an approved change look like drift. Conversely, a documented size can still fail user resizing or spacing adaptations.

## Correction guidance

Confirm the intended text role and current scale with the design-system owner. Compare `DESIGN.md` with tokens, declarations, inheritance, breakpoints, and rendered results at relevant widths and zoom levels. Replace accidental values with the appropriate token; for intentional choices, document the role, scope, and responsive behavior and add a reusable token when warranted. Verify text can be resized to 200% without loss and tolerates text-spacing overrides.

## Independent research references

- [USWDS font-size tokens](https://designsystem.digital.gov/design-tokens/typesetting/font-size) — scale, customization, and additional system sizes.
- [MDN `clamp()`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/clamp) — bounded fluid sizes and scaling considerations.
- [W3C WAI WCAG 2.2 text resize](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) — 200% text resize and no-loss criterion.
- [W3C WAI WCAG 2.2 text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) — user-applied spacing overrides and content/functionality preservation.
- [MDN `font-size`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/font-size) — absolute/relative values and their behavior.