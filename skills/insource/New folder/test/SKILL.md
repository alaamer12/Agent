---
name: test
description: General testing principles and ethics for any test the agent writes or reviews — unit, integration, contract, e2e, property, invariant, regression, or pipeline. Use whenever writing, refactoring, reviewing, or deciding what tests a change needs. Covers one-reason-to-fail, test vs verifier distinction, test data as contracts, selective execution, minimal mocking with feature-flag style seams, and discrimination. Do not use for project-specific tooling or mandated workflows.
---

# Test

A test is a named behavioral claim. The strength of a suite is measured by the quality and discrimination of its claims, not by the number of tests.

## Core principles

- **One reason to fail.** A test asserts a single coherent behavior. Multiple assertions are acceptable only when they all serve that same claim.
- **Test the contract, not the implementation.** Prefer the public observable behavior. A pure refactor that preserves behavior must not break tests.
- **Test at the level that matters.** When a change affects a chain of collaborators, prefer verifying the final consumer. Intermediate hops are tested only when the end-of-path signal is insufficient.
- **Meaningful over quantity.** Ten discriminating claims beat two hundred shallow ones.
- **Discriminating assertions.** Temporarily break the production code; the test must go red.
- **Flakiness is a red test.** Fix root causes; never silence.

## Tests vs verifiers

Testing ≠ verification.

- A **test** is a promise about behavior (regression protection).
- A **verifier** is a proof of current success via a concrete medium (CLI output, binary runs, screenshot, HTTP body, etc.).

A test can verify an outcome. A pure verifier cannot test a behavior.

Verifiers are fast, always-on, untagged, and live in a conventional location (`verify/`, `smoke/`, or ecosystem equivalent). Anything slower or behavioral belongs in selectable tests.

See `references/tests-vs-verifiers.md`.

## Test data as contracts

Every test owns its data. Prefer factories / builders / fixtures that produce minimal, role-named data. Hard-coded literals are a defect. Keep them in a conventional location that documents “how to construct X”.

See `references/test-data-contracts.md`.

## Selective execution

Selectable tests must be filterable by category. Prefer native tags/markers; otherwise use the lightest workaround or a thin wrapper script. Default command runs the fast suite + always-on verifiers.

Verifiers are intentionally not selectable.

See `references/selective-execution.md`.

## Mocks and dependency substitution

Minimize mocks. Prefer real collaborators. Mocks exist to make local development faster, not to permanently replace real integrations.

Treat mock vs real as a feature-flag style switch: on by default in dev, aim for zero mocks in CI. Prefer source-code seams that allow a single command/flag to swap the entire graph. Thin scripts are acceptable when the language lacks native support.

See `references/mocks-and-seams.md`.

## Property, invariants, and contracts

- Prefer property-based tests for clear invariants.
- In multi-service systems prefer consumer-driven contracts when the risk is interface compatibility.

## Common anti-patterns

Mirror tests, mega-tests, quantity theater, leaf-only testing, shared mutable fixtures, fixed sleeps, hard-coded data, heavy/permanent mocking, drifting mocks.

See `references/anti-patterns.md` and `references/principles-deep.md`.

## When reviewing or writing

1. What behavioral claim does this make?
2. Why does the claim matter?
3. At which level is it most efficiently verified?
4. Would a pure refactor break this test?
5. If it fails tomorrow, will the next engineer immediately understand what broke?

For polyglot illustrations see `examples/`.
