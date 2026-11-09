# doctrine

> This document defines the `doctrine` steering folder: engineering guidelines and mandated technical behavior for a specific technical part or task. It lives exclusively in the **tech tier** (`tech/`); see [`index.md`](index.md) for the taxonomy overview.

**Holds.** Technical guidelines and non-negotiable engineering mandates for one specific component, layer, or activity (e.g., test quality invariants, API error payload wire shapes, database transaction isolation levels, concurrency locks). Think of it as the project's technical jurisprudence: reasoned engineering standards applied consistently when writing or refactoring code.

**Shape.** Flat folder of topic-named Markdown files (e.g., `test-quality.md`, `balance-concurrency.md`, `api-error-contracts.md`).

**Does not hold.**
- Business rules, user entitlements, or policy decisions (which belong in [`policy.md`](policy.md)).
- Platform-wide runtime mechanisms (the steering function folder, [`function.md`](function.md)).
- Technology rosters stated as "We use X" ([`stack.md`](stack.md)).
- Step-by-step operational runbooks ([`playbook.md`](playbook.md)).
- Architectural decision records (ADRs) explaining past decision history (which live outside the taxonomy).

**The test.** Is it an engineering guideline or mandated implementation behavior for a specific technical part?
- *Doctrine vs. Policy*: "A wallet balance cannot be negative" is a business rule (`perception/policy`). "Debits must execute within a serializable database transaction and reject any operation where balance minus amount is less than zero" is an engineering doctrine (`tech/doctrine`).
- *Doctrine vs. Playbook*: How to write robust tests is `doctrine`. The command-line steps to run the test suite in CI is `playbook`.

**Writing Guidance.**
- **Describe behavior, not fragile mechanism**: State the technical invariant that must hold rather than hardcoding SQL-specific keywords (e.g., avoid writing `ON DELETE CASCADE` or database dialect syntax directly in prose unless the standard explicitly mandates that mechanism).
- State rationale clearly next to the mandate.

**Example (`tech/shared/doctrine/concurrency-invariants`).**
"Ledger mutations on a user wallet must be executed under atomic row locking or serialized transactions. Parallel mutation attempts on the same wallet ID must wait or abort with a concurrency conflict rather than risking balance desynchronization."

**Example (`tech/shared/doctrine/test-invariants`).**
"Unit and integration tests must verify mathematical invariants and state transitions across edge boundaries rather than asserting simple non-null returns. Tests for ledger arithmetic must verify that total debits plus final balance strictly equal initial balance."
