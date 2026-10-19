# Detection: Justified text

## Catalog route

The official catalog classifies this as a **source** rule. `text-align: justify` is a candidate; inspect actual spacing and language/context.

## Candidate signals

1. Find justified text rules and identify affected elements, language, script, and role.
2. Render real paragraphs at narrow/wide widths and inspect word spacing, rivers, hyphenation, and font-loading changes.
3. Check applicable user presentation controls; WCAG SC 1.4.8 is Level AAA.

## False-positive controls

- Do not treat all justified text as unreadable or WCAG AA failure.
- Do not assume every language justifies by expanding word spaces.
- Do not infer actual rivers or readability from the CSS declaration alone.
- Consider legitimate fixed-layout print/editorial contexts.

## Test disposition

Source fixtures can locate justified paragraphs. Visual cases should include an awkward narrow-column rendering and a well-typeset editorial column in a supported language; assess presentation options separately. Regex cannot confirm readability.