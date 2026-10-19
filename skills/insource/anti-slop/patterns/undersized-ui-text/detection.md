# Detection: Tiny interface text

## Catalog route

The official catalog classifies this as a **source** rule. Use source sizes to identify candidates, not a universal pixel threshold; actual legibility is a rendered/user-context judgment.

## Candidate signals

1. Inspect authored sizes/tokens for labels, controls, helper text, captions, and dense data roles.
2. Trace relative units, inherited styles, responsive queries, and user-adjustable settings before interpreting source values.
3. Record the role, computed size at relevant viewports, contrast pair, and any clipping/overlap evidence.
4. Test 200% text resizing, reflow, and user spacing overrides; keep contrast as a separate measured criterion.

## False-positive controls

- Do not invent a universal CSS px cutoff.
- Do not flag a readable caption/footnote/dense-data role solely because it is smaller than body text.
- Do not equate low size with low contrast or WCAG failure.
- Do not infer legibility from a source value without checking rendered size and user settings.

## Test disposition

Source-candidate fixtures should contrast an important label that becomes unusually small with legitimate captions/dense data and responsive relative sizing. Visual/runtime tests should verify actual readability, text scaling, and spacing behavior; a regex result cannot confirm harm.