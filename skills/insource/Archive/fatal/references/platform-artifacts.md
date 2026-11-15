# Where the evidence lives, per platform (and how to turn it on)

Use after `scripts/crash_triage.py`. Each section: artifacts → enable → analyse → symbols → blind spots.

## Contents
Windows · Linux · macOS · iOS · Android · JVM · .NET (any OS) · Node · Python · Go/Rust · Cross-platform (Breakpad/Crashpad/Sentry)

## Windows
- **Artifacts**: Event Log (*Application*: ID 1000 Application Error, 1001 Windows Error Reporting, 1002 Hang, 1026 .NET Runtime);
  WER archive `C:\ProgramData\Microsoft\Windows\WER\ReportArchive\AppCrash_<exe>_*\Report.wer` (UTF-16 text: `Sig[]`, `LoadedModule[]`, `IsFatal`);
  LocalDumps `%LOCALAPPDATA%\CrashDumps\<exe>.<pid>.dmp`; kernel dumps `C:\Windows\Minidump`, `MEMORY.DMP` (BSOD, class I).
- **Enable dumps**: `scripts/enable_crash_dumps.ps1 -ExeName app.exe` (HKLM `...\Windows Error Reporting\LocalDumps\<exe>`: `DumpType` 1 mini / 2 full, `DumpFolder`, `DumpCount`). Needs admin. 
- **Read**: `Get-WinEvent -FilterHashtable @{LogName='Application';StartTime=...}`; then `scripts/minidump_report.py`; symbolicate with `scripts/win_symbolicate.py`; or WinDbg `!analyze -v`, `~*k`, `.ecxr`.
- **Symbols**: PDB (`srv*cache*https://msdl.microsoft.com/download/symbols`; your own PDBs from the build output).
- **Blind spots**: fail-fast skips every in-process handler (Sentry/AppDomain). WER dump exists only if enabled. `Stop-Process -Force` produces exit code `-1`/`0xFFFFFFFF` and **no** WER entry.
- Deep dive: `windows-failfast-playbook.md`.

## Linux
- **Artifacts**: core file (name from `/proc/sys/kernel/core_pattern`; `ulimit -c` must be non-zero); `coredumpctl list|info|gdb|dump` (systemd-coredump); Ubuntu apport `/var/crash/*.crash`; kernel line `segfault at ... ip ... in libfoo.so` in `dmesg`/`journalctl -k`; OOM killer: `Out of memory: Killed process <pid>`.
- **Enable**: `ulimit -c unlimited` (per shell/service `LimitCORE=infinity`), keep systemd-coredump installed, containers need `--ulimit core=-1` and a writable core path.
- **Read**: `gdb -batch -ex 'thread apply all bt full' <exe> <core>`; `eu-stack -p`; `lldb -c core exe`. Build-id: `readelf -n exe`; `debuginfod-find debuginfo <buildid>`.
- **Symbols**: DWARF inside the binary or `.debug` files in `/usr/lib/debug/.build-id/xx/yyy.debug`; `addr2line -e exe -f -C -i <addr>`; `llvm-symbolizer`.
- **Signals**: see `assets/status_codes.json` (`decode_status.py SIGSEGV`). Exit status `128+N` in shells; `137` in containers often = OOM.
- **Blind spots**: SIGKILL (class E) leaves **no** core and no handler runs; check kernel log/cgroup OOM events.

## macOS
- **Artifacts**: `~/Library/Logs/DiagnosticReports/*.ips` (modern) and `*.crash` (older); `/Library/Logs/DiagnosticReports` for system processes; unified log `log show --last 6h --predicate 'process == "App"'`. Core dumps are off by default (`/cores`).
- **Read**: the report states *Exception Type* (`EXC_BAD_ACCESS`, `EXC_CRASH`, `EXC_BREAKPOINT`...), *Termination Reason*, *Triggered by Thread*, and per-thread backtraces with image offsets.
- **Symbols**: dSYM matched by **UUID** (`dwarfdump --uuid App.dSYM`); `atos -o App.app/Contents/MacOS/App -l <load addr> -arch arm64 <addr>`; `symbolicatecrash`.
- **Blind spots**: user force-quit / jetsam leaves no crash report; look for termination codes (`0x8badf00d` watchdog, `0xdead10cc` file lock held while suspended).

