# Case 3 - support ticket thread to pattern documentation

**Artifact:** a 24-message support thread about a customer whose nightly sync silently stopped. Wanted as
documentation of the failure pattern for the whole support org.
**Destination:** company-wide. Level 2.

## The inventory that mattered

Personal and customer data dominate here, and the interesting decisions are about *roles* and *times*:

```text
customer company + account id     | pseudonymize | [customer-1], [ACCOUNT-ID]
  (the account id is how support would look it up - inside the company it is kept, outside it never is)
customer contact name + email     | pseudonymize | [customer-admin]
  role, not person: the thread's lesson is about a role's behavior, so no stand-in person is needed
three agent names + internal IDs  | pseudonymize | [support-1], [support-2]
our Slack escalation channel      | generalize   | the escalation channel
ticket ref TICK-44812             | keep         | same-org audience needs the trail
every timestamp (14:02, 14:03…)   | generalize   | relative: "day 1 morning", "about 30 hours later"
the error string from the customer| keep verbatim | it is the diagnostic content; verbatim is the value
customer's file names             | pseudonymize | [import-1.csv] … keeps multiplicity
```

## Why timestamps went relative and names went roles

Absolute timestamps plus a customer name plus a region pin the event to a specific outage window that the
customer may not have disclosed publicly. Relative timing preserves the only thing the pattern needs - *the
sync died and nobody noticed for a day and a half*.

Names became roles because the thread's lesson is structural: *the person who could approve the change was
not the person watching the alert.* `[customer-admin]` and `[support-2]` carry that; `Marta` and `Sam` carry
nothing extra and two people's identities.

## What the first pass got wrong

The draft collapsed the two agents into one placeholder. The escalation story - support chased the vendor
while a second engineer independently restarted the job, which is why the cause was found twice and the fix
was applied once - became nonsense. `verify` flagged the collision; `[support-1]` and `[support-2]` restored
the point. **This is the meaning-survival rule earning its keep:** a sanitized document that merges actors
loses the causal chain the reader came for.

## Report

```text
INVENTORY: 41 items  redacted 4 | pseudonymized 22 | generalized 9 | aggregated 2 | kept 4
LOST     : exact times, the customer's own file names, who personally approved the restart
RESIDUAL : low for internal use - ticket ref kept, so the trail survives inside the company
ORIGINAL : untouched in the ticketing system   MAP: retained with the source, not in the doc
```

The kept ticket reference is the instructive line: at level 2 it is a feature (traceability), at level 3 it
would be the leak. Same artifact, different destination, different map.
