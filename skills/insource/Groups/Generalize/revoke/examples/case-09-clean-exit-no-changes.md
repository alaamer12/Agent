# Case 9 - when the honest output is the original, unchanged

**Artifact:** a 6-paragraph engineering explainer on API rate-limiting patterns (token bucket vs leaky bucket,
retry-after headers, idempotency keys), written by someone who works at the company but containing only
general knowledge and public references. Wanted for the company's public blog.
**Destination:** public. Level 3 - the aggressive setting, which makes a real inventory mandatory, not
optional.

## The inventory: the scan ran, the rows came back empty

`revoke.py scan` surfaced 9 candidates. The walk disposed of every one:

- "Stripe's idempotency-key guide" and two `docs.stripe.com` links - a public vendor's public documentation,
  tied to *Stripe*, not to us. [keep]
- `billing-service`, `api-gateway` as example service names - generic role labels, the §9 kind. [keep]
- Port 443, a Redis 7 mention, `Retry-After: 30` in a header example - standards and public products. [keep]
- "100 req/s" in a worked example - labeled in the text as a hypothetical, used to make the math readable.
  Not a measurement of anything real. [keep]
- Three dates ("since 2019", "the August 2023 outage") - all about *public* incidents at *other* companies,
  cited as motivation. [keep]

Then the two checks that catch what scanners cannot: any combinatorial set that names our company (the
outage references are Stripe's and Cloudflare's, public postmortems; nothing here is ours); any non-text
surface (no metadata, no internal links, no paths, no usernames). Nothing pins this document to an origin.

**Identity rows: 0.**

## The temptation, named

The moment an empty inventory exists, *doing something* starts to feel like the job. The moves that would be
wrong here, each of which a diligent-looking agent is tempted to make:

| Temptation | Why it is not revocation |
|---|---|
| Generalize "Stripe" to "a payments API" | the tie is to Stripe's public docs, not to us; the edit costs the reader a real, checkable reference and removes no disclosure |
| Round "100 req/s" to "some requests per second" | the number is hypothetical and load-bearing for the arithmetic; softening it makes the explainer worse and protects nothing |
| Drop the public-outage dates for "vagueness" | they are public facts about other companies that anchor the timeline argument; removing them is rewriting history, not masking ours |
| Reword "our api-gateway" to "a gateway" for neutrality | the label is already generic; "neutrality" is a style goal, and style is not this skill |

Every one of these passes the test that matters: **which identity tie does this cut?** If the answer is
"none," the edit does not belong to this run.

## What was reported

```text
ARTIFACT  : rate-limiting-explainer.md -> unchanged      CLEARED FOR: public blog (level 3)
INVENTORY : 0 identity rows (9 scan candidates, all [keep] with reasons above; surfaces swept:
            text, links, metadata, filenames)
CHANGES   : none - the document ties to no specific origin
CHECKS    : shape scan pass | metadata surfaces pass
LOST      : nothing - no substitution was required or made
RESIDUAL  : low - public vendor references only; no combinatorial set names our company
ORIGINAL  : untouched - it is also the output
```

The artifact ships as written. The record is the deliverable: it says the aggressive-level walk ran and why
each candidate survived, so a later reader can disagree with a specific [keep] instead of wondering whether
anyone looked.

## The failure this case prevents

A run that returns a diff when the inventory was empty is not more thorough - it is evidence of one of two
faults: the walk **missed** something real (redo the inventory before touching the text), or the model went
**looking for work** and paid for the appearance of diligence with the author's content. The skill's product
is the removal of identity ties, not the performance of removal. Zero ties found, zero changes made, report
and stop: that is the job, correctly done, and it is as complete an output as case 6's refusal - its mirror
image at the other end of the scale.
