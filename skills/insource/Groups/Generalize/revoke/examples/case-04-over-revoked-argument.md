# Case 4 - the pass that over-revoked and killed the argument

**Artifact:** an internal design note explaining why a multi-region deployment chose append-only replication
over conflict-merging. Wanted as a public engineering blog post.
**Destination:** public. Level 3.

This case is in the set because the most common failure of revocation is not a leak. It is a document that
survives verification and no longer says anything.

## What the mechanical pass produced

Every specific noun treated as suspicious, replaced with a generic:

```text
region names            -> [region]        (three of them, one placeholder)
the two services        -> [service]       (writer and reader merged)
"900ms cross-region"    -> "slow"
"24h retention"         -> [REDACTED]
"we chose append-only"  -> "a strategy was chosen"
the customer who needs  -> "some customers"
  strong ordering
```

`verify` passed. Nothing leaked. And the post was unreadable: a reader could not tell that there were three
regions, two roles, one constraint, and one decision - which is the entire content of the note.

## The four repairs

| Breakage | Repair | Why this and not more redaction |
|---|---|---|
| `[region]` x3 for eu/us/ap | `[region-a]`, `[region-b]`, `[region-c]`, plus one preserved fact: *one is 900ms from the others and the other two are 80ms apart* | the ordering relationship is the argument; geography is identity |
| writer/reader merged | `[writer-service]`, `[reader-service]` | distinct actors, role labels, zero disclosure |
| latency generalized to "slow" | keep as "roughly a second of cross-region write latency" | magnitude was never the secret; "slow" is a fabricated claim |
| retention redacted | "one day" | it is a design parameter the post depends on, not a customer fact |
| "a strategy was chosen" | keep the actual choice: append-only replication, conflict resolution deferred to the application | the decision *is* the post |

## The rule that came out of it

> Revoke **who, where, when, how much**. Never revoke **what and why**.

An easy test to run on each row of the inventory: *does the reader need this to follow the reasoning?* If yes,
find the operation that keeps the reasoning (pseudonymize, band, relative timing) instead of the one that
removes it. Redaction is the last resort, used when the value itself is the exposure.

## Report line that tells the truth about cost

```text
LOST: exact region names and the customer's identity; a reader cannot benchmark our latency against ours,
      only against the pattern.  RESIDUAL: medium - the architecture plus the sector plus the launch window
      narrows the candidate companies to a handful. Accepted for a blog post; not accepted for a talk
      where the diagram would carry our internal service names.
```

And the honest alternative was offered: publish the pattern as a generalized write-up without our incident
as the framing example. Sometimes that is both safer *and* a better article.
