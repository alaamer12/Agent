# Font outside DESIGN.md

**ID:** `design-system-font`  
**Catalog section:** Your design system  
**Official modality:** Source

## Definition and empirical evidence

The Impeccable catalog flags a font used in the interface that is not included in the typography declared by `DESIGN.md`. The supplied local description clarifies the intended outcome: use the documented type system, or update `DESIGN.md` if the new font is an intentional brand addition. The source map links the official catalog evidence and the original local record.

## Underlying principle and potential harm

Keep implemented typography aligned with the current design-system decision, not necessarily with a single font family everywhere. Unrecorded family changes can make equivalent roles inconsistent or weaken a deliberate typographic voice and hierarchy. Font loading can also change what users see while a web font is pending; CSS `font-display` governs whether fallback text is shown, swapped, or remains in use.

This is not automatically an accessibility violation. WCAG text-spacing guidance addresses whether content and functionality survive user overrides; it does not require a particular font family.

## Recognition signals

- A declared `font-family`, font token, `@font-face`, inline style, or component-level typography choice is absent from the current `DESIGN.md` typography section.
- A component bypasses a shared type token with a new literal family.
- A rendered page uses a different computed face than the implementation or documentation suggests; verify after font loading, since a valid fallback can be the currently rendered face.
- Similar semantic roles use different families without a documented role, component, or brand rationale.

## Causes to investigate

Common explanations include stale design documentation after an approved rebrand; a copied or third-party component with independent typography; hard-coded styles bypassing shared tokens; or an intentional role-specific choice that was never recorded. These are hypotheses to verify, not conclusions from a match.

## Exceptions and false positives

- A `font-family` stack normally lists fallback families; those alternatives do not necessarily represent separate design choices.
- Heading, body, code, and interface roles may intentionally use different families. The U.S. Web Design System documents font-family tokens by role.
- A live brand change may be implemented before its design record is updated. Impeccable explicitly allows updating the record when the implementation reflects the approved decision.
- The source match cannot establish that documentation is current, that a family is actually rendered, or that a deviation is unintended.

## Correction guidance

First establish the current typography decision and compare `DESIGN.md`, tokens, component styles, font-face declarations, and the rendered computed face. If the deviation is accidental, replace the literal with the intended shared token/family and verify all affected roles and loading states. If intentional, document the family’s role, scope, fallback, and loading behavior in the maintained design-system record; keep the exception narrow and reviewable. Verify that user text-spacing overrides preserve content and functionality.

## Independent research references

- [Impeccable context files](https://impeccable.style/docs/context) — the rule’s comparison target and resolution when code and documentation disagree.
- [USWDS font-family tokens](https://designsystem.digital.gov/design-tokens/typesetting/font-family) — examples of role-based font tokens and customization.
- [MDN `font-family`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/font-family) — ordered family selection and generic fallback behavior.
- [MDN `font-display`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@font-face/font-display) — browser font-loading display and fallback behavior.
- [W3C WAI WCAG 2.2 text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) — text-spacing override criterion; it does not prescribe a font family.