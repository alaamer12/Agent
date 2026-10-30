# Ultra Mode: Worked Examples

These show the *shape* of ultra-mode reasoning. The specific tools named are illustrative and may be stale: verify every pick via Step 0 before stating it, and never reuse an example's tools without a trace from the current system.

## Example 1: Narrow answer vs. covered answer

**System:** a server-rendered web application that calls two third-party HTTP APIs and accepts user-submitted forms.

**Narrow (what ultra mode exists to prevent):** names the primary framework, maybe one validation library, and stops.

**Covered:**

| Concern | Trace | Detail for this system |
|---|---|---|
| Input validation | User-submitted forms cross a trust boundary | One set of rules shared by the form layer and the server so they cannot drift; the validation result feeds the page's error display |
| Retrying outbound calls | Both third-party APIs are called at request time and fail transiently | Retry only idempotent calls and transient failures, cap the attempts, add jitter; non-idempotent calls are not retried unless an idempotency key exists |
| Timeouts | Page rendering waits on those calls, so a slow upstream stalls the user | A budget per call below the page's total budget, so retries cannot push the page past it |
| Rendering model | A server-rendering requirement | The primary choice, decided by the requirements |

The timeout and retry rows depend on each other: retry attempts must fit inside the timeout budget. Fit between tools is part of the answer.

**Not needed here:** rate limiting of inbound traffic (single-tenant, behind an authenticated gateway). **Deferred:** a shared cache, until the upstream APIs show repeated identical lookups.

How this resolves to concrete tools differs by ecosystem. See `examples/polyglot-walkthrough.md`, which runs this same system through TypeScript, C#, Python, Go, and Rust.

## Example 2: Same concern, different verdicts by system

**Concern:** metrics and monitoring.

- **Small internal tool, one server, a handful of users.** Trace is weak: the failure mode is "someone tells us it is broken." Verdict: *Not needed here*, with structured logs from whatever the platform provides as the lightweight answer.
- **High-traffic API with an availability target.** Trace is strong: the availability target requires detecting latency and error-rate regressions. Verdict: *Needed*. Here a metrics stack (or the ecosystem's standard instrumentation toolkit) may be right, with detail: which signals (request rate, error rate, latency distribution), what alert thresholds follow from the stated target, and who operates it.

The tool is never the answer on its own; the trace and the detail are.

## Example 3: The inflated anti-example

For a static site with one contact form, an answer that adds a message queue, a metrics stack, a feature-flag service, and a caching layer has inflated. Each entry fails the trace rule: nothing in the system creates the need. The correct ultra answer here is short: form validation, spam protection on the form, and a clear *Not needed here* list.

## Example 4: Deferred done right

**Concern:** background job processing, for a product that currently sends one email per signup.

Verdict: *Deferred*. Reason tied to the system: volume is a few emails a day and sending inline is acceptable. Trigger: adopt a queue when sends must be retried independently of the request, or when volume or a second job type appears. Not an acceptable reason: "we can write a cron job ourselves."

## Example 5: Consolidated vs. separate

Continuing Example 1, a topic search in the user's ecosystem for tools covering retries and timeouts together surfaces a consolidated tool (a resilience bundle, an effect-system toolkit, or a middleware stack, depending on the ecosystem; see `examples/polyglot-walkthrough.md`).

- If one concern outside that group is **critical-depth** (for instance validation with many complex shared schemas), use a hybrid: the consolidated tool for retries, timeouts, and error handling, with a dedicated specialist for the critical concern, since specialists are often deeper on their one job (verify for the actual candidates).
- If every concern in the group is **commodity** and the team is open to the consolidated tool's model, fully consolidated can beat several independent libraries plus glue, and gives one error model.
- If the team is small and the codebase conventional, separate small libraries may win because the consolidated tool's paradigm would cost more than the problem is worth.

Whichever way it goes, the answer states which concern was critical, what the paradigm cost is, and why that tipped the call, based on a fresh check of the consolidated tool's real coverage rather than its marketing.

## Example 6: Fewer features can be the better fit

A back-office tool with about fifty pages, all behind authentication, built by a small team. The ecosystem offers a richer application model that adds server rendering, convention-based routing, and deployment conventions on top of a lighter one. Usage test: nothing in the requirements needs server rendering or search visibility, and the common operation is "add another page." The lighter model makes that operation trivial, and the richer model's extra scope would be carried unused. Verdict: the lighter model, with the trigger for revisiting named (for example, a public, indexable section appearing). Choosing the larger tool because it is more capable would have been the error.

This holds across ecosystems: in a JavaScript stack it is a UI framework with a router versus a meta-framework; in Python a micro-framework plus libraries versus a batteries-included framework; in .NET the choice among its server-rendered, component-based, and cross-platform UI models by which model's distinctive capabilities the app would actually use. The reasoning is identical; only the names change.
