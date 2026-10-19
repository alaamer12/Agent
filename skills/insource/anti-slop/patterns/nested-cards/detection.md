# Detection: Nested cards

## Catalog route

The official catalog classifies this as a **source** rule. Nested component structure is a candidate; assess distinct grouping and interaction semantics.

## Candidate signals

1. Locate card-like components nested in other card-like components and record parent/child roles.
2. Compare borders/fills/shadows/radii and determine whether each boundary communicates a distinct group.
3. Check whether simpler spacing/headings/dividers preserve the same information architecture.
4. Separately inspect nested focusable controls, click targets, and keyboard/focus order.

## False-positive controls

- Do not flag meaningful nested task/data/action units solely because both use card components.
- Do not classify internal sections/controls as a second card without a distinct surface boundary.
- Do not equate visual nesting with nested-interactive accessibility defects.

## Test disposition

Source candidates can identify nested card components/styles. Tests should distinguish redundant identical boundaries from a meaningful, differentiated child card; interaction fixtures should separately cover valid/invalid nested actions. Regex cannot confirm hierarchy.