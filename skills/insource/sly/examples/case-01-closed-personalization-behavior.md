# Case 1 - a closed personalization behavior, reproduced from what any user can see

**The ask:** "we're building a video streaming site and we want the kind of personalization a big platform
gives its users - but there's no API for it."

**Why this case is in the set:** it is the cleanest illustration of *capture the value, not the access*, and
of the line where that stops being clever and starts being intrusion. Validate it against your intent - if
this is not what sly is for, the case is wrong, not the skill.

## Step 1 - goal, separated from the method

```text
GOAL  : a feed on our site where each user's next watches feel personally relevant
VALUE : a relevance ordering over our own catalogue, conditioned on what this user has watched
TEST  : on held-out watch histories, our ordering puts the item they actually chose next in the top N
        at a rate we can measure and that beats a recency baseline
```

The rewrite is the whole game. The goal is not "their model". It is *an ordering over our catalogue for our
users*. Their system is existence proof that such an ordering is learnable, plus a set of principles worth
encoding: mixed categories near the top, freshness weighted, completion fraction beats click, nothing
repeated, diversity penalty.

## Step 2 - the block, proven

Their public data API exposes search, video and channel metadata, playlist lookup by id, and analytics for
*your own* channel. There is no recommendation endpoint for third parties, and watch history is
user-private. Two independent signals: the API reference lists no such operation; the public watch page
renders its "suggested" column with no backing call that returns third-party-relevant data. Class: blocker.
Confidence: high.

## Step 3 - routes, from different families

| Route | Family | Note |
|---|---|---|
| Fit our own ranker: published design material + open implementations for structure, trained and evaluated on the operator's own catalogue and interaction logs | rebuild | the real prize |
| Use the public API for what it does return - our channel's metadata and analytics - as item features | reroute | cheap enrichment, not a workaround |
| Third-party personalization service | replace | needs a data-sharing review before it is even feasible |
| Ship category affinity + recency now, visibly early-stage, while logs accrue | reduce | unblocks this week |
| **Bulk-collect their result orderings to imitate the system** | rebuild, badly | **rejected at the gate** |

## Step 4 - why the rejected route is rejected

It fails both parity questions at once. An ordinary user asks for a feed and receives a feed; nobody
systematically harvests thousands of orderings to reconstruct a function. It also exceeds what a person
could generate (a volume load their servers would feel), which is a hard line on its own - and it is
fragile: their next model change silently invalidates everything collected.

Note what did **not** stop it: no ToS citation was needed. The access-parity test did the work. The ToS
question still belongs in the record as one contextual line, because the operator is building a commercial
product, but it was not the reason the route died.

Ordinary-user observation is still allowed and useful here: watch how a real interface orders and
diversifies results as a person would, extract the *principle*, encode that. It is wholesale output
collection that crosses over.

## Step 5 - chosen route and its cost

reduce-then-rebuild. Ship the heuristic now; start logging the events a ranker needs (impression, dwell,
completion, negative signal); train when volume supports honest evaluation; compare against the recency
baseline before calling anything personalization.

Trade-off accepted: the first quarter is a plain feed with a diversity rule on top.

## Step 6 - what gets said out loud

- our ranker is an approximation fitted to this catalogue and these users, not a copy of anyone's system;
- it will be weak and near-random until there is real interaction volume - cold start is handled by a
  popularity prior, which is a product decision, not a technical footnote;
- the ordering is derived, so the UI must never present it as "because you watched X" when it is really
  "because users like you watched X" - or worse, "because our prior says so";
- re-check condition: if the platform ever ships a genuine partner endpoint for recommendations, the
  workaround retires and the record says so.
