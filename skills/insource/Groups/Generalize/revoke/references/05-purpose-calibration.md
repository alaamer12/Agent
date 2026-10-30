# Purpose calibration - the destination sets the budget

The same document sanitized for four destinations produces four different artifacts. Decide the destination
first; almost every bad revocation is an unasked question about who reads this.

## The levels

### 1. Internal, same team, different repo

- **Aggressiveness:** low. Revoke credentials and anything a stranger to the team could misuse.
- **Must survive:** real system names, ticket IDs, internal URLs, exact timestamps - the team needs to look
  things up. Over-revoking here creates an artifact nobody can act on, which is its own defect.
- **Typical moves:** redact secrets, keep everything else.

### 2. Company-wide

- **Aggressiveness:** medium. Customers, contracts and unreleased product details stop being usable as casual
  reading material.
- **Must survive:** role names, service names, the causal chain, the numbers that teach the lesson.
- **Typical moves:** pseudonymize customers, generalize pricing, keep architecture, aggregate per-account
  figures.

### 3. External public - blog, talk, open-source issue, vendor forum

- **Aggressiveness:** high, and combinatorial thinking is mandatory. Assume the reader searches.
- **Must survive:** the mechanism and at least one quantitative anchor, in rounded or relative form.
- **Typical moves:** pseudonymize or omit organisations, generalize stack and region, replace dates with
  relative timing, aggregate counts, strip internal tool names, genericize filenames, scrub metadata, and
  check that the remaining incident shape is not unique.
- **Extra question:** are you allowed to publish at all - does a customer contract, an NDA, or a disclosure
  policy gate this? That is their call, not yours; flag it and continue preparing the draft.

### 4. Handed to a third party - a hosted model, a contractor, a support vendor

- **Aggressiveness:** high, plus a policy check before anything leaves.
- **Must survive:** only what the third party needs to answer the specific question.
- **The question that decides the level:** *whose data is this?* Customer records, employee data, and internal
  source code are not yours to route to a vendor by sanitizing them. Revoke harder, ask first, or restate the
  problem without the artifact.
- **Also:** retention and training use are separate from identifiability - a "clean" paste can still be a
  disclosure.

### 5. Regulated content - personal, health, financial, security findings

- **Aggressiveness:** highest, and the decision is not the agent's.
- **Must survive:** the lesson. Sometimes nothing else can.
- **Move:** draft the minimal version, state the residual risk, and route it to whoever owns the disclosure.
  Do not self-authorize. Undisclosed security findings get an additional rule: revoking the vulnerability
  detail from a shared document is fine, but the affected party's disclosure timeline is not a formatting
  question.

## If the destination is unstated

Ask one question and stop guessing: *"Where is this going - company-wide, public, or to an outside tool?"*
Three answers, three budgets. This is the one case where a clarifying question is cheaper than a wrong pass,
because a document sanitized too lightly gets re-done and one sanitized too hard has quietly lost the thing
the reader came for.

## Calibrate the loss, not just the leak

At the aggressive levels the binding constraint is not "did I remove enough" but "is what remains still
worth sending". A public postmortem with no causal story and no numbers should not be published - say so.
The deliverable in that case is either a rewrite that carries the lesson at a coarser grain, or the finding
that this artifact cannot travel.
