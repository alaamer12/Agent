# JavaScript errors on load

**ID:** `script-error`  
**Catalog section:** General quality  
**Official modality:** Browser

## Definition and empirical evidence

This pattern concerns JavaScript/runtime errors observed during page load. A console Error-level entry may be a deliberate `console.error()`, browser-reported network/resource error, or uncaught exception; these are distinct events with different implications. A console error is evidence to investigate, not proof of user-visible failure.

## Underlying principle and potential harm

Establish whether the error interrupts a user flow or page capability. An uncaught synchronous error stops the current script; unhandled Promise rejection is reported separately. If initialization or interaction is interrupted, users may lose functionality or receive incomplete content. Severity should be based on affected feature/users/frequency, not console color/count alone.

## Recognition signals

- Browser reports an uncaught exception or unhandled rejection during load/interaction.
- A relevant network/script/API resource fails and the dependent feature does not recover.
- Stack/source information identifies first-party code versus extension/injected/third-party scripts.
- A clean console does not prove all functionality works; a single logged line does not prove failure.

## Causes to investigate

Possible causes include initialization/handler defects; failed script/API/resource requests; rejected async work without a suitable handler; or third-party widgets, extensions, or injected scripts.

## Exceptions and false positives

- An expected exception may be caught and recovered; the record can remain useful diagnostically.
- Explicit `console.error()` creates a console error message but is not necessarily an uncaught exception.
- Network/source-map/environment errors and extension noise are not automatically first-party defects.
- Third-party code can still be user-critical; verify its role before filtering.
- A console line alone cannot establish impact, root cause, or persistence.

## Correction guidance

Reproduce the load/action, inspect message source/stack and related requests, then verify the affected behavior. Fix the underlying defect/dependency; for expected recoverable failure, handle the specific condition, preserve a useful fallback/message, and report unexpected errors with diagnostic context. Avoid silently swallowing failures. Correlate telemetry with route/action/release and filter known irrelevant third-party reports narrowly while retaining inspectability.

## Independent research references

- [Chrome DevTools — Log messages in the Console](https://developer.chrome.com/docs/devtools/console/log) — developer logs versus browser/network/uncaught errors and source inspection.
- [MDN `Window:error`](https://developer.mozilla.org/en-US/docs/Web/API/Window/error_event) and [`unhandledrejection`](https://developer.mozilla.org/en-US/docs/Web/API/Window/unhandledrejection_event) — runtime/resource errors and Promise rejection reporting.
- [MDN `try...catch`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/try...catch) — catch/recovery behavior.
- [Sentry — JavaScript error filtering](https://docs.sentry.io/platforms/javascript/configuration/filtering/) — third-party/injected error attribution and filtering.