# Legal Notice / Impressum

Answers one question no other document answers: **who is legally behind this** - the entity, its
registration, its address, its accountable human. Mandatory in parts of the EU (the German
`Impressum` is the strictest), and the right shape for operator identity everywhere. This is the
user's "contract information" page: the data is precise, legal, and **config-driven by definition**
(`engineering.md` §1 - every field resolves from the same config the documents render).

## Must include

1. **Operator** - full legal entity name exactly as registered, legal form, jurisdiction of
   registration.
2. **Registration identifiers** - company registration number, VAT ID if operating cross-border.
3. **Address** - a real postal address (a registered-agent service is a valid answer, an invented
   one is not).
4. **Representative** - who is accountable for the content (name or role).
5. **Contact** - the fastest lawful route to a human; email display per the obfuscation rule.
6. **Supervisory / licensing authority** [regulated sectors only] - ask if the product claims any
   regulated status; if none, the section stays out.
7. **Liability notes** - for links and service availability, in the jurisdiction's expected shape.
8. **Dispute-resolution pointers** [EU consumer-facing] - platform/OADR statements where still
   applicable; ASK rather than paste.

## Writing professionally

- Zero marketing. This document is read by lawyers, courts, tax offices, and journalists - the
  tone is a letterhead.
- Accuracy over completeness: a wrong registration number is worse than an honest "pending -
  provided at launch" (never silently shipped).
- Every field is the config's - the notice renders, it does not store.

## Ask the user - never invent

ALL of it: entity name, numbers, address, representative, VAT. No generator placeholder may
survive - grep the build for the config's absence rather than trusting the template.

## Failure patterns

"Your Company Name LLC" shipped to production; a mailbox in one country, a VAT ID for another,
the app store listing naming a third entity (the canon test: one entity, cited everywhere);
an Impressum on one domain, missing on the mirror (the web canon rule applies: one notice URL
linked from every platform).
