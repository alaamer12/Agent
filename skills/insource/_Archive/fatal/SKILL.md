---
name: fatal
description: Investigate fatal, unrecoverable process terminations (crashes, fail-fasts, silent disappearances) on any platform - Windows .dmp/minidump/WER, Linux core files, macOS/iOS .ips/.crash, Android tombstones/ANR, JVM hs_err, Node/Go/Rust aborts - and explain them with evidence. Use whenever an app "just disappears", "closes after N hours", "tray icon vanishes", "stops without an error", exits with 0xC000027B/0xC0000005/0xC0000409/SIGSEGV/SIGABRT/SIGKILL/139/137, or the user mentions a dump, crash report, stack scan, symbolication (PDB/dSYM/DWARF/mapping.txt/source map), watchdog, Sentry not catching a crash, or asks concept questions like "off-thread", "fail-fast", "finalizer", "is this a race condition", "what is a .pdb", "what is it called on macOS". Also use to read huge crash-investigation transcripts or logs. Trigger even if the user never says "fatal".
---

# fatal - understand unrecoverable terminations from the evidence

A fatal termination ends the process before its own code can explain it, so the story lives **outside** the process: dumps, OS records, other processes' logs. Your job is to classify the death, collect those artifacts, extract facts without over-reading them, build a causal chain whose every link is graded, fix in layers, and **say honestly what is proven**. The skill is built from a real 4,500-line investigation (see `references/lessons-from-a-winui-case.md`) including its detours - the rules below exist because each detour cost real time.

## Quick start (do these in order)

1. **Intake** - ask only what artifacts can't tell you (`assets/intake-questions.md`). If the user pasted a huge log/transcript, shrink it first: `python scripts/condense_log.py FILE` (keeps every turn, tool call, failure and line number).
2. **Triage the machine** - `python scripts/crash_triage.py --app <name> [--search DIR]`: which debuggers exist, where dumps/reports/logs are, newest first. Do this *before* installing tools.
3. **Classify the death** (table below). It decides everything that follows.
4. **Timeline** - `python scripts/build_timeline.py app.log:app heartbeat.log:hb events.txt:os --death "<time>"`: find the **last sign of life vs time of death**. A gap longer than the logging interval means *no instrumentation covers the death* - state it.
5. **Read the dump/report** (platform in `references/platform-artifacts.md`):
   - Windows: `python scripts/minidump_report.py a.dmp [b.dmp --compare]` → `python scripts/win_symbolicate.py a.dmp` (Windows only).
   - Other platforms: gdb/lldb/atos/ndk-stack/hs_err per the reference; `python scripts/decode_status.py <code|signal>` for any number.
6. **Reason with grades** (`references/evidence-and-reasoning.md`): ledger of facts, causal chain, ≥2 alternatives, a falsification test.
7. **Fix in layers and verify honestly** (`references/fix-verify-observe.md`): remove cause / contain / observe; report each as Observed / Reasoned / Untested.
8. **Report** with `assets/report-template.md`. Lead with the bottom line; plain-language explanation for the user.

## Classify first (termination classes)

| Class | Meaning | Signature | Next |
|---|---|---|---|
| A | Deliberate abort / fail-fast | `0xC000027B`, `0xC0000409`, SIGABRT, `EXC_CRASH`/`EXC_BREAKPOINT`, Go `fatal error` | dump → which **thread** raised it |
| B | Hard fault | `0xC0000005`, SIGSEGV/SIGBUS, `EXC_BAD_ACCESS` | fault address (<0x10000 ⇒ null+offset), module+offset |
| C | Unhandled language exception | `0xE0434352`, Java/Python/Node uncaught | your own logs/event log - handlers *can* run |
| D | Resource exhaustion | OOM, stack overflow `0xC00000FD` | memory/handle trend (heartbeat) |
| E | **External kill** | exit `-1`/`0xFFFFFFFF`, 137, SIGKILL, jetsam, **no dump, no crash event** | who killed it: script, installer, user, OOM killer, supervisor |
| F | Hang-kill | ANR, `0x8badf00d` | what the main thread was blocked on |
| G/H/I | Clean exit / loader failure / system-level | exit 0; `0xC0000135`; kernel panic | exit marker / event log / boot logs |

"Process vanished" is **not** "crashed": rule out class E and G before analysing a dump. `python scripts/decode_status.py 0xC000027B 139 SIGKILL` gives class + next step.

## Hard-won rules (each one was a real mistake)

