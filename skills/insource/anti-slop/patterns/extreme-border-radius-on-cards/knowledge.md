# Extreme border-radius on cards

**ID:** `extreme-border-radius-on-cards`  
**Catalog section:** Visual Details  
**Official modality:** Design review

## Definition and empirical evidence

The catalog warns that very large card corners can squeeze content and make every card look alike. The relevant assessment is a radius relative to card dimensions, content, role, and surrounding shape language; a large radius is not inherently wrong.

## Underlying principle and potential harm

Use a coherent shape vocabulary while choosing forms that suit each component. Curves that intrude into text/media/control space can create crowding, clipping, or awkward alignment. If all cards share an equally conspicuous rounded silhouette, role distinctions may become less clear and shape can compete with content. These are contextual risks, not properties proven by a numeric threshold.

## Visual recognition signals

- Text, controls, or media crowd a rounded corner or appear clipped/masked.
- Inner and outer curves appear unbalanced, especially in nested cards/media.
- Small cards are proportionally overwhelmed by the same radius used on large surfaces.
- Cards with distinct roles read as the same shape, or rounded corners compete with their content.

## Causes to investigate

Possible causes include a trendy radius applied as a blanket default; a pill-like treatment copied from buttons/badges to container cards; failure to evaluate different card sizes; or nested rounded surfaces whose curves and padding were not coordinated.

## Exceptions and false positives

- Pills/tags, selection chips, circles/avatars, and brand-defined rounded surfaces have intentional shapes.
- A spacious card can use a large radius successfully if content remains comfortable and hierarchy is clear.
- Cards in one component family can intentionally share a silhouette; repetition alone does not prove lost hierarchy.
- Nested shapes may need coordinated/concentric geometry rather than simply reducing the outer radius.
- There is no universal pixel cutoff for “extreme.”

## Correction guidance

Confirm intended card roles and the applicable platform/brand shape system. If corners crowd content or create unwanted sameness, use the established card token or a narrower component variant, then verify content insets, clipping, and grouping across sizes, states, and narrow layouts. If intentional, document the component scope and coordinate nested curves; keep pill/circular forms for roles they suit.

## Independent research references

- [Microsoft Fluent 2 — Shapes](https://fluent2.microsoft.design/shapes) — shape vocabulary and radius changes by size/role, with pill/circle examples.
- [Apple WWDC25 — Get to know the new design system](https://developer.apple.com/videos/play/wwdc2025/356) — proportional and nested shape relationships and balanced curves.
- [Nielsen Norman Group — Cards](https://www.nngroup.com/articles/cards-component) — cards group information and may contain varied content; shape depends on context.