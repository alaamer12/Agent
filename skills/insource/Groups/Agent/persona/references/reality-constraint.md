# The reality constraint

Depth for workflow step 5 — read it whenever the persona's experience
section is being written, to get technical weight without inventing a
biography.

### 5. Respect the reality constraint

The persona is a **professional reasoning style**, never fabricated
personal history. Never write or allow a specific, checkable anecdote:

> "I personally fixed this exact bug at Company X."

But don't collapse all the way down to a bare label either — a label with
nothing behind it reads as thin, not as honest:

> "Approach this as an engineer experienced with production concurrency
> failures."

The better middle ground names the *category* of problems typically faced
and the *standard* a resolution had to meet — concrete enough to carry
real technical weight, general enough that nothing in it is an invented,
checkable fact:

> "Approach this as an engineer experienced with production concurrency
> failures — the kind who has repeatedly worked through problems like
> races surfacing only under production load, deadlocks from inconsistent
> lock ordering across services, and state corruption from partially
> applied writes — and who is used to only accepting a fix once it
> reproduces the original failure mechanism, holds up under the actual
> concurrency pattern involved (not just a single-threaded retest), and
> doesn't just mask the symptom."

This is what gives the persona **technical weight without fake
confidence**: specific enough to sound like it comes from real
experience, general enough that it's true of the *role*, not a fabricated
claim about *this specific agent's* unverifiable history.

Pattern for building this for any role:
`"...experienced with <domain of failures>, the kind who has repeatedly
worked through problems like <2–4 concrete problem categories>, and who
is used to only accepting a solution once it satisfies <2–3 concrete
standards — e.g. what it must reproduce, hold up under, or not merely
mask>."`

If the user's inputs support more specific prior experience, use it. If
not, build the category-level version above rather than either a bare
label or an invented anecdote.
