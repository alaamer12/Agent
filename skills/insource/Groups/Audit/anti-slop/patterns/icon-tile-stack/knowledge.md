# Icon tile stacked above heading

**ID:** `icon-tile-stack`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

The catalog flags a rounded-square icon tile placed above a heading as a familiar feature-card motif and suggests moving the icon beside the heading or removing its container. The arrangement alone does not prove that the icon is unnecessary. An icon tile can help users scan and recognize a product entity or resource.

## Underlying principle and potential harm

Judge an icon by its job: recognition, orientation, category, or another distinct meaning. A large tile can draw attention away from its heading, add visual weight without information, or make repeated feature blocks formulaic. Icons can also be ambiguous; visible text may be needed to clarify meaning.

## Recognition signals

- A rounded, colored tile consistently appears above feature headings without conveying a distinct concept.
- The icon merely repeats what the heading already states or is not recognizable in context.
- Tile size/color makes the decoration more prominent than the feature it introduces.
- Repeated cards use the same visual formula without improving scanability.

## Causes to investigate

Possible causes include applying a familiar feature-card template by default; filling empty space; creating emphasis without semantic role; or reusing a product/category badge where the heading already supplies that information.

## Exceptions and false positives

- An icon tile can aid recognition of a product/entity/resource or page type.
- Familiar, labeled icons can support navigation/wayfinding.
- An informative icon may add meaning beyond the heading (such as file type or product family).
- A decorative tile may be part of a deliberate brand style; assess page hierarchy rather than flagging its presence.
- Decorative images can be hidden from assistive technology if adjacent text already provides their information; functional/informative icons need an appropriate accessible name/alternative.

## Correction guidance

Establish the icon’s role. Preserve it when it contributes recognition or wayfinding, keep the heading primary, and pair ambiguous imagery with visible text. If it is redundant ornament, remove the tile, reduce its prominence, or place a meaningful icon beside the heading. Use decorative versus informative accessibility semantics appropriately and recheck repeated instances to avoid removing a useful scanning cue.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop#rule-icon-tile-stack) — the stacked tile signal and suggested alternatives.
- [HashiCorp Helios Icon Tile](https://helios.hashicorp.design/components/icon-tile) — legitimate product/entity recognition and decorative/accessibility behavior.
- [Nielsen Norman Group — Icon Usability](https://www.nngroup.com/articles/icon-usability) — icon ambiguity, labels, and contextual testing.
- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — intended attention hierarchy and clutter.
- [W3C WAI — Functional Images](https://www.w3.org/WAI/tutorials/images/functional) — decorative, informative, and functional image alternatives.