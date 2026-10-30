# What counts as a risk — and what is just the product

> **Illustrative, not exhaustive.** The classes below are shapes to reason from, not a checklist to run. A risk
> you cannot name the mechanism of is not yet a risk — it is a suspicion, and suspicions do not get cards.

## Rule zero: flag the guard, never the goal

A product choice is not a risk because it has a theoretical downside. Every product has one: a server can be
attacked, a database can be corrupted, a website can be scraped, a phone can be stolen. If the skill fired on
those, it would fire on every sentence and be ignored within a day.

The trigger is narrower: **the answer removed the thing that would have prevented the failure, or accepted a
cost that never stops growing.** Say the same sentence with the protection in place — if the failure disappears,
the missing guard is the risk, and that is what the card names. If the failure survives the protection, you are
arguing with the business, and the card does not fire.

| The business shape (never a card) | The protection that changes the verdict |
|---|---|
| data stored on a server | encrypted at rest; access control on who can read it |
| accounts and sessions | passwords hashed; tokens expiring; authorisation per object |
| a public API | authenticated where it acts, rate-limited, input validated |
| two devices syncing | transport encryption; pairing/trust on first use |
| history kept | a retention bound; a deletion path; export |
| file uploads | size and type limits; storage outside the web root; scanning |
| a third-party payment provider | you never store the card numbers yourself |
| logs and analytics | no secrets or personal data in them; a retention window |
| a microservice split, SQL vs document store, hosted vs self-hosted | a backup, a migration plan, a rollback |
| telemetry | consent, and the fields that are actually needed |

Two follow-ups that settle most cases:

1. **"Could a competent engineer make exactly this business choice and never hit this failure?"** Yes → the
   failure is about the guard. No → it is about the product, and it is not yours to veto.
2. **"Did the user choose the unprotected variant, or did they merely accept the product?"** "Sync between phone
   and laptop" accepts the product. "Skip E2EE, just send it" chooses the unprotected variant.

## The nine consequence classes

Each entry: what the answer looks like, the mechanism, the disclosure the card owes.

### 1. Protection declined

*Sounds like:* "no encryption", "skip auth for now", "trust the LAN", "disable the check", "no rate limit",
"everyone can read it", "don't validate, the client checks it", "share one password".

*Mechanism:* an attacker — or simply another user of the same system — does what the protection prevented. The
disclosure must name the actor and the asset: *who* can now do *what* to *whose data*.

*Undo cost:* cannot be backfilled. Traffic read yesterday cannot be un-read; a token captured yesterday is still
valid. The point of no return is the first message sent, not the incident.

### 2. Unbounded growth — the non-security class

*Sounds like:* "keep everything forever", "we have space", "log every request body", "no pagination", "retry
until it works", "cache it all", "one row per event per user", "no TTL", "just add indexes later".

*Mechanism:* rate × time. Every unbounded thing has a date at which it becomes a problem; the decision is only
whether you meet it as a graph or as an incident. Compute it, do not gesture at it:

```text
rows/day      = events × users × per-user rate
storage/year  = rows/day × bytes/row × 365        (indexes: often +50–100 %)
first pain    = when storage or query latency crosses the backup window, the RAM, or the SLA
```

*Disclosure:* the rate, the first pain date, what breaks first (backup window, disk, query time, bill), and the
deletion/escape path that does not exist yet. Deleted history is recoverable only until it is deleted.

### 3. Irreversible action

*Sounds like:* "drop the table", "rewrite the history", "force-push", "overwrite the file", "send it to
everyone", "delete the old backups", "run it against prod".

*Mechanism:* the action destroys the state that a rollback would need. The card must separate *irreversible now*
from *irreversible after a point*: a migration is reversible until new rows arrive in the new shape; a publish is
reversible until someone consumes it.

*Disclosure:* what exactly is lost, whether a backup exists **and has been restored once**, and the reversible
version of the same action (dry run, copy first, soft-delete, feature flag).

### 4. Outward-facing contract

