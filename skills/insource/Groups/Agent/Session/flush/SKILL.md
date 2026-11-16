---
name: flush
version: 1.1.0
author: Amr
specialized: none
description: 'Agent continuity capture, manual — persist working state before session end, environment change, loss, milestone, handoff, or when the conversation grew too large: CONTEXT.md (how we got here — decisions, reversals, what worked/failed, open questions), PLAN.md (the ACTUAL plan, not the original), SNAPSHOT.md (facts verified against the project, not memory), STATUS.md (assessment) — one job per note; compression, never transcript or continuation. Each flush carries an agent-chosen kebab-case session name with a sequence number in every note header and appends one entry to the append-only SESSIONS.md journal, so later sessions see each session''s record; past entries are never rewritten and git owns old note content — no hand-rolled archives. Uncertainty stays Unknown, partial work is never written as done, stale notes are replaced not accumulated, cross-note consistency checked before completion. The companion context skill reads these back. Triggers: flush, save/persist state, hand off the project.'
---

# flush — persist the state that files alone cannot recover

**Core principle: the current conversation contains more than can safely be
reconstructed from the project's files.** Flush converts that working
context into four persistent notes so another agent or a future session
resumes with minimal loss. It does not continue the task and does not solve
the project problem — its whole job is capture.

The four questions the notes answer, together:

```text
CONTEXT.md   → Why and how did we get here?
PLAN.md      → What are we doing and how?
SNAPSHOT.md  → What objectively exists right now?
STATUS.md    → What is the overall state and progress?
SESSIONS.md  → Which sessions happened, and how did each one end?
               (append-only journal — see "Session identity")
```

Copyable skeletons for all four: `assets/note-templates.md`. The consumer of
these files is the `context` skill (its "Flush notes" step reads exactly
these filenames) — write so a reader who never saw this conversation can
reconstruct the working state from the notes alone.

## What each note owns

One job per note, with its include list, its exclusions and its governing
rule — CONTEXT (reconstruct, never transcribe), PLAN (the actual current
plan), SNAPSHOT (facts, not interpretation), STATUS (the assessment):
[`references/note-responsibilities.md`](references/note-responsibilities.md).

## Invocation — manual, by design

Flush is **not an automatic interruption handler**. Agent or user invokes it
deliberately. Typical points: before moving work to another machine or
environment · before ending a long session · before expected context loss ·
after a major milestone · before handing off to another agent · when the
conversation is too large to continue safely · before resetting/replacing
the session.

## Freshness — verify before writing

Flush represents the state **at the moment it is invoked**. Memory is the
worst source here. Before writing anything:

1. If notes and `SESSIONS.md` already exist, read them — the flush extends
   that history, it does not overwrite blindly.
2. Inspect the current project state where possible (files, `git status`,
   existing config) — reconcile it with the conversation, and prefer the
   verifiable state when they disagree.
3. Update the plan to reflect what *actually* happened.
4. Capture the true current snapshot.
5. Determine the current status from the snapshot, not from optimism.
6. Write the four notes and append the journal entry.

Never blindly reuse old notes that no longer represent reality.

## Preservation rules

- **Decisions:** when a decision materially affects future work, preserve
  the decision *and* the reasoning needed to maintain it — not unnecessary
  internal reasoning.
- **Changes of direction:** keep the final decision plus enough history to
  explain why the old direction must not be resumed
  ("approach A rejected because it couldn't satisfy X; do not revert unless
  the underlying constraint changes").
- **Uncertainty:** never turn uncertainty into fact. Mark it explicitly —
  `Unknown: the production configuration has not been verified` — instead
  of writing a plausible claim.
- **Incomplete work:** never write partial as done. Use explicit states —
  `Completed · In Progress · Partial · Blocked · Not Started · Unknown` —
  where useful.

## Notes are living files

If any of the four already exist: **update them — never create conflicting
duplicates.** Preserve historical information while it remains relevant;
remove or replace what is demonstrably obsolete. Stale state does not get
kept "for completeness" — a note that misleads the next agent is worse than
a missing one.

## Session identity & continuity across sessions

The four notes always describe **the latest flush**. What happened over
*many* sessions lives in `SESSIONS.md` — an append-only journal, one short
entry per flush. This is what makes follow-up work ("we did this in an
earlier session, pick it up") and entirely different later sessions safe:
the reader sees which sessions happened, what each was for, and how it
ended, without the notes accreting into a history dump.

**Every flush names its session.** The agent derives a short kebab-case
name (2–4 words) from what the work *actually was* — specific, not
decorative: `auth-token-refresh`, `mine-skill-pdf-mining`,
`search-perf-audit` — never `work`, `update`, `session-3`. Sequence numbers
come from the journal's current length, and a name already taken gets a
more precise qualifier, not a suffix fudge. Every note header carries
`Session: <name> #<n> · <date>`, plus the previous session when relevant —
so any note read alone still says which era it belongs to.

**Follow-up procedure** (notes already exist):

1. Read `SESSIONS.md` and the four notes first — that is the incoming
   working state, exactly what the `context` skill reconstructs.
2. Work, then flush: update the four notes to the *new* current truth and
   **append** this session's journal entry (name, date, goal, outcome,
   status line, notable decisions/reversals in one clause each).
3. Never rewrite past journal entries — corrections are appended as
   amendments, since "session 4 believed X and session 7 fixed it" is
   itself useful continuity.

**No hand-rolled archives.** Old note *contents* are already preserved by
the project's version control — `git log -- SNAPSHOT.md` outlives any
copy-directory scheme. If the project has no VCS, say so once in the
journal and keep only the freshest notes; do not silently fork the files
into numbered duplicates.

## Checks before finishing

The cross-note consistency pass and the final validation checklist are the
gate on completion — run both:
[`references/consistency-checks.md`](references/consistency-checks.md).

## Handoff goal

A new agent must be able to run:

```text
read SESSIONS.md (how we got here, briefly)
→ read CONTEXT → read PLAN → read SNAPSHOT → read STATUS
→ reconstruct working state → continue the work
```

without the original conversation and without rediscovering what the
project is, what already happened, why decisions were made, the current
plan, what exists, and what remains. (The `context` skill is exactly this
reader — flush exists so context never has to guess.)

## Reference index

| File | Load when |
|---|---|
| `references/note-responsibilities.md` | writing any note: its include list, exclusions, governing rule |
| `references/consistency-checks.md` | finishing: cross-note consistency + the final validation list |
| `assets/note-templates.md` | the copyable skeleton of each note and of the `SESSIONS.md` journal |
