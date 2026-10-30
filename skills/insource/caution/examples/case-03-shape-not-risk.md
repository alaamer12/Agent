# Case 03 — the shape is not the risk (and how to stay quiet)

> The failure mode this file exists to prevent: cautioning the product. Three answers that a badly calibrated
> screen would flag, and why the right response is silence — or one checked fact.

## Vignette 1 — "the data has to live on our server"

The user is designing a notes app and says:

> "Everything is stored on our server, that's the product idea — no local-only mode."

A screen that asks *"is there any way this could go wrong?"* answers yes: a server can be attacked, breached,
seized, or simply lose a disk. That is true of every product ever built, and it is not this skill's business.

The screen that asks *"did the answer remove a guard, accept unbounded growth, lock something in, or commit
outward?"* answers: **no**. Server storage is the business shape. Grade: **CLEAR**. No card, no warning, no
sentence in the reply. Work continues.

The *next* answer is where the guard shows up:

| Answer | Verdict |
|---|---|
| "Everything is on our server." | CLEAR — the architecture |
| "Everything is on our server, encrypted at rest, one account per user." | CLEAR — shape plus guards |
| "Everything is on our server, anyone with the URL can read a note." | **DANGER** — the access control is missing |
| "Everything is on our server, stored in plaintext because encryption complicates search." | **DANGER** — a protection declined *for a stated reason* is still a knowledge gap unless the cost was named |

Same product, four answers, one card. The word that changes everything is the guard, never the server.

## Vignette 2 — "drop the dev database"

> "Drop it, it's the dev database I made an hour ago."

A screen that only reads "drop" fires a DANGER card here. That is noise: the action is reversible in the only
sense that matters — the data is a copy the user controls, minutes old.

The screen does not guess. It spends two seconds checking the one fact that decides it: **which connection** the
command would use.

```text
DATABASE_URL → localhost/dev_notes        (not the production host)
rows                                       1 240, all created today
```

Grade: **CLEAR**, and the reply is one clause at most: "Dropped `dev_notes` — it was the local copy from 10:04."
No card. The verification was cheaper than the warning, and it is the stronger answer: *"I checked, it is the
scratch copy"* beats *"are you sure?"*.

Reverse the fact and the grade flips: same sentence, but the connection string points at the shared staging
host — now the answer's cost claim is wrong, and it is a DANGER with the mechanism named ("every teammate's
staging data disappears; the last snapshot is from Friday").

## Vignette 3 — an informed owner and a scratch instance

> "No backups on this scratch instance — if it dies I rebuild it in ten minutes."

Protection declined? Formally yes. But the sentence names the cost, the recovery time, and the scope. That is the
definition of an informed decision.

Grade: **NOTE**. Nothing visible in the reply. Re-raising this is how
the skill teaches an expert to ignore it — and the same expert will be the one who needs the card on a decision
they *haven't* priced.

## Vignette 4 — "public API"

> "Make the API public, no key required for reads."

- "public API" is the product → CLEAR.
- "no key required **for reads**" can be a deliberate, informed choice → NOTE.
- the *write* endpoints, if they inherit the same setting → **DANGER**: the sentence's scope is about reads, and
  the mechanism says anyone who finds the URL can corrupt data.

The boundary of the answer is part of the answer. Read the scope before grading, and card the scope creep —
never the part the user actually decided.

## What staying quiet buys you

Every unnecessary card has a price, and it is paid later:

1. The user learns that `!! DANGER` precedes a lecture, and starts skimming it.
2. The one card that matters — the plaintext sync, the unbounded table, the unauthenticated admin route — reads
   exactly like the nine that did not.
3. The agent starts looking like it is arguing with the product, which is the fastest way to lose the authority
   line `dtb` establishes.

The discipline is asymmetric on purpose: **verify instead of warning when a fact settles it, and stay silent when
the answer is the product.** The card is spent on decisions whose cost the answerer cannot see — not on the ones
they made deliberately, and never on the ones that are simply the thing they are building.
