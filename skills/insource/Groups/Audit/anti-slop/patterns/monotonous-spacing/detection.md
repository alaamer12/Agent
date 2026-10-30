# Detection: Monotonous spacing

## Catalog route

The official catalog classifies this as a **source** rule. Token/value repetition can locate candidates, but only rendered semantic grouping establishes whether rhythm is flat.

## Candidate signals

1. Inventory margins, padding, `gap`, and spacing tokens in a component/page.
2. Compare actual gaps between peer elements, related content, and distinct groups.
3. Inspect responsive reflow to see whether relationships change at narrower widths.
4. Check whether alignment, typography, dividers, or other cues compensate for similar gaps.

## False-positive controls

- Do not flag consistent spacing tokens or repeated peer-item gaps by themselves.
- Do not vary spacing arbitrarily to create novelty.
- Do not infer semantic grouping from source values alone.

## Test disposition

Source candidates can test one-gap-everywhere styles, but positive/negative classification needs rendered group context. Include consistent peer spacing with distinct group gaps and a layout whose groups remain clear through other cues. Regex cannot confirm.