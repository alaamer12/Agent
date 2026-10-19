# Monotonous spacing

**ID:** `monotonous-spacing`  
**Catalog section:** Layout & Space  
**Official modality:** Source

## Definition and empirical evidence

The catalog describes equal gaps everywhere making it hard to tell what belongs together; related items should sit closer than separate groups. The principle is not “vary every gap”: design systems use consistent spacing scales to make components predictable.

## Underlying principle and potential harm

Use proximity to express semantic relationships. Keep peer elements consistently spaced, use tighter gaps within meaningful groups and larger separations between groups. If unrelated groups have the same gaps as their internal relationships, boundaries may be unclear and the page may feel flat or harder to scan.

## Recognition signals

- Label-to-control/title-to-description relationships are not closer than unrelated sections/actions.
- Different component groups appear equally connected because all gaps are indistinguishable.
- Responsive reflow changes adjacency and makes previously distinct groups appear connected.
- Repeated margin/padding/`gap` values or one shared layout token are source clues only; they do not establish semantics or visual rhythm.

## Causes to investigate

Possible causes include one spacing token applied to all nested relationships; component spacing copied without page context; spacing consistency without distinct group boundaries; or responsive layouts flattening groups.

## Exceptions and false positives

- Lists, tables, and equivalent controls benefit from predictable spacing among peers.
- Consistent component internals support a coherent system.
- Dense interfaces can use similar gaps when typography/alignment/other cues preserve hierarchy.
- Small optical adjustments can be appropriate; variation need not be random.
- Repeated values may be correct; many different values do not guarantee clarity.

## Correction guidance

Identify intended groups and hierarchy. Keep peer spacing consistent, tighten gaps within groups, and increase separation between distinct groups using the project’s scale. Make limited optical adjustments if system values do not produce visual balance. Verify the rendered page across relevant widths and realistic content.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — equal-gap signal and contextual-review caveat.
- [Nielsen Norman Group — Proximity Principle](https://www.nngroup.com/articles/gestalt-proximity/) — closeness/grouping, whitespace, and responsive adjacency.
- [Atlassian Design System — Spacing](https://atlassian.design/foundations/spacing) — spacing scales, peer consistency, hierarchy, and optical adjustment.
- [GC Design System — Spacing tokens](https://design-system.canada.ca/en/styles/spacing) — smaller gaps for related concepts and larger group boundaries.