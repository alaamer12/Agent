# Lessons from the DemoApp investigation (mistakes → rules)

Source: a long agent session diagnosing "tray icon vanishes after ~3 h hidden" in a .NET 10 / MAUI / WinUI 3, unpackaged,
single-file Windows app, plus a write-up of it and a later explanatory chat. The session ended well (root cause traced to
a mechanism, layered fix, watchdog verified) but contained avoidable detours and a few claims stated more firmly than the
evidence allowed. Those are the lessons. Read the "rules" column; the narrative is context.

## Contents
1. Case in one paragraph · 2. What went right (keep doing) · 3. Mistakes → rules · 4. Claims that were stronger than the evidence · 5. Explanation errors seen in the learning chat · 6. Reusable case fingerprint

## 1. Case in one paragraph
User: app hidden to tray; after ~3 h the tray icon is gone. Earlier "fixes" and postmortem docs existed; it kept happening.
Evidence: app logs ended 28 min before death; Event Log showed `0xC000027B` in `Microsoft.UI.Xaml.dll` with WER inner code
`0x8000000E`; two minidumps existed. Both pointed at WinUI releasing XAML transform objects. Symbolication (via a hand-built
dbghelp script) placed the 03-12 fail-fast on the **CLR finalizer thread** while the UI thread idled; reading MAUI source showed
every transform property update allocates new native `CompositeTransform`/`ScaleTransform` objects; hidden-window animations ran
~60 fps. Fix: reuse one transform per element, pause ambient animation while hidden, out-of-process watchdog with relaunch,
post-mortem forwarding of native crashes to Sentry, heartbeat log. A later "it vanished again!" scare was the rebuild script force-killing everything.

## 2. What went right (preserve)
- Read the artifacts before theorising; used three independent evidence channels (app log, Event Log/WER, dump).
- Noticed the **log-vs-death gap** and turned it into instrumentation (heartbeat).
- Pivoted from `dotnet-dump` to raw minidump parsing when SOS was structurally impossible.
- Cross-checked a **second dump** and found the same object family.
- Went to source (MAUI `TransformationExtensions.cs`) to find the allocator, not just the victim.
- Fixed in layers (remove cause / contain / observe) and unit-tested the pure decision logic.
- Investigated the "disappeared again" report with timestamps rather than assuming a crash, and found the self-inflicted kill.
- Reported what could NOT be done (404 on WinUI source) in the write-up.

