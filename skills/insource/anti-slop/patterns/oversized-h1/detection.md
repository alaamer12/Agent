# Detection: Oversized hero headline

## Catalog route

The official catalog classifies this as a **source** rule. Source values can identify large display headlines; actual composition and task impact require rendered review.

## Candidate signals

1. Locate hero/page H1 roles and inspect computed font size, line height, width/measure, and text length.
2. Trace `clamp()`, breakpoints, forced breaks, and whitespace rules.
3. Render real copy at representative desktop/mobile sizes and 200% text resize; record crowding, clipping, overlap, and visibility of necessary context/actions.
4. Evaluate whether headline prominence serves its brand/editorial role and the page’s purpose.

## False-positive controls

- Do not set a universal px cutoff or treat above-the-fold placement as a requirement for every CTA.
- Do not flag large display type when the page intentionally centers on the headline and remains usable.
- A source value alone cannot establish composition or loss of content/functionality.

## Test disposition

Source candidates may be tested with large, long hero text versus responsive fluid typography. Visual tests should include deliberate editorial display treatments and a layout where necessary context/action becomes crowded or lost. Regex cannot confirm.