# Detection: Label above a heading

## Catalog route

The official catalog classifies this as a **source** rule. A repeated small label is a candidate; editorial context and semantic markup determine whether it is redundant or useful.

## Candidate signals

1. Find text immediately preceding a heading in repeated cards/sections, using markup/component structure rather than typography alone.
2. Compare label meaning to the heading and nearby taxonomy; record examples where it restates rather than orients/categorizes.
3. Check that the actual content heading remains a semantic heading with a rank appropriate to the document structure.
4. Review visual prominence and repetition in the rendered page.

## False-positive controls

- Do not flag a category, content-type, or navigational/orientation label solely because it sits above a heading.
- Do not classify an element as a heading based only on font size or uppercase styling.
- Do not infer editorial redundancy from one isolated component without page context.

## Test disposition

Source candidate tests can cover generic repeated labels, useful category labels, and semantic heading markup. Visual/context review must decide whether context adds value; regex cannot establish editorial redundancy.