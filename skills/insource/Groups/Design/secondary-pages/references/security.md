# Security / Vulnerability Disclosure

Tells researchers how to report, tells users how seriously security is taken, and gives the
machine-readable hook (`/.well-known/security.txt`, RFC 9116). Every shipped product needs the
page; the depth scales with the product, the honesty never scales.

## Must include

1. **How to report** - the channel (security email or form), encryption preference with the real
   fingerprint (a PGP block that was never published is worse than none).
2. **Safe harbor** - the sentence that protects good-faith research: what conduct is in scope
   (no privacy violation of users, no disruption, no data exfiltration), and that the operator
   will not pursue good-faith reports.
3. **Out of scope** - the list (social engineering, physical attacks, third-party services,
   best-effort scanner spam) - keeps the channel usable.
4. **What happens** - acknowledgment window, triage, fix, disclosure coordination; the
   90-day-style timeline is a policy choice: ASK for the number and publish only a number the
   team can keep.
5. **Bounty** - or the honest "we do not run a bounty program."
6. **`security.txt`** - `Contact`, `Expires`, optional `Encryption`/`Acknowledgement` fields;
   served at `/.well-known/security.txt` pointing at this page.

## Writing professionally

- Researchers skim: first paragraph answers where to send the report and what protection applies.
- The document's claims about data handling should match `privacy-policy.md` and infrastructure
  reality; "bank-grade encryption" is ad copy, "TLS 1.2+ everywhere, AES-256 at rest" is a claim.
- A status/security posture section (hosting, encryption, audits) is fine ONLY with evidence;
  audits named or absent.

## Ask the user - never invent

Channel and humans; response windows the team will keep; disclosure timeline stance; bounty yes/no;
real encryption/at-rest facts; whether any third-party audit exists.

## Failure patterns

A `security.txt` listing an expired contact; safe-harbor promises contradicting a legal threat
letter from the same company; claiming "SOC2 audited" with no report (the badges are statements of
fact, checked against evidence).
