# What revoking is - five operations and one rule

Revoking is not "black out everything". It is choosing, item by item, how much specificity to give up so the
artifact can travel. Every choice is one of five operations.

## The five operations

| Operation | What it does | Preserves | Costs |
|---|---|---|---|
| **[redact]** | removes the value, leaves a marker | the fact that something exists there, and its role in the sentence | the reader cannot use or verify the value |
| **[pseudonymize]** | swaps a stable stand-in: `acme-corp` → `[customer-1]` | distinctness, relations, traceability inside the document | nothing, if the map is kept out of the artifact |
| **[generalize]** | moves up an abstraction level: `"Kafka 3.6"` → `"a log broker"` | the role the thing played | precision, and any argument that depended on that precision |
| **[aggregate]** | replaces individual values with a group figure: 14 per-customer counts → `"a few dozen"` | the scale | per-entity reasoning |
| **[keep]** | explicitly retained, with a reason | everything | risk, accepted on the record |

Selection is by question, not by reflex: **is the identity load-bearing here, or is the role load-bearing?**
When the role carries the argument, generalize. When the identity carries it - and the identity is not
sensitive - pseudonymize. When the value itself is the exposure, redact. When the number is the exposure but
the magnitude is the point, aggregate.

## The meaning-survival rule

> A revoked artifact has to still make its argument to a stranger.

Three failure modes, in the order they occur:

1. **Collapsed distinctness.** `[service]` appears eight times for three different systems, and the causal
   chain becomes unreadable. The reader cannot tell what called what.
2. **False generalization.** "We stayed on the free tier" becomes "a small deployment", which reads like a
   deliberate architecture choice; or "on 12 April" becomes "recently", which silently changes a fact into an
   impression. Generalizing must not fabricate a claim the source does not support.
3. **Precision the argument needed.** A postmortem where every duration is `[REDACTED]` no longer teaches
   anything about timeouts. If the lesson is quantitative, keep a quantitative shape - rounded, banded, or
   relative (`"about 40x the p99"`).

The test is mechanical enough to run: read the sanitized version cold, and ask of each paragraph *could someone
act on this?* Where the answer is no, either restore precision at a coarser grain or accept it as a stated loss
in the record.

## Revoking is not anonymisation magic

Two honest limits, because overstating them is how sanitized documents get treated as safe:

- **Combination is identity.** Removing names while keeping the unusual details leaves a document that a
  curious reader can resolve from public information. Uniqueness is the risk measure, not secrecy.
- **You cannot revoke a style.** Writing voice, project-specific vocabulary, an idiosyncratic incident shape -
  these identify as strongly as a name for anyone in the small community that cares. Say so when the audience
  is that community.

So the deliverable is *reduced identifiability at a stated level*, never "anonymous".

## And it is not `polyglot`

- `polyglot` answers: *would this document mislead someone on a different stack?* It removes
  technology-specific assumptions.
- `revoke` answers: *would this document identify someone, a customer, a system, a contract, a date?* It
  removes origin-specific facts.

They compose, and the order matters: generalize the stack first (`polyglot`), then revoke the identity
(`revoke`) - because a polyglot pass often removes an incidental vendor name that you would otherwise have
spent a revocation decision on. Neither one makes the other safe. A stack-neutral document still names your
customer on line one.

## And it is not deletion

Revocation writes a **new version**. The original keeps living where it lived. If the request is to remove
data from the system of record, from history, or from someone's account, that is a different operation with
its own authority requirements - say so rather than quietly overwriting the source.
