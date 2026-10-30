# Detection: Icon tile stacked above heading

## Catalog route

The official catalog classifies this as a **source** rule. Component structure may identify the motif, but whether the icon adds useful meaning is contextual.

## Candidate signals

1. Find icon/SVG/image components inside rounded or colored tiles adjacent to or preceding headings.
2. Compare repeated feature summaries and record icon role, heading text, tile prominence, and location.
3. Determine whether the icon adds a recognizable category/entity/function beyond the heading.
4. Check accessible semantics separately: decorative, informative, or functional.

## False-positive controls

- Do not flag icon tiles used for entity recognition, navigation, file type, or other distinct information solely due to placement.
- Do not assume familiar icons are universally understood; inspect visible labels and user context.
- Source structure cannot establish visual dominance or intended meaning.

## Test disposition

Source candidates should include repeated decorative feature tiles and negative fixtures with meaningful labeled icons and entity/navigation use. Visual review should calibrate prominence and redundancy; regex cannot confirm the pattern.