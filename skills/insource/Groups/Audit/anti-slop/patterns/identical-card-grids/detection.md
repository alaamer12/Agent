# Detection: Identical card grids

## Catalog route

This is a **design-review** pattern. Repeated geometry is evidence to compare with content roles, not a violation by itself.

## Visual/contextual checks

1. Review the whole page and identify the user’s task and relationships among card contents.
2. Compare card size/emphasis with importance, content role, and information length.
3. Check whether corresponding fields/actions appear predictably and aid comparison.
4. Compare with a simpler list/table, headings with spacing, or a varied grid when appropriate.

## Structural clues (candidate only)

Repeated component templates, equal grid tracks, and uniform card styles can locate candidate regions; source structure cannot determine content comparability or hierarchy.

## False-positive controls

- Do not flag consistent grids of related/equivalent options solely for repetition.
- Do not vary cards merely for visual novelty; predictability can help scanning.
- Do not infer equal priority from equal geometry alone without understanding the content/task.

## Test disposition

Not regex-confirmable. Visual cases should include comparable collection cards, unrelated content forced into one template, and deliberate equal-choice tiles; compare scanability against simpler list/table layouts.