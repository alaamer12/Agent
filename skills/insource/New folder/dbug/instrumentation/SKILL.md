---
name: dbug-instrumentation
description: Controlled observation and artifact discipline during a debug session — use the moment you feel the urge to add a console.log, write a scratch check script, or "just quickly query the DB": routes debug output through a dev-only, scope-gated facility instead of scattered prints, keeps every throwaway script in .debugging/tmp/, and runs the end-of-session lifecycle (promote reusable tools to .debugging/instruments/, record significant bugs in .debugging/bugs/, delete the rest) so debugging leaves capability behind instead of cruft.
---

# dbug-instrumentation — controlled observation, disciplined artifacts

Two jobs: (1) make the system observable **without polluting it**, (2) make
everything debugging creates **have a lifecycle**.

## Instrumentation rules

1. **Dev-only by construction.** Debug output must be inert in production —
   gated on environment and/or an explicit opt-in variable, never on
   "remember to delete these lines later". A forgotten `console.log` of a
   payload is a leak waiting to happen; a debug path that runs in prod is a
   second, untested code path.
2. **Scoped, not scattered.** The facility is *addressable per unit*:
   enable `service-a` or `orders-module` only, while everything else stays
   quiet. Uncontrolled logs everywhere = signal destroyed + diff noise.
   Pattern (any language): tiny module exporting a gated logger — see
   [`assets/scoped-debugger-example.md`](assets/scoped-debugger-example.md).
3. **Checkpoint discipline.** Put instrumentation at *pipeline midpoints*
   chosen to halve the search space (see
   `../investigation/references/escalation-ladder.md`), not at every line
   that looks interesting. Log: what enters, what leaves, ids for
   correlation, state deltas. One experiment per run — change one thing.
4. **The instrumentation may stay.** A gated, scoped debug facility is
   project tooling, not dirt — promoting it (in the reusable sense) is
   encouraged; what must not survive is raw uncontrolled print noise.

## Temp scripts: `.debugging/tmp/`

Every ad-hoc investigate/verify/apply script starts and lives here:

```
.debugging/tmp/check-users-schema.ts        # is the live DB what the schema says?
.debugging/tmp/replay-webhook.ts            # simulate the consumer one message
.debugging/tmp/repro.sh                     # exit 1 on bug → bisect driver
```

Conventions (details → [`references/artifact-lifecycle.md`](references/artifact-lifecycle.md)):
self-contained (loads its own env per `../backend/`), deterministic exit
codes (0/1 — usable as test/bisect driver), redacts credentials from
output, cleans its connections (`finally`) and any DB rows it writes
(prefer transaction + `ROLLBACK` for anything mutating).

## End-of-session lifecycle

```
                 ┌─► has value beyond THIS bug? ── yes ─► generalize inputs
.debugging/tmp/* ┤        (reusable check? will re-run?)          (no hardcoded target)
                 │                                             ─► .debugging/instruments/
                 └─ no / one-shot done ────────────────────► delete
 investigation was non-trivial & its path is worth keeping? ─► .debugging/bugs/<slug>.md
```

- **Promote** (`tmp/ → instruments/`) only when generalization genuinely
  applies (accepts `--table`, reads env, no incident-specific constants);
  borderline = *ask the user* (dbug gate #3) rather than unilaterally
  adding permanent complexity.
- **Bug record** only for investigations with lasting value (see the keep
  criteria in the reference); trivia belongs in the commit message.
- **Delete the rest.** `tmp/` is empty at session end — a leftover means
  the lifecycle didn't run.

Before finishing: also fold the *procedure* you learned into **how-to-do**
(if it's a class of task) — `.debugging/bugs/` remembers what happened,
`.htd/` remembers how to do it.

## Quick decisions table

| Urge | Do instead |
|---|---|
| "quick console.log here" | gated scoped logger (dev-only, this module) |
| "quick query on the DB" | `.debugging/tmp/` script, read-only, exits 0/1 |
| "I'll remove the logs later" | no — design them inert in prod, then keep or delete deliberately |
| "this script was useful, keep it at repo root" | promote path: generalize → `instruments/` (+ header template), else it dies in `tmp/` |
| "we should remember this bug" | `.debugging/bugs/<slug>.md` from the template — or if it's really a *procedure*, how-to-do |

---
**Feeds:** the repro scripts become `../regression-testing/` seeds ·
**uses:** `../backend/` env-resolution patterns inside scripts ·
**next stop:** close-out checklist in `../investigation/SKILL.md`.
