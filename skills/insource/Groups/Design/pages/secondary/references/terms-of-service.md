# Terms of Service

The contract between operator and user: what both sides may do, what breaks the deal, and what
happens after. Referenced by every other document; the canon location question (`presentation.md`)
starts here because signup flows on ALL platforms accept it.

## Must include, in this order

1. **Who and what** - the operator entity (config-sourced, `engineering.md` §1), what service the
   terms cover, what they do not (third-party integrations, store platforms).
2. **Effective date + change policy** - dated header; how changes arrive ([notice by email],
   [in-app], "continued use = acceptance" stated honestly, material changes get real consent where
   the project chooses it).
3. **Accounts** - who may hold one (age gate → child-privacy pointer), responsibility for
   credentials, one-person-one-account stances, transfer prohibition, deletion (`delete-account.md`).
4. **Acceptable use - violations and consequences** - the user's own demand, in two halves:
   what counts as a violation (link the AUP as the canon list rather than restating it) AND what
   each violation leads to: the enforcement ladder - [warning] → [feature limited] → [suspension]
   → [termination] - severity mapping stated, not hidden.
5. **Content** - who owns what users bring, what license the operator takes over it (the minimum
   needed, said plainly), and the takedown path (`takedown.md`).
6. **Payments** (if paid) - price changes, billing cycle, cancellation, refund policy pointer
   (the window itself lives in `refund-policy.md`, never restated).
7. **Disclaimers + liability limits** - with a plain-language summary line above the clause.
8. **Termination effects** - what dies, what survives (billing records with retention from the
   Privacy document), how to appeal.
9. **Disputes** - governing law and venue: ASK the user (jurisdiction is a fact about them, not a
   template field).
10. **How to reach a human** - contact pointer.

## Writing professionally

- Second person, short sections, a one-line summary ABOVE each dense clause ("In short: we can
  pause the account for confirmed abuse; you can appeal."). Deliberately confusing ToS is
  documented research territory and legislated against - plain language is the standard, not a
  favor.
- Every "we may X" gets its when and its check; every prohibition gets its consequence.
  A rule without an outcome is a wish.
- Cross-link the set: Privacy owns data facts, AUP owns the violation list, this owns the deal.

## Ask the user - never invent

Service description; violation severities and the ladder; jurisdiction/venue; notice channel for
changes; data classes (pointer to Privacy); age threshold; anything about money.

## Failure patterns

Generator text with a wrong or absent entity name; "we may monitor anything forever" clauses that
contradict the Privacy document (two owners, disagreement); violations defined nowhere while
termination is claimed everywhere; a ToS that restates retention days (drift waiting to happen).

*Not legal advice: transparency and internal consistency are the goal; review with counsel for
the project's jurisdictions.*
