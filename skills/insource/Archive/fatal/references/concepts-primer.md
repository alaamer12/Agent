# Concepts primer: plain-English explanations (with the traps)

Read this when the user is learning ("explain off-thread", "is this a race condition?", "what is a
finalizer?") or when you must justify a claim in a report to a non-specialist. Lead with the analogy,
then the precise statement, then the common misconception.

## Contents
1. Process, thread, main/UI thread
2. Thread affinity and "off-thread"
3. Race condition vs thread-affinity violation vs deadlock
4. Managed vs native; wrappers and peers
5. Garbage collector and finalizer thread (and the ARC analogue)
6. Exceptions vs fatal terminations; fail-fast; first-chance
7. Dumps, stacks, symbols
8. Is this Windows-only? (portability of each idea)
9. Intermittent bugs: why "after 3 hours"

## 1. Process, thread, UI thread
A **process** is a running program with its own memory. **Threads** are workers inside it sharing that
memory. GUI frameworks designate one worker as the **UI thread** (main thread): it runs the *message
loop* - take next event (click, paint, timer), handle it, repeat. 
*Misconception*: "closing the window to the tray stops the UI." The window is hidden; the UI thread, render
thread and timers keep running unless you stop them. In the DemoApp case a hidden window still ran ~60 fps animations.

## 2. Thread affinity and "off-thread"
Analogy: a hotel room key only works for the guest it was issued to; housekeeping (another thread)
must not rearrange the room while the guest is mid-sentence. 
Precise: many UI objects have **thread affinity** - they must be created, used and **released** on the owning
thread. **Off-thread** means "executing on any thread other than the owner." 
Platforms react differently: Android throws `CalledFromWrongThreadException`; WPF/WinForms throw
`InvalidOperationException`/check `Dispatcher.VerifyAccess`; UIKit has the Main Thread Checker (a dev tool) and
otherwise behaves undefined; WinUI's native layer can **fail-fast**. "The same rule everywhere, different
punishment" is accurate; "every platform uses STA" is not - STA is a COM term; the *rule* is general, the
*mechanism* is not.
*Misconception*: "Windows kernel catches the violation." In the WinUI case the check lives in WinUI's own
native library (`Microsoft.UI.Xaml.dll`), which then asks the OS to terminate the process.

## 3. Race condition vs thread-affinity violation vs deadlock
- **Data race**: two threads touch the same memory without coordination; result depends on timing.
- **Thread-affinity violation**: the *wrong thread* performs an operation, even with no simultaneous access.
- **Deadlock**: threads wait on each other forever (a hang, not a crash).
The finalizer bug is best called a *thread-affinity violation whose timing is nondeterministic*. It is
race-**like** (it appears only when the GC happens to run the finalizer at the wrong moment) but it is not
a data race. If the user asks "is this a race condition?", answer: "related by timing, but the precise
label is a thread-affinity violation".

## 4. Managed vs native; wrappers
C# objects live in the **managed** world (garbage-collected). A WinUI button is really a **native** C++ object;
the C# object is a **wrapper** holding a pointer to its **native peer**. Two lifetimes, two systems of rules.
The GC knows only about the wrapper.

## 5. GC and the finalizer thread
The **garbage collector** frees managed objects nobody references. Objects with cleanup code
(`~Finalizer`) are queued to the **finalizer thread**, a hidden runtime thread that runs that cleanup
whenever convenient. It does not know which thread "owns" the native peer, so a wrapper's finalizer may
release a native UI object from the wrong thread. Frameworks usually avoid this by *marshalling the release
to the UI thread* (WinUI has a queue for it); when that path is unavailable or overwhelmed, the release can
fail-fast. 
Analogue elsewhere: Swift/Obj-C **ARC** destroys an object on whichever thread drops the last reference; if that
is a background thread, UIKit objects get deallocated off the main thread (classic "UIKit must be used from main thread" warnings/crashes).
Fix pattern everywhere: **stop creating the garbage** (reuse objects), or **release explicitly on the owning thread**.

## 6. Exceptions vs fatal terminations
A normal **exception** travels up the call stack until a `catch` handles it. A **fail-fast** is a deliberate
"stop now" with no unwinding: the runtime calls an OS routine that ends the process. Therefore `try/catch`,
`AppDomain.UnhandledException`, `Application.UnhandledException` and SEH filters never run. WER (or an equivalent
out-of-process observer) still sees it, which is why dumps exist. 
**First-chance exception**: the debugger-style notification when an exception is *thrown*, before any handler
decides. A log full of first-chance messages is mostly noise from handled exceptions (`Missing file: ''` in the
case study) - correlate in time and mechanism before calling it a cause.
**Stowed exception**: WinRT's way to carry saved error info inside a fail-fast (code `0xC000027B`).

## 7. Dumps, stacks, symbols
A **call stack** is the chain "A called B called C...". A **dump** captures every thread's stack bytes plus
registers. A **minidump** keeps stacks/modules and little else; a **full dump** adds heap. Stack data in a dump is
raw memory; reconstructing the real call chain is **unwinding** (needs unwind tables/symbols). A quick **scan**
for code addresses finds plausible frames but also stale values. **Symbols** (PDB/dSYM/DWARF) translate addresses
to names. Public symbols give only exported names, so offsets inside them can be huge and misleading.
JS analogy: `.js` + `.js.map` ≈ binary + PDB; but the PDB maps *addresses*, and a dump supplies the addresses.

## 8. Portability of each idea
| Idea | Portable? |
|---|---|
| UI objects have thread affinity | Yes, nearly every toolkit |
| Native release from finalizer/background thread can crash | Yes in any GC/ARC language with native peers (WinUI, Android views via JNI, UIKit via ARC) |
| `0xC000027B`, `RoFailFast…`, stowed exceptions | Windows/WinRT only |
| A terminated process leaves a dump/report | Yes, but name and location differ (see platform-artifacts.md) |
| "Handlers can't catch it" | True for fail-fast/SIGKILL; false for class C and (unsafely) SIGSEGV |

## 9. Why "after 3 hours"
Delay + only when idle usually means *accumulation* or *a periodic event that rarely hits a bad moment*:
leaked/queued objects, GC cycles that only run when memory pressure crosses a line, timers, power-state
changes, token/cert expiry. Hypothesise a **rate × time** budget (e.g. ~120 native objects/s × 3 h ≈ 1.3 M) and look for
what produces objects when nobody is looking. Always rule out class E (something killing it on a schedule) first.
