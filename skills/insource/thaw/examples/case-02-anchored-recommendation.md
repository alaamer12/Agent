# Case 02 — defending your own earlier pick

## The situation

Early in a design session an agent recommends a custom API framework for a project's backend, and the
user accepts. Several turns later the user's priority sharpens: *"I want to write less code and lean on
a BaaS for auth and storage."* The agent keeps proposing the custom framework, adding a thin service
layer each time the user pushes toward less code.

## The freeze

The agent is **anchoring on its own earlier recommendation**. It said the framework first, so it keeps
defending it — patching the design to preserve the pick instead of re-deriving from the goal. It also
treats the user's earlier "yes" as a settled mandate, though the goal has since changed.

## The thaw

1. **Notice the freeze.** "I'm defending last turn's framework because I picked it, not because it still
   serves the goal."
2. **Split invariant from mechanism.** Invariant: *clients get a safe, typed contract; integrity logic
   runs server-side.* Mechanism (draft): *a custom framework service.* The mechanism is not the goal.
3. **Re-open the option set.** A BaaS that supplies auth, storage, and server-side functions can satisfy
   the invariant with far less code. The custom framework is back on the table as *one* option, not the
   default.
4. **Question both sides.**
   - Own pick: steelman it (control, portability), then attack it (more code and ops than the stated goal
     warrants; the goal moved).
   - User's earlier answer: their first "yes" was under the old frame. The new less-code priority outranks
     it. Surface this; let them re-decide.
5. **Aim for better.** Re-derive from the invariant + the current priority. The BaaS-centric design is
   now the better fit; the custom framework is recorded as a rejected alternative with its trade-off.
6. **Re-close provisionally.** Write the new decision; mark the old one superseded, not erased.

## What it settles

A recommendation is a **hypothesis, not a possession**. When the goal or evidence moves, re-derive —
don't patch the old answer to survive. And the user's prior answer is input under the frame that produced
it; a changed frame reopens it. New evidence beats old answers, yours and theirs.