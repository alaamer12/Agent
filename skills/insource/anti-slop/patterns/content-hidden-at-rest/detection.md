# Detection: Content stuck waiting to appear

## Catalog route

The official catalog classifies this as a **browser** rule. Runtime state and user paths are required; hidden content may be intentional.

## Browser checks

1. Test cold load, slow connection, script disabled/failure, and relevant scroll/interaction triggers.
2. Observe whether content is loading, intentionally disclosed, or permanently stuck.
3. Compare visual visibility with DOM/accessibility-tree presence, focusability, `hidden`, `display`, `visibility`, `opacity`, `inert`, and `aria-hidden`.
4. Verify loading resolves to content or a clear error/retry; test disclosures by keyboard and check expanded state.
5. Review reduced-motion behavior and whether content remains available if animation never runs.

## False-positive controls

- Do not flag clearly labeled, user-controlled disclosures solely because initially collapsed.
- Do not treat a temporary skeleton as failure while the request is pending.
- Do not use DOM presence as proof that content is visible or accessible.
- Do not use `aria-hidden` to hide visible content or opacity alone to make focusable content unavailable.

## Test disposition

Browser fixtures should include a stuck hidden panel, a resolving loading skeleton, an accessible disclosure, and a hidden/visible state mismatch. Regex is not applicable to confirmation.