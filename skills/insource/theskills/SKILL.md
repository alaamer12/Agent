---
name: theskills
description: 'Pin skills as fixed, auto-apply behavior and persist that into the agent''s memory context, so future sessions run them without being asked. Run at the start of a conversation or project to load the pinned set and apply it all session: pinning `clean-code` with the trigger "writing or editing code" makes every later turn that writes code run clean-code first. The registry (.theskills/pins.json) is the source of truth; `sync` renders it into the AGENTS.md managed block — the baseline every harness reads — plus, only when the harness has them, secondary layers: a feedback memory entry with its MEMORY.md index line, or notes a session-start hook injects. `status` audits drift across the layers that exist. Pins resolving to no invocable skill are refused. Use for "make X a fixed skill", "always use X", "pin these skills", "so you never have to ask me to run X", /theskills, or to list/add/pause/unpin/sync/audit the set. Not for running one skill once, and not general memory cleanup (the remember skill).'
when_to_use: /theskills at the start of a session or project; the user asks that certain skills always apply, wants the pinned list seen or changed, or a repo has .theskills/pins.json.
argument-hint: "[bootstrap|pin <skill> --when \"…\"|list|sync|status]"
---

# theskills — fixed skills, remembered

## Overview

A pin is `skill + when + status`. `when` is a predicate on the current request; when it matches, the
skill is invoked **before** the work, unprompted. The registry (`.theskills/pins.json`) is what you
edit; `sync` renders it into whatever persistence layers this harness actually offers.

## Layers: one baseline, the rest optional

Different agents and harnesses remember things differently. Do not assume one of them exists — detect
it, write what is there, and say what was skipped.

