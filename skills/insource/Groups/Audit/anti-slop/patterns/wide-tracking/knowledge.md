# Wide letter spacing on body text

**ID:** `wide-tracking`  
**Catalog section:** General quality  
**Official modality:** Source

## Definition and empirical evidence

This pattern concerns positive `letter-spacing` broadly applied to continuous body copy. CSS adds the specified spacing to a font’s natural spacing; excessive tracking can make letters appear disconnected and words harder to read. Legibility depends on typeface, script, size, and role, so no universal authoring threshold applies.

## Underlying principle and potential harm

Spacing should fit the content role and writing system. In sustained paragraphs, widely separated letters may weaken word grouping and interrupt reading flow. WCAG text spacing concerns whether users can override author spacing without content/functionality loss; it does not prescribe normal/default tracking.

## Recognition signals

- Letter gaps approach word gaps or words appear fragmented at the rendered size.
- Wide tracking affects long paragraphs rather than short labels/headings.
- Font loading, viewport, zoom, or localization changes how the spacing appears.
- Cursive scripts may need special handling to preserve joining; do not apply Latin assumptions.

## Causes to investigate

Possible causes include a display/uppercase-label style inherited by paragraphs; tracking compensating for one font/layout without checking alternatives; or a short-label treatment applied to a content block.

## Exceptions and false positives

- Tracking can be intentional for short headings, uppercase labels, or brand display.
- Design systems may use role-specific spacing, including looser tracking in some small-cap contexts.
- Writing-system conventions and shaping differ; inspect actual supported languages.
- Positive tracking alone does not prove unreadability; normal tracking does not guarantee legibility.
- WCAG’s `0.12em` letter-spacing value is part of a user-override test, not an author default.

## Correction guidance

Confirm the affected content is continuous body text. If wide tracking fragments words, remove or reduce the broad rule (often restoring `normal`) and scope intentional spacing to its heading/label/brand role. Recheck the actual font, responsive sizes, supported scripts, and text-spacing override for content loss.

## Independent research references

- [MDN `letter-spacing`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/letter-spacing) — added spacing, natural font spacing, and legibility dependence.
- [W3C WAI WCAG 2.2 text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) — user-override/no-loss test and author-default distinction.
- [W3C CSS Text Level 3 — Cursive scripts](https://www.w3.org/TR/css-text-3/#letter-spacing) — script-sensitive handling and joined forms.
- [USWDS Typography](https://designsystem.digital.gov/components/typography) — role-specific tracking, including short labels and display text.