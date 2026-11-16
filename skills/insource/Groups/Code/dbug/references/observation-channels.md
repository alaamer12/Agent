# Ways to see — pick the observation, not a favorite

Same loop, every stack; what changes is only how you look. In
cheapest-first order (ladder with costs: [`escalation-ladder.md`](escalation-ladder.md)):

| Way to see | Use for | Discipline |
|---|---|---|
| Error/traceback verbatim + duck-debug it | where and how it broke | capture word-for-word, never paraphrase |
| Browser console & DevTools (Sources, Network + **Initiator chain** = the network edition of a call stack, Watch/Call Stack/Scope panels, Request Blocking as ablation, storage) | client-side failures, what the UI received | arm the Network panel BEFORE reproducing — it records only while open; normalize repeats with empty-cache hard reload; prefer evaluating in page context over editing source → `frontend.md` |
| **Dev-only debug page/endpoint** returning JSON of live state (config, cache, pool stats, session, flags) — the Go `net/http/pprof` genre, self-describing index included | "what does the server actually BELIEVE right now?" | read its index first to discover what is observable instead of guessing names; some data is empty until the runtime opts in — **no data ≠ no problem**; gated to non-prod, no secrets, keep-or-delete deliberately → `instrumentation.md` |
| **Debug-mode app boot** — a registered entry point (flag, `debug`-style command, env switch, deep link) that skips human gates, opens a named page directly, freezes interact-to-change state, or seeds fixture data | sessions that burn tokens reproducing navigation instead of observing the bug | use only what the project's rulebook registers — an unlisted instrument does not exist; when gates dominate and none is registered, propose engineering a gated one, dead in production → `instrumentation.md` §Debugging engineering |
| Existing logs/metrics/traces | what happened over time | filter to failing request/correlation IDs only; aggregates (SLO, p99) characterize the symptom — per-request evidence locates the cause |
| Scoped gated logger — verbosity hot-switchable without restart where the platform offers it | is state correct *at this hop* | dev-only by construction, addressable per module; tag every temporary print with a unique token (`[DEBUG-a4f2]`) so cleanup is one grep → `instrumentation.md` |
| Scratch script in `.debugging/tmp/` (exit 0/1) | question the DB/env/service directly | deterministic verdict, redacted output, self-cleaning |
| Isolated harness — call the suspect function with controlled inputs | our code vs its callers vs its dependencies | → `backend.md`, `../examples/isolated-harness-polyglot.md` |
| Debugger channels: breakpoints; **tracepoints** (breakpoint that logs and keeps running); conditional & hit-count breakpoints; **data breakpoints** (write-watch — answers "when did this change?"); race detectors; profilers | exact values at a point; reaching a rare loop iteration; mutation timing; resource causality | prefer the non-perturbing variants first — breakpoints and chatty logs shift timing and can make a timing bug vanish; a *broken* condition expression still breaks — never read that as confirmation → `escalation-ladder.md` |
| OS/tool-level structured reports: live-process stack dumps, serialized crash reports (stack+registers+disassembly as machine-readable JSON), time-travel/replay recordings, allocation tags | when app channels are blind to the truth | demand/parse them from users and CI artifacts too — structured external reports have localized bugs before any maintainer repro existed |

**Channel rules** (what separates a fast session from a thrashing one):
establish the **black-box symptom first** (reproduce and probe from
outside, as a user sees it), then go white-box for causes; **read the
same boundary from both sides** — caller's view AND callee's view, one
vantage point cannot discriminate two hypotheses; if no existing
channel shows what you suspect, **create one** (tag the subsystem's
allocations/so that existing tools see it separately); for performance
defects **measure before fixing** — attribute time to a hop, never
optimize a guess.
