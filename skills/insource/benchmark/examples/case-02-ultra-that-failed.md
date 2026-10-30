# Case 02 — an ultra attempt that failed, and how the data proved it

> Real numbers from the authoring machine, 2026-10-29. Kept as a negative result on purpose: this is the failure
> mode ultra mode is most likely to produce, and the run detects it.
>
> **The stack here is incidental.** The lesson is "verify the control, then check the noise floor", which applies
> to any runtime; the read-back commands below are examples per stack, not a Python-only procedure.

**Question.** Same workload as [`case-01`](case-01-sqlite-normal-mode.md) (SQLite `LIKE '%kestrel%'` vs FTS5
`MATCH`, 200 000 rows). Now in **ultra** mode: pin one core, disable GC, discard warmup, more iterations.

## What was applied, and what was not

| Control | Intended | Actually happened |
|---|---|---|
| process affinity → one logical core | remove scheduler migration | **failed**: `GetProcessAffinityMask` returned 0 — the call was built wrong (handle truncation from an unset `restype`), so the process stayed unpinned |
| `gc.disable()` | remove collection pauses | applied |
| `gc.collect()` per sample, **outside** the timer | deterministic heap state | applied — but it adds a pause that lands in the *interval between* samples, and on a laptop with background activity it is variance, not control |
| warmup discarded (8 rounds), 40 iterations | stable JIT/cache state | applied |
| CPU governor / turbo / C-states locked | the big one | **not possible without admin rights on this box** — never claimed, only disclosed |

## The numbers

| Run | Noise floor (`like` vs `like2`) | fts5 median | like median | ratio (95 % CI) |
|---|---|---|---|---|
| normal, 24 iters, no controls | **2.76 %** | 3.57 ms | 55.0 ms | 0.0662 [0.0610, 0.0706] |
| "ultra", 40 iters, controls above | **6.98 %** | 3.55 ms | 53.4 ms | 0.0676 [0.0628, 0.0705] |

The gap conclusion is identical — FTS5 is ~15× faster here and the CI is nowhere near 1, so the *decision* was
never in doubt. But look at the control column: **the run that tried to be quieter was 2.5× noisier than the
one that admitted it was uncontrolled.** The `like2 vs like` check called it inconclusive in both, correctly.

## Why the "ultra" run was worse

1. **The pin never engaged**, so scheduling migration — the thing ultra mode exists to remove — stayed in the
   data, and the extra per-sample `gc.collect()` added its own rhythm on top of it.
2. More iterations were spent, and they bought a wider interval, because the added work was noise, not control.
3. Nothing in the numbers is *wrong*; the mode label was. That is the trap: "ultra" is a claim about what you
   controlled, and an unverified control is a false claim in the header of an otherwise honest report.

## The rule this case earns

**Prove every control engaged, before labelling anything ultra.** Read the setting back *from inside the process
being measured* — the launcher's view is not the process's view, and every stack has a way to fail at exactly
that: an ignored error return, a truncated FFI handle, a call that succeeds but is overridden by a cgroup or a
scheduler policy.

| Stack | Pin, then read it back | Runtime knob, printed from inside |
|---|---|---|
| [Linux, any language] | `taskset -pc <pid>` after `taskset -c`; in-process `[sched_getaffinity]` | `/proc/self/status` → `Cpus_allowed_list`, `governor` from sysfs |
| [Windows / PowerShell] | `Start-Process -ProcessorAffinity`, then `(Get-Process -Id <pid>).ProcessorAffinity` | the process's own priority class, not the shell's |
| [Python] | `os.sched_getaffinity(0)` on POSIX; on Windows the `kernel32` call **with `restype` set**, else the handle truncates and the mask reads 0 | `gc.isenabled()` |
| [Go] | `runtime.LockOSThread` + `GOMAXPROCS(1)`; verify with `syscall.SchedGetaffinity` | `runtime.GC()` off-window; `debug.SetGCPercent(-1)` echoed |
| [Rust]/[C] | `[libc::sched_setaffinity]` then `sched_getaffinity` into a struct and print it | the allocator in use, the `-C opt-level`/`-O` actually passed at build time |
| [JVM] | `[-XX:+UseThreadPriorities]` etc. are advisory — check via `[ThreadMXBean]`/`jinfo -flags` | `jinfo -flags <pid>` shows the flags the *running* VM got |
| [.NET] | `Process.GetCurrentProcess().ProcessorAffinity` read back | `GCHandler`/`GCSettings.LatencyMode`, `Environment.ProcessorCount` |
| [Node]/[Bun] | `os.cpus()` tells you nothing about pinning — read the OS for that | `--jitless` / tier settings confirmed by the process's own `process.execArgv` |

And the cheap self-test that catches all of this without reading a manual page: **run the same implementation
twice under two labels and look at the noise floor.** If it is wider than the normal-mode floor, the controls are
not controlling anything, and the honest label is *normal*.

A second rule this case keeps: **report the controls that were impossible**, not just the ones that worked. Here,
"governor and turbo could not be locked without admin rights" is the reason a laptop run can beat a server run by
a factor and neither is lying.

A third, from the isolation side: the controls this run attempted were all **per-process** (affinity, GC,
priority), so they died with the process and left the machine as it was; the machine-wide ones it could not
attempt are exactly the ones that would have owed a restore. Anything installed stayed out of the global
environment — stdlib only, scratch database in a temp dir. If ultra work needs a system change, capture the
before-value first and put it back in teardown, not at the end of a script that may crash
([`../references/01-normal-vs-ultra.md`](../references/01-normal-vs-ultra.md) — "restore what you touched").

## What to conclude when you see this pattern

- the *ranking* was stable across both modes (0.0662 vs 0.0676) → the decision is safe;
- the *absolute numbers* moved with thermal/background state → do not quote them outside this machine;
- the mode label needs correcting in the report, and the fix is cheaper than the mistake: verify the control,
  or run normal mode and say so.
