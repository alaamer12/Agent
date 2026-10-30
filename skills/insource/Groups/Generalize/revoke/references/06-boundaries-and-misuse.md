# Boundaries - the stop list

Revocation has one legitimate use: preparing a version of an artifact for a wider audience than it was written
for. Every item below is a request that is *not* that use. Detecting them is the skill's most important job,
because the mechanics of revoking are identical and a capable agent can drift into the wrong purpose without
noticing.

## Revoking is a disclosure decision, not an alteration decision

The subject is a copy going somewhere. The source of truth is never in scope.

## Stop the job when the request is any of these

| The request | What it actually is | Do instead |
|---|---|---|
| "remove this from the document so the audit doesn't see it" | concealing material information from a review that is entitled to it | say plainly that you won't produce a version whose purpose is to mislead the auditor; help prepare a complete disclosure instead |
| "we're under legal hold / preservation order, but tidy the files anyway" | destruction or alteration of a preserved record | stop; preservation duty outranks tidiness; route to whoever owns the hold |
| "delete the old passages from the incident report so our mistake isn't recorded" | rewriting an operational record | produce a sanitized *sharing copy*; the record stays complete |
| "strip the safety warning / the consent notice / the license header" | removing protective or legally required content | keep those lines; they are the part that must survive |
| "anonymise this dataset so it can't be traced back" (for people who never agreed) | repurposing personal data, and a promise statistics cannot keep | draft the minimal version, state the residual risk, escalate to whoever owns the decision |
| "remove the names from the timeline" when the point of the timeline is who approved what | laundering accountability | replace names with roles - `[on-call]`, `[billing-owner]` - so *who did what* stays knowable while *who* stays private |
| "scrub the customer's data out of this export and send it to the vendor" when the vendor needs the real data to help | a disclosure dressed as sanitization | ask who authorized the transfer; a redacted copy of someone else's records is still about them |
| "make the numbers look reasonable in the shared doc" | fabrication | revoke to bands or relatives, or keep the numbers and restrict the audience |
| "overwrite the original with the sanitized version so nobody leaks it" | destroying the source of truth | create a new file, leave the original untouched, and control distribution by access, not by deletion |

## The boundary is not a style preference

These are the cases where "I was asked to" is not an answer. A sanitized document has an audience; naming
that audience is how you notice the purpose is wrong. If the destination is a regulator, a court, an auditor,
an affected person, or the public, and the revocation reduces what they can learn, that mismatch is the whole
signal.

## Never overstate what you achieved

- Do not write "fully anonymised". Combining detail, retained style and metadata mean identifiability is
  reduced, never eliminated ([`00`](00-what-revoking-is.md)).
- Do not treat partial masks as removal.
- Do not certify regulated or third-party content. Draft, flag, route.
- Say what was lost ([`04`](04-verification.md)). An artifact whose cost is hidden is a document that will be
  trusted wrongly.

## "We cannot share this" is a complete and correct output

Sometimes the only honest result is: the artifact's value depends on details that identify the customer, and no
version both travels and teaches. Report it, propose the alternative - a rewritten lesson abstract, a
restricted audience, or the access request that would make sharing legitimate - and stop. Shipping a
look-sanitized document to satisfy a deadline is the specific harm this skill exists to prevent.
