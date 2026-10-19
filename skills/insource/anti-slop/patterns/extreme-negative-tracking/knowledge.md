# Crushed letter spacing

**ID:** `extreme-negative-tracking`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

This pattern is a signal for unusually tight letter spacing. CSS `letter-spacing` adds to the font’s natural spacing; negative values compress it, with relative units scaling differently from fixed lengths. No universal negative-tracking cutoff is established. Severe-looking compression is a reason to inspect actual text, not proof by itself.

## Underlying principle and potential harm

Tracking is a typographic tone/hierarchy choice whose effect depends on the font, size, role, and writing system. Negative tracking is rarely used for body text because it can look squashed; if glyphs crowd together, recognition may become harder. Experimental findings vary by task and reader, so they do not establish one universal effect.

## Recognition signals

- Glyphs touch/merge, counters close, or words become difficult to distinguish at actual display size.
- Tight tracking affects sustained body/UI text or small labels rather than a short display role.
- The style was tuned for one font but appears crowded after web-font loading or fallback.
- A Latin-oriented value affects another script without checking shaping/spacing conventions.

## Causes to investigate

Possible causes include compressing a title to fit; extending a display style to body text; tuning one face but rendering another; or applying Latin-oriented spacing to other scripts without reviewing shaping.

## Exceptions and false positives

- Negative tracking can be an intentional optical choice for headlines, logotypes, or editorial display.
- Font metrics differ, so an identical CSS value may look different across faces.
- Script behavior differs; cursive connections and writing-system conventions matter.
- Mild negative tracking is not automatically illegible; non-negative tracking does not guarantee readability.
- WCAG text-spacing values test user overrides, not author defaults, and contain a language/script exception.

## Correction guidance

Confirm role, actual loaded face, text, and writing system. If characters crowd, reduce compression toward the font’s natural spacing and test before revising the whole system. Check fallback/loading behavior and multiple viewport/script cases. Ensure users can override text spacing without losing content/functionality.

## Independent research references

- [MDN `letter-spacing`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/letter-spacing) — negative values, natural spacing, and units.
- [W3C CSS Text Level 4](https://www.w3.org/TR/css-text-4/) — script-dependent spacing units and cursive handling.
- [Adobe — Adjust letter spacing](https://helpx.adobe.com/ph_fil/indesign/how-to/adjust-letter-spacing.html) — tracking as contextual design adjustment and risks in body text.
- [Korinth et al. — Letter spacing and reading rates](https://pmc.ncbi.nlm.nih.gov/articles/PMC7090332/) — experimental results vary by task/reader.
- [W3C WAI WCAG 2.2 text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) — user-override test, not a mandated author default.