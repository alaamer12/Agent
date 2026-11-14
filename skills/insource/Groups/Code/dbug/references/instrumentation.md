# Instrumentation — controlled observation, disciplined artifacts

Use the moment you feel the urge to add a `console.log`-style print, write
a scratch check script, or "just quickly query the DB". Two jobs:
(1) make the system observable **without polluting it**, (2) make
everything debugging creates **have a lifecycle**.

## Instrumentation rules

1. **Dev-only by construction.** Debug output must be inert in production —
   gated on environment and/or an explicit opt-in variable, never on
   "remember to delete these lines later". A forgotten log of a
   payload is a leak waiting to happen; a debug path that runs in prod is a
   second, untested code path.
2. **Scoped, not scattered.** The facility is *addressable per unit*:
   enable `service-a` or `orders-module` only, while everything else stays
   quiet. Uncontrolled logs everywhere = signal destroyed + diff noise.
   Pattern (any language): tiny module exporting a gated logger — see
   [`../assets/scoped-debugger-example.md`](../assets/scoped-debugger-example.md).
3. **Checkpoint discipline.** Put instrumentation at *pipeline midpoints*
   chosen to halve the search space (see
   [`escalation-ladder.md`](escalation-ladder.md)), not at every line
   that looks interesting. Log: what enters, what leaves, ids for
   correlation, state deltas. One experiment per run — change one thing.
   Tag every temporary print with a unique token (`[DEBUG-a4f2]`) so
   session-end cleanup is one grep, not archaeology.
4. **The instrumentation may stay.** A gated, scoped debug facility is
   project tooling, not dirt — promoting it (in the reusable sense) is
   encouraged; what must not survive is raw uncontrolled print noise.
5. **Debug status pages/counts too.** A dev-only route or endpoint that
   returns live state as JSON (config, cache keys, pool stats, flags) is
   instrumentation in the same sense — gate it, keep secrets out of the
   payload, and give it the same keep-or-delete decision as any other
   instrument. Read its index/discovery path first instead of guessing
   names, and remember some datasets stay empty until the program opts
   in — no data is ambiguous, not evidence.
6. **Zero-edit channels beat edits.** Where the debugger or platform
   offers tracepoints (a breakpoint that logs and keeps running),
   conditional/hit-count logging, data breakpoints (write-watch —
   answers "when did this variable change?"), or hot verbosity
   switching without restart: observe through those instead of editing
   source at all — no rebuild loop, no diff, no cleanup debt.
7. **Mind the observer effect.** Added prints and pausing change timing;
   a timing-dependent defect can vanish precisely because you're
   watching. Rank non-perturbing telemetry first for anything racy, and
   when observation perturbs, widen the suspect window deliberately
   (controlled delay behind a dev flag) rather than concluding absence.

## Debugging engineering — making the product itself debuggable

Debuggability is a design variable, not luck. An instrumented product lets
the agent boot past human gates and read live state directly: fewer tokens
spent fighting navigation, less time reaching the failing state, better
proof behind every claim. The same door is the cost: an instrument alive in
a shipped build is an attack surface and an untested second path. The trade
is only worth making when each instrument is **provably dead in
production** — by mechanism, not memory.

Whether a project carries these instruments is the project's decision: the
agents-md skill owns the asking (its interview: *"how do you want the agent
instrumented into debugging?"*) and the registration (the debugging doc
lists every instrument, its gating, and its never-bypassed line). This file
owns the engineering.

**The choice rule: KISS, because the code is disposable.** The ways to
reach a failing state are infinite — disable the auth step in a dev-only
composition, inject a session token through a debug hook, fake a service
at the DI seam, a route that renders one state on demand. Do not compare
implementations for elegance: pick the *simplest, most direct* one that
reaches the state deterministically, build it in minutes, do not fight
yourself. Instrumentation is paid for by time saved, never by design
quality — an ugly one-liner at the composition root beats a beautiful
subsystem, and the hours it would cost are hours the bug did not spend.

The patterns below are specified as **capabilities** — reaching a state
directly — not as "launch flags". The carrier is a project choice: any
capability may be a startup flag, a generic `[debug <value>]` command, an
environment variable, a config override, a deep link, or a dev-only
route; require the capability and its rails, never its syntax. Every
bracketed name is a PLACEHOLDER shape — the project invents its own
vocabulary and its rulebook registers the real names and real carriers;
never type a placeholder at a prompt:

1. **Gate bypass** (`[--skip-<gate>]`, `[debug skip-gate <name>]`, [env
   switch]) — reach the working screen without walking the human gates
   ([onboarding], [first-run], [consent prompt]): latch the
   first-run/completion preference before the first window is created,
   injected through the product's own persistence surface
   (settings/preferences) rather than a branch inside product code — no
   component ever gains harness knowledge, and the unflagged launch is
   byte-identical to the user's.
2. **Page direct-open** (`[--open-page=<id>]`, [deep link], [dev route]) —
   land on any named screen, dialog, or view at startup instead of
   replaying the click path that happens to lead there; the page ids are
   the ones the app itself enumerates, not free text.
