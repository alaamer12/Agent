# Detection: JavaScript errors on load

## Catalog route

The official catalog classifies this as a **browser** rule. Runtime errors must be reproduced and correlated with actual page behavior.

## Browser checks

1. Reproduce initial load and relevant interactions in a clean browser session.
2. Classify each message: explicit developer log, uncaught exception, unhandled rejection, failed resource/network request, or extension/third-party report.
3. Inspect source/stack/request details and identify first-party ownership.
4. Verify the affected feature/flow and whether recovery/fallback works; repeat across route/release where relevant.

## False-positive controls

- Do not treat every console “Error” as a user-facing failure.
- Do not filter third-party reports until their role and impact are understood.
- Do not assume no console errors means the interface is correct.

## Test disposition

Browser fixtures should include an uncaught load error that breaks a flow, an explicit diagnostic log with healthy behavior, a recovered exception/fallback, and third-party noise. Record impact separately from console presence.