# Worked example — folder mode (condensed)

> Invented incident for teaching. Folder mode is the same document plus a **self-sufficient package**: every
> script, log and test the reasoning depends on is inside, indexed and hashed.

**Request.** "Folder mode. The sync worker crashed on startup in production; here are the logs."

**Title (unsanitized, stays as the H1):** `Postmortem: Sync service — startup crash — 2026-10-12`

**Folder name (sanitized):** `Postmortem - Sync service — startup crash — 2026-10-12`
(produced by `python scripts/pm_check.py --sanitize "Postmortem: Sync service — startup crash — 2026-10-12"` —
the `:` becomes ` -`; `/ \ * ? " < > |` would be removed; the em dashes and spaces stay.)

```text
Postmortem - Sync service — startup crash — 2026-10-12/
├── index.md
├── index.html                      # bundled reader, SOURCE = 'index.md', <title> = the postmortem title
├── evidence/
│   ├── prod-crash-2026-10-12T03-14.log
│   ├── crash-9f2a.dmp
│   └── ntp-step-events.csv
├── investigation/
│   ├── repro-startup-crash.py      # minimal reproducer
│   ├── bisect.log                  # git bisect run output
│   ├── jwt-echo-check.py           # dead end: proved the library was not at fault
│   └── redactions.md               # what was stripped, from which file, original checksums
├── fix/
│   ├── 0001-guard-server-clock.patch
│   ├── apply.sh
│   └── rollback.sh
└── verification/
    ├── test_skew_guard.py
    ├── soak-18h.log
    └── results.md
```

**Nothing was created in `verification/` until results existed; no empty `screenshots/` folder was made.**

## Slice of `index.md` §18 — Files and Artifacts Index

| Path | Role | What it is | How to run it | What it showed | Supports | SHA256 |
|---|---|---|---|---|---|---|
| `evidence/prod-crash-2026-10-12T03-14.log` | evidence | API log around the first failure | — | 1,842 `skew guard rejected iat` lines; pool `waiting=1204` | §1, §3, §4 | `9be1c0…` |
| `evidence/crash-9f2a.dmp` | evidence | WER dump of the crashing worker | `windbg -z crash-9f2a.dmp -c '!analyze -v'` | crash signature matches the guard assertion | §8 | `4c77aa…` |
| `investigation/repro-startup-crash.py` | find | sets a client clock step, mints token, asserts rejection | `python investigation/repro-startup-crash.py` | fails on `9c1f0a4`, passes on `c4a8d1f` | §5, §13 (V4) | `e001a2…` |
| `investigation/bisect.log` | find | `git bisect run` log | `git bisect log` replays it | first bad commit `9c1f0a4` | §2 | `b6d93f…` |
| `investigation/jwt-echo-check.py` | find | proves the jwt lib echoes the supplied `iat` and has no clock of its own | `python investigation/jwt-echo-check.py` | library not at fault → dead end | §9 alternatives | `77fa13…` |
| `fix/0001-guard-server-clock.patch` | fix | the one-hunk patch | `git apply fix/0001-guard-server-clock.patch` | server clock is the only reference now | §11 | `c0a5d1…` |
| `fix/rollback.sh` | fix | reverts to `37b4e2c` | `bash fix/rollback.sh` | used at 03:52Z in the incident | §11, §12 | `1d4b8e…` |
| `verification/test_skew_guard.py` | verify | regression test | `pytest -q verification/test_skew_guard.py` | red on old SHA, green on fix | §14 | `a83fe0…` |
| `verification/soak-18h.log` | verify | 18 h × 6 instances soak | `tail -n 3 verification/soak-18h.log` | 0 failures in 108 instance-hours | §15 | `52ce61…` |

Every path above exists; every file in the folder has a row. `index.md` links them relatively — `investigation/repro-startup-crash.py`,
`fix/0001-guard-server-clock.patch` — written as code here because this example lives in the skill, not beside
those files.

## Slice of `index.md` §18 — How we reached this conclusion

1. **Suspected** a pool-exhaustion bug, because the first symptom was `waiting=1204`. **Ran** an inventory of
   the pool config (`investigation/repro-startup-crash.py` with `--pool-only`). **Returned** max=200, active=200,
   no leak over 30 min. **Ruled out:** pool sizing. The pool was a consequence, not the cause.
2. **Suspected** the NTP step was a coincidence. **Ran** `evidence/ntp-step-events.csv` against the crash
   timeline. **Returned** a +410 ms step 0.6 s before the first rejection, on 91% of affected hosts.
   **Supported:** the clock is part of the mechanism.
3. **Dead end —** mined the jwt library for a clock. **Ran** `investigation/jwt-echo-check.py`: the library
   echoes the `iat` it is given and reads no clock. **Rejected:** "library bug" (evidence kept, §9).
4. **Confirmed the unit** by bisecting with `repro-startup-crash.py` as the predicate: `bisect.log` lands on
   `9c1f0a4`, the commit that introduced the guard. **Proved:** introduced by the guard, not by the NTP step.
5. **Fixed** with `fix/0001-guard-server-clock.patch`; **proved** by `test_skew_guard.py` (red on `9c1f0a4`,
   green on `c4a8d1f`) and the 108-instance-hour soak; level claimed **V4**, not V5, because the shared timer
   still exists (§16 A2). Watch: alert `sync_reconnect_overlap_total > 0` for 14 days.

## Serving the package

```bash
cd "Postmortem - Sync service — startup crash — 2026-10-12"
python -m http.server 8000            # POSIX: python3 -m http.server 8000
# open http://localhost:8000/  → the reader renders index.md; TOC, search-free navigation, copy buttons
```

Verify inside the reader that `investigation/…`, `fix/…`, `verification/…` and `evidence/…` links open (they are
relative paths; a browser opened via `file://` will refuse them — that is why the server is the instruction).

## Redaction note (kept in `investigation/redactions.md`)

```text
evidence/prod-crash-…log   removed: 3 bearer tokens, 11 emails, 2 internal IPs
                           original SHA256: 9be1c0…   redacted copy SHA256: 3ac812…
evidence/crash-9f2a.dmp    removed: user home path, machine name (dump string patch)
                           original SHA256: 4c77aa…   redacted copy SHA256: c19d07…
```

The index table hashes the **redacted copies** that are actually in the folder; the originals' hashes live here,
so an auditor can still match against the source of truth without the sensitive content being present.

## Final check (what `pm_check.py` enforces)

```text
$ python scripts/pm_check.py --folder "Postmortem - Sync service — startup crash — 2026-10-12"
OK   18/18 sections present
OK   index table lists 9/9 files · 0 files missing · 0 rows pointing at absent files
OK   all 14 relative links resolve
OK   SHA256 matches for 9/9 artifacts
OK   index.html SOURCE = 'index.md', title set
WARN §15 uses "should be fine" — replace with an explicit level/coverage statement (§13/§15)
2 warnings, 0 errors
```
