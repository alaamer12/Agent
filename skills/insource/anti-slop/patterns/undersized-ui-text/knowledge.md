# Tiny interface text

**ID:** `undersized-ui-text`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

The catalog flags interface text that appears unusually small in its actual context. “Tiny” is role- and display-dependent; WCAG does not impose one universal minimum authored pixel size. Small text alone does not prove a WCAG failure.

## Underlying principle and potential harm

Judge size by role, importance, legibility, contrast, and user control. Small labels or dense content can be harder to distinguish and scan; this may increase effort or error when users need that information. WCAG separately evaluates text contrast, resizing, reflow, and tolerance for user-applied spacing changes.

## Recognition signals

- Frequently used control labels or important supporting copy is difficult to read at normal rendered conditions.
- Compact sizing appears outside its intended caption/data role or becomes smaller at narrow breakpoints.
- Text clips, overlaps, disappears, or makes controls/content unusable at 200% resizing or text-spacing overrides.
- Contrast is poor for the rendered foreground/background pair; treat this as a separate issue from size.

## Causes to investigate

Possible causes include shrinking text to fit a constrained component; compact typography spreading beyond its intended role; responsive rules that reduce text on small screens; inheritance/overrides; or lack of testing with user scaling.

## Exceptions and false positives

- Captions, footnotes, photo credits, and specialized UI may intentionally be smaller when still legible.
- Dense tables/dashboards may use compact text; check practical reading, zoom, and spacing behavior.
- A small label may properly be subordinate to a heading/primary value.
- User vision, device, typeface, and viewing conditions vary; no single pixel size determines a violation.
- WCAG’s synchronized-media caption exception is not a blanket exemption for UI captions.

## Correction guidance

Establish the text’s role and hierarchy. If important content or a frequent label is hard to read, increase size/weight, improve contrast, or reduce competing content; prefer scalable sizing. If compact text is necessary, limit it to appropriate roles and test typical/narrow viewports, 200% resizing, reflow, and text-spacing overrides. Verify that nothing clips, overlaps, vanishes, or becomes unusable; assess contrast separately.

## Independent research references

- [W3C WAI WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) — resize, reflow, spacing, contrast outcomes; not a general authored-size minimum.
- [USWDS Typography](https://designsystem.digital.gov/components/typography) — practical type guidance, including limited smaller-text roles.
- [Nielsen Norman Group — Legibility, Readability, and Comprehension](https://www.nngroup.com/articles/legibility-readability-comprehension/) — user variation, legibility risk, and text-size control.