## iOS / iPadOS
- **Artifacts**: Settings ▸ Privacy & Security ▸ Analytics & Improvements ▸ Analytics Data (`.ips`); Xcode Organizer ▸ Crashes; MetricKit payloads; `JetsamEvent-*.ips` for memory kills.
- **Same format and tooling as macOS** (dSYM + UUID; upload dSYMs to Sentry/Crashlytics or you get unreadable traces).
- **Typical class-A/F signatures**: `EXC_BREAKPOINT` from Swift runtime traps (force-unwrap nil, index out of range); `0x8badf00d` (main thread blocked too long). UI-off-main-thread shows as Main Thread Checker messages or undefined behaviour.
- **Blind spots**: crashes under memory pressure are jetsam kills (class E), not crashes.

## Android
- **Artifacts**: logcat crash buffer `adb logcat -b crash -d` (Java: `FATAL EXCEPTION`); native crash → **tombstone** (`/data/tombstones`, in `adb bugreport`); ANR traces (`/data/anr`, "ANR in <pkg>" in logcat); Android 11+ `ApplicationExitInfo` (`getHistoricalProcessExitReasons`; `adb shell dumpsys activity exit-info <pkg>`) giving REASON_CRASH / CRASH_NATIVE / ANR / LOW_MEMORY / SIGNALED...; Play Console Android vitals.
- **Symbols**: native: unstripped `.so` from the NDK build, `ndk-stack -sym <dir> < tombstone.txt`; Java/Kotlin: R8/ProGuard `mapping.txt` + `retrace`.
- **Blind spots**: lmkd low-memory kills and seccomp `SIGSYS` look like silent deaths; check exit reasons first.

## JVM (any OS)
- **Artifacts**: `hs_err_pid<pid>.log` in cwd (`-XX:ErrorFile=` to relocate); optional core (`-XX:+CreateCoredumpOnCrash`). Header names the signal and "Problematic frame"; sections for Java and native frames.
- **Note**: `OutOfMemoryError` is a catchable class-C/D exception; a JVM *crash* (hs_err) is class B/A.

## .NET (any OS)
- **Enable dumps without WER**: env vars `DOTNET_DbgEnableMiniDump=1`, `DOTNET_DbgMiniDumpType` (1 mini, 2 heap, 3 triage, 4 full), `DOTNET_DbgMiniDumpName=<path>`. Dumps are produced by `createdump` for *runtime-detected* crashes.
- **Read**: `dotnet-dump analyze <dump>` (`clrthreads`, `clrstack`, `pe`) **requires the matching DAC** (`mscordaccore`); for single-file/self-contained/bundled apps it often fails with *Failed to request ThreadStore* - then stop and use native tools (see lessons). 
- **Managed stack of an unhandled exception** is in the Windows event log (.NET Runtime 1026) or stderr/journal; fail-fast reason string likewise.

## Node.js
`node --report-on-fatalerror --report-uncaught-exception --report-on-signal` writes a JSON diagnostic report; `--abort-on-uncaught-exception` yields a core on uncaught throws; V8 "FATAL ERROR: ... heap out of memory" ends in SIGABRT.

## Python
`python -X faulthandler` (or `faulthandler.enable()`) dumps Python tracebacks on SIGSEGV/SIGABRT/etc. Native extension crashes need gdb/core. A subprocess exit code of `-11` means "killed by signal 11".

## Go / Rust
Go: `GOTRACEBACK=crash` makes fatal errors abort with a core; `fatal error:` (e.g. concurrent map writes, deadlock) cannot be `recover()`ed; exit code 2. Rust: `RUST_BACKTRACE=1`; `panic = "abort"` → SIGABRT; panics in FFI boundaries abort.

## Cross-platform crash reporters (Breakpad, Crashpad, Sentry native)
They install an **out-of-process** handler/helper that writes a minidump on every OS, then upload it with symbols (`dump_syms`/`sentry-cli debug-files upload`). Managed-only SDKs (e.g. Sentry .NET) cannot see class A/B deaths in native code - **know your observer's coverage**.
