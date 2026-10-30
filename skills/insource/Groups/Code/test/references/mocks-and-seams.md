# Mocks, Seams, and Dependency Substitution

## Core stance

Mocks are a development convenience, not a permanent replacement for real collaborators.

- Prefer real dependencies and real source when the cost is acceptable.
- Use mocks primarily to keep local feedback loops fast and cheap.
- In CI / automated runs the target is the highest practical fidelity to real source (ideally zero mocks).

## Feature-flag style swapping

Treat mock vs real as a switch, not a permanent wiring decision:

- Default for local development may enable mocks.
- CI, nightly, or release verification paths should disable mocks and exercise real implementations.
- The switch should be controllable by a single command, CLI flag, environment variable, or feature flag.

Changing source code to introduce a clean seam (factory, interface, composition root, environment-selected implementation) is encouraged when it makes the swap reliable and low-friction.

## Why minimize mocks

- A mock can silently drift from the real implementation.
- A mock never exercises the real integration surface, serialization, error paths, or performance characteristics.
- Over-mocking produces a green suite that fails to protect the system that actually ships.

## Acceptable techniques

- Source-level seams that select implementation at composition time.
- Test-specific factories or builders that can return either a mock or a real collaborator.
- Environment or build flags that select the dependency graph.
- Thin wrapper scripts that set the correct flags and invoke the test runner (especially useful when the language lacks first-class support).

## Anti-patterns

- Leaving mocks enabled in CI “because it is faster”.
- Mocking owned code that could be tested directly.
- Deep mock hierarchies that re-implement large parts of the system.
- Mocks that are never verified against the real collaborator’s current contract.
- Treating the inability of a language to swap dependencies as a reason to keep permanent mocks instead of introducing a small seam or script.
