# Nested cards

**ID:** `nested-cards`  
**Catalog section:** Layout & Space  
**Official modality:** Source

## Definition and empirical evidence

The catalog signal is one visual card/container inside another. The arrangement can add unnecessary layers, but nested structure is not inherently wrong. Cards group content; each visible boundary should have a distinct job.

## Underlying principle and potential harm

Use boundaries only where they clarify meaningful groups. Redundant nested surfaces can obscure parent/child hierarchy, create visual clutter, and imply separation/interactivity that is not present. Visual container nesting is distinct from nested interactive controls, which can create separate keyboard/accessibility risks.

## Recognition signals

- Parent and child repeat equally prominent borders, fills, shadows, or rounded corners.
- The inner surface does not represent a distinct subject, state, data unit, or action.
- Simpler spacing, heading, or divider could convey the same grouping.
- A clickable parent contains a separate link/button; inspect interaction and focus semantics, not just nested appearance.

## Causes to investigate

Possible causes include reusing a card component for every grouping; adding a second boundary where whitespace/divider suffices; or putting independently actionable content inside a clickable parent without defining interaction boundaries.

## Exceptions and false positives

- A child card can group a meaningful task, selectable item, data unit, or independent action within a parent summary.
- A differentiated filled child within an outlined parent may clarify levels; equal outlines can be noisier.
- A card containing sections/text/controls is not automatically a second card.
- Salesforce documents nested cards for hierarchical related content.
- Do not confuse visual card nesting with nested interactive controls; keep action semantics valid and independently accessible.

## Correction guidance

Confirm what each card represents and which actions it supports. If both boundaries repeat the same grouping, keep one and express internal structure with spacing, a heading, or divider. If the child is a meaningful independent unit, preserve it but differentiate its role/weight. Keep interactive actions separate and valid in the DOM; test keyboard/assistive-technology behavior and responsive layouts.

## Independent research references

- [Material Design 3 — Cards](https://m3.material.io/components/cards/guidelines) — cards represent one subject; spacing/headings/dividers can replace unnecessary layers.
- [Nielsen Norman Group — Common Region](https://www.nngroup.com/articles/common-region/) — boundaries group content but can clutter when overused.
- [Salesforce Lightning — Cards](https://www.lightningdesignsystem.com/2e1ef8501/p/33cd77-cards) — documented hierarchical nested-card use.
- [Mews Design System — Card usage](https://www.mews.design/latest/components/card/usage-kW4eJuQo) — differentiated child treatment and simpler grouping alternatives.
- [Accessibility Insights — nested interactive](https://accessibilityinsights.io/info-examples/web/nested-interactive) — focusable descendants inside unsupported interactive parents.