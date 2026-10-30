# Side-tab accent border

**ID:** `side-tab`  
**Catalog section:** Visual Details  
**Official modality:** Source

## Definition and empirical evidence

The catalog describes a thick colored stripe on one side of ordinary rounded cards when it marks nothing useful. A stripe may be decoration, but it can also convey a real state or category; appearance alone does not decide which.

## Underlying principle and potential harm

Reserve conspicuous emphasis for information or states users need to notice, and give a repeated stripe a clear, consistent role. Applying it indiscriminately can compete with content and weaken hierarchy. If users read it as urgency, status, or selection when none exists, it can mislead; if it conveys meaning, color alone may not be enough for access.

## Recognition signals

- A thick, high-contrast side stripe appears on many otherwise ordinary cards.
- Stripe color/placement is not tied to a documented status, selected/active state, priority, interaction, or category.
- Cards of the same role receive inconsistent treatment, or state styling persists where the state is absent.
- The stripe is a more prominent cue than the card’s content or actual task importance.

## Causes to investigate

Possible causes include generic embellishment applied to every card; a former status indicator whose meaning changed; copied component styling; or state-specific treatment applied outside that state.

## Exceptions and false positives

- Warning, error, success, or other status stripes can be semantic.
- Selection/active-state borders and priority/category indicators may be intentional when their meaning is consistent.
- A stripe may be part of a documented visual identity.
- Where the border identifies a component/state, inspect applicable non-text contrast; where it conveys information, do not rely on color alone.
- Do not claim clutter or accessibility failure based solely on its existence.

## Correction guidance

Confirm the stripe’s role with the design/component owner. If it is ornament that competes with more important content, remove it or lower its weight and use the established card treatment. If it communicates status, selection, priority, or category, apply it only where appropriate, use the semantic token, and pair color with text, icon, shape, or behavior as needed. Verify contrast for meaningful cues and review representative cards/states.

## Independent research references

- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/) — emphasis/grouping and the risk of excessive borders/backgrounds.
- [USWDS state color tokens](https://designsystem.digital.gov/design-tokens/color/state-tokens) — semantic state colors including border use.
- [GitLab Pajamas design tokens](https://design.gitlab.com/product-foundations/design-tokens) — status and selected-action border tokens across interaction states.
- [Section 508 — Making color usage accessible](https://www.section508.gov/create/making-color-usage-accessible) — WCAG color-only and non-text contrast requirements and scope.