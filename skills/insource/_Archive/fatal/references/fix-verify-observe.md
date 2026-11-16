# Fix, verify, observe: from diagnosis to something that stays fixed

## Contents
1. Three-layer fix · 2. Heartbeat design · 3. Watchdog design · 4. Post-mortem forwarding · 5. Verification ladder and honest status
6. False-alarm checklist ("it disappeared again") · 7. Regression guards · 8. Report wording

## 1. Three layers (do all three when the cost of recurrence is high)
1. **Remove the cause** - stop producing the hazard (reuse native objects instead of allocating per frame; pause ambient work when hidden; release on the owner thread). This is the only layer that *fixes*.
2. **Contain** - an out-of-process supervisor relaunches after class A/B/D deaths so a residual bug costs seconds, not a silent outage.
3. **Observe** - make the next death bracketed, attributable and delivered (heartbeat, dumps, post-mortem upload). Without this you can't tell whether layer 1 worked.

## 2. Heartbeat design (what it should record)
Every N minutes (2 in the case) and on state transitions (foreground/background): uptime, bg state, working set / private / managed memory, GC gen0/1/2 counts, **finalizer backlog** (`GC.GetGCMemoryInfo().FinalizationPendingCount`), handles, threads. Append-only, flush each line, daily file. Purpose: bracket death to ≤ 1 interval and expose *trends* (growing finalizer backlog = native churn returning). A heartbeat that stops with the watchdog silent ⇒ suspect external kill.

## 3. Watchdog design
- Same exe in `--watchdog <pid>` mode (works portable/packaged). Spawn at primary start; guard single instance with a named mutex.
- **Intent signal**: primary creates a per-PID named event (`Local\App.CleanExit.<pid>`); set it on *every* deliberate exit path (tray Quit, window close, ProcessExit). Watchdog relaunches only if the process died with the event unset.
- Don't relaunch during Windows shutdown/logoff (`GetSystemMetrics(SM_SHUTTINGDOWN)`), when a debugger is attached, or after a **crash-loop limit** (e.g. 5 in 30 min). Delay (e.g. 4 s) so WER finishes writing the dump and singleton mutexes free.
- Keep decision logic in a **pure class** (inputs → Relaunch/StopCleanExit/StopSystemShutdown/StopCrashLoop) and unit-test it without killing processes.
- Relaunch silently (`--silent-start --supervised`) and don't spawn a second watchdog.
- Use `Local\` (session) names unless cross-session is required.

## 4. Post-mortem forwarding
Managed SDKs cannot capture class A/B deaths. The observer that *saw* the death (watchdog) writes `pending-crashes/<id>.json` (pid, exit code+name, uptime, dump path). On next launch, after the SDK is initialised and a settle delay, send one event per record with: tags (crash type, exit code, witnessed-by), fingerprint, dump (gzip; mind size limits), same-day logs; also sweep dumps no watchdog saw (cap count/age; dedupe by name|size|mtime). Configure disk caching of envelopes and session tracking so an instant kill still registers as an abnormal session. Order matters: the old reporter ran *before* the SDK initialised and looked for the wrong file name.

## 5. Verification ladder - state which rung you reached
| Rung | What | Claim you may make |
|---|---|---|
| 1 Build/lint/unit | decision logic tests, compile clean | "logic correct" |
| 2 Simulated failure | kill the process, watch relaunch + logs + pending record | "containment works" |
| 3 Targeted reproduction | force the hazard (e.g. run animations hidden with GC stress) before/after | "cause is plausibly removed" |
| 4 Soak | run ≥ the failure horizon (e.g. 3-6 h hidden), compare heartbeat trends to baseline | "fix holds in this environment" |
| 5 Field | releases + crash-free sessions in Sentry/Play/Organizer | "fixed" |
Report as **Observed / Reasoned / Untested** per layer, and give the soak test plus a success criterion (e.g. finalizer backlog bounded, no exit without marker over 6 h).

## 6. False-alarm checklist ("it disappeared again!")
1. Any new dump / WER ReportArchive entry / Event Log 1000-1001 *after* the fix build? (None ⇒ not a crash.)
2. Watchdog log: did it record a death? Heartbeat: do beats just stop? **Both silent together** ⇒ both processes were killed together.
3. Timestamps of: last heartbeat, exe rewrite time (rebuild), installer/updater runs, logoff/sleep, scripts that `Stop-Process`/`taskkill` (e.g. a release script freeing a file lock).
4. Exit code `-1`/`0xFFFFFFFF` vs `0xC…` status.
5. Is the Event Log crash you see from the *old* build (module path/version/timestamp)?
Only then say crash or not-crash.

## 7. Regression guards
Unit tests for policy; a startup log line stating build version/timestamp and watchdog attach; CI check that animation loops consult the "ambient motion suspended" flag; a lint/grep for per-frame allocation of UI objects; keep PDBs per release.

## 8. Report wording
"Layer 1 removes X (Reasoned: source + dump show Y; Untested: 6 h soak). Layer 2 tested by simulated kill (Observed: relaunched in 4 s, record written). Layer 3 active: `heartbeat.log` every 2 min; expect finalizePending to stay bounded. If the app disappears again, send `heartbeat.log`, `watchdog.log`, and any new dump."
