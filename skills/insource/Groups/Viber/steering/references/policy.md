# policy

> This document defines the `policy` steering folder: what is allowed, forbidden, and who has authority. It lives in the **perception tier** (`perception/`); see [`index.md`](index.md) for the taxonomy overview.

**Holds.** Business rules, entitlements, constraints, and authority boundaries (sentence shape: *"must / must not / may / only / who decides"*). It records what the business permits or forbids, regardless of how engineers choose to enforce it.

**Shape.** Topic-named Markdown files describing business constraints and authority rules (e.g., `balance-constraints.md`, `org-creation-policy.md`, `cms-authority-limits.md`).

**Does not hold.**
- What the system provides or does ([`capabilities.md`](capabilities.md)).
- Conceptual definitions and entity states ([`domain.md`](domain.md)).
- Engineering guidelines, technical validation algorithms, or code invariants ([`doctrine.md`](doctrine.md)).
- Step-by-step operator workflows ([`playbook.md`](playbook.md)).

**The test.** Modal verbs and authority. Does the statement forbid something, require something as a business invariant, or define who has the power to decide?
- *Policy vs. Capabilities*: "The console allows admins to provision organizations" is a capability. "Individual users are forbidden from creating organizations on their own; only an admin may provision them" is a policy.
- *Policy vs. Doctrine*: "Virtual balances must never become negative" is a business policy (`perception/policy`). "Every debit transaction must query current balance using a database row lock before inserting a ledger entry" is an engineering doctrine (`tech/doctrine`).

**Example (`perception/shared/policy/non-negative-balance`).**
"A user's virtual wallet balance can never go below zero. There is no overdraft, margin borrowing, or leverage permitted in any experience tier."

**Example (`perception/shared/policy/governance-boundaries`).**
"Scoring formulas and achievement trigger thresholds are non-negotiable business rules defined strictly by the core management team and cannot be altered or customized by operator accounts in the admin console."
