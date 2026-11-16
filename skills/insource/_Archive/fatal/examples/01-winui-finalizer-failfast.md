# Example 1 - Class A fail-fast on the finalizer thread (the DemoApp case, condensed)

**Prompt:** "App hidden in tray; after ~3 h the tray icon is gone. Fix it for real. Data is in %LOCALAPPDATA%\DemoApp; add logging if needed."

## Good run (what the skill makes the agent do)
1. `crash_triage.py --app DemoApp` → tools: only `dotnet`; artifacts: two `.dmp` in `CrashDumps`, WER ReportArchive with hundreds of folders; note "no cdb/WinDbg; single-file app ⇒ SOS likely unusable".
2. `build_timeline.py interaction-log.txt:app events.txt:os --death "2026-03-12 13:49:35"` → **28 min gap**: "death is not covered by instrumentation" (→ heartbeat later).
3. Classify: Event 1000 `0xc000027b` in `Microsoft.UI.Xaml.dll`, WER P7 `8000000e` ⇒ class A (stowed fail-fast), inner `E_ILLEGAL_METHOD_CALL`. [E1]
4. `minidump_report.py a.dmp b.dmp --compare`; faulting thread `0x38FC` ≠ UI thread `0x4700` (UI thread idle in message loop). [E1]
5. Stowed pointer not in dump ⇒ record "heap missing", run `enable_crash_dumps.ps1` advice; do not keep trying. [E0 + action]
6. `win_symbolicate.py --image-dir <bundle-cache>`; grade frames. Anchors: `FinalizerThreadStart/Worker/FinalizeAllObjects` (small offsets, coherent) [E1/E3]; `ReleaseImpl+0x1b2b55` flagged `(?)` - **not quoted as a function**.
7. Chain: hidden window animates (E1 heartbeat/log needed → E4 until heartbeat exists) → MAUI allocates native transforms per update (E3 from source) → finalizer releases off-thread (E1) → WinUI fail-fast (E1) → no handler (E3).
8. Second dump: different top frames (exception dispatch in `UIAffinityReleaseQueue::DoCleanup`, different thread) ⇒ verdict **related** (same object family), not "same".
9. Fix in three layers; verification table: unit tests Observed, simulated kill Observed, root-cause removal Reasoned, 3-6 h soak **Untested** (plan: heartbeat `finalizePending` bounded).
10. Report in `assets/report-template.md` with Proven/Inferred/Untested.

## Bad run (what to avoid - all happened)
Installed `dotnet-dump` and retried `setclrpath` three times; wrote a dump script that crashed on an enum; wrote a symbolizer with 5 bugs; filtered out the host frames that named the cause; quoted `ReleaseImpl` as "the" frame; called the second dump "same family" without a comparison; said "fixed" before any soak.

## Output sketch
> **Bottom line:** Class A fail-fast (`0xC000027B`) raised on the runtime's finalizer thread (Observed). Most likely feeder: per-frame native transform allocation by hidden animations (Inferred from MAUI source + dump object names). Fix applied in 3 layers; root-cause removal not yet soak-tested (Untested - 6 h hidden run, watch `finalizePending`).
