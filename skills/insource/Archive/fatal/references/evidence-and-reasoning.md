# Evidence and reasoning: how to understand the problem without over-reading the data

Read before writing any conclusion. The goal is a causal chain in which every link is labelled by how it is known.

## Contents
1. Evidence grades · 2. Frame/symbol confidence · 3. The ledger · 4. Causal chain and alternatives · 5. Falsification tests
6. Observer coverage · 7. Multiple dumps · 8. Correlation vs cause (noise) · 9. Wording confidence · 10. Stop conditions

## 1. Evidence grades
| Grade | Meaning | Examples |
|---|---|---|
| **E1 Direct** | A tool-read field that states the fact | exception code, exit code, faulting thread id, module version, dump kind, saved-context IP |
| **E2 Corroborated** | Two independent artifacts agree | Event Log fault module = dump fault module; heartbeat stops = watchdog sees exit |
| **E3 Inferred** | Follows from E1/E2 plus documented behaviour | "finalizer thread raised it, therefore a managed-object release path" |
| **E4 Hypothesis** | Plausible, not yet tested | "transform churn feeds the finalizer" before a soak test |
| **E0 Absent** | Looked, found nothing - record *where* you looked | no dump; no event-log entry |
Never promote a grade by repetition. Ten E4s are not an E2.

## 2. Frame and symbol confidence
A dump's raw stack scan + PUBLIC symbols (exports only) is a *lead*. Rules:
- Offset > 0x10000, or wrapped (`+0xffffffffffffffff`) ⇒ the name is the nearest earlier export, not the function. 
- Placeholder/data symbols (`` `string' ``, `_tls_end`, `__ImageBase`, `_xmm`) ⇒ not a function.
- Frames from stale stack slots look real. Only an unwind (WinDbg `k`, gdb `bt`, `lldb bt`) proves call order.
- **Anchors** you may trust more: exception record, saved context IP per thread, the thread's *root* frames (thread-start thunks, `FinalizerThreadStart`, `BaseThreadInitThunk`), frames with small offsets in a coherent caller→callee chain, and names that match across two dumps.
- Private (app/own) symbols give line-level truth; public Microsoft symbols give module-level truth. Say which you have.
- Symbols must match the binary (timestamp/size, GUID+age, build-id, UUID). A wrong PDB is worse than none.

## 3. The ledger (use assets/evidence-ledger.md)
One row per fact: `ID | fact | grade | source (file:line / tool+args) | what it rules in/out`. Facts first, interpretation in a separate column.
Add rows for E0 (looked and found none). Keep the *time* of each fact; many cases are decided by ordering.

## 4. Causal chain and alternatives
Write the chain as numbered links from trigger → mechanism → symptom, each with a grade:
`(1) hidden window keeps animating [E1 log/heartbeat] → (2) each update allocates native objects [E3 source] → (3) finalizer releases them off-thread [E1 dump thread] → (4) WinUI fail-fasts [E1 exception] → (5) process gone, no handlers [E3 docs]`.
Then list **at least two alternative explanations** and what evidence separates them (e.g. external kill vs fail-fast: exit code, WER entry, dump presence).
The weakest link sets the confidence of the whole chain.

## 5. Falsification tests
For the leading hypothesis ask "what would I see if I'm wrong?" and go look:
- If it is a thread-affinity release, the faulting thread must NOT be the owner (UI) thread. (Check thread role.)
- If animation churn is the feeder, finalizer backlog should grow while hidden and stay flat with animations paused (heartbeat `finalizePending`).
- If an external kill, there is no WER entry and the exit code is `-1`/137 with a timestamp matching some script or user action.
- If memory exhaustion, working set trends up in the heartbeat before death.
A hypothesis that survived a test that could have killed it is worth more than five that merely fit.

## 6. Observer coverage
Ask for every missing signal: **who could have seen this?** In-process: language exception handlers, SDKs (blind to class A/B in native code, and to class E). Out-of-process: OS (WER/ReportArchive, kernel log), supervisor/watchdog, Crashpad helper. If no observer could see the event, absence of a record is **not** evidence that nothing happened. (Sentry .NET never saw the fail-fasts for exactly this reason.)

## 7. Multiple dumps
Table: file, time, code, faulting module+offset, faulting **thread role**, top anchors, build/version. Verdict = **same** only if code, module and thread role match; **related** if the mechanism family matches (state the shared element); **different** otherwise. Different dumps for one symptom may mean several bugs.

## 8. Correlation vs cause (noise)
A log line that appears "around" the death is a candidate, not a cause. Require (a) timing - it precedes in a plausible way, (b) mechanism - a path from it to the fatal event, (c) specificity - it is absent in healthy runs. First-chance exception spam fails (c) almost always. Fix noise separately and say that it is separate.

## 9. Wording confidence
- E1: "The exception record shows…" · E3: "This implies… because…" · E4: "Hypothesis: …; test: …".
- Final report always has **Proven / Inferred / Untested** sections. Say what you could not read (404, missing heap, no symbols).
- Never say "root cause confirmed" unless a change in the cause changed the outcome (before/after observation).

## 10. Stop conditions (don't over-investigate)
Stop analysing when: the chain's weakest link is E3 or better *and* the fix is cheap and reversible; or further reading requires an artifact that does not exist (then change instrumentation and wait). Escalate the two-strike rule: same structural failure twice ⇒ change approach.
