# Tools and commands cheat sheet

Every row is a starting point with the trap named, not a mandate. Use what the project already has; a tool you
install during an incident is a new risk and belongs in the record as such. Commands are shown as they run in
`bash`; Windows equivalents are noted once per section and in brackets otherwise.

## Find the introducing commit

```bash
git bisect start <bad> <good>
git bisect run ./investigation/repro.sh          # exit 0 = good, non-zero = bad (1..127); 125 = skip
git bisect log > investigation/bisect.log        # keep the log: it is the proof, not the summary
git bisect reset
```

- A bisect needs a **deterministic** predicate. If the repro is probabilistic, run it N times and fail on ≥1;
  say N in the record — the commit is then "most likely" not "proven".
- `git log --follow -p -- path/file` when the suspect is a single file.
- `git blame -w -C -C -C <file>` ignores whitespace and detects moves; useful for latent conditions.

## Log and metric analysis

```bash
journalctl --since "2026-10-12 03:00" --until "2026-10-12 04:00" -u <unit>   # systemd
docker logs --since 2026-10-12T03:00:00Z <container> 2>&1 | grep -F '<signature>'
rg -n '<error signature>' --glob '*.log' | head -50
awk '$0 ~ /pattern/ {c++} END {print c}' big.log
```

- Normalize timestamps to UTC **before** correlating; a mixed-timezone timeline invents causality.
- Count first, then read: "1,842 of 12,000 (15.4%)" is a fact; ten selected lines are an anecdote.
- Keep the raw extract as an evidence file; a grep result pasted into chat is not reproducible.

## Debuggers, dumps, crash reports

```bash
gdb -p <pid> -ex 'thread apply all bt full' -ex detach -ex quit
lldb -p <pid> -o 'thread backtrace all' -o detach -o quit
dotnet-dump collect -p <pid> && dotnet-dump analyze <dump>      # .NET
windbg -z crash.dmp -c '!analyze -v; ~*kb; q'                    # Windows
python -m pdb app.py                                             # or py-spy dump --pid <pid>
node --inspect-brk app.js
```

- A dump answers "what was the state at that instant", never "why it got there". Pair with logs/tracing.
- On Windows, WER `.dmp` plus `!analyze -v` is the fastest crash signature; keep the dump as evidence.

## Windows-native: dump versus trace (and the tools around them)

The distinction that picks the tool: **a dump is the state at the crash; a trace is how the state got corrupted.**
A dump answers "what was true at 03:14:07"; a Time Travel Debugging trace answers "which write, in which frame,
made it true" — and replays forwards and backwards. For the once-per-100-hours crash, the trace is usually the
only way to see the moment, because you cannot wait for it twice.

```bat
:: always-on crash dumps for a service (set this up before the incident)
reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\<app.exe>" /v DumpFolder /t REG_EXPAND_SZ /d C:\dumps /f
reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\<app.exe>" /v DumpType /t REG_DWORD /d 2 /f
procdump -ma -e 1 -w <app.exe> C:\dumps\      :: -e 1 first-chance, -w wait for the process
procdump -ma -c 90 -s 5 <pid> C:\dumps\       :: CPU > 90% for 5 s — catches hangs, not just crashes

:: time travel: record once, replay forever
ttd.exe -out C:\traces\run01.run <app.exe> <args>
ttd.exe -out C:\traces\attach.run -attach <pid>
windbg -z C:\dumps\crash.dmp -c "!analyze -v; ~*k; q"
windbg -z C:\traces\run01.run                  :: then step backwards (g-, p, t) to the corrupting write

:: the "it corrupts something later" setup
gflags /p /enable <app.exe> /full              :: PageHeap — crash at the free, near the corruption
appverif -enable Heaps Handles Locks -for <app.exe>
verifier /standard /driver <driver>.sys        :: driver leftovers
wpr -start CPU -start DiskIO -filemode && wpr -stop C:\traces\session.etl   :: ETW, open in WPA
```

Traps: TTD traces reach gigabytes and cover user-mode only — record a short window, not a day. PageHeap
multiplies memory use; never on production. Driver Verifier can bugcheck the machine; snapshot first. WER
LocalDumps only helps if it was configured before the crash — a missing dump is a finding for §15, not a reason
to guess.

