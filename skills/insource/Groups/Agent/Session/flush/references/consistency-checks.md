# Checks before finishing

Run both lists at the end of every flush: the cross-note consistency pass,
then the per-note validation. They are the gate on "this flush is done".

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