- **Prior postmortems are hypotheses.** Check that an earlier "fix" touches the mechanism in *this* artifact.
- **Look at the gap** between last log line and death. Event-only logs hide the lead-up.
- **Two-strike rule.** If a tool fails for a structural reason twice (e.g. `dotnet-dump`: *Failed to request ThreadStore* on a single-file app - no DAC), change approach; don't tweak flags.
- **Know what the dump captured** (`dump kind`). No heap ⇒ stowed/inner exception unreadable ⇒ enable full dumps for next time; don't guess.
- **A stack *scan* is not a stack.** Grade frames: offsets > 0x10000, wrapped offsets and placeholder symbols (`_tls_end`, `` `string' ``) are noise. Trust anchors: exception record, saved thread IPs, thread-root/host frames with small offsets.
- **Thread role beats function name.** Which thread raised it (UI / finalizer / worker / RPC)? That separates "bad call" from "bad release".
- **Compare dumps in a table** before saying "same". Use same / related / different + why.
- **Never construct source URLs**; search, fetch what exists, and downgrade claims when source is unreadable.
- **Verify constants and flags against headers** - comments lie (a `0x40` flag was labelled NO_PROMPTS; it is LOAD_ANYTHING).
- **Don't suppress stderr or truncate pipes while debugging a tool.**
- **Observer coverage:** ask who *could* have seen this death. Managed SDKs (Sentry .NET) cannot see fail-fasts; out-of-process observers (watchdog, WER, Crashpad) can. Absence of a report ≠ absence of a crash.
- **Noise ≠ cause.** First-chance exception spam needs a timing *and* mechanism link; fix it separately.
- **Before declaring "it crashed again"** run the false-alarm checklist (new dump? Event Log for *this* build? heartbeat+watchdog silent together? rebuild/kill script?).
- **Never say "fixed" without a soak** that matches the failure horizon; otherwise say "Reasoned" and give the test.

## Teaching mode
When the user asks conceptual questions ("off-thread", "fail-fast", "finalizer", "race condition?", ".pdb vs .js.map", "what's it called on macOS"), read `references/concepts-primer.md` and `references/universal-vocabulary.md`, then answer as in `examples/06-teaching-qa.md`: analogy → precise statement → misconception → portability. Correct known wrong claims (SIGKILL ≠ fail-fast; thread-affinity violation ≠ data race; `.js.map`; WinUI itself raises the fail-fast, not "Windows"). Universal terms: **fatal termination** (umbrella) + class; **crash dump** (memory file) vs **crash report** (text).

## Bundled resources (read when needed)

| Path | Use |
|---|---|
| `scripts/crash_triage.py` | tool + artifact inventory for the current OS |
| `scripts/build_timeline.py` | merge logs, last-sign-of-life vs death, observers, silent gaps |
| `scripts/minidump_report.py`, `scripts/mdparse.py` | dependency-free minidump reader: exception, thread IPs, dump kind, stowed exceptions, `--compare` |
| `scripts/win_symbolicate.py` | dbghelp symbolication with the 5 known bugs fixed + frame grading (`--selftest` runs anywhere) |
| `scripts/decode_status.py` + `assets/status_codes.json` | NTSTATUS/HRESULT/signal/exit-code/Apple/Android decoder (extend the JSON) |
| `scripts/condense_log.py` | short-but-complete digest of huge logs/transcripts, with line numbers |
| `scripts/enable_crash_dumps.ps1` | enable/inspect/remove WER LocalDumps (full dumps) |
| `references/universal-vocabulary.md` | classes, artifact words, cross-platform table |
| `references/concepts-primer.md` | plain-English concepts + misconceptions |
| `references/platform-artifacts.md` | where evidence lives, how to enable, tools, per platform |
| `references/windows-failfast-playbook.md` | Event Log, status codes, stowed exceptions, WinUI, dump ladder |
| `references/symbolication.md` | matching rules, dbghelp bugs, public vs private symbols |
| `references/evidence-and-reasoning.md` | grades, ledger, chain, falsification, observer coverage |
| `references/fix-verify-observe.md` | layered fix, heartbeat, watchdog, post-mortem upload, verification ladder, false alarms |
| `references/lessons-from-a-winui-case.md` | the case, mistakes → rules, over-strong claims |
| `examples/01-06` | worked investigations (Windows, Linux, Android, iOS, false alarm, teaching) |
| `assets/*.md`, `assets/samples/` | report template, ledger, intake questions, cheat sheet, sample logs, synthetic-dump generator |

To test the scripts without a real crash: `python assets/samples/make_synthetic_minidump.py /tmp/x.dmp` then `python scripts/minidump_report.py /tmp/x.dmp`.

## Output style
Direct and concrete; users in this domain are often frustrated by hand-waving. Start with the bottom line and its confidence, then evidence, then fix. Use **Observed / Inferred / Untested** labels. Say what you could not read. Explain jargon on first use. Don't over-format short answers.