3. **State freeze** (`[--state=<name>]`, `[debug state <name>]`) — force
   an interact-to-change state (modal open, panel collapsed, tab chosen)
   to a deterministic, enumerated value, so captures and repros stay
   comparable. Exact-value allowlists only: code that keys off "any flag
   present" leaks harness state into normal launches.
4. **Deterministic seed** (`[--seed=<dataset>]`, with `off` as the explicit
   inverse) — replace live/fetched data with the fixed fixture set and
   stop the live pipeline for the session, so two runs are comparable.
   Carry the purge path: `off` clears the latch and removes seeded rows,
   so a forgotten instrument can never strand the product on demo data.
5. **State export** (`[--export-state]`, [dev-only JSON route],
   `[debug dump]`) — read what the running app believes: dump live state
   to a file or endpoint at startup, gated at compile time or by build
   flavor — a gate a release build cannot re-enable by configuration.
6. **Harness hygiene** — single-subsystem probe consoles, preference- and
   store-reset scripts, and capture harnesses that kill stray processes
   before launch and record the exact instrument and arguments with every
   observation, so any captured state is relaunchable verbatim.

The dead-in-production rails, non-negotiable:

- A launch without the instruments behaves exactly as the user sees it:
  inert by default, gated by mechanism (compile flag, build flavor),
  never by "remember not to pass it".
- Bypasses skip **human gates** — wizards, first-run screens, modal
  choreography. They never skip auth, authorization, or validation
  boundaries: a pasted session cookie is a fixture; a skipped login check
  is a hole. (If a session must exist for the state to be reachable,
  inject the credential as dev-only fixture data — token-in — never turn
  the boundary check itself off where it could be flipped on for real.)
- **Quarantine, don't sprinkle.** Each instrument lives in a dedicated
  unit — a debug-only module/file/source set whose registration is one
  gated line at the composition root ([build tags/conditional
  compilation], [dev flavor/source set], [DI registration inside the
  debug block], as the stack names them). One gate line, one removal, one
  grep to audit. Sprinkled `if (debug)` checks inside product code cannot
  be proven dead.
- **Prove death by tool, not by claim.** The release build runs a check
  that FAILS if instrumentation survives into it — a lint rule or CI step
  grepping for the instrumented symbols/routes/flags, a compile pass
  without the debug symbol that must not reference them, a startup
  assertion that the debug route table is empty. That check IS the
  security review: "we gated it" is intent, "the production build breaks
  otherwise" is evidence.
- An instrument not registered in the project's rulebook does not exist:
  never guess an entry point, and propose one (gate #3) instead of either fighting
  the UI all session or quietly adding permanent complexity.

## Temp scripts: `.debugging/tmp/`

Every ad-hoc investigate/verify/apply script starts and lives here:

```
.debugging/tmp/check_users_schema.py        # is the live DB what the schema says?
.debugging/tmp/replay_webhook.ts            # simulate the consumer one message
.debugging/tmp/repro.sh                     # exit 1 on bug → bisect driver
```

Conventions (details → [`artifact-lifecycle.md`](artifact-lifecycle.md)):
self-contained (loads its own env per
[`env-and-resolution.md`](env-and-resolution.md)), deterministic exit
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
  borderline = *ask the user* (gate #3, [`../SKILL.md`](../SKILL.md))
  rather than unilaterally adding permanent complexity.
- **Bug record** only for investigations with lasting value (see the keep
  criteria in [`artifact-lifecycle.md`](artifact-lifecycle.md)); trivia
  belongs in the commit message.
- **Delete the rest.** `tmp/` is empty at session end — a leftover means
  the lifecycle didn't run.

Before finishing: also fold the *procedure* you learned into the
project's procedure library, if it has one (e.g. **how-to-do**) —
`.debugging/bugs/` remembers what happened; procedures remember how to
do it.

## Quick decisions table

| Urge | Do instead |
|---|---|
| "quick print here" | gated scoped logger (dev-only, this module) |
| "quick query on the DB" | `.debugging/tmp/` script, read-only, exits 0/1 |
| "I'll remove the logs later" | no — design them inert in prod, then keep or delete deliberately |
| "this script was useful, keep it at repo root" | promote path: generalize → `instruments/` (+ header template), else it dies in `tmp/` |
| "we should remember this bug" | `.debugging/bugs/<slug>.md` from the template — or if it's really a *procedure*, the project's procedure library |
| "I must click through the same wizard/login/modal every session to reach the bug" | debugging engineering: propose the gated bypass/seed instrument (above), register it in the project's rulebook once accepted |

---
**Feeds:** the repro scripts become [`regression-testing.md`](regression-testing.md)
seeds · **uses:** [`env-and-resolution.md`](env-and-resolution.md) patterns
inside scripts · **instrument inventory:** the project's debugging doc —
the agents-md skill asks and registers, this file builds ·
**next stop:** close-out checklist in [`../SKILL.md`](../SKILL.md).
