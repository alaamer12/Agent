# Badge above the main headline

**ID:** `hero-eyebrow-chip`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

This pattern concerns a compact chip/badge above the hero’s main headline. That placement can be a useful category, audience, announcement, or status cue. Keep it only when it contributes distinct context; the H1 remains the primary statement.

## Underlying principle and potential harm

Visual hierarchy should direct attention to the most important message. A vague or redundant chip adds weight without helping users understand the hero, competes with the headline, or implies a status that is not real. Badges are useful for concise status information, but should not serve as generic decorations or substitute for the main message.

## Recognition signals

- A badge’s label repeats the H1 or supplies no useful topic/category/audience/state information.
- Its color, size, or placement competes with the main headline.
- A launch/status label remains after the status expires or is applied inconsistently.
- Markup treats static metadata as a heading/control only to obtain styling; the actual H1 should preserve semantic hierarchy.
- Color conveys status without text or another cue.

## Causes to investigate

Possible causes include a hero template that adds a chip by default; marketing styling used to manufacture emphasis; an outdated launch/status marker; or taxonomy that repeats the headline without helping orientation.

## Exceptions and false positives

- A short category/section label can orient the reader to a broader content group.
- “Beta” or another concise status can be useful if accurate and consistently applied.
- A timely announcement may add context when the headline remains primary.
- A visually prominent badge may still communicate meaningful category/status; a subtle one can still be redundant. Judge the full page.
- Do not rely on color alone for status and do not replace a semantic H1 with the badge.

## Correction guidance

Confirm the label’s meaning with the content/design owner. Remove it if it adds no distinct information; otherwise keep it concise, accurate, and visually secondary to the H1. Apply status labels only while true, pair color with a text/shape cue, and preserve heading structure. Verify responsive hero hierarchy and any interactive behavior in context.

## Independent research references

- [HarvardSites Design System — Hero](https://designsystem.harvardsites.harvard.edu/hero) — eyebrow as topic category and a clear primary hero focus.
- [CFPB Design System — Headings](https://cfpb.github.io/design-system/foundation/headings) — eyebrow as optional orientation/context for an H1.
- [Ontario Design System — Badges](https://designsystem.ontario.ca/components/detail/badges.html) — concise, consistent status labels and limited use.
- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — competing treatments and attention hierarchy.
- [W3C WAI — Headings in page structure](https://www.w3.org/WAI/tutorials/page-structure/headings) — heading semantics and assistive-technology navigation.