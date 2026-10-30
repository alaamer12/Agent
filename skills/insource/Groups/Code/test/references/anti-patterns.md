# Common Anti-Patterns

## Mirror tests
Re-implementing the production arithmetic (or calling the same helper) to compute the expected value. Expected values must be independent literals or derived from a separate, trusted source, with the derivation noted in a comment.

## Mega-tests
One test method that asserts many unrelated behaviors. When it fails, the engineer cannot tell which claim broke. Split by behavioral claim.

## Quantity theater
Measuring suite health by the number of tests. Prefer fewer, higher-quality, discriminating claims.

## Leaf-only testing
Changing a producer and only testing that the producer now returns the new value, while ignoring whether downstream consumers still behave correctly. Prefer an end-of-path check when the chain is long.

## Shared mutable fixtures
Fixtures that tests mutate and leave dirty. Order dependence and flakiness follow. Every test must own its data.

## Fixed sleeps
`sleep(2)` or equivalent to “wait for the system”. Replace with condition-based waits that observe the actual outcome, with a deadline.

## Silent failures
Assertions that only check “did not throw”, or tests that catch and ignore errors. Failures must be loud and informative.

## Implementation coupling
Asserting private call sequences, internal state, or exact algorithm steps when those are not part of the public contract. A pure refactor then breaks the suite.

## Green-checking the fixture
Editing the expected value to match the current (possibly wrong) output without deriving why the new value is correct.