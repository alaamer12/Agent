# Testing Architecture — discovery interview

Ask only what the codebase cannot answer. Recon already read the runner config, the test tree, the
generators, the seed scripts, the CI lanes, and the skip markers. What remains is intent.

## A. What the suite must protect

1. Which behaviors are **contractual** — a change would be a breaking change for a user, a client,
   or another team? These earn explicit tests and named invariants.
2. Which parts of the system are **pure and deterministic** (parsers, money, dates, state machines)
   and therefore cheap to test exhaustively and with properties?
3. Which failures have actually hurt in production? Their tests are the first migration targets.
4. Which documented rules does the project already claim are "enforced by tests"? Confirm the claim
   is true; list the ones that are only prose today.

## B. Environments and determinism

5. Must the default suite run with **no network and no shared services**? (Almost always yes; say
   it explicitly so the guard can be built.)
6. Which external systems are unavoidable, and can they be wrapped in an adapter the project owns?
   Payment, mail, SMS, object storage, third-party APIs, clocks, filesystems.
7. Is there a **live** lane today, and who owns its failures? Live tests need an owner, or they
   become vendor-outage noise.
8. Does anything depend on the host timezone, locale, or date in a way that would fail on another
   machine? (Pin both in global setup unless the product genuinely varies per locale.)
9. What is the **flake policy** — quarantine, retry, or delete? A retry policy without a metric is
   a decision to hide the problem.

## C. Data

10. Is test data allowed to resemble production data? If any real customer data has ever been
    copied into the repo or a fixture, that is a privacy incident to stop, not a style question.
11. Which aggregates are the most duplicated across tests today? They get the first generators.
12. Does the product have **sessions** (auth, impersonation, tenant scoping, token rotation)? How is
    a session's identity tied to a user, a tenant, and a role?
13. Are there **multi-tenant** or multi-workspace requirements that make a shared `tenantId`
    dangerous in tests?
14. Which values change upstream (prices, availability, third-party content)? Those must be asserted
    by structure and absence, not by value.

## D. Organization and budget

15. Colocate tests next to source, or centralize under `tests/`? (Pick one; state why.)
16. What are the **lanes** and their time budgets — pre-commit, pull request, nightly, release? What
    must block a merge?
17. Is test code typechecked and linted today? If not, is a separate test project acceptable?
18. Where does the shared corpus live — under `tests/fixtures/` or at the repository root shared
    with scripts? Who may add to it, and what review does a new capture require?
19. Which conformance tests already exist, and which documentation rules should become executable
    next?
20. Who owns a quarantined test, and where is the expiry tracked?

## Hand-off

Conclude by restating four things in one block and getting confirmation: the **lane table** (lane,
folder, environment, timeout, blocking?), the **generator registry** (aggregate → generator →
identity rule → special states), the **data homes** (schema, vocabulary, instances, scenarios,
corpus), and the **enforcement list** (which rules become conformance tests, which stay review
checks). The template's sections 2, 5, and 6 become exactly that block. Anything unanswered goes to
Open Decisions, never defaulted silently.
