# Detection: Side-tab accent border

## Catalog route

The official catalog classifies this as a **source** rule. Source analysis may locate repeated thick side borders; it cannot determine whether a stripe has semantic meaning.

## Candidate signals

1. Find prominent left/right border styles on rounded cards and capture the declaration and component.
2. Compare repetition across same-role cards and correlate each stripe with a state, category, priority, or interaction.
3. Inspect state changes and accompanying text/icons; check whether the visual cue is consistent with behavior.
4. Evaluate rendered hierarchy and applicable non-text contrast only when the stripe carries required information.

## False-positive controls

- Do not flag alert, validation, selection, active, priority, category, or documented brand stripes solely for being colored.
- A repeating class or border declaration cannot establish visual prominence or user interpretation.
- If the stripe is meaningful, assess its semantics and redundant cues rather than removing it reflexively.

## Test disposition

Source candidates can be tested with repeated decorative card stripes and negative status/selection/priority fixtures. Visual/contextual review must decide whether meaning and hierarchy are appropriate; regex alone cannot confirm.