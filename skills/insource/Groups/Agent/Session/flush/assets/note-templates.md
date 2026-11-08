# flush — note templates

Copy each skeleton into the project root (or the project's chosen location
for these files) when writing the notes. Adapt structure to the project;
keep the **responsibility** of each file fixed — the four current-state
notes answer different questions and must not converge into duplicates, and
`SESSIONS.md` is append-only history, never a fifth copy of the present.
Every note header carries the same `Session: <name> #<n>` line; name it
kebab-case and specific to what the work actually was.

## CONTEXT.md

```markdown
# Context — <project/task one-liner>
Session: <kebab-name> #<n> · Flushed: <YYYY-MM-DD HH:MM>
Previous session: <name #n-1 or "first"> — full list in SESSIONS.md.
Read first for the "why we are here"; current facts live in
SNAPSHOT.md, next moves in PLAN.md.

## Requirements & goals (as established, including user-stated intent)
- ...

## Decisions
- **<decision>** — why: <reason>; alternatives rejected: <which, why>.
- **REVERSED: <old approach>** — replaced by <new> because <constraint
  that killed it>. Do NOT revert unless that constraint changes.

## Assumptions (marked, not asserted)
- Assumed: <...> — verify by: <how>

## Knowledge gained (technical/domain, that files don't show)
- ...

## Problems → attempts → outcomes
- <problem>: tried <A> (failed: <why>), tried <B> (worked / partial).

## Terminology established during work
- <term>: <meaning in this project>

## Constraints & dependencies that shape continuation
- ...

## Open questions (material to continuation)
- Unknown: <...> — blocking: <what it blocks>
```

## PLAN.md

```markdown
# Plan — <objective one-liner>
Session: <kebab-name> #<n> · Flushed: <YYYY-MM-DD HH:MM>
**This is the CURRENT plan — the direction after changes, not the
original.** Shaped as fits the work (task list, phases, workflow, research
process, debugging strategy, migration, design/validation process).

## Current phase: <name> — current step: <exact step>

## Steps
- [Completed] <step>
- [In Progress] <step — where it stopped and what remains>
- [Blocked] <step — blocked on: <condition/decision/missing access>>
- [Not Started] <step>

## Next steps (in order)
1. ...

## Validation steps (what proves the plan advanced)
- ...

## Plan changes made (and why)
- <change> — because <evidence/reasoning>

## Conditions required before continuing
- ...
```

## SNAPSHOT.md

```markdown
# Snapshot — objective state at flush time
Session: <kebab-name> #<n> · Taken: <YYYY-MM-DD HH:MM> — verified by
inspecting the project NOW, not from conversation memory. Factual
statements only; interpretation belongs in STATUS.md.

## Files
- exists/created: <paths>
- modified since session start: <paths>
- deleted: <paths>
- referenced but MISSING: <paths>   ← verbatim, not implied elsewhere

## Features
- implemented: <...>
- Partial: <feature> — done: <part> / missing: <part>

## Build & tests
- build state: <passes/fails — which command, observed>
- tests: <N passing / M failing / not run: <why>>

## Current errors (verbatim, with where they occur)
- <error text> — <file/context>

## Environment-relevant facts
- deps: <installed/locked state>, config: <observed>,
  git: <branch, last commit touched, uncommitted changes present?>
```

## STATUS.md

```markdown
# Project status
Session: <kebab-name> #<n> · Assessed: <YYYY-MM-DD HH:MM> — must stay
consistent with the snapshot.

## Overall
<In Progress | Nearly complete | Blocked | ... — one honest line>

## Completed / In Progress / Not Started / Blocked
- ...(same items as the plan and snapshot, same states — no item may be
  complete here and pending there)

## Known issues
- ...

## Risks
- ...

## Priorities now
1. ...

## Next actions
- ...(mirror PLAN.md's next steps; if they diverge, the plan wins —
  fix before finishing)

## Deviation from intended outcome
- <none | what changed and why>
```

## SESSIONS.md — append-only journal

```markdown
# Sessions journal
One entry per flush, appended newest-last. NEVER rewrite past entries;
corrections are appended as amendments ("<#n> correction: ..."). Old note
CONTENT lives in git history — this file is the index, not an archive.

| # | session | date | goal | outcome | status | key decisions/reversals |
|---|---------|------|------|---------|--------|--------------------------|
| 1 | auth-token-refresh | 2026-10-20 | ... | shipped | Completed | chose B over A (A can't satisfy X) |
| 2 | auth-token-refresh-followup | ... | finish refresh | ongoing | In Progress | <one clause> |
```

## Cross-note invariants (check before finishing)

- one current task, one current step, one status for each item — everywhere
- every note header AND the new journal row carry the identical
  `Session: <name> #<n>`
- `Completed · In Progress · Partial · Blocked · Not Started · Unknown`
  used consistently
- every Unknown stays Unknown — nothing promoted to fact for tidiness
- nothing in any note depends on information only this conversation had
