# Case 7 - it works, until it has to do ten thousand

**The ask:** "sync every customer's ticket list every five minutes."

## Goal, separated

```text
GOAL  : our view of open tickets is close enough to the truth that nobody acts on stale info
VALUE : changed tickets, promptly - not the whole list, repeatedly
TEST  : median time from a ticket change upstream to it being visible here, and the error rate we
        were willing to tolerate when a sync fails
```

"Sync everything" was the method. "Changed things, quickly" is the value. The full-list assumption is what
makes the job impossible.

## Diagnose the block properly

Rate limiting is the symptom. The question that decides everything: **is this limit a protection or a
capacity?** Here it is capacity-shaped - the API documents per-minute quotas designed for integration
partners, and returns `Retry-After`. The public docs also describe a webhook for ticket updates.

If the limit had instead been anti-automation shaped - CAPTCHAs, fingerprint checks, "verify you are human" -
it would be a protection, and increasing volume would fall under the hard line about defeating protections and
about degrading someone else's system. That distinction is made *before* choosing routes, not after.

## Routes

| Route | Family | Notes |
|---|---|---|
| Subscribe to the change webhook, reconcile nightly | reroute | the correct shape of the whole feature |
| Conditional fetches with `ETag`/`If-None-Match` so unchanged records cost nothing | reroute | shrinks volume roughly 100x |
| Pull only tickets touched since the cursor, page by page | reroute | the obvious fix if the sync endpoint supports a cursor |
| Queue the requests with concurrency caps and exponential backoff, respect `Retry-After` | reshape | required regardless of which pull you choose |
| Ask for a partner quota bump | reduce-the-problem | cheap to ask, sometimes yes |
| Different provider with a bulk export | replace | last resort; migration is the expensive part |
| Rotate fingerprints or proxies to multiply the effective quota | rejected | defeats a protection and loads their system; not a route |

## Chosen

Webhook plus nightly reconciliation plus conditional fetching, all behind a queue that honors `Retry-After`.
The five-minute full sweep disappears because nothing in the goal needed it.

## Fragility flagged

The webhook delivery guarantees are documented but observed to be at-least-once with occasional long gaps, so
the nightly reconcile is not optional belt-and-braces - it is the correctness mechanism. That is written in
the record, along with the alert that fires when the gap exceeds the tolerance.

## What this case teaches

Volume problems are usually shape problems, and the first duty is naming what kind of limit you are dealing
with. Circumventing a capacity limit is engineering; circumventing a protection is not a route.
