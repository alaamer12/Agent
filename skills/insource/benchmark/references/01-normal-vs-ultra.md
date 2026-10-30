# Normal and ultra — what each mode controls, and what each can honestly claim

> **Illustrative, not exhaustive.** Engines, runtimes, OS tools and flag names in this file are examples
to reason from. The measurement logic is stack-neutral, and an unlisted or hybrid option is a valid answer.

The same candidates, two different questions.

| | **normal** (default) | **ultra** |
|---|---|---|
| Measures | what a developer or a deployment will actually experience | the mechanism, with as much noise removed as the machine allows |
| GC / runtime | left at defaults, running, visible in the numbers | disabled or forced between iterations where the runtime permits, and the knob is named |
| Warmup | none — first calls included, JIT and caches cold like real usage | discarded warmup rounds, then measured rounds; warmup count recorded |
| Caches (OS, disk, CPU) | as they are | page cache primed or dropped deliberately; either choice stated |
| CPU | scheduler as usual, other apps running | pinned core, frequency locked to a sustainable value, turbo/C-states/hyperthreading off **if permitted** |
| Memory | as the process gets it | pre-touched, allocator pinned, buffers pre-allocated, page-fault count fixed |
| Isolation | whatever the machine is doing | idle machine, no indexers/AV/updates, temperature noted, background load captured |
| Env deps | whatever the project already has — isolated for the benchmark anyway (see below) | same: ultra never means "installed globally" |
| Ordering | whatever order you ran them in | strictly interleaved A B A B, so drift hits both equally |
| Iterations | whatever the budget allows (often 10) | as many as the budget allows, usually several times more, plus repeats in a second session |
| Reporting | "on this machine, as configured" | "under controlled conditions: <list>", plus every control you could not apply |

Neither is the true answer. Normal answers *"what will I feel"*; ultra answers *"what is actually faster"*.
**The gap between them is a finding**: a candidate that wins in normal and loses in ultra is winning on
warm-up or GC behaviour, not on the algorithm — say that instead of picking whichever looks better.

## Ultra checklist — apply what the machine allows

```bash
# before anything: what is this machine doing right now?
uptime                                   # load average: the first honesty check
powerinfo / setpowerplan                 # Windows: high performance plan, or note "on battery"
# Linux:
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
rdmsr -p 0 0x1a0 2>/dev/null            # turbo disabled? (needs msr)
taskset -c 3 ./bench                     # pin to one core (core 3 = sibling of 1... check topology)
# Windows:
start /high /affinity 8 bench.exe        # high priority, pinned to one logical core
# macOS:
sudo powermetrics -n 1 -i 1000 | grep -i freq
```

Then, per runtime, the knobs that actually move numbers — **name them in the report**, because they change what
is being measured:

| Runtime | Ultra knob | What it removes |
|---|---|---|
| [Java/Kotlin/Scala] | `-XX:+UnlockDiagnosticVMOptions -XX:-TieredCompilation`, forced `System.gc()` between rounds, JMH `@Fork`/`@Warmup` | JIT tiers, heap-state carry-over |
| [.NET] | `ServerGarbageCollection=false`, `_gcConcurrent=0`, `GCSettings.LatencyMode`, `dotnet run -c Release` | background GC noise, debug builds |
| [Python] | `python -X int_max_str_digits=0 --` + `gc.disable()` around the timed block, or a warm-up call first, `time.perf_counter_ns` | collection pauses, `time.time` resolution |
| [Go] | `GOMAXPROCS(1)`, `debug.SetGCPercent(-1)` when measuring pure compute, `go test -bench . -count=10 -cpu=1` | scheduler and GC variance |
| [Rust]/[C/C++] | release/`-O2 -g0` (state the flags), pinned allocator, `perf` counters instead of wall time if asked | debug-mode cost, allocator drift |
| [Node]/[Bun] | `--predictable-gc-scope` / `--jitless` where available, forced GC between rounds via the inspector, warmup loops | JIT tiering, background compaction |
| SQLite and other embedded engines | same page-cache size, same `PRAGMA synchronous/journal_mode`, same journal file state; warm vs cold cache stated | I/O policy differences masquerading as engine differences |

## Isolation is not a mode — it applies in normal too

Ultra controls the *machine*. Isolation protects the *user's* environment, and belongs to both modes: the
benchmark's dependencies never enter a global package dir, and never enter the project's manifest unless the
project genuinely depends on the thing being benchmarked.

