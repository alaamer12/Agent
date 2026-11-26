# Example — Errors and Typing Must Agree

This example shows a relational contradiction: each document can be reasonable alone while their shared boundary is incompatible.

## Evidence

**`language-architecture.md:42`**

> Public failure values must use a typed, exhaustive contract. Raw strings and untyped catch-all values are prohibited at application boundaries.

**`error-architecture.md:28`**

> Public failures are returned as a free-form message string plus an unstructured diagnostic string.

**`testing-architecture.md:55`**

> Tests assert the exact public error payload.

## Classification

- **Primary class:** D2 — Relational Contract Mismatch.
- **Facet owners:** Language owns type safety; Error owns failure taxonomy and payload semantics; Testing owns assertions; Gates owns enforcement.
- **Joint invariant:** Every public failure must be representable, consumable, testable, and enforceable without bypassing the language boundary contract.
- **Not a single-winner case:** Deleting the error payload model would lose failure semantics; deleting the language rule would weaken the boundary.

## Agreement Matrix Row

| Concern | Facet owners | Joint invariant | Status |
| :--- | :--- | :--- | :--- |
| Public failure representation | Language + Error + Testing + Gates | Typed public failures preserve structured semantics and remain exhaustively handled | Open |

## Illustrative Resolution Options

These options are examples, not an exhaustive menu:

- **Typed end to end:** Error adopts the language contract for all public failures.
- **Typed domain, validated wire boundary:** Language keeps typed internal contracts; Error owns a validated external representation and the explicit mapping between them.
- **Scoped exception:** Language grants a named boundary exception with validation, tests, and an enforcement gate.

A hybrid is valid. Recommend the smallest option that preserves both type safety and required error semantics, then ask the user to decide.

## Reconciled Ownership

- Language document: owns allowed type and exhaustiveness rules.
- Error document: owns failure categories, payload meaning, and the boundary mapping.
- Testing document: asserts the canonical mapped payload and exhaustiveness behavior.
- Gates document: enforces the approved boundary rule.

None of these documents absorbs the others' whole responsibility.

## False-Conflict Decoy

If the language rule applies only to public APIs and the error document's free-form string applies only to internal diagnostic logs, the documents do not conflict. Record the scope distinction as **Scoped non-conflict**; do not rewrite either document.
