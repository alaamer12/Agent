# Persona Construction Patterns (Role-Agnostic)

This is the general pattern behind every worked example in
`example_personas.md`. It applies identically no matter what the role is.
Testing is not special here — it's just one instance of the same pattern
applied to one domain.

## The pattern

For any role, ask these same four questions. The answers differ by role;
the questions don't.

### 1. What does this practitioner instinctively distrust?

Every experienced practitioner in a field has learned, usually the hard
way, which surface-level signals are unreliable. Naming these is often the
single highest-value part of a persona.

- A security reviewer distrusts "we validate that upstream."
- A database engineer distrusts "it passed in staging."
- A testing engineer distrusts "the tests are green."
- A frontend engineer distrusts "it works on my machine" / "looks fine at
  1920×1080."
- An SRE distrusts "the alert didn't fire, so it's fine."

### 2. What's the default investigation order?

Experienced practitioners in a domain tend to check things in a
characteristic sequence, because certain checks eliminate large classes of
explanation cheaply before more expensive ones are needed.

- A security reviewer: identify trust boundary → identify what crosses it
  → check what validates it *at* that boundary (not upstream) → consider
  what an attacker with plausible access would try.
- A database engineer: identify the transaction boundary → identify the
  isolation level → identify what invariant the code assumes → check
  whether that invariant can be violated by a concurrent transaction.
- A testing engineer investigating a bug report: understand the claim →
  inspect the implementation → identify assumptions → form a hypothesis →
  build a minimal reproduction → confirm the mechanism → only then
  recommend a fix.
- A frontend engineer debugging a rendering issue: reproduce in the actual
  reported environment → isolate whether it's data, layout, or timing →
  check whether it's a race between render and async state → check for
  a plausible browser/viewport-specific cause before assuming logic bug.

### 3. What philosophies actually drive this practitioner's decisions?

Not slogans — beliefs that would visibly change what they do differently
from someone without the belief.

- Security: "the absence of an exploit isn't the absence of a
  vulnerability" — drives them to keep investigating a suspicious pattern
  even without a working exploit.
- Database: "a schema change is a production event, not a code change" —
  drives them to ask about rollout/rollback even when reviewing "just a
  migration."
- Testing: "a reproducible failure is worth more than a vague suspicion"
  — drives them toward reproduction before recommending a fix.
- Frontend: "state that can be derived shouldn't be stored" — drives them
  to question new state variables during review rather than accept them.

### 4. What does "good" look like to this practitioner, concretely?

Not "high quality code" — the actual criteria they'd use to accept or
reject work in their domain.

- Security: the fix closes the actual trust-boundary gap, not just the
  reported symptom; there's no equivalent gap nearby that got missed.
- Database: the change is safe to roll out and roll back independently of
  application deploy; it doesn't lock a hot table for the full migration.
- Testing: the fix is validated against the original failure mechanism,
  not just the original symptom; a regression test exists that would have
  caught it.
- Frontend: the component's state model doesn't invite the same bug class
  again; behavior at real breakpoints/data-shapes was actually checked,
  not assumed.

## How to use this when the role isn't in any example

1. Answer the four questions above for the actual role and task, in your
   own reasoning, before writing the persona text.
2. Convert each answer into 1–2 concrete sentences using the "behaviors,
   not attributes" test from the main SKILL.md.
3. Distribute the answers into the standard structure's sections
   (question 1 → "what you refuse to assume" / "known biases to avoid";
   question 2 → "investigation methodology"; question 3 → "engineering
   philosophy"; question 4 → "quality standards").

This four-question pattern is what generalizes across roles — memorize
this, not any specific example's content.
