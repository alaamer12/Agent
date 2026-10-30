# Detection: Rough SVG illustrations

## Catalog route

This is a **design-review** pattern; it cannot be confirmed by regex or by SVG syntax/path complexity.

## Visual/contextual checks

1. Review the image at its actual size and in the page; identify intended message, audience, and role.
2. Compare line quality, silhouette, palette, detail, and rendering defects with the product’s art direction and related assets.
3. Distinguish intentional texture/irregularity from accidental gaps, overlaps, clipping, or unfinished details.
4. Assess whether decoration overpowers information and whether the style matches product tone.

## Structural/semantic checks (separate from visual quality)

Locate inline/embedded SVGs and establish whether each is informative or decorative. Check accessible names/alternatives for meaningful images and ensure decorative art does not create redundant accessibility output. These checks do not determine craftsmanship.

## False-positive controls

- Do not equate hand-drawn or irregular with careless.
- Do not infer quality from SVG path count, hand-authored source, or file extension.
- Do not treat semantic accessibility defects as evidence of visual roughness, or vice versa.

## Test disposition

Not regex-confirmable. Visual calibration should include obviously unfinished art, intentionally hand-drawn/brand-consistent work, a placeholder, and SVGs whose accessibility semantics differ while their visual quality remains constant.