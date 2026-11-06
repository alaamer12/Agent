# Case 7 - the recovery screen that had to stay recognizable

**Artifact:** the account-recovery page of a support tool: it must show the owner *which* account/email/
phone a reset is going to, while the page can be shoulder-surfed, screenshotted into a ticket, or logged.
**Destination:** the owner's own eyes - the one case where `partial` mode applies
([`07`](../references/07-partial-masking.md)).

## The request

"/revoke partial - mask these values so the owner recognizes them but nobody reading the screen can use them."

The naive pass: `Amr Muhamed -> A****`, `amr.muhammed@school.edu -> ***@***.***`. Both wrong, in opposite
directions - which is why the mode has rules instead of a format.

## What the rules changed

```text
name      "Amr Muhamed"    -> "A**** M******"     keep head of each token; the initial is the owner's hook,
                                                  near-worthless to a stranger among many A's
email     local part        -> "a************@school.edu"   head kept, length hidden with fixed stars;
                                                  the DOMAIN stays visible on purpose: the owner is deciding
                                                  "which of my addresses", and school.edu is the hook.
                                                  The domain is identifying to attackers - that is acceptable
                                                  HERE because the viewer is the owner; the same string in a
                                                  shared artifact would be a Step-4 finding.
phone     +20 100 555 4821  -> "+20 •••• ••• 4821"  tail-kept: last digits are the convention the owner
                                                  checks; the masked middle holds 10^7 - enough entropy.
account id 71768            -> "****8"             tail-only; head would leak that ids are sequential
                                                  5-digit numbers, which is a shape worth hiding.
```

## The two decisions that were not obvious

**Head vs tail is a threat-model choice, not a style.** For the name, the head is the hook. For the account
id, the head was *the secret* - the first digits of a sequential id tell an attacker the id space. Each row
answered "what does the owner need to recall, and what does a stranger gain?" separately.

**The password field got no mask at all.** "Show first char for recognition" was proposed and refused:
credential-class values have no safe fragment - the first character is a discount on cracking, and partial
mode's rule is that it applies to identifiers, never to secrets. The screen shows `••••••` (full redaction)
and that is the correct outcome.

## The verification that caught a leak

The masked strings sat in a support ticket: `Reset sent to a************@school.edu for customer Amr's
account` - the partial mask was fine, the *prose around it* named the person outright, and the combination
re-identified across the boundary. Fixed by running the ordinary Step-4 combinatorial check over the partial
output like over any other artifact: the mask protects the field, not the sentence.

## The record

```text
map: name -> head-initial fixed stars | email -> head + visible domain (owner-recall need, viewer=owner)
     phone -> last 4 | id -> last 1 (head leaks id space) | password -> FULL redaction, partial refused
formula per class recorded once; every screen renders from the formula, not ad hoc.
residual risk stated: masked email + visible domain identifies the school; accepted because the viewer is
the owner. The same strings must never appear in shared artifacts - flagged in the ticket template.
```
