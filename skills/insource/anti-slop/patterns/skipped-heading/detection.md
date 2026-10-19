# Detection: Skipped heading level

## Catalog route

The official catalog classifies this as a **source** rule. A source rank jump is a candidate; inspect content hierarchy and the combined page outline.

## Candidate signals

1. Build an ordered heading list from the runtime DOM, including shared navigation/sidebar components.
2. Compare each rank with the section/subsection relationship it introduces.
3. Distinguish entering a deeper subsection from closing one and starting a new peer section.
4. Inspect separate fixed regions independently and confirm heading semantics in the accessibility tree.

## False-positive controls

- Do not flag every numerical jump without examining outline context.
- Do not equate visual size changes with semantic rank.
- Do not choose heading elements solely for default font size.
- Do not assume sectioning elements erase the semantic rank relationship.

## Test disposition

Source tests should include a true missing subsection rank, a valid jump that closes a deeper section, separate fixed regions, and CSS-styled semantic headings. The validator should report candidate outline evidence, not assert conformance from a regex sequence alone.