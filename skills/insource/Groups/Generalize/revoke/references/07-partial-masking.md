# Partial masking - showing enough that only the owner recognizes it

Requested only as `/revoke partial`. Never entered because a redaction looked like it could use it: the
normal rule of this skill is that partial masks **leak** (a shape-revealing `a**@acme.com` is a Step 4
finding, not a technique), and the whole point of this mode is that sometimes the leak is the feature.

## When the leak is the feature

A recovery or confirmation screen has one viewer who matters: the owner. "Amr Muhamed" is their own name;
they do not need it revealed, they need to recognize which record is theirs while everyone else in the room,
in the screenshot, or in the log sees nothing usable. So the artifact is not sanitized for a wide audience -
it is *shrunk to a fragment only its owner can verify*:

| Source value | Head-kept | Tail-kept |
|---|---|---|
| `Amr Muhamed` | `A**** M******` | `***r *****d` |
| `amr.muhammed@school.edu` | `a***@school.edu` *only if the domain is safe to show* | `***@school.edu` |
| an account id `71768` | `7****` | `****8` |

The fragment is the hook the owner checks against their memory; the masked body is what a stranger cannot
finish. Same operation under other names: email recovery ("we sent a link to a***@***.com"), the bank card's
last four, the phone ending - 4821.

## The rule that keeps it honest

**Keep the fragment that identifies *to the owner*; mask every part that identifies *to everyone else*.**
That distinction does the work:

- A name's first letter is a hook for its owner and near-worthless to a stranger - good fragment.
- A card's last four digits are the convention: the owner knows them, and four digits of a 16-digit value
  leave 10^12 of hidden entropy - good fragment.
- A domain is the opposite of both: `***@acme.com` tells the owner nothing they need (they know their email)
  while telling an attacker exactly which customer list to target - the tail-kept form of an email is usually
  the *wrong* one to show. Choose head vs tail by what the owner must recall and what an adversary gains,
  not by symmetry.
- Never fragment where the whole shape *is* the secret: API keys, one-time codes, password characters, and
  short joinable values. A password's first letter is not a courtesy, it is a discount on cracking it. If the
  value is credential-class, this mode does not apply - full redaction or nothing.

## Entropy, not aesthetics

`****` is a mask; how much it protects is the hidden part's guess-space, so:

- **Fixed-length `****` hides the length; length-preserving `A**********` leaks one more fact** (a 12-char
  token is shaped like a token). Recovery UIs standardize on fixed-length masks precisely for this; keep the
  real length only when the owner needs it to distinguish between two of their own values.
- Below roughly three visible characters of a large space, or above roughly four of a small one
  (first-initial + surname in a 40-person company is a lookup, not a guess), the fragment has stopped being a
  hint and started being an answer. Say so when the user asks for a mask that cannot hold.
- Fragments compound. The head of the name, plus the domain, plus "your order from March" in the sentence
  around it can re-identify across the boundary of the mask - run the ordinary Step 4 combinatorial check
  over partial output like over any other artifact.

## Two artifacts, one discipline

`/revoke partial` produces two things people confuse:

1. **A mask formula** - how this value class is always shrunk (`name -> keep initial of each token, fixed
   four stars`). Chosen once, applied consistently, recorded in the substitution map like every other
   decision: same value, same fragment, everywhere.
2. **A display convention** - where the masked form may live (a screen for a signed-in owner) and where it
   must not leak (a shared report, a log line, a screenshot in a postmortem - if the fragment survives into
   those, the partial mask becomes an accidental live leak, which is how `a**@acme.com` earned its warning in
   the first place). A partial-masked string inside a normal shared artifact is a verification failure, not
   a technique - except when it is the *point* ("we emailed a***@***.com" in a comms postmortem), which gets
   said as a decision with the fragment justified, not shipped silently.

## Boundaries

- The owner-verification assumption is load-bearing: confirm the viewer is the owner (a recovery screen, an
  account page). If the artifact will be seen by anyone else, this mode is the wrong tool and the ordinary
  five operations apply.
- A fragment is not an authentication factor. Anyone who can watch a screen sees `A****`; recognition is a
  UX affordance, and "the owner recognized it" must never close a security decision by itself.
- Partial masking of *other people's* values for *your* screen ("which contact should I confirm?") inherits
  every authority rule from the parent skill: you may shrink only what you were allowed to show at all.