## Sanitizers and race detectors

```bash
gcc -fsanitize=address,undefined -fno-omit-frame-pointer -g app.c     # C/C++
cargo run --release --target x86_64-unknown-linux-gnu                  # + RUSTFLAGS="-Zsanitizer=address" (nightly)
go test -race ./...                                                   # Go
valgrind --tool=helgrind ./app                                        # races; --tool=memcheck for leaks
dotnet test --blame-hang-timeout 60s                                  # .NET hang/leak triage
```

`-fsanitize=thread` for data races (build separately — it does not mix with ASan). A sanitizer run that passes
once is V1; the record should say how many iterations and under what load.

## Profilers and tracing

```bash
perf record -F 99 -g -- ./app && perf report
py-spy record -o investigation/profile.svg --pid <pid> --duration 60
node --cpu-prof app.js
dotnet-trace collect --process-id <pid>
rr record ./app && rr replay                      # Linux record-and-replay, gdb-compatible
# continuous profiling (Parca / Pyroscope / OTel eBPF profilers): query the incident window afterwards
#   instead of trying to catch it live - the profile of 03:00-03:40 is still there tomorrow
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'     # Linux only, needs root
```

## Syscall, OS and network tracing

```bash
strace -f -tt -T -o investigation/trace.txt ./app          # Linux
dtruss -f ./app                                            # macOS (SIP off)
wpr -start CPU -filemode && wpr -stop investigation/trace.etl   # Windows (WPR/WPA)
tcpdump -i any -w investigation/capture.pcap 'tcp port 443'
tshark -r investigation/capture.pcap -Y 'tcp.analysis.retransmission'
```

Capture files follow the redaction rule: strip payloads/credentials, keep the original checksum in the notes.

## Fault and timing injection

```bash
tc qdisc add dev eth0 root netem delay 300ms loss 2%      # Linux; remove with: tc qdisc del dev eth0 root
toxiproxy-cli toxic add -t latency -a latency=500 <proxy>  # service-level faults
faketime '2026-12-31 23:59:00' ./app                       # clock, without touching the system clock
kill -STOP <pid>; sleep 5; kill -CONT <pid>                # freeze/resume = pause the world
```

Only inject in a disposable environment, and record the exact command plus how you reverted it.

## Fuzzing

```bash
afl-fuzz -i corpus -o investigation/afl -- ./target @@
cargo fuzz run target -- -max_total_time=600
python - <<'PY'   # quick property fuzz with hypothesis
from hypothesis import given, strategies as st
@given(st.binary(max_size=2048))
def test_parse(b): parse(b)   # must not raise unexpected exceptions
PY
```

The crash input is evidence: copy it in, hash it, name the seed.

## Security forensics (only when §9 has an "outside" cause)

```bash
sha256sum <artifact> && stat <artifact>          # preserve before touching anything
git log --all --oneline -S'<suspicious token>'   # was something injected?
rg -n 'AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}' --hidden -g '!evidence/**'
```

Do not paste live credentials into the document; record the finding, redact the value, and rotate it.

## Verification commands

```bash
pytest -q tests/test_regression_<bug>.py -k <name>        # must fail on the old commit, pass on the fix
go test -run TestRegression<Bug> -count=20 ./...          # determinism: 20 runs
npx playwright test tests/e2e/<scenario>.spec.ts --repeat-each=5
hyperfine --warmup 3 'before' 'after'                     # performance claims with error bars
for i in $(seq 1 1000); do (timeout 5 ./app || echo FAIL) ; done | sort | uniq -c   # soak wrapper
```

Prove the regression test first: `git stash` the fix (or check out the old SHA in a worktree) and watch it fail.
A test that has never failed proves nothing about this bug.

## Tooling hygiene

- Every command that produced a decision goes in §10/§12 with its output summary — including the ones that
  failed and changed the direction.
- Scripts written during the incident live in `investigation/`; scripts that are part of the fix live in `fix/`;
  verification harnesses in `verification/`. Copy them even when they also live in the repo (cite repo path + SHA).
- No absolute machine paths in the document; relative to the folder, or repo-relative with the SHA.
