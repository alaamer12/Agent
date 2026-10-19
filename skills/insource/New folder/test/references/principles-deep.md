# Deeper Principles

## One reason to fail
The name of the test states a single behavioral claim. Multiple assertions are allowed only when they all evaluate aspects of that same claim. If a test can fail for two unrelated reasons, split it.

## Test at the level that matters
When service A changes its output from A→B and the result flows through B → C → D:

- Prefer a test of D that verifies it correctly receives and handles B.
- If D behaves correctly, the entire path succeeded.
- Only add intermediate tests when the end-to-end signal is too expensive, too slow, or insufficiently diagnostic.

This is the cheapest way to protect long pipelines and microservice chains.

## Meaningful claims
A test earns its place by protecting an invariant, a critical path, a failure mode, or a regression that once hurt users. “It increases coverage” is not a sufficient reason.

## Discriminating assertions
After writing a test, temporarily break the production code in a plausible way and confirm the test goes red. If it stays green, the assertion does not discriminate.

## Flakiness is a red test
Root causes cluster around:

- Async waits with fixed timeouts
- Shared mutable state / test-order dependence
- Uncontrolled time or randomness
- Live external services
- Environment differences (CI vs local)

Fix the root cause. Quarantine only with an explicit owner and ticket; never as a permanent solution.

## Pesticide paradox
The same tests run repeatedly against the same code stop finding new defects. Periodically refresh or replace long-lived regression suites, especially those that no longer discriminate.