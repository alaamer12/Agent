# Universal vocabulary for fatal (unrecoverable) terminations

Read when you must name things consistently across platforms, or the user asks "what is this called on macOS / Linux / Android?".

## Contents
1. The umbrella term and the nine termination classes
2. Artifact words: dump vs report vs log vs symbols
3. Cross-platform mapping table
4. One-sentence definitions you can reuse
5. Terms that are NOT standard

## 1. Umbrella term and classes

Recommended umbrella: **fatal termination** = the process ended in a way application code could not intercept, recover
from, or (usually) log. It is broader than "crash" on purpose: the commonest mistake is treating every disappearance as a crash.

| Class | Name | Who ended the process | App handlers run? | Typical evidence |
|---|---|---|---|---|
| A | **Deliberate abort** (Windows *fail-fast*; Unix `abort()`/SIGABRT; Apple EXC_CRASH/EXC_BREAKPOINT; Go `fatal error`) | The process's own runtime/OS library, because an invariant broke | No | dump/report + exception code or abort message |
| B | **Hard fault** (access violation, SIGSEGV, SIGBUS, SIGILL) | CPU/OS, invalid instruction/address | Only unsafe signal/SEH handlers | dump/core/tombstone |
| C | **Unhandled language exception** | The runtime, after nobody caught it | Yes (last-chance handlers) | your logs, runtime event log |
| D | **Resource exhaustion** (OOM, stack overflow, handles) | Allocator/OS | Sometimes | heartbeat trend, OOM log |
| E | **External kill** (user, script, installer, OOM killer, SIGKILL, TerminateProcess, jetsam) | **Someone else** | No | exit code, absence of dump, the killer's logs |
| F | **Hang-kill** (watchdog, ANR, Apple 0x8badf00d) | A timer, after the process stopped responding | No | system report naming the watchdog |
| G | **Clean exit** | The app, intentionally | n/a | exit code 0, exit marker |
| H | **Startup/loader failure** | Loader | n/a | event-log entry, missing-DLL status |
| I | **System-level** (kernel panic, BSOD, power loss) | The machine | No | kernel dump, boot logs |

**Classify first - the next step differs entirely.** A/B → analyse a dump. E → find who sent the kill (no dump will exist).
F → find what the main thread was blocked on.

If asked for "one term that always means the same thing everywhere": use *fatal termination* for the umbrella and name the
class when precision matters ("a class-A deliberate abort - Windows calls it a fail-fast"). Don't use "Fatal Process Abort"
as an umbrella: "abort" already means class A specifically.

## 2. Artifact words
| Word | Meaning | Examples |
|---|---|---|
| **crash dump / memory dump** | Binary snapshot of process memory at death | Windows `.dmp` (mini/full), Unix **core file**, Breakpad/Crashpad `.dmp` |
| **crash report** | Human-readable rendering of one crash | Apple `.ips`/`.crash`, Android **tombstone**, JVM `hs_err_pid*.log`, Windows `Report.wer`, Node diagnostic report |
| **crash log** | Ambiguous: "dump", "report" or "your own text log". **Define it or ask** | |
| **event record** | OS one-liner that a crash/kill happened | Windows Event Log 1000/1001/1026, `dmesg` segfault line, `journalctl` coredump entry, Android `ApplicationExitInfo` |
| **symbols** | Files mapping addresses to names/lines | PDB, dSYM, DWARF/`.debug`, `mapping.txt` (R8), `.js.map`, Breakpad `.sym` |
| **symbolication** | Applying symbols to raw addresses | `atos`, `addr2line`, `ndk-stack`, dbghelp, retrace |
The JavaScript file is `app.js.map` (not `.map.js`).

## 3. Cross-platform mapping
| Concept | Windows | Linux | macOS / iOS | Android | JVM | .NET |
|---|---|---|---|---|---|---|
| Deliberate abort | `__fastfail`, `RaiseFailFastException`, WinRT `RoFailFastWithErrorContext` | `abort()` → SIGABRT | `EXC_CRASH` (SIGABRT), `EXC_BREAKPOINT` (SIGTRAP) | SIGABRT + "Abort message" | JVM fatal error → `hs_err` | `Environment.FailFast` |
| Hard fault | Access violation `0xC0000005` | SIGSEGV / SIGBUS | `EXC_BAD_ACCESS` | SIGSEGV (`SEGV_MAPERR`/`ACCERR`) | SIGSEGV in native/JIT | AV in native code |
| External kill | `TerminateProcess` (exit `-1`) | SIGKILL / OOM killer | jetsam / force-quit (no crash report) | lmkd, `REASON_SIGNALED`/`LOW_MEMORY` | as host OS | as host OS |
| Dump | `.dmp` | core file | rare; `.ips` report instead | tombstone (text) | `hs_err` + optional core | `createdump` → `.dmp`/core |
| Where | `%LOCALAPPDATA%\CrashDumps`, WER ReportArchive | cwd, `/var/lib/systemd/coredump`, `/var/crash` | `~/Library/Logs/DiagnosticReports` | `/data/tombstones`, `logcat -b crash` | cwd `hs_err_pid<pid>.log` | `DOTNET_DbgMiniDumpName` |
| Symbols | PDB | DWARF / build-id | dSYM (UUID) | unstripped `.so`, `mapping.txt` | `mapping.txt` | PDB (portable) |
| Tool | WinDbg, cdb, this skill's scripts | gdb, lldb, `coredumpctl`, eu-stack | lldb, `atos`, Xcode Organizer | `ndk-stack`, `retrace` | `jcmd`, read hs_err | `dotnet-dump`, WinDbg+SOS |
Breakpad/Crashpad (Chromium, Electron, Sentry native) write the *Windows minidump container* on every OS.

## 4. Reusable one-sentence definitions
- **Fail-fast**: the runtime decides continuing is unsafe and kills its own process immediately, running no application error handlers.
- **Hard fault**: the CPU refused an instruction (bad address); with no safe handler the process dies.
- **External kill**: something outside the process ended it; it had no say and no chance to log.
- **Crash dump**: a frozen copy of the process's memory and thread states at the moment it died.
- **Symbols**: a decoder ring turning raw addresses into names/lines, kept apart from the program to keep it small.
- **Thread affinity**: some objects may only be touched by the thread that owns them.
- **Observer coverage**: which monitors could possibly have seen this kind of death?

## 5. Terms that are NOT standard
- **"Fail-fast sandwich"**: informal phrase from one engineer's notes for a scanned stack with fail-fast machinery frames on top, the culprit in the middle and the thread root at the bottom. Never present as an industry term.
- **"Fatal Process Abort"** as an umbrella: coined in a chat; see §1.
- **"SIGKILL is the Unix fail-fast"**: wrong. SIGKILL comes from someone else; the Unix analogue of fail-fast is `abort()`/SIGABRT or a deliberate trap (SIGILL/SIGTRAP).
- Don't expand ".ips"; say "Apple's `.ips` crash-report format".
