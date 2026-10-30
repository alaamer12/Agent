# The Danger card — seven lines that make a cost real

> **Illustrative, not exhaustive.** The wording below is a shape. Adapt the sentences to the project's own
> language — the fields are the contract, not the phrasing.

The card exists for one moment: the user has just answered, the answer is costly, and they do not yet know how
costly. It is not a document and not a lecture. If it takes more than a few seconds to read, it will be skimmed,
and a skimmed warning is worse than none.

## The card

```text
!! DANGER — <the decision, in the user's own words>
What is gone: <the protection that stops existing>
How it fails: <actor> can now <action> on <asset>, because <the missing guard>
If it happens: "<postmortem headline, past tense, a year from now>"
Blast radius: <who/what, how much, how long>
Undo cost: now <…> · later <…>
Cheapest adequate option: <the smallest guard that removes the exposure>
```

Then the question, exactly once:

> **Are you sure?** Reply "yes, accept the risk" to proceed — or take the alternative and we move on.

A copy-ready version with the WARN and NOTE variants is in
[`../assets/templates/danger-card.md`](../assets/templates/danger-card.md).

## Writing each line

**The decision, in the user's words.** Quote the answer, not your interpretation: *"no E2EE, sounds
complicated"*. It confirms you heard them, and it is what they will remember saying.

**What is gone.** Name the protection, not the badness. "Traffic between the two devices is no longer encrypted"
— not "security is compromised". If the protection never existed, say that: "no guard was ever added; you are
choosing not to add one".

**How it fails.** One sentence with an actor and an asset: *who* can now do *what* to *whose* data. Passive
voice hides the actor, and an actor-less risk reads as superstition.

| Weak | Strong |
|---|---|
| "This is insecure." | "Anyone on the same Wi-Fi can read the sync traffic; a coffee-shop network is enough." |
| "Storage will explode." | "1.4 GB/day at today's rate: 500 GB in a year, and the nightly backup window is already 5 h." |
| "You will regret dropping backups." | "A failed migration leaves no state to restore from; recovery then means asking every user to re-enter their data." |

**The postmortem headline.** The most effective line in the card, because it converts an abstraction into a
sentence someone would have to write later:

```text
"<What happened> because <the missing guard> — <how it was discovered>"

"Sync traffic between phone and laptop was readable on shared Wi-Fi: session tokens captured at a
conference network; accounts taken over and reported two days later."

"The events table reached 1.4 TB in seven months, backups silently stopped completing, and three days
of events were lost when the disk filled; discovered when a customer asked for data that no longer existed."
```

Past tense, no adjectives, a discoverer at the end. If you cannot write that sentence, you do not yet understand
the risk well enough to grade it DANGER ([`00`](00-what-counts-as-a-risk.md), rule zero).

**Blast radius.** Who or what, how much, how long. Users affected, rows, money, hours of downtime — whichever
the project actually feels. "Everyone on the same network, for as long as the feature exists" is a valid
answer.

**Undo cost — now versus later.** State the point of no return explicitly:

- unencrypted traffic: cannot be retroactively encrypted once sent;
- deleted rows: gone unless a backup has been **restored at least once**;
- a public API shape: frozen from the first external consumer;
- a leaked token: valid until rotated, and possibly already used.

"Now: one code change. Later: a migration plus every user re-pairing." That contrast is the card's argument.

**Cheapest adequate option.** The smallest guard that removes the exposure — not the ideal system. Be honest
about its cost too; an alternative presented as free is a sales pitch and invites the same distrust:

- encrypt the transport with the platform's built-in primitive instead of designing a protocol;
- cap retention at a window that fits the backup;
- make the endpoint authenticated and rate-limited, keep it public otherwise;
- delete behind a soft-delete with a 7-day purge.

## Quantifying

You do not need precision; you need units and a direction. State the formula and the assumptions you used, so a
reader can disagree with a number instead of with a feeling:

```text
rows/day   = <events> × <users> × <rate>
GB/year    = rows/day × <bytes/row> × 365 × (1 + index factor)
$/month    = GB × <$/GB> + <requests> × <$/M requests>
first pain = the first of {backup window, RAM, SLA, budget} to be crossed
```

When you genuinely cannot quantify, say what you *would measure* and grade down: "no numbers yet; at 200 k rows
a full scan is already 47 ms here, so at 10× it becomes the query — `benchmark` can settle it." An honest unknown
beats an invented number, and an invented number destroys the card's credibility for every future card.

## Renderings

| Where | Form |
|---|---|
| Chat / IDE assistant | the seven-line card, then the question; the `!! DANGER` prefix so it is findable by eye and by search |
| Terminal output | the same, ASCII only; no colour assumptions |
| Code review comment | the card minus the question, plus "was this risk accepted? (the decision thread says so)" |
| HTML or report doc | the card as a callout, with the postmortem headline highlighted |
| WARN | one line, in the reply, no banner: "WARN — this removes the retry cap; recoverable by re-enabling it; continuing." |

Length caps: DANGER ≤ 7 lines plus the question · WARN = 1 line · NOTE = nothing visible. If a decision carries
three risks, put the top three rows in one card, never three cards; if it carries more, the decision is too
broad — split it into the decisions it actually contains.

## Tone

- **No scaremongering.** No "catastrophic", "disaster", "you will be hacked". The mechanism is the argument.
- **No hedging.** "Might possibly be a concern" tells the user nothing. Say what you know, label what you do not
  ("I have not measured this").
- **No shame.** The card is about the decision, never about the person: "the answer did not mention X" — not
  "you seem not to understand X".
- **No moralising and no repetition.** One card, one question, one acceptance. The user owns the outcome;
  their decision is the only thing you are owed — not agreement, not a second warning.
- **Say what stays true.** If part of the system is still protected ("the pairing step still authenticates both
  devices; only the transport is open"), say it — accuracy makes the rest believable.