## 3. Mistakes → rules
| # | What happened | Cost | Rule |
|---|---|---|---|
| 1 | Prior postmortems/fixes (e.g. a canvas-memory policy) were inherited and the bug recurred | Weeks of recurrence | Treat prior diagnoses as **hypotheses**. Ask "does that fix touch the mechanism seen in *this* dump?" before accepting it. |
| 2 | Event-only app log; last line 13:21, death 13:49 | No data about the lead-up | Compute **last sign of life vs time of death** (`build_timeline.py`). A gap > one heartbeat interval = instrumentation hole; say so. |
| 3 | Discovered tools one at a time (cdb? windbg? dotnet-dump?) | Several steps | Run `crash_triage.py` first: tools + artifact locations in one pass. |
| 4 | Kept trying `dotnet-dump`/SOS on a single-file app: `Failed to request ThreadStore` | 3 runs | **Two-strike rule**: when a tool fails for a *structural* reason (no DAC for bundled runtime), pivot; don't tweak flags. Know: single-file/self-contained/AOT ⇒ SOS usually unusable. |
| 5 | Path with a space broke a debugger command (`Program Files`) | 1 run | Quote or use 8.3 (`PROGRA~1`) paths in tool args; but see #4: a working path didn't fix the real blocker. |
| 6 | Parsing library returned an *enum*, script assumed int | 1 run | Print `type()`/`repr()` of unfamiliar fields first. (`mdparse.py` returns plain ints.) |
| 7 | Mini dump lacked the heap: stowed-exception pointer unreadable | Lost the inner error detail | Check **dump kind** immediately; if heap missing, enable full dumps for the next occurrence (`enable_crash_dumps.ps1`) and stop trying to read what isn't there. |
| 8 | Symbolication script had 5 bugs (precedence trap, DEFERRED loads, missing `symsrv.yes`, wrong `SizeOfStruct`, filtered host frames) + misleading stale `GetLastError` | ~6 runs | Use `win_symbolicate.py`. Always **inspect what a loader returned** (return value, not stale last-error); `ls` the symbol cache after the first run; never filter frames in the first pass. See `symbolication.md`. |
| 9 | A comment claimed flag `0x40` was "NO_PROMPTS"; it is `SYMOPT_LOAD_ANYTHING` (NO_PROMPTS is `0x80000`). The write-up repeated it | Wrong documentation | **Verify constants against the header**; don't trust code comments, including your own. |
| 10 | `2>$null` and `| Select-Object -First 45` hid diagnostics / broke the pipe, so a good run looked "Failed to run" | Confusion | Don't suppress stderr during diagnosis; don't truncate with a pipe that kills the producer - write to a file then `head`. |
| 11 | Heuristic stack **scan** output was read like a call stack | Misattributed frames | Grade every frame (`grade_frame`). Large/negative offsets and placeholder symbols (`_tls_end`, `` `string' ``) are noise. Call it a *scan*, never *the stack*. |
| 12 | Guessed raw GitHub URLs → 404 twice | 2 fetches | Never construct source URLs; search for the real path. If unreadable, **say so and downgrade the claim** (done well in the write-up). |
| 13 | Second dump (03-07) described as "same family" although its top frames are exception dispatch inside `UIAffinityReleaseQueue::DoCleanup` on a different thread | Over-claim | Compare dumps in a table (`minidump_report.py --compare`): code, fault module, **thread role**. Label *same / related / different* and justify. |
| 14 | Fix verified by unit tests + a simulated kill, but no multi-hour soak showing the **root-cause** fix worked | "Fixed" without proof | Report verification status per layer: **Observed / Reasoned / Untested**, and state the soak test + success criterion. |
| 15 | "It disappeared again!" - assumed crash | Alarm | Run the **false-alarm checklist** (`fix-verify-observe.md`): exit marker, new dump?, Event Log, heartbeat/watchdog silence together, build/script timestamps. A script was force-killing app+watchdog together. |
| 16 | Sentry "should have caught it" | User confusion | Ask **who can observe this class of death?** Managed SDKs can't see fail-fast; out-of-process observers (watchdog, WER, Crashpad) can. |
| 17 | Multi-file edits partially lost ("file corruption"), noticed later | Rework | After a batch edit, re-read/compile before building on it. |
| 18 | Noise (`Missing file: ''` first-chance) and cause mixed in the user's mind | Possible wrong credit | Separate **noise vs cause**: need temporal AND mechanistic link. Fix noise separately; say it is separate. |

## 4. Claims that were stronger than the evidence
- "`ctl::ComBase::ReleaseImpl` is the smoking-gun frame": its offset was `+0x1b2b55` (≈1.7 MB into a "function") → a nearest-public-symbol artifact.
  What *is* strong: the thread root and host frames (`FinalizerThreadStart`, `FinalizerThreadWorker`, `FinalizeAllObjects`) have small plausible offsets and a coherent chain, plus the finalizer thread id matching the exception thread.
- "Root cause proven": proven = *a finalizer-thread release of a XAML object triggers the fail-fast*. Inferred = *the transform churn from MAUI is what feeds the finalizer*. Reasoned from source reading + dump objects, not from a controlled reproduction.
- "Same family" for the older dump (see #13).
- "Fixed": unverified over hours; the heartbeat's `finalizePending` trend is the right instrument to prove it.
Phrase such claims as: *"Observed X. Inferred Y because Z. Not yet verified: W (test: ...)."*

## 5. Explanation errors seen in the learning chat (don't repeat)
- Called it a "race condition" - better: thread-affinity violation with nondeterministic timing (see concepts-primer §3).
- "Windows intercepts the call" - in this case WinUI's own native library detects the wrong-thread release.
- "SIGKILL is the equivalent of fail-fast" - no; SIGABRT/deliberate trap is. SIGKILL is an external kill.
- Treated "all platforms do STA" as true - the rule (thread affinity) is general, STA is a COM term, and enforcement differs.
- Invented a gloss for "fail-fast sandwich" as if standard; it was informal.
- Said MAUI on macOS/Linux "uses Blazor, GTK" - not accurate (Mac Catalyst/AppKit; Linux isn't officially supported). When unsure of a platform detail, say so or check.
- `.map.js` for source maps (it is `.js.map`); an invented expansion of `.ips`.
- "Windows saves a .dmp at the exact microsecond" - only if LocalDumps/WER is configured; contents depend on dump type.

## 6. Reusable case fingerprint (pattern to recognise)
*Symptom*: GUI app, hidden/idle for hours, vanishes with no error. *Signals*: Event Log 1000 with `0xC000027B`; WER P7 `8000000e`; fault in a framework native DLL; app log ends long before; dump's faulting thread is the **runtime finalizer** (GC/ARC), not the UI thread; stowed inner `E_ILLEGAL_METHOD_CALL`; periodic animation/polling producing short-lived native peers.
*Investigate*: object-allocation rate of native peers, finalizer backlog, whether animations run while hidden, third-party wrappers (CsWinRT, MAUI handlers).
*Fix family*: reuse/pool native peers; dispose on owning thread; stop ambient work when hidden; out-of-process watchdog; post-mortem upload.
