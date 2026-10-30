# Case 6 - when there is no safe version, and saying so is the deliverable

**Artifact:** a churn analysis written up with per-account revenue, the reasons each customer gave in
renewal calls, and named competitors they said they were evaluating. Wanted as a slide in a partner deck.
**Destination:** an external company under a standard NDA. Level 3, arguably level 4.

## The inventory did its job

Roughly 60 specific items. Then the test that decides this case: **the artifact's value is the specifics.**

- Revenue per account: the number *is* the finding. Aggregating it to "a material amount" removes the
  argument, not just the identity.
- Customer names: pseudonymizable. But three of them are public case studies, so `[customer-3]` with
  "the one who moved to real-time in March" resolves in one search.
- Verbatim reasons from renewal calls: this is what named individuals said to us, in confidence, about our
  commercial relationship. Revoking their names does not make it theirs to share.
- Named competitors' pricing, from our customers' mouths: unverifiable, third-party commercial information,
  and legally the most interesting row in the document.
- The churn dates: combine with public filings to identify accounts.

## The passes that were tried and why each failed

| Attempt | Result |
|---|---|
| Pseudonymize customers, keep everything else | fails on the two public case studies and the combinatorial dates |
| Aggregate revenue into bands, keep quotes | the quotes remain attributable, and attribution is the exposure |
| Drop the numbers, tell the story qualitatively | no longer a churn analysis - the deck's purpose gone, so over-revoked and useless |
| Remove the competitor rows only | the remaining rows still carry the confidential third-party statements |
| Share only the methodology | safe, useful, and *not what was asked for* - which is the honest finding |

## What was reported instead

```text
DECISION: no sanitized version both travels and teaches.
REASON  : the identifying content is the substantive content; and parts of it are not ours to disclose at all.
OPTIONS : (a) methodology-only slide - pattern, thresholds, how we segment - with the concrete outcomes
             withheld;  (b) aggregate-only view (counts by segment, no accounts, no quotes), cleared by
             whoever owns the customer relationships;  (c) restricted audience - internal, or the accounts
             team, with the full document.
ASKED   : who owns the disclosure decision for verbatim customer statements, and does the NDA permit
          third-party commercial information at all.
```

Two of those are legitimate artifacts that can be produced immediately: the methodology slide, and the
aggregate view. The third is not a revocation problem; it is an audience restriction, which is often the
cheaper and more correct control.

## The failure this case prevents

The tempting move at this point is to produce *something* - a document with 40 placeholders, three surviving
public case studies, and a "fully anonymized" label. That version ships the exposure and launders the
judgment, because nobody challenges a document that claims to have been cleaned.

A stop recommendation is a complete output for this skill. It names what cannot travel, why, what could, and
who decides. `revoke.py verify` cannot tell you this case from a successful revocation - the check that
catches it is the one no script runs: *after removing what must be removed, is anything left that was worth
sending?*
