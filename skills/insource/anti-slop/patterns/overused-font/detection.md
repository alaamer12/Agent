# Detection: Overused font

## Catalog route

The official catalog classifies this as a **source** rule, but popularity and brand-fit judgment are contextual; a font-name match is not a violation.

## Candidate signals

1. Inventory declared font families and compare with loaded/computed families.
2. Identify which text roles use each family and inspect language coverage, weights, fallbacks, and loading behavior.
3. Review representative screens against the product’s documented voice and intended audience; compare with relevant product/competitor context.
4. Evaluate type hierarchy and readability using the full system, not the family name alone.

## False-positive controls

- Do not flag Inter, Geist, system-ui, or another common family solely by name.
- Do not assume multiple typefaces are required for hierarchy.
- Do not recommend novelty as a substitute for product fit or accessibility checks.
- A declared family may not be the one actually rendered.

## Test disposition

Source can report common-family usage as a review candidate only when project context supports it; it cannot prove “overuse” or lack of brand fit. Visual calibration should include intentional neutral/system typography and a generic default that conflicts with an established voice.