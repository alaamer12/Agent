# Overused font

**ID:** `overused-font`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

The catalog uses familiar default typefaces such as Inter and Geist as prompts to review whether unrelated products are becoming visually interchangeable. It frames this as a contextual design judgment, not an automatic failure. A common font may be neutral, useful, and well matched to a product.

## Underlying principle and potential harm

Typeface choice contributes to product tone, but familiarity alone establishes neither harm nor genericness. An unconsidered default can make a product’s voice less distinctive; a font that performs poorly in its actual role, size, language, or rendering context can impair reading. WCAG evaluates text contrast/resizing/spacing outcomes, not a mandatory typeface.

## Recognition signals

- A common family is used without a clear relationship to the product’s audience, voice, language, and text roles.
- The whole type system remains interchangeable despite the product’s intended distinctive character.
- The declared `font-family` is assumed to be the rendered face; verify loaded/computed fonts and fallbacks.
- Language coverage, available weights, or actual text rendering does not support the product’s content.

## Causes to investigate

Possible causes include selecting a starter-template default without a rationale; prioritizing convenient familiarity over brand expression; or assuming the same font choice works for every audience, role, and script.

## Exceptions and false positives

- Neutral, familiar fonts can suit products that prioritize unobtrusive, clear interface text.
- System fonts may be a deliberate platform-native choice; validate across operating systems and scripts.
- A coherent single-family system can create hierarchy through size, weight, spacing, and layout; Impeccable notes that one family can work well across a page.
- Shared family names do not make products’ typography or brand expression identical.
- Popularity, CSS name, or serif/sans category alone is not an accessibility test.

## Correction guidance

Establish product voice, audience, content/interface roles, languages, and platform constraints. Assess the actual rendered face and representative screens/copy. If the current default lacks intended character, explore alternatives and verify readability, hierarchy, script coverage, licensing, loading, and fallbacks. If the common/system font is deliberate and works, retain and document the decision rather than changing it for novelty. Separately test contrast, 200% text resize, and user spacing overrides.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — common fonts as contextual signals and possibility of one family with good hierarchy.
- [Nielsen Norman Group — Pairing Typefaces](https://www.nngroup.com/articles/pairing-typefaces) — typeface relationship to tone, role, readability, and consistent guidance.
- [USWDS Typography](https://designsystem.digital.gov/components/typography) — intentionally neutral interface typography and intended uses.
- [MDN `font-family`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/font-family) — ordered fallback and `system-ui` caveats.
- [W3C WAI WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) — measurable text contrast, resize, and spacing outcomes.