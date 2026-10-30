# All-caps body text

**ID:** `all-caps-body`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

This pattern is a visual-review signal for body copy or other text-heavy content presented entirely in uppercase. Evidence is conditional: case effects vary with text size, readers, task, and role. Uppercase is not inherently a defect.

## Underlying principle and potential harm

Assess casing in the actual reading context, language, and audience. Extended capitalized copy may be harder for some readers to scan; this is a risk to test, not something proved by the uppercase style alone. Studies of very short, isolated text have found conditions where capitals can aid glance recognition, which should not be generalized to paragraphs.

CSS `text-transform` is presentational; semantic casing belongs in source text/markup. Case mapping can be language-specific, and not all writing systems use case.

## Recognition signals

- Sentences/paragraphs that require continuous reading appear entirely in capitals.
- CSS transforms text to uppercase beyond a short label/brand role.
- The underlying source text’s casing is incorrect or semantic content relies on a visual transformation.
- Text spacing/resize adaptations cause clipping or loss; this is separate from case choice.

## Causes to investigate

Possible causes include a component applying `uppercase` too broadly; using capitals in place of hierarchy/emphasis; extending a label convention to explanatory copy; or applying brand styling to content-heavy areas without testing reading context.

## Exceptions and false positives

- Short, isolated labels may work well in uppercase for glance recognition.
- Acronyms, conventional controls, wordmarks, and brief display treatments may intentionally use capitals.
- Preserve semantically correct source text and use CSS for presentation; check localized language/case rules.
- An uppercase screenshot alone does not prove readability failure, semantic error, or WCAG failure.

## Correction guidance

Confirm role and intended voice. If extended copy is hard to scan, use sentence/mixed case there and reserve capitals for concise labels or deliberate brand treatments. Keep semantic casing correct in the source and test localized rendering; involve representative readers/assistive technology when pronunciation or interpretation may be affected. Independently check text-spacing overrides for content loss.

## Independent research references

- [Arditi & Cho — Letter case and text legibility](https://pubmed.ncbi.nlm.nih.gov/17675131/) — case effects under specified size/vision conditions; not a universal outcome.
- [Nielsen Norman Group — Typography for Glanceable Reading](https://www.nngroup.com/articles/glanceable-fonts/) — uppercase in short isolated text and limits of generalizing to passages.
- [MDN `text-transform`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/text-transform) — CSS behavior, language mapping, and potential difficulty for some readers.
- [W3C CSS Text Level 3](https://www.w3.org/TR/css-text-3/) — transformation is presentational, not semantic.
- [W3C WAI WCAG 2.2 text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) — user spacing resilience separate from casing.