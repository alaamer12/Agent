# Windows fail-fast / native crash playbook

Use for any Windows process that vanished. Companion scripts: `crash_triage.py`, `minidump_report.py`, `win_symbolicate.py`, `decode_status.py`, `enable_crash_dumps.ps1`.

## Contents
1. Triage ladder · 2. Reading Event Log 1000/1001/1026 · 3. Status codes that matter · 4. Fail-fast mechanisms · 5. Stowed exceptions
6. WinUI/Windows App SDK specifics · 7. Dump analysis ladder and tool failure modes · 8. Enabling dumps · 9. Searching the web well

## 1. Triage ladder
1. Class? Exit code (watchdog/parent), Event Log, presence of dump. `-1`/`0xFFFFFFFF` with no WER entry ⇒ external kill (class E).
2. Event Log Application 1000/1001 for exact code, module, offset, module path/version.
3. `Report.wer` in WER ReportArchive (UTF-16): `Sig[]`, `IsFatal`, `LoadedModule[]`.
4. Dump: `minidump_report.py` → thread roles → `win_symbolicate.py`.
5. Source/issue research (§9). 6. Fix + instrument (`fix-verify-observe.md`).

## 2. Event Log fields
- **Application Error (1000)**: *Faulting application/module name+version+timestamp*, *Exception code*, *Fault offset*, *Faulting process id*, *module path*. The module path tells you **which copy** ran (e.g. a bundle-extraction cache vs install folder).
- **Windows Error Reporting (1001)**: bucket + `P1..P10` signature; P7 is often the exception code - and can differ from 1000's. In the case study 1000 said `0xc000027b` while 1001's P7 said `8000000e`: the **inner stowed HRESULT** versus the outer fail-fast code. Different layers, same crash.
- **.NET Runtime (1026)**: unhandled managed exception with managed stack (class C).
- Query: `Get-WinEvent -FilterHashtable @{LogName='Application';StartTime=(Get-Date).AddHours(-6)} | ? { $_.Id -in 1000,1001,1002,1026 }`.

## 3. Codes that matter (full table: `assets/status_codes.json`, `decode_status.py`)
`0xC0000005` access violation (class B) · `0xC0000409` __fastfail, read Params[0] (A) · `0xC000027B` stowed/WinRT fail-fast (A) · `0xC0000374` heap corruption (A, cause is earlier) · `0xC00000FD` stack overflow (D) · `0xE0434352` unhandled .NET (C) · `0xC0000135` DLL missing (H) · exit `-1` external kill (E).

## 4. Fail-fast mechanisms (why handlers don't run)
`__fastfail` / `RaiseFailFastException` / `RoFailFastWithErrorContext` end the process via the kernel/WER path **without unwinding**. `try/catch`, `AppDomain.UnhandledException`, `Application.UnhandledException`, SEH filters and `SetUnhandledExceptionFilter` don't run. WER (if configured) writes the dump. Only out-of-process observers can act.

## 5. Stowed exceptions (`0xC000027B`)
Exception record: `Params[0]` → array of pointers to `STOWED_EXCEPTION_INFORMATION_V2` (signature `SE02`), `Params[1]` = count. Each: HRESULT, form (1 = stack trace of return addresses, 2 = nested exception), thread id, frames. `minidump_report.py` decodes them **when the heap is in the dump**. Common inner HRESULTs: `E_ILLEGAL_METHOD_CALL 0x8000000E`, `RPC_E_WRONG_THREAD 0x8001010E`, `RO_E_CLOSED 0x80000013`, `E_UNEXPECTED 0x8000FFFF`. The **thread that raised it** matters more than the HRESULT: UI thread = a bad call you made; finalizer/worker thread = a bad release or off-thread touch.

## 6. WinUI / Windows App SDK specifics
- Native objects (`DependencyObject`s: transforms, brushes, images) are COM objects with UI-thread affinity; WinUI queues cross-thread releases (a UI-affinity release queue). When the queue cannot be serviced (dispatcher gone/busy/torn down) the release can fail-fast. Heavy churn of short-lived native objects raises the odds.
- MAUI's Windows transform mapping creates new `ScaleTransform`/`CompositeTransform` per property change (observed from source reading in the case). Animations driving `Rotation/Scale/Translation` at frame rate while the window is hidden multiply that cost.
- Hidden ≠ stopped: the compositor render loop and animations may continue. Gate ambient animation on visibility; prefer reusing transform objects; avoid per-frame allocation of UI objects.
- Unpackaged + self-contained + single-file: modules extract to a cache folder (check module paths in the event); `mscordaccore` is not on disk, so SOS fails.

## 7. Dump analysis ladder and failure modes
| Step | Tool | If it fails |
|---|---|---|
| a | `minidump_report.py` | not MDMP → kernel dump (kd) / ELF core (gdb) |
| b | `win_symbolicate.py` | modules not on disk → copy them, `--image-dir`, or WinDbg with symbol path |
| c | WinDbg `!analyze -v`, `~*k`, `.ecxr`, `!pe` | not installed → stay with a/b |
| d | `dotnet-dump analyze` (`clrthreads`, `clrstack`, `pe -nested`) | `Failed to request ThreadStore` = no DAC for this runtime (bundled) → STOP (two-strike), don't loop on `setclrpath`; spaces in paths: use 8.3 |
| e | ClrMD / `dotnet-symbol` | needs matching runtime bits |
Heap not in dump ⇒ enable full dumps and wait for recurrence rather than guessing the inner exception.

## 8. Enabling dumps
`scripts/enable_crash_dumps.ps1 -ExeName app.exe` (admin; DumpType 2 full, DumpCount 5). For .NET runtime-detected crashes also `DOTNET_DbgEnableMiniDump=1`. For apps you ship, add Crashpad/Sentry native or your own out-of-process watchdog.

## 9. Searching the web well
Query shapes that worked: `<exception code> <module> <function name>`; `<framework> <symptom> finalizer thread`; `<framework> github issue <exact frame>`. Prefer the framework's own issue tracker. **Do not construct raw-source URLs** - search and fetch what the search returns; if source is unreachable record it as E0 and downgrade dependent claims. Match versions: an issue about another version is E4 for yours.
