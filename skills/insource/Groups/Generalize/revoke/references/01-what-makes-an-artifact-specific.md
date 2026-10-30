# What makes an artifact specific - the inventory

Run this as a checklist over the whole artifact, including code blocks and captions. Memory-based inventories
miss things; `scripts/revoke.py scan` proposes candidates mechanically, and this list tells you which of them
matter and what the scanner cannot see.

The question for every row is not "is this secret" but **"would this let a reader pin the artifact to a
specific company, system, person, contract or moment?"** Uniqueness is the risk, not classification.

## 1. People and organisations

Names, initials, usernames, handle names, email addresses, job titles combined with a small team, Slack
display names, "the CEO", reviewer/approver signatures, customer company names, partner vendors, contractor
firms, an author in metadata.

## 2. Credentials and machine secrets

API keys, tokens, JWTs, private key material, connection strings, `.env` values, passwords in examples,
webhook URLs (a webhook URL *is* a credential), signed URLs with embedded tokens, base64 blobs, seed phrases,
certificate contents. These are redact-always, and rotating anything that ever appeared in a shared document
is a separate action worth recommending loudly.

## 3. Network and infrastructure identity

Hostnames and internal domains (`.corp`, `.local`, `staging.acme.io`), IPs including NAT and IPv6 suffixes,
region and availability-zone names, cloud account/project IDs, bucket and queue names, cluster names, ports
that are unusual for the service, CDN and DNS provider choices that fingerprint a company.

## 4. Identifiers and codes

Ticket IDs with a recognizable prefix, order and invoice numbers, customer IDs, account numbers, tenant IDs,
device and session IDs, trace and request IDs, commit hashes, package names under a private registry, database
schema and table names, internal API paths, repo names and paths.

## 5. Places, dates and quantities

Precise timestamps, migration and launch dates, incident dates, contract start/end dates, headcounts, revenue,
user counts, per-customer volumes, SLA numbers, budget figures. Individually dull; in combination, an
identification kit.

## 6. Contracts, customers and market-sensitive content

Pricing and discount terms, negotiation state, named customers in a pipeline, roadmap items, unreleased
features, churn and outage history, security findings not yet disclosed, vendor performance reviews.

## 7. Personal data

Names with roles, emails, phone numbers, physical addresses, user-generated content quoted verbatim,
support-conversation text, avatars, screenshots containing someone's mailbox, anything that identifies a
natural person - the category with the heaviest external rules attached and the least room for judgment by
an agent.

## 8. The categories everyone forgets

- **Non-text surfaces** - filenames, image content and its metadata, document properties, git trailers, PDF
  annotations, embedded paths in stack traces, hyperlinks, footnotes and citations, code comments, example
  values inside configuration samples, sample data in fixtures. See [`03`](03-leak-surfaces.md).
- **Combinatorial identity** - "40-engineer fintech in Austin, migrated in Q3 2025, hit by the Postgres 14.9
  bug": every atom is public, the set is unique.
- **Narrative fingerprints** - an unusually specific sequence of events, a distinctive internal tool name, an
  in-joke, an acronym only your company uses.
- **Residual shape** - partial redactions that leak length or domain (`a**@acme.com`), redaction counts that
  imply a number, alphabetical ordering that hints at names.

## 9. What usually does not need revoking

Public library and product names, generic role labels (`[on-call]`, `[billing-service]`), standard ports and
well-known protocols, documentation URLs, anything the artifact's argument depends on staying real. Write
**[keep]** with a reason rather than leaving it unexamined - the unexamined row is where the leak lives.

## Inventory row format

One line per item, and this is exactly what the script's map file consumes:

```text
original              | operation      | replacement            | why
----------------------+----------------+------------------------+----------------------------
acme-corp             | pseudonymize   | [customer-1]           | referenced 6 times, must stay distinct
10.42.7.19            | redact         | [REDACTED-HOST]        | internal address, no role in the story
2025-03-03 02:14 UTC  | generalize     | about two hours later  | relative timing is the lesson
postgres 14.9         | generalize     | a relational database  | version is incidental here
$2b$...secret hash    | redact         | [REDACTED-HASH]        | credential material
```
