# Case 2 - production config to a reusable snippet

**Artifact:** the `.env` block and a Helm values file from a live deployment, wanted as a template in an
open-source README.
**Destination:** public repository. Level 3, and the highest-value target: configuration files are almost
all identity, and their usefulness depends on looking real.

## What leaked, in the order it was found

```text
1. real secrets in values          -> redact, keep the line shape
2. the SaaS webhook URL            -> the URL *is* the secret; redact it, do not mask the last chars
3. an "example" bucket name        -> acme-prod-uploads; example values are rarely examples
4. the Postgres DSN with a host    -> generalize the host, keep the driver and the pool settings
5. comments                        -> "# raised after the March incident with Acme" - prose inside code is
                                      the surface nobody re-reads
6. the registry path               -> registry.internal.corp/acme/  (internal DNS discloses the org)
7. nodePool / instance type        -> keep: it is generic infra knowledge, not identity
8. resource-name prefixes          -> acme-eu-west-orders-*; pseudonymize the prefix, keep the shape
```

## Before and after, one block

```diff
- DATABASE_URL=postgres://orders_svc:9f2c11ab@db-1.prod.acme.internal:5432/orders
- S3_BUCKET=acme-prod-uploads
- SLACK_WEBHOOK=https://hooks.slack.com/services/T02ABCDE/BL0FGHIJ/xYz123
- # replicas raised to 12 after the Acme checkout incident, 14 March
+ DATABASE_URL=postgres://[db-user]:[REDACTED-SECRET]@[db-host]:5432/[database]
+ S3_BUCKET=[customer]-prod-uploads
+ SLACK_WEBHOOK=[REDACTED-WEBHOOK-URL]
+ # replicas raised after the checkout incident (see postmortem)
```

The shape survives: a reader still learns that the driver, port, user, and database are separate knobs, and
that replica count was tuned upward after an incident. That is the entire value of the snippet.

## The trap this case exists to record

Masking is not revoking. `9f2c11ab****`, `T02ABCDE/**`, or keeping a bucket name minus one word all leave
enough shape to confirm a guess, and in the webhook's case the surviving prefix identifies the workspace.
`revoke.py verify` reports these as `mask`.

## Also

**Rotate what was ever exposed.** A secret that appeared in a shared document, a screenshot, or a chat log is
leaked history regardless of what the sanitized copy says. Saying so is part of the job, not an
overreach - and it is the one recommendation here that changes the security posture rather than the document.