*Sounds like:* "make the API public", "that's the response shape, freeze it", "users will parse the export",
"put it in the URL", "use the package name", "it's just an internal format".

*Mechanism:* someone outside the repo starts depending on it; changing it later breaks them, not you. Wire
formats, URLs, file formats, SDK names and database schemas that another team reads are API surface whether or
not you called them that.

*Disclosure:* who will depend on it, what change becomes impossible, and the versioning escape (a version prefix,
an additive field, a separate export format) that costs nothing today.

### 5. Authority and safety boundary

*Sounds like:* "run it as admin", "disable the approval step", "skip the review", "give the token full access",
"automate the deploy on every push", "let the agent delete files".

*Mechanism:* a human check or a least-privilege limit disappears; the first mistake, not an attacker, does the
damage. The blast radius is whatever the permission reaches.

*Disclosure:* what the widened permission can now touch, and which single mistake it turns into an incident.
Prefer scoped credentials, a staging target, or an approval step that costs one click.

### 6. Silent failure and removed observability

*Sounds like:* "catch and ignore", "no need for a timeout", "don't log that", "retry quietly", "the user won't
notice".

*Mechanism:* the system keeps running wrong, and nobody learns for days. This is the hardest class to justify
and the easiest to fix: the card should be short, because the alternative is usually one line of code.

*Disclosure:* how the failure would be discovered today (usually: a user complains), how long it could run, and
what one signal would have caught it.

### 7. Compliance, consent, and other people's data

*Sounds like:* "store the raw request", "we don't need a deletion path", "send it to the analytics vendor",
"it's fine, they agreed to the terms", "keep it for debugging".

*Mechanism:* obligations that outlive the feature — deletion requests, retention limits, consent scope,
jurisdiction. You do not need to be a lawyer to flag it; you need to name the obligation and that the user owns
the call.

*Disclosure:* which data, which obligation, and the cheap structural fix (field-level exclusion, retention
window, a deletion path) that keeps the feature.

### 8. Resilience and rollback

*Sounds like:* "one server is enough", "we'll restore from backup if it breaks", "no need for a rollback plan",
"deploy on Friday", "the migration can't fail".

*Mechanism:* no tested restore, no second path, no quota → a single fault becomes an outage whose length is set
by how long it takes to improvise.

*Disclosure:* time-to-recover without the missing piece, and the smallest addition (a restore rehearsal, a second
instance, a rollback script) that changes it.

### 9. Compounding debt that becomes a product failure

*Sounds like:* "we'll optimise later", "it's fine at our size", "add the index when it's slow", "do it in the
request".

*Mechanism:* the cost grows with the thing that is also growing. This is a card **only** when the user is
knowingly deferring on a path that scales — `benchmark` can supply the numbers, and the disclosure is the size
at which the debt is paid (10× rows, first concurrent user).

## Detection cues in the answer

These words usually mark a decision made without its cost on the table: **just, for now, later, skip, disable,
no need, we have space, it's fine, sounds complicated, everyone should be able to, public, no limit, keep
everything, delete all, trust**.

They are cues, not verdicts: "just use the staging database, it's a copy" is CLEAR; "just drop the column, the
app doesn't read it" needs one check before it is CLEAR.

## What never belongs here

- The product's shape: server storage, accounts, sync, history, public APIs, hosted services, telemetry as a
  concept.
- Reversible engineering detail: naming, file layout, a library choice the agent owns.
- A trade-off the user stated themselves, with the cost named — that is an informed decision, so it is a NOTE.
- A policy someone else set and the user is relaying (raise it with the owner, not as a card to the relay).
- Anything where you cannot say **how** it fails. If you cannot name the mechanism, you do not know it is a
  risk; verify, measure, or stay quiet.

## Calibrating to the user

Consequence size alone is not the trigger — **consequence × ignorance**. A database administrator saying "no
backups on this scratch instance" is informed; the same sentence from someone building their first app is not.
The screen asks one question about the answerer, not a profile: *does this sentence show they know what it
costs?* Their own words are the evidence ([`01-the-screen.md`](01-the-screen.md)).
