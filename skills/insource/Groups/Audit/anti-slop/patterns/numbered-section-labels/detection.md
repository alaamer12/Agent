# Detection: Tiny numbered section labels

## Catalog route

The official catalog classifies this as a **source** rule. Source text/counters can locate numbers near headings; their informational purpose needs page context.

## Candidate signals

1. Find numeric labels or CSS counters paired with repeated section headings.
2. Trace whether the numbers correspond to a real sequence, workflow stage, hierarchy, or cross-reference.
3. Compare numbering with actual section order and navigation; review the whole page and related pages.
4. Check semantic heading structure and ordered-list semantics separately from visual numbering.

## False-positive controls

- Do not flag real ordered steps, progress indicators, or meaningful editorial references solely for numbering.
- Do not treat visual counters as a substitute for heading/list semantics.
- Do not infer user confusion from one isolated numbered heading.

## Test disposition

Source candidate fixtures can compare numbered independent headings with real ordered steps/cross-references. Contextual visual review decides whether the numbering misleads or helps wayfinding; regex cannot confirm.