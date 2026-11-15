# Example 6 - Teaching mode: answering the concept questions well

Use when the user is learning. Pattern: **analogy → precise statement → misconception → where it does/doesn't generalise.**

**Q: Is this some type of race condition in threads?**
Related by timing, but the precise name is a *thread-affinity violation*: the wrong thread performs an operation on an object that only its owner thread may release. A data race is two threads touching the same memory at once. The finalizer runs "whenever the GC decides", which makes it intermittent - that's the race-like part.

**Q: What does "off-thread" mean?** Executing on any thread other than the one that owns the object. Hotel-key analogy; UI thread is the guest, finalizer thread is housekeeping.

**Q: If the GC is automatic, how can it break rules?** The GC frees *C# wrappers*; each wrapper owns a native peer with its own rules. The finalizer thread doesn't know which thread owns the peer. Frameworks avoid it by marshalling releases to the UI thread; heavy churn/teardown can defeat that.

**Q: Can fail-fast be caught? Is it only C#/only Windows?** No handler in the process can catch it (try/catch, unhandled-exception events). Concept is universal; names differ (see universal-vocabulary): Windows fail-fast ≈ Unix `abort()`/SIGABRT ≈ Apple `EXC_CRASH`/`EXC_BREAKPOINT`. **SIGKILL is not the equivalent** - it comes from someone else.

**Q: What is a .pdb? Like .js.map?** Yes in role (decoder for addresses→names), but it decodes *addresses from a dump*, and must match the binary's GUID+age. Other platforms: dSYM, DWARF, mapping.txt.

**Q: What's the universal single term?** "Fatal termination" (umbrella) with a class when precision matters; "crash dump" for the memory file, "crash report" for a text rendering.

**Q: Does every UI use XAML?** No. XAML is one declarative UI system (WinUI/WPF/MAUI-on-Windows). Others: Win32/HWND, AppKit/SwiftUI, UIKit, Android Views/Compose, web DOM (Electron), immediate-mode GPU UIs. The *lesson* (thread affinity + native peers) applies to most retained-mode toolkits.

**Q: Why "after 3 hours"?** Accumulation or a rare periodic collision; compute rate × time; rule out external kills first.
