# Invariant vs mechanism — the lens that does the thawing

Most rigidity in a draft is a **mechanism mistaken for an invariant**. The thaw is telling them apart.

## The two kinds of statement

- **Invariant** — a stable truth about the *problem*, independent of any technology. It survives a full
  rewrite. *"A wallet balance can never go negative."* *"A credit award must never be paid twice."*
  These live in the business/perception tier. They are the real requirements.
- **Mechanism** — a chosen *way* to enforce an invariant. It is draft, evolvable, replaceable. *"Use
  row-level locking."* *"Use a particular relational engine."* *"Use an append-only table with a unique key."*
  These live in the tech tier. They are means, not mandates.

## The tier test

Ask of any statement you are about to treat as law:

> **If the entire technology stack were rewritten, would this still be true?**

- **Yes** → invariant. Hold it firm. It is a real constraint on the design.
- **No** → mechanism. Hold it loosely. It is the current best way, open to a better way.

A draft doctrine that names a specific tool, SQL keyword, library, or table shape is almost always a
mechanism. The invariant it serves is usually one sentence quieter and one level higher.

## Worked splits

| Draft statement (frozen) | Invariant (keep) | Mechanism (revisable) |
|---|---|---|
| "Balance uses row-level locking" | concurrent mutations must not desync a balance; balance ≥ 0 | row locks vs serialized transactions vs atomic ops |
| "A credit ledger is append-only in a specific engine" | an award is idempotent; corrections never erase history | append-only table vs event log vs unique-key upsert |
| "The API uses a specific framework with a typed client" | clients get a typed, safe contract | a typed RPC layer vs a BaaS SDK vs codegen |
| "Auth uses a specific token scheme" | sessions are secure; delegated access is scoped | custom tokens vs BaaS auth vs sessions |

The left column reads like law. The middle column is the actual requirement. The right column is where
a better design can enter. **Thawing = moving your grip from the left column to the middle, then
re-opening the right.**

## The trap to name out loud

When you catch yourself saying *"we can't use X because the doc says Y"*, check: is Y an invariant or a
mechanism? If Y is a mechanism, it cannot eliminate X — only the invariant behind it can, and X might
satisfy that invariant a different way. Say the split explicitly; it is the whole move.

## What stays firm

Thawing mechanisms does **not** thaw invariants. The business truth — non-negative balances, idempotent
awards, server-owned business logic, isolation between tenants — is the ground the design stands on. Re-open how it is
enforced, never whether it holds. If a candidate cannot satisfy the invariant *by any mechanism*, that
is a real elimination — and you can say so with the invariant cited, not the draft doctrine.