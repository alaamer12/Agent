# Transaction failure

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** server/provider-confirmed failure, decline, or timeout on the consequential
action — *plus the unresolved middle*: a timeout where the outcome is unknown is its own state
and gets its own copy ("we could not confirm — check your bank before retrying"), never
silently drawn as either success or failure.

**The hierarchy of jobs:** tell them what did not happen → tell them what happened to the
money/attempt → give the exits. Every one of those beats any explanation of *why* — cause
text is third, and only in human terms ("card issuer declined" not `code 05`), with the raw
code available for support, never as the sentence.

## Exits (all of them, this family more than any)

- **Fix-and-retry path** — the one that addresses the actual failure class: expired card →
  update method; insufficient funds → different method; network timeout → check-status then
  retry; provider unavailable → try later. A retry button that re-sends the *identical
  doomed attempt* is decoration.
- **Alternative route** — change method, save-for-later, different provider — offered when
  the product has one.
- **Safe abandon** — explicit "nothing was charged / your cart is kept", then the way home.
  The reassurance line *is* the feature; a person who cannot tell whether they got charged
  calls their bank, not support.

## Laws specific to this family

- **Retry obeys the contract** — if the project keeps `automatic_retry`/`manual_retry`
  ownership contracts, this page renders only what they permit: no silent auto-loop, no
  manual button before automatic policy exhausted. The page serves the policy; it does not
  invent one.
- **Never re-ask silently for secrets** — a failure that returns the person to a form must
  not pre-fill or cache card/PIV data beyond what rules allow; fields cleared honestly beat
  convenience with exposure.
- **The unknown-state page is a first-class design** — the timeout/pending screen needs its
  own anatomy row (source: provider status lookup + local transaction state), because both
  wrong guesses here cost money.
- **Support anchor** — reference id + timestamp visible even on failure; failures generate the
  tickets, and the page is what the agent reads over the phone.

## Anti-patterns

Blame-shaped copy ("you entered it wrong"); a red wall of text that never says whether the
attempt happened; retry the same card 5× as if persistence defeats declines; hiding the
"nothing was charged" line because the vendor's response is ambiguous — that ambiguity means
this is the *pending* page, not a failure page with false reassurance glued on.