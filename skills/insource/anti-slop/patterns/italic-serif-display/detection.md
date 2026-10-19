# Detection: Italic serif display headline

## Catalog route

The official catalog classifies this as a **source** rule, but it is a style/context signal rather than a deterministic typeface ban.

## Candidate signals

1. Locate headline/display styles using serif families and italic/oblique styles.
2. Record the text role, length, size, line breaks, token, and affected pages/components.
3. Inspect rendered readability, hierarchy, brand/editorial fit, and how often the treatment is repeated.
4. Check contrast and text resizing separately from type classification.

## False-positive controls

- Do not flag serif or italic styling alone.
- Do not claim a universal serif legibility problem or WCAG failure from the font category.
- A static declaration cannot determine editorial purpose or rendered clarity.

## Test disposition

Source tests may locate serif+italic display declarations as candidates. Visual calibration should include an intentional editorial hero, an overused/illegible treatment, and a short italic emphasis. No regex result is a confirmation.