# Onboarding & first-run

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** `setup incomplete` for this account/install — a real server-side (or device)
boolean, not "first visit" guessed from localStorage.

**The shape:** one *step* = one decision the product needs from a person who has not yet been
shown why. Order steps by dependency of understanding, not by database column order.

## Laws specific to this family

- **Skippable** — every step that can be deferred without breaking the product shows a skip;
  "you must set up a workspace to see the app" converts an optional journey into a wall, and
  walls are churn.
- **Resumable** — mid-onboarding exit returns to the same place next time, with progress
  kept. A person who abandons at step 3 is not a new person tomorrow.
- **Replayable** — a way back in from the app proper (help/settings entry). Someone competent
  in month two still asks "what did that setup mean"; and support asks them to walk it.
- **The condition updates truthfully** — completing step *n* must persist to the real
  condition source, or the app re-onboards a person who finished, which teaches that nothing
  they do is remembered.
- **Empty-state handoff, not duplicate** — onboarding *teaches the first action*; the
  populated view's empty states (another skill's surface) show *what to do next without
  lecturing*. Decide which owns each moment so the product explains itself once.

## Reachability states

Cold deep-link while already onboarded → redirect into the app (never "complete again for
fun"). Logged out → the login gate is `session-gates`; onboarding resumes after, at the step
interrupted. Second device mid-flow → same progress, or an honest "continue on the other
device? no — start here" decision made here, not discovered later.

## Anti-patterns

Feature tour that overlays the real UI and captures clicks (teach *in* the interface where
possible); 9-dot pagination that announces its own size before any value is shown; "welcome
aboard" screens that exist purely as celebration with no decision — that is
`transaction-success`'s job at the right moment, not a step; marking every checkbox
"recommended" so none is.