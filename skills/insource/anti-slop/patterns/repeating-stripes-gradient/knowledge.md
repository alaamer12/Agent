# Repeating-gradient stripes

**ID:** `repeating-stripes-gradient`  
**Catalog section:** Visual Details  
**Official modality:** Source

## Definition and empirical evidence

The Impeccable catalog flags repeating stripes used to fill otherwise empty space when they add visual noise, and recommends a plain surface or texture that belongs to the design. A CSS repeating gradient is a neutral way to tile color stops; the technique alone is not the problem.

## Underlying principle and potential harm

Give a pattern a clear visual or informational purpose and keep it subordinate to the content it supports. Dense, high-contrast, or pervasive stripes can compete with text and controls, obscure grouping, or make meaningful states less distinguishable. Accessibility depends on rendered text/background contrast and meaningful graphics/states; color must not be the only cue when information is conveyed.

## Recognition signals

- A repeating stripe texture fills a hero or empty surface without aligning to content, data, progress, selection, or state.
- Its density, contrast, or coverage draws attention away from controls/data or complicates grouping.
- Removing or softening the pattern does not reduce the information available or task performance.
- CSS `repeating-linear-gradient()` is a useful lead; images/SVGs can produce similar patterns and source text cannot establish prominence.

## Causes to investigate

Possible causes include fashionable texture added to occupy negative space; a decorative pattern retained from a template; or a functional data/state pattern reused outside the context that gave it meaning.

## Exceptions and false positives

- Striped/alternating table rows can help users follow rows; chart textures can distinguish data when color alone is insufficient.
- A stripe can encode progress, selection, status, or another defined value when mapping is consistent and perceivable.
- A restrained pattern can be an intentional brand texture.
- CSS matches or visual similarity do not resolve whether the pattern is functional or gratuitous.

## Correction guidance

Confirm the pattern’s purpose with its owner. If it merely fills space and competes with content, remove it or reduce area, density, and contrast; review representative screen sizes. If it encodes data or state, retain only the distinctions users need, document the mapping, and pair color with another cue where information is conveyed. Recheck text readability and applicable non-text contrast over the rendered background.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — repeating stripes as empty-space texture that can create noise.
- [MDN `repeating-linear-gradient()`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/gradient/repeating-linear-gradient) — neutral CSS mechanism that repeats color stops.
- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — attention and clutter from unnecessary backgrounds.
- [W3C WAI WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) — rendered contrast and color-only information constraints.
- [USWDS Table](https://designsystem.digital.gov/components/table/) — striped rows as a legitimate readability use.