| Stack | Throwaway environment (example option) | Check it stayed clean |
|---|---|---|
| [Python] | `[python -m venv .venv-bench && source .venv-bench/bin/activate]`, `[uv venv .venv-bench]`, `[conda create -p ./.conda-bench]` | `git diff requirements.txt pyproject.toml uv.lock poetry.lock` → empty |
| [Node]/[Bun] | `[npm ci --prefix ./.bench-node]`, a temp dir with its own `package.json`, `[pnpm --dir]` | `git diff package.json package-lock.json` → empty; no `npm i -g` |
| [Ruby] | `[bundle config set --local path vendor/bundle]` in a copy of the tree | `Gemfile.lock` unchanged outside the copy |
| [PHP] | `[composer install --working-dir=bench/.]` | root `composer.lock` unchanged |
| [Java] | `[maven -Dmaven.repo.local=./.m2-bench]`, `[gradle --project-cache-dir]` | global `~/.m2` untouched |
| [.NET] | `[dotnet restore --packages ./.nuget-bench]` | global package cache untouched |
| [Go] | `[go mod vendor]` into the bench module, `[GOFLAGS=-mod=vendor]` | `go.mod`/`go.sum` of the project unchanged |
| [Rust]/[C/C++] | build in a temp target dir (`[CARGO_TARGET_DIR=./.bench-target]`), source-only deps vendored | no `[apt/pacman]` installs without asking |
| engines/services (DB, broker) | a container, a VM, a second data dir on a spare port, or `[nix develop]` | the running service the user uses is not repurposed as a scratch instance |

If no isolation exists for the stack, **ask before writing to a shared or global location** — that is a
side effect the user did not request. Scratch artifacts (databases, generated workloads, temp files) go under a
temp dir or the `bench/<date>-<topic>/` folder, and get deleted or listed in the report.

## Restore what you touched

A control is a borrowed setting, not a configuration you own. Capture the value before changing it, put it back
when the last sample is taken, and show the read-back in the report — a laptop left on a high-performance plan or
a machine left with turbo disabled changes how the *user's* next hour behaves.

```bash
# Linux — record, change, restore
cp /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor /tmp/gov.bak
echo performance | sudo tee .../scaling_governor
cat /tmp/gov.bak | sudo tee .../scaling_governor && rm -f /tmp/*.bak
sudo cpupower frequency-set -r          # restore the auto range if you set one

# Windows — record, change, restore
powercfg /getactivescheme                                  # remember this GUID
powercfg /setactive <guid>                                 # back to it afterwards
powercfg /query | grep -i "Maximum processor state"        # proof it is restored

# macOS
pmset -g | tee /tmp/pmset.bak ; sudo pmset -a ... ; sudo pmset -g   # diff against the backup
```

Per-process settings (affinity, priority, `GOMAXPROCS`, `gc.disable()`, JIT tiers) die with the process and need
no restore — but they must be **read back while running** to prove the control engaged
([`../SKILL.md`](../SKILL.md), step 4). Machine-wide settings need the explicit restore above, and a killed or
failed run still owes one: restore in the harness's teardown path, not in a final line you may never reach.

## When ultra is not available, and when it is a lie

- **Shared or cloud machines**: steal time, burst credits and noisy neighbours are not removable. Say
  *"ultra conditions were not achievable: <reason>"* and report normal numbers. A pinned core on a vCPU is not
  a pinned core.
- **Laptops**: thermal throttling makes run 40 slower than run 5 for reasons unrelated to the candidates. Either
  cool and note it, or keep N small and stop pretending the tail is real.
- **End-to-end or networked systems**: pinning the process does nothing when the variable is a remote service.
  Ultra here means fixing *the dependency's* state (same dataset version, same cache warmth), and if you cannot,
  the honest number is a wide interval, not a point.
- **Never tune the candidate for the benchmark and present it as generic.** A `-O3 -march=native -ffast-math`
  build beating a default build measures compiler flags. If you change build flags, both candidates get them
  and the report says so.

## Reporting rule

Every table carries the mode in the header line, and every control that was applied — or could not be — is
listed under "Conditions". A reader who cannot tell which mode produced a number cannot use it: ultra numbers
are not "more correct", they answer a different question. The same line states the isolated environment used and
confirms the machine-wide settings were restored, with the read-back as proof.
