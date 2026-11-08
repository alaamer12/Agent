---
name: flush
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

## The four notes — responsibilities and boundaries

### 1. CONTEXT.md — working context

The deepest note: how we arrived here and what the next agent must
understand. Include: user requirements and goals · important decisions and
their reasons · decisions changed or reversed · relevant assumptions ·
constraints · important discoveries · technical/domain knowledge learned
during the task · problems encountered · solutions attempted, worked, and
failed · trade-offs · relevant dependencies · terminology established
during work · earlier-conversation context that affects current work ·
unresolved questions that materially affect continuation.

Exclude (this is compression, not archiving): casual conversation,
greetings, repetitive discussion, tool-call noise, internal execution
details with no future value, temporary reasoning that doesn't affect the
resulting understanding, repeated versions of the same fact, information
represented more accurately elsewhere.

Rule: **never copy the conversation verbatim — reconstruct the meaningful
working context.**

### 2. PLAN.md — the current operating plan

Any form appropriate to the work — task list, phased implementation plan,
workflow, research process, debugging strategy, migration plan, design or
validation process, or a combination. **Do not force every project into a
generic TODO list.** Include: main objective · current phase · planned
phases · tasks/subtasks · dependencies · completed steps · the current step
· next steps · blocked steps · validation steps · important changes made to
the original plan **with their reasons** · conditions required before
continuing.

Rule: it must be the **actual current plan** — the latest valid direction
wins over the plan the conversation started with.

### 3. SNAPSHOT.md — objective point-in-time state

Answers *what objectively exists right now* — not how we got here (that is
CONTEXT.md) and not evaluation (that is STATUS.md). Include (as
applicable): existing/created/modified/deleted/missing files · implemented
and partially-implemented features · configurations · current architecture
· data/state · dependencies · tests **and current test results** · current
errors · build state · environment-relevant facts · other verifiable state.

Rule: **prefer factual statements over interpretation** —
"`src/search.ts` exists; the filter implementation is incomplete; search
tests currently pass" — never "the project is almost finished" (that
belongs in STATUS.md). Verify these claims against the project before writing
them.

### 4. STATUS.md — high-level assessment

Answers *where the project stands*: overall status · completed · in
progress · remaining · not started · blocked · known issues · important
risks · current priorities · immediate next actions · milestones · any
major deviation from the intended outcome. Structure (see templates) may be
adapted when another format represents the project more accurately.

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

## Consistency check before finishing

Compare the four notes against each other:

- context does not contradict the current plan
- plan reflects the current project state
- snapshot reflects the actual state at flush time (re-verified)
- status is consistent with the snapshot
- nothing is completed-and-incomplete at once; blocked tasks are described
  the same way everywhere; the current task is the same task in all notes
- recent important decisions appear wherever they matter
- no note depends on information that only existed in this agent's memory
- all four notes and the new journal entry carry the same session name and
  number

On conflict: resolve with the most recent, most reliable information — for
objective state, directly verifiable project facts beat remembered
conversation.

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

## Final validation

- [ ] `CONTEXT.md` holds the meaningful working context
- [ ] `PLAN.md` is the current, actual plan
- [ ] `SNAPSHOT.md` matches the project as verified at flush time
- [ ] `STATUS.md` is consistent with the snapshot
- [ ] the four notes do not materially contradict each other
- [ ] stale information removed or corrected
- [ ] important decisions preserved with their reasons
- [ ] incomplete work clearly marked; unknowns not presented as facts
- [ ] conversational and execution noise removed
- [ ] a new agent could continue from these notes alone
- [ ] the session is named specifically (`kebab-case`, 2–4 words, what the
  work actually was) and every note header carries it
- [ ] `SESSIONS.md` was read at start and this flush's entry appended —
  past entries untouched
