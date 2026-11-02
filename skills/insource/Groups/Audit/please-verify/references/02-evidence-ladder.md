# The evidence ladder

The verdict may not claim more than the weakest deciding piece of evidence supports. This ladder is what
keeps "done" from being a feeling.

| Level | Name | What it actually proves | Typical artifact |
|---|---|---|---|
| **L0** | Exists | Someone typed this. It says nothing about it working. | File, function, route, component in the tree |
| **L1** | Builds / type-checks | The code is coherent enough for the toolchain to accept it. | Build log, `tsc --noEmit`, compiler output, exit code 0 |
| **L2** | Tests pass | Whatever the tests assert holds - no more. | Test run output, coverage report, attached CI log from *this* state |
| **L3** | Runs / integrates | The system actually starts and the path executes. | Boot logs, smoke request, end-to-end run, exit code |
| **L4** | Observed expected behavior | The promised outcome was watched happening. | Screen render, file opened, message shown, screenshot, transcript |

## What counts as evidence

- **From this delivery, not from history.** An old green log, a screenshot before the last change, a test
  report for a different commit: none count unless tied to the current state (hash, timestamp, or a fresh
  run). Re-run rather than cite.
- **Command + output, not narration.** "Ran the tests, all pass" is a claim. The command and its output is
  evidence. Keep both in the report (trimmed, exit code preserved).
- **The environment matters.** Desktop success is not device success; empty-database success is not
  realistic-data success. State the environment next to the level ("L3 on desktop build, Xcode 16").
- **Absence of an error is not proof of a feature.** A silent log during a flow that never executed is L0.

## Labels for what could not be proven

| Situation | Label |
|---|---|
| Ran, passed, artifact attached | the level reached |
| Could not run (no toolchain, no device, no credentials) | `UNVERIFIED (reason)` - never PASS |
| Ran and failed | `BROKEN` at that level, with the failure output |
| Static review only | `L0/STATIC` - explicitly say nothing was executed |
| Partially proven (unit tests pass, app never started) | state both: L2 reached, L3/L4 unverified |

## Running things safely

Verification executes the project; it does not modify it.

- **Read-only on source.** No edits to make a check pass; if you must temporarily change something to test
  (a config toggle, a test fixture), revert it and say so in the report.
- **Isolated environments.** Install dependencies into the project's own environment (`[venv]`,
  `[npm ci]`-style local installs, containers) - never pollute the machine to verify someone else's repo.
- **No destructive runs on real state.** Do not point a fresh migration, seed, or delete-flow test at real
  data; use a scratch database/data directory, or mark the outcome UNVERIFIED.
- **Bounded time.** Set a budget for the sweep (builds and app launches can crawl). When it runs out, report
  which areas were reached and which were not - a labeled partial audit beats a silent pass.
- **Capture as you go.** For every run: the exact command, exit code, and the relevant output lines. The
  report quotes these; without them the level claim is unsupported.

## The false-PASS catalog

These are the shapes of a wrong "verified", in order of how often they happen:

1. **Green tests, dead app** - suite passes, nobody launched it (L2 masquerading as L3/L4).
2. **"It should work"** - reasoning about code as if reasoning were execution.
3. **The agent's own summary** - "implemented X, tested Y" with no artifacts; the summary is the claim under
   test, not its proof.
4. **Stale evidence** - an old log or screenshot from before the last change.
5. **Wrong scope's evidence** - the README's instructions work, but for a different branch/version.
6. **The happy path only** - the baseline promised an error state or empty state; only the happy path was
   run.
7. **Checks that do not touch the claim** - lint passing for a promise about behavior.

Each has one cure: name the level the artifact actually supports, and let the verdict follow.
