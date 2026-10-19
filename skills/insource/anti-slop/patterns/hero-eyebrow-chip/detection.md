# Detection: Badge above the main headline

## Catalog route

The official catalog classifies this as a **source** rule. Source structure can locate a chip above an H1; editorial meaning and status accuracy require context.

## Candidate signals

1. Locate hero/page H1 elements and preceding badge/chip/eyebrow components.
2. Record exact chip text, relation to H1, semantic role, source path, and repeated occurrences.
3. Determine whether it adds category, audience, announcement, or current state information not already in the headline.
4. Check its visual prominence, validity over time, and whether color has accompanying text/shape cues.

## False-positive controls

- Do not flag useful category/orientation labels or current status badges solely for placement.
- Do not equate pill shape, uppercase text, or color with redundancy.
- Preserve the actual semantic H1; a static badge is not a heading by appearance.

## Test disposition

Source candidates can cover redundant hero chips and negative fixtures for useful taxonomy/current status labels. Visual/contextual review must assess hierarchy and meaning; regex cannot confirm.