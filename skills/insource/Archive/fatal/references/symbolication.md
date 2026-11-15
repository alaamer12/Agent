# Symbolication: turning addresses into names, and the ways it silently lies

## Contents
1. The idea · 2. Matching rules per platform · 3. dbghelp via ctypes - the five bugs · 4. Public vs private symbols · 5. Managed frames · 6. Per-platform commands · 7. Verification checklist

## 1. The idea
A dump holds *addresses*. Symbols (PDB, dSYM, DWARF, mapping.txt, source map) hold *names and lines*. Like `.js` + `.js.map`, but the key is `module base + offset`. The dump never contains the symbols; they live in the build output or a symbol server.

## 2. Matching rules (a wrong symbol file is worse than none)
| Platform | Identity key | Check |
|---|---|---|
| Windows PDB | GUID + age (CodeView `RSDS`), also timestamp+size | `minidump_report.py` prints `pdb guid+age` |
| macOS/iOS dSYM | Mach-O UUID | `dwarfdump --uuid App.dSYM` vs crash report "Binary Images" |
| Linux | build-id | `readelf -n bin`; `/usr/lib/debug/.build-id/..`; `debuginfod-find` |
| Android native | build-id of `.so` in tombstone | use the *unstripped* `.so` from the same build |
| Android Java / JS | mapping.txt / .js.map from the same release | keep them per release; upload to Sentry/Play |
Keep PDBs/dSYMs for **every shipped build**; "which build crashed" is answered by version + timestamp in the dump.

## 3. dbghelp via ctypes - the five bugs (all fixed in scripts/win_symbolicate.py)
1. `SymSetOptions(0x2 | 0x4 | 0x10 | 0x80000000 & 0)`: `&` binds tighter than `|`, so the last term was `0`; and `0x4` = `SYMOPT_DEFERRED_LOADS` meant symbols were only fetched lazily and the download never fired. Use explicit named flags: `UNDNAME 0x2 | LOAD_LINES 0x10 | NO_PROMPTS 0x80000` (+ `EXACT_SYMBOLS 0x400`). The first "fix" used `0x40` (that is `LOAD_ANYTHING`, not NO_PROMPTS) - verify constants in `dbghelp.h`.
2. `symsrv.dll` will not touch the network until a file named `symsrv.yes` sits beside it (EULA gate).
3. `SYMBOL_INFOW.SizeOfStruct` must be the *header* size (88 on x64 with `Name[1]`), not `sizeof` of your oversized struct; `MaxNameLen` is in characters.
4. Frames from the app's own host/runtime (`MyApp.exe!FinalizerThread::…`) were filtered as noise. Those frames **named the root cause**. Never filter in the first pass.
5. `GetLastError()` printed after successful `SymLoadModuleExW` showed stale `487` and suggested failure. Only read the error when the call returned 0.
Also: after the first run, list the symbol cache folder - empty ⇒ nothing was downloaded; don't iterate blind. Don't hide stderr (`2>$null`) while debugging the tool itself.
Prerequisite: dbghelp finds the PDB through the *image on disk*, so the dump's modules must exist locally (same machine/same build). For a bundle-extracted app point `--image-dir` at the extraction folder.

## 4. Public vs private symbols
Microsoft's public symbol server serves **public** PDBs: exported/limited names only, no locals, no lines. Names between exports are attributed to the nearest earlier export (hence `+0x1b2b55`). Your own PDBs are private. A runtime statically linked into your single-file exe (coreclr) takes symbols from *your* PDB - that is why `FinalizerThread::…` resolved there.
Use `grade_frame` (in `_common.py`) / the `(?)` marks to avoid quoting noise.

## 5. Managed frames (.NET/Java/JS)
dbghelp sees native frames only. Managed frames need the runtime's debugging interface (DAC for .NET: `dotnet-dump`/SOS/ClrMD; `jcmd`/hs_err for Java) or your own logs. For single-file/self-contained .NET with no matching `mscordaccore`, expect SOS to fail; get managed context from logs + Sentry breadcrumbs, and infer the managed side from native host frames (finalizer thread, GC allocator).

## 6. Per-platform commands
- Linux: `addr2line -e bin -f -C -i 0xOFFSET`; `gdb -batch -ex "info symbol 0x…" bin`; `llvm-symbolizer --obj=bin 0x…`.
- macOS/iOS: `atos -o App.app/Contents/MacOS/App -l <load address> -arch arm64 0x…`; `symbolicatecrash`.
- Android native: `ndk-stack -sym obj/local/arm64-v8a < tombstone.txt`; Java: `retrace mapping.txt trace.txt`.
- Windows: `scripts/win_symbolicate.py`, or WinDbg `.symfix; .reload; k`.
- Cross-platform minidump: `dump_syms` + `minidump_stackwalk`.

## 7. Verification checklist
[ ] symbol files match the crashing build (key compared) [ ] first run: cache populated? [ ] frames graded, suspect ones excluded from the narrative
[ ] anchors identified (thread root, exception site) [ ] statement says "scan" vs "unwound stack" [ ] second dump gives consistent names