| Layer | Coverage | What goes there |
|---|---|---|
| **`AGENTS.md`** (repo root) | **baseline — universal.** Every harness reads an instruction file: `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, Qoder's global/project instructions all take this form. Always written. | Managed block: intro, a `skill / when / note` table, four operating rules, pin-count footer, between two HTML comment markers |
| **Auto-memory** | secondary, harness-specific. Present only where a memory dir with a `MEMORY.md` index exists (e.g. `~/.qoder/projects/<repo-slug>/memory`). | `pinned-skills.md` as a `type: feedback` entry plus one index line — survives a clobbered instruction file |
| **Session-start hook** | secondary, stronger, opt-in. Only if the harness runs a startup hook AND the user asks for it. | Nothing generated automatically: point the hook at `bootstrap` output (or copy the block) so the list is re-injected every session rather than only read |

Detection is the rule: `sync` writes `AGENTS.md`, then looks for a memory dir. `status` reports
`memory absent (not a drift)` when there is none — a missing optional layer is never drift, and pins
written to no layer at all are the failure mode to avoid.

- `<memoryDir>` = `~/.qoder/projects/<repo-slug>/memory` when it exists, or an explicit `--memory <dir>`
  / `THESKILLS_MEMORY_DIR`. **The user-global `~/.qoder/memory` is never auto-targeted**: a pin made in
  one repo does not belong in every project's memory. Pass it deliberately if that is what is wanted.
- Skills resolve from `~/.qoder/skills`, `~/.agents/skills`, the repo's `.qoder/skills` and
  `.agents/skills`, and the runtime built-ins — **by their frontmatter `name`, which is what invocation
  matches on, not the folder**.

## At the start of a session

1. `node <skill-dir>/scripts/theskills.mjs bootstrap` — prints the active contract (or "no active
   pins", in which case there is nothing to apply; stop).
2. Hold that table for the whole session. Every turn: match each `when` against the request, invoke
   the matches first, name it in one clause ("running `/clean-code` — this writes code"), then work.
3. Do not re-run `bootstrap` per turn, and do not paste the table into replies. If it disagrees with
   `AGENTS.md`, run `status`; pins.json wins over memory, and reality wins over pins.json.

## Pinning

1. `discover` first. Three groups: installed (pinnable), runtime built-ins (pinnable), and
   "in this repo but NOT installed" — **only installed skills can be pinned**, because only installed
   skills can be invoked. An authored-but-uninstalled folder is refused unless `--force`, which marks
   the pin `uninstalled` and `status` keeps warning about it.
2. Propose the pins with their exact `when` wording, then confirm before writing. A pin changes the
   agent's behavior in every future session of this repo — that is the whole point, and the reason not
   to invent pins the user never named.
3. `pin <skill...> --when "<trigger>" [--note "<caveat or why>"]` — `--when` is mandatory; one command
   pins many skills with the same trigger.
4. `sync` — renders `AGENTS.md` and every optional layer that exists. A pin without `sync` is invisible
   to the next session. Read its output: `memory SKIPPED` means the second layer is not there, which is
   fine for the baseline and worth telling the user.
5. `status` — must end CLEAN over the layers present. Then tell the user: applies from the next session
   (or after `/skills reload`), undo with `unpin <skill>` + `sync`.
6. Only if the user asks for stronger enforcement: wire a session-start hook (with the harness's own
   hook mechanism, e.g. its hook config) that injects `bootstrap` output. That is a config change
   outside the repo — propose it, do not perform it silently.

A trigger is decidable from one message. "coding" is a topic, not a trigger; "writing or editing
application code, including one-line changes" is a trigger. Put the words the request will contain into
`when`.

## Changing the set

| Intent | Command |
| --- | --- |
| Stop auto-applying, keep the record | `pause <skill>` → `sync` |
| Start again | `resume <skill>` → `sync` |
| Trigger misfires (too wide or too narrow) | `when <skill> --trigger "…"` → `sync` |
| Remove | `unpin <skill>` or `unpin --all` → `sync` |
| Skill was renamed (`parity` ← `visual-parity-testing`) | `unpin <old>` → `pin <new> --when …` → `sync` → `status` |
| pins.json hand-edited | `sync` → `status` |
| Moved to another machine/repo | `--root <dir>`, `--memory <dir>` |

Keep it small: **about eight active pins is the ceiling.** Past that the block stops being honored
reliably, costs tokens in every turn of every session, and starts contradicting itself. Merge
overlapping triggers, or pause the weakest — `pause` keeps the reasoning visible.

## Verify, do not assume

- `status` (exit 2 on drift) checks the agreements for the layers that exist: block present and
  byte-equal to what the registry would render, memory file equal and `MEMORY.md` pointing at it *when
  a memory dir was resolved*, and every active pin resolving to a real skill. It never writes;
  `audit` is `status` plus a `skill_state` refresh.
- After any `sync`, re-read the block in `AGENTS.md` and confirm the user's own content above and
  below it is untouched — `sync` replaces only the region between the two markers.
- Then test the mechanism the only way that counts: next session, give a request that matches one
  `when` and see whether the skill runs unprompted. If it doesn't, the trigger wording is the bug
  (or the harness is not loading `AGENTS.md` — check that before blaming the pin).
- `bootstrap` in a repo with no pins must say "No active pins", not invent defaults.

## Limits worth stating out loud

An always-on directive is **advisory**. It sits in context, not in the enforcement path; a model under
context pressure can skip it, and no wording in a markdown file makes it a guarantee. The honest
strengths are: it is one instruction file edit, reversible in one command, and auditable. If something
must happen with certainty, that belongs in a hook or CI, not here.

Also honest: pinning `security-scan`-style skills that carry their own "auto-invoke" rule duplicates
behavior the harness already has — `discover` output and the skill's own description tell you when a
pin is redundant.

## Conventions

- Never hand-write the managed block or the memory entry; both are generated and `status` will flag
  them as drift the moment someone does.
- Never invent a persistence layer: no memory dir, no memory sink; no hook support, no hook config edit.
- Never `--force` a pin into the block just to make a command pass; report the missing install instead.
- Other agents may edit this repo concurrently: `sync` preserves everything outside its markers and
  never reverts edits it did not make.
- Pins are per-repo (`.theskills/pins.json` lives in the repo). Decide deliberately whether to commit
  it: committed pins are shared policy for everyone's agent; gitignored ones stay personal. Ask once.
- No dependency beyond Node; no network; no writes outside the repo and the resolved memory dir.

## Commands

```bash
node <skill-dir>/scripts/theskills.mjs discover
node <skill-dir>/scripts/theskills.mjs pin polyglot --when "authoring or refactoring a skill, standard, or example in any language" --note "keep examples platform-neutral"
node <skill-dir>/scripts/theskills.mjs pin humanizer subagent --when "drafting prose the user will read, or writing a worker brief"
node <skill-dir>/scripts/theskills.mjs sync
node <skill-dir>/scripts/theskills.mjs status          # exit 0 clean · 2 drift · 1 no registry
node <skill-dir>/scripts/theskills.mjs bootstrap       # what applies right now
node <skill-dir>/scripts/theskills.mjs list            # the registry as a table
node <skill-dir>/scripts/theskills.mjs pause humanizer && node <skill-dir>/scripts/theskills.mjs sync
```

`--when`/`--note`/`--trigger` take a quoted value or the `--when=value` form; only the quoted form is
safe when the value contains spaces.

## Resources

- `scripts/theskills.mjs` — the entire mechanism, one dependency-free file (Node ≥ 18). Layer policy
  lives in `memoryDir()` and the `sync`/`status` cases: baseline `AGENTS.md`, optional memory sink only
  when a memory dir exists or is named. Commands:
  `init`, `discover`, `list`, `pin`, `unpin`, `pause`, `resume`, `when`, `sync`, `status`, `audit`,
  `bootstrap`. Read-only: `discover`/`list`/`status`/`bootstrap`. Registry-only: `pin`/`unpin`/
  `pause`/`resume`/`when`. Only `sync` touches the sinks. Flags: `--when`, `--note`, `--trigger`,
  `--force`, `--all`, `--root`, `--memory`. Resolves the repo root by walking up for
  `.theskills`/`.git`, matches skills by frontmatter `name`, folds YAML block scalars when reading
  descriptions, and exits 2 when it finds drift.

Verified end to end in a scratch repo: pin/sync/unpin/pause/when/audit/bootstrap; sync idempotency
(re-running produces byte-identical sinks); a hand-edited block and a deleted memory file both
detected (exit 2) and repaired; user content above and below the block preserved; the `MEMORY.md`
index line added once with existing entries untouched; typo and uninstalled names refused with the
closest installed matches; a forced pin on an uninstalled skill reported by `status` until installed
or paused.
