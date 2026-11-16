# Quality check and anti-patterns

Depth for workflow step 9 — read this immediately before returning the
finished persona: the self-review questions and the failure modes they are
meant to catch.

### 9. Final quality check before returning the persona

Run through these questions. If any answer is "no," revise before
returning:

- Can I tell what this engineer would notice that an ordinary agent
  would miss?
- Can I predict how this engineer would investigate a problem in their
  domain?
- Does the persona contain actual mental models, not just labels?
- Does the experience section influence behavior, not just list nouns?
- Does the philosophy section influence decisions, not just sound nice?
- Is it specific to this task and domain, not swappable to any other?
- Does it avoid generic "expert" language unless immediately cashed out
  behaviorally?
- Does it avoid fabricated personal history?
- Would this persona cause the subagent to behave differently from a
  different role given the same task?

## Anti-patterns to avoid

- Listing every dimension from the menu regardless of relevance.
- Generic trait adjectives ("detail-oriented," "highly skilled") without
  behavioral payoff.
- Superhuman experience — a persona that has personally encountered every
  failure mode in existence. Keep it to what a real specialist plausibly
  has encountered.
- Checklist-driven philosophy for any role ("run through these 50 checks")
  instead of hypothesis-driven, high-information investigation.
- Fabricated specific personal history ("I fixed bug #4471 at my last
  job").
- Copy-pasting the full criticism protocol from the orchestration system
  into the persona instead of just the professional's angle on it.
- A persona identical in substance to one written for a different
  role/task — if nothing in it is actually tied to this context, it
  hasn't done its job.
- Treating any one role (including testing) as the "main" case with
  special built-in machinery, while other roles get generic treatment.
  Every role goes through the same construction process in section 3.
