# One-page cheat sheet

**Classify:** exit `-1`/`137` + no dump ⇒ external kill · `0xC0000005`/SIGSEGV ⇒ hard fault · `0xC000027B`/`0xC0000409`/SIGABRT ⇒ deliberate abort · `0xE0434352` ⇒ unhandled .NET exception · `8badf00d` ⇒ hang-kill.
**Tools by platform:** Win `minidump_report.py`→`win_symbolicate.py`/WinDbg · Linux `gdb -batch -ex 'thread apply all bt'` · macOS/iOS `atos`+dSYM · Android `ndk-stack`/`retrace` · JVM read `hs_err`.
**Always:** last sign of life vs death · dump kind (heap?) · thread ROLE of the faulting thread · frame grades · second dump · who could have observed this?
**Two-strike rule:** same structural failure twice ⇒ change approach.
**Never:** call a stack scan "the stack" · quote an offset > 0x10000 as a function · guess source URLs · say "fixed" without a soak · expand an acronym you aren't sure of.
**Wording:** Observed … · Inferred … because … · Untested … (test: …).
