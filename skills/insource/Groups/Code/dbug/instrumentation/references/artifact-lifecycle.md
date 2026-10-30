# The `.debugging/` artifact lifecycle — full rules

Source: `data/debug.txt` §7–9, §13. The system exists so debugging is
repeatable **without** one-off scripts and incident notes calcifying into
permanent project complexity.

## Layout

```
.debugging/                (repo root, like .htd/ — once per repo, not per package)
├── tmp/                   this session's workspace — empty at session end
├── instruments/           promoted, generalized, reusable debug/verify tools
└── bugs/                  significant investigation records (markdown)
```

First use: create the directories as needed. Add `.debugging/tmp/` to
`.gitignore` if the user agrees (it's by definition disposable; `instruments/`
and `bugs/` are worth committing — they're the durable output).

## `tmp/` — rules of the workspace

- **Everything ad-hoc starts here**: inspection scripts, repro drivers,
  verification checks, prepared escalation SQL (for the user to run —
  investigation §7 protocol), scratch notes.
- Script contract (universal, any language):
  1. self-contained env loading (never hardcode secrets — resolve per
     `../../backend/references/env-and-resolution.md`);
  2. deterministic exit code: `0` = condition holds, `1` = violated — so
     the same file serves as manual check, bisect driver, and CI-able probe;
  3. read-only by default; anything mutating runs inside a transaction and
     ends `ROLLBACK` unless the explicit purpose is applying a change;
  4. closes connections/handles in `finally`;
  5. prints what it checked and the verdict, with credentials redacted.
- Nothing in `tmp/` is allowed to be imported by production code paths.

## Promotion: `tmp/ → instruments/`

A tool is promoted when **all** hold:

| Criterion | Test |
|---|---|
| Reusable beyond this bug | it checks a *class* ("does live DB match schema file for table T?"), not one incident |
| Generalized inputs | incident constants become parameters (`--table users` → `--table`), env/config, never hardcode |
| Will realistically be needed again | schema drift, env checks, dep audits recur in most projects |
| Acceptable to live in the repo | user agrees (dbug gate #3) — promotion adds permanent maintenance surface |

Promotion procedure:
1. Rewrite for generality (parameters, no story-specific names/values).
2. Prepend the header block
   ([`../assets/instrument-header-template.md`](../assets/instrument-header-template.md)):
   purpose, usage, inputs, origin-bug pointer.
3. Move file `tmp/<one-off>.ext → instruments/<verb-object>.ext`.
4. Delete the `tmp/` original; note the promotion in the session summary.

Example: `tmp/verify-users-schema.py` (table name baked in) proves its
worth → rewrite as `instruments/verify-schema.py --table <name>` → usable
for `users`, `orders`, every future drift suspicion.

Do **not** promote reflexively. One-shot repro wrappers, migration-specific
patches, "check the thing we just broke" probes: their job done → deleted.

## `bugs/` — when an investigation becomes a record

Write one when **any** of:

- the root cause was *non-obvious* (a trap, a hidden coupling, an
  environment difference) such that rediscovery would cost real time;
- the same class of failure plausibly recurs (stale cache after deploys,
  drift after manual DB edits);
- hypotheses and *rejected* explanations carry signal ("we proved it
  wasn't the pool — here's the evidence");
- the fix involved an unusual escalation or external step worth scripting
  next time.

Otherwise: skip it (commit message + PR description suffice). Not every
bug is a story; a `bugs/` folder full of trivia is worse than none.

Record = [`../assets/bug-record-template.md`](../assets/bug-record-template.md),
filename `bugs/<yyyymmdd>-<short-slug>.md`. Keep it short — a page; the
template sections are ceilings, not minimums.

## Session-end cleanup checklist

- [ ] every `tmp/` file: promoted, folded into a committed test, or deleted
- [ ] promoted instruments carry header blocks + generalized inputs work as claimed (run once)
- [ ] bug record written **or** a one-line "no record — cause trivial" noted
- [ ] debug logging left behind: either gated-and-deliberate (fine) or removed
- [ ] `.debugging/tmp/` physically empty (not just "should be")
- [ ] procedure candidate identified → hand to **how-to-do** (it owns `.htd/`;
      dbug never writes `.htd/` files itself)
