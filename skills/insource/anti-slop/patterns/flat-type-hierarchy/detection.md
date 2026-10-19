# Detection: Flat type hierarchy

## Catalog route

The official catalog classifies this as a **source** rule. Size/weight source values can indicate a candidate; rendered hierarchy uses multiple cues and must be reviewed in context.

## Candidate signals

1. Identify semantic/display roles (page title, section heading, body, label) and their design tokens.
2. Inspect computed size, weight, spacing, color, and placement at representative routes and breakpoints.
3. Compare adjacent roles expected to differ; record which relationships become visually indistinguishable.
4. Separately inspect semantic heading order and text scaling; do not conflate markup structure with visual hierarchy.

## False-positive controls

- Do not use one universal type-size ratio or size threshold.
- Do not assume headings need large size jumps when other cues provide hierarchy.
- Do not treat a valid semantic outline as proof of visual clarity or a small size scale as proof of failure.

## Test disposition

Source candidate tests can find flat assigned type tokens in positive fixtures and distinguish a compact but role-differentiated system in negatives. Rendered visual tests should include strong hierarchy through non-size cues and genuinely indistinguishable roles; regex alone cannot confirm.