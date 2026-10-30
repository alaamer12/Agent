# Case 1 - incident report to public postmortem

**Artifact:** internal incident report about a checkout outage affecting one named customer.
**Destination:** the company engineering blog. Level 3 in [`05`](../references/05-purpose-calibration.md).

## Inventory (the interesting part is what got kept)

```text
original                     | operation      | replacement              | why
-----------------------------+----------------+--------------------------+---------------------------
Acme Retail Ltd              | pseudonymize   | [customer-1]             | named 7 times, must stay one entity
checkout.acme-retail.io      | generalize     | the customer-facing store | the host adds nothing to the lesson
orders-api-v3                | pseudonymize   | [orders-service]         | it is an actor in the causality
postgres 14.9                | generalize     | a relational database     | version incidental; the *lock* is the lesson
2025-03-03 02:14 - 04:02 UTC | generalize     | about two hours          | duration is the point, calendar is not
14,207 failed orders         | aggregate      | "five-figure-ish volume"  | exact count + date + sector = identifiable
Marta Nowak (on-call)        | pseudonymize   | [on-call]                | role preserved so the timeline still works
Slack thread link            | redact         | [internal thread]        | the URL host discloses
Grafana dashboard URL        | redact         | [internal dashboard]     | same
```

**[keep], with reasons:** the error class (`lock timeout on the inventory table`), the sequence
(deploy → migration lock → write queue → timeout), the mitigation that worked, and the follow-up owners as
roles. Removing those would remove the postmortem.

## What the rewrite had to protect

Causality needs distinct actors. The first pass mapped `orders-api`, `inventory-api` and `billing-api` all to
`[service]`, and the paragraph became unreadable - the reader could no longer tell who was blocked by whom.
Fixed by role labels: `[orders-service]`, `[inventory-service]`, `[billing-service]`. `revoke.py verify`
caught it as a collision.

## What verification found that the author missed

- A `TODO(marta)` comment left inside the quoted config block.
- The filename itself: `acme-outage-postmortem-public.md`.
- A screenshot of the queue-depth graph whose axis label read "acme-retail orders/min", and whose PNG
  metadata carried the exporter's hostname.

## Reported losses

`LOST: exact failure count, precise start/end timestamps, the table name, the dashboard link.` A reader can
still learn the lesson; a reader cannot reproduce our graphs. Stated in the postmortem footer, not hidden.

`RESIDUAL: medium` - the incident sequence is distinctive. Anyone from `[customer-1]`'s team who was in the
calls would recognise it, so the customer's consent to publish was the real gate, not the redaction. That is
called out to whoever owns publication rather than being solved by more black boxes.
