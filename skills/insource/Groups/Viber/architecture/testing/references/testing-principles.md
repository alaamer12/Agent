# Testing Principles, Mistakes, and Rules of Thumb

This reference is the standards layer: what a good test is, how large it may be, how it stays
deterministic, and which failure patterns to reject in review. It is framework-agnostic; the runner
and assertion library change, the rules do not.

---

## 1. What a test is for

A test exists to make a **specific future change safe**. That sentence explains every rule below. A
test that cannot name the change it protects is not protecting anything; a test that fails for a
change that did not alter behavior is actively harmful, because it trains the team to ignore red.

Kent Beck's **Test Desiderata** is the most useful review vocabulary because it states the trade-offs
instead of pretending they do not exist:

| Property | Meaning | What it buys | What it costs |
|---|---|---|---|
| **Isolated** | Result independent of other tests and of run order | Reliable signal; parallel execution | Setup repeated per test |
| **Composable** | Any subset can run together | Fast local loops, targeted CI | Requires real isolation |
| **Fast** | Milliseconds for small tests | Tests actually run during development | Doubles instead of real edges |
| **Inspiring** | A green run creates confidence | Suite is trusted and maintained | Investment in failure messages |
| **Writable** | Cheap relative to the behavior | Tests get written at all | Generator and harness investment |
| **Readable** | A stranger understands intent | Tests double as documentation | Naming and data discipline |
| **Behavioral** | Changes when behavior changes | Catches regressions | Must know the contract, not the code |
| **Structure-insensitive** | Survives refactoring | Refactors stay cheap | Requires boundary-level assertions |
| **Automated** | No human step | Runs in CI | Tooling setup |
| **Specific** | Failure names the cause | Fast diagnosis | One concern per test |
| **Deterministic** | Same input, same result | Trust; no rerun ritual | Seams for time, RNG, network |
| **Predictive** | Green means production-suitable | Real risk reduction | Slower, broader tests |

Use the table as a review lens, not a checklist. No test has all twelve. The doctrine is Beck's own:
no property is given up without receiving a greater one in return — and the trade-off is written
down, not discovered later. An end-to-end test deliberately trades speed, isolation, and specificity
for predictiveness. A unit test deliberately trades predictiveness for speed. A suite that is all
one or all the other has made the trade by accident.

---

## 2. Test sizes and the budget

Google's size taxonomy is more actionable than "unit vs integration" because it names the resource
constraints, which are what actually make a suite slow or flaky:

| Size | Process / threads | Network | Database / FS | Typical role | Budget |
|---|---|---|---|---|---|
| **Small** | one process, one thread | forbidden | no DB; local assets only | pure logic, parsing, validation, formatting, state machines | milliseconds; thousands |
| **Medium** | one machine, threads allowed | localhost only | local DB, temp FS, containers | wiring: repository + schema, HTTP handler + service, serializer + contract | tens–hundreds of ms; hundreds |
| **Large** | unrestricted | allowed | anything | a handful of real user journeys, migration rehearsals | seconds–minutes; a few dozen |

Two consequences most teams learn late:

1. **Size is a property of the test, not of the folder.** A "unit" test that opens a socket is a
   large test in disguise and belongs in the large lane, where its cost is visible.
2. **The budget is a ratio, not a target count.** Logic bugs live in the small lane; interface bugs
   live in the medium lane; integration and journey bugs live in the large lane. The **ice-cream
   cone** — a wide top of end-to-end tests over a thin base — is the expensive way to discover that
   most failures were local and could have been caught in milliseconds.

The shape is a budget decision recorded in `testing-architecture.md`, with timeouts per lane. A lane
with no timeout is a lane that will one day hang CI.

**Hermetic** means the default suite needs nothing from outside the repository: no internet, no
shared database, no developer's machine state, no wall-clock date. Live tests exist, but behind an
explicit profile (`TEST_PROFILE=live` or equivalent) with their own lane, and the default run must
still be able to prove — not assume — that it cannot egress.

---

## 3. The shape of a single test

**Arrange / Act / Assert**, or its BDD spelling **Given / When / Then**. The names matter less than
the discipline: setup, one action, one observable outcome.

```text
def test_expired_subscription_is_rejected_at_checkout():
    user = UserGenerator.create()
    subscription = SubscriptionGenerator.expiredFor(user)     # Arrange
    cart = CartGenerator.withItem(price=Money.of(10, "USD"))  # Arrange

    result = checkout(cart, actor=user)                        # Act

    assert result == Rejected(Reason.SubscriptionExpired)      # Assert
    assert result.retryable is False
```

Rules that make this shape hold:

- **One reason to fail.** If two assertions can fail for unrelated causes, split the test. This is
  the single largest readability win available.
- **Assert behavior, not calls.** `assert result.status == 201` beats `verify(service).save(...)`.
  Call assertions belong only where the call *is* the contract (an event was published, a payment
  was captured).
- **No control flow in the test body.** No `if`, no `try`, no loops except the parameterized case
  table the runner provides. A test with branches has untested branches.
- **Assertion messages name the expectation.** `assert total == 0, f"total after refund, got {total}"`
  or the framework's equivalent. Assertion roulette is a test smell precisely because the failure
  output cannot say which claim broke.
- **Names state the claim, not the method.** `rejects_expired_subscription` beats `testCheckout2`.
  The file names the unit; the test name names the rule.
- **Test the public seam.** If the rule cannot be reached without calling a private helper, the
  design has a seam problem, not a testing problem. Do not solve it with reflection.
- **Explicit over implicit setup.** A reader must see which values matter to this test. Generator
  defaults hide the irrelevant; overrides highlight the relevant. A test that overrides nothing is
  either a happy-path smoke test or is testing the default — say which.

---

## 4. Behavior versus structure

The two desiderata that decide whether a suite survives a refactor are **behavioral** and
**structure-insensitive**. They are also the two most frequently violated.

- A test asserts an **outcome the caller can observe**: returned value, persisted state, emitted
  event, HTTP response, rendered text the user sees.
- A test must not assert **how** the outcome was produced: private method order, internal field
  names, number of queries, class composition, the fact that a helper was invoked.
- **Mocking what you do not own** (a payment gateway, an email provider, the clock, the filesystem)
  is legitimate and necessary. Wrap it in a narrow adapter owned by the project, then fake the
  adapter. Mocking what you do own couples the test to the current call graph.
- **The test double ladder**, from least to most coupling: real object → in-memory fake with real
  semantics → stub returning canned data → mock with call expectations. Climb only as far as the
  test requires. Every step up is a promise to maintain an internal shape.
- **If every refactor turns the suite red, the suite is a change detector.** Its failures are noise,
  and noise is deleted. The fix is not "fewer tests"; it is assertions at the boundary.

A useful diagnostic: delete a private method, extract a class, rename an internal variable, and
re-run. A healthy suite stays green. If it goes red, the tests are asserting structure.

---

## 5. Determinism

Flakiness is not a nuisance; it is a defect in the test's architecture. Martin Fowler's taxonomy of
non-determinism still covers almost every real case:

| Source | Symptom | Fix |
|---|---|---|
| **Wall clock** | Passes in the morning, fails at midnight or month-end | Inject a `Clock`; freeze or advance it per test |
| **Sleeps / timeouts** | Fails on slow CI, passes locally | Poll the observable condition with a bounded timeout; never `sleep` |
| **Randomness** | Intermittent failure, different data each run | Seeded generator per test, or fixed data; record the seed in the failure message |
| **Order dependence** | Passes alone, fails in suite | Fresh fixture per test; no shared mutable state |
| **State leakage** | Second run fails, first passes | Transaction rollback / truncate / unique namespace; teardown asserted |
| **Network** | Fails when a third party is slow, rate-limited, or changed | Archived bytes / fake adapter; live profile is opt-in |
| **Concurrency** | Rare interleaving failure | Deterministic scheduler or explicit synchronization; stress lane, not default |
| **Locale / timezone** | Date or number assertions differ per machine | Pin locale and zone in global setup; assert ISO/UTC internally |
| **Unstable identifiers** | Snapshot or equality fails on a new UUID | Generate IDs deterministically; normalize volatile fields before comparing |
| **Filesystem** | Temp path length, case sensitivity, separator | Temp root per test; normalize paths; never assert absolute paths |

The **flake policy** is part of the architecture, not a Slack thread:

1. A flaky test is quarantined within one working day, with an owner, a tracking link, and an
   expiry date. Quarantine means excluded from the blocking lane, still run in a non-blocking one.
2. Never retry-to-green as the default. If retries exist, report the retry rate as a metric; a
   rising rate is a defect, not a success.
3. Reproduce with the seed, the clock value, and the execution order printed in the failure.
4. Delete or fix before the expiry. An expired quarantine fails the build — that is the enforcement.

---

## 6. Invariants over examples

Example-based tests pin known cases. They are the base of every suite, but they only cover the cases
someone thought of. **Property-based testing** states the rule and lets the generator hunt for the
counterexample. The value is not "more tests"; it is a different kind of claim.

The five property shapes worth knowing:

1. **Round-trip / inversion** — `decode(encode(x)) == x` for every valid `x` (serializers, codecs,
   parsers, compression).
2. **Idempotence** — `normalize(normalize(x)) == normalize(x)` (dedupe, migrations re-run, sync).
3. **Oracle** — compare an optimized implementation with a simple, trusted one
   (`fast_sort(x) == sorted(x)`), or with the previous release.
4. **Invariant preservation** — a property that survives the operation: the sum of ledger entries
   equals the balance; every emitted event has a valid schema; row count never decreases on upsert.
5. **Metamorphic relation** — change the input in a known way and predict the output change
   (`f(x + 5) == f(x) + 5` for a linear function; sorting does not change the multiset).

Rules for using it well:

- **Start with the pure core.** Parsers, normalizers, money, dates, state machines. Property tests
  against I/O are slow and hard to shrink.
- **Generate domain-valid inputs, not arbitrary bytes.** A strategy that produces invalid emails
  spends its budget rediscovering the validator.
- **Keep the example tests.** A property test proves a rule; an example test documents a case and
  names the regression it prevents. Both, not either.
- **Make the failure reproducible.** Persist the seed/counterexample and print it in the failure.
  A property failure you cannot replay is a rumour.
- **Do not force it.** If the only property is "it returns something", the test asserts nothing. Use
  an example.

The phrase to review against: *test invariants, not by how many tests you have, but by how useful
those tests are.* A single property that catches a real off-by-one on a boundary is worth a hundred
happy-path assertions.

---

## 7. Coverage, mutation, and the honest metric

Coverage answers one question: **was this line executed?** It does not answer whether the result was
checked, whether the branch mattered, or whether the assertion could fail. The thought experiment is
decisive: delete every assertion in a 100%-covered suite and coverage stays at 100%.

- Coverage is a **gap detector**, not a quality score. Use it to find untouched modules, never as a
  target that gates a merge without inspection.
- **Mutation testing** is the honest version: mutate the production code (flip a comparison, drop a
  return, change a constant) and check that some test fails. A surviving mutant is a line the suite
  executes but does not understand. Run it on the core domain modules, not the whole repo, and treat
  the score as a trend.
- **Goodhart's law is the failure mode**: once coverage is a target, tests are written to touch
  lines. The result is assertion-free coverage theatre and a team that no longer trusts the suite.
- What to report instead: the invariants covered, the mutation score for core modules, the flake
  rate, the time-to-signal for the blocking lane, and the number of quarantined tests past expiry.

---

## 8. Snapshot, golden-master, and approval tests

One mechanism, three names: capture output, store it as a baseline, compare future output. It is
excellent when the output is large and structure matters more than individual values; it is a trap
when it becomes a rubber stamp.

Use it for: serialized payloads, generated code, rendered documents, CLI output, report formats,
and characterization tests over legacy code with no other safety net.

Rules:

- **A snapshot is a reviewed artifact, not a build by-product.** It lives in version control, and a
  changed baseline is reviewed like code. `-u` without reading the diff is how a bug becomes the
  new expected behavior.
- **Normalize volatile fields first.** Timestamps, UUIDs, absolute paths, durations, and ordering
  must be frozen or masked, or the test is flaky by design.
- **Keep it small and purposeful.** A 500-line JSON snapshot nobody reads is not a test; it is an
  archive. Snapshot the contract surface, not the whole object graph.
- **Prefer an explicit assertion when it is readable.** Snapshots win when writing the assertion is
  impractical; they lose when the assertion is three lines and states intent.
- **Never use a snapshot as the only test of behavior.** It proves "unchanged", not "correct". Pair
  it with at least one semantic assertion.

---

## 9. Common mistakes catalog

| # | Mistake | Why it fails | Correction |
|---|---|---|---|
| 1 | Assertion-free test | Executes code, verifies nothing | Assert the observable outcome or delete the test |
| 2 | Testing the framework | Re-tests the ORM, HTTP client, or language | Test your rule at the seam you own |
| 3 | Over-mocking | Suite asserts call graphs; refactors punished | Real object, fake only the boundary |
| 4 | Mocking value objects / DTOs | No behavior to isolate | Construct the real value |
| 5 | One giant test | Many reasons to fail; unclear diagnosis | One behavior per test |
| 6 | Assertion roulette | Bare assertions, no messages, no attribution | Split tests; add messages |
| 7 | Eager test | Calls five methods to reach one claim | Arrange data directly; act once |
| 8 | Mystery guest | Test depends on a file/row no one can see | Inline the setup or name the fixture |
| 9 | Shared mutable fixture | Order dependence, parallel collisions | Fresh fixture per test |
| 10 | Sleep-based wait | Flaky on slow machines, slow on fast ones | Poll condition / fake clock |
| 11 | Time-of-day assertion | Fails at month-end, midnight, leap day | Injected clock, fixed instant |
| 12 | Random data unseeded | Irreproducible failures | Seed per test; print the seed |
| 13 | Hardcoded domain strings | Change hunt; collision; meaningless data | Generators + No-String Rule |
| 14 | Generator calls the SUT | Oracle agrees with implementation by construction | Build input independently of the code under test |
| 15 | Silent skip | Green suite that never ran | Skip loudly with reason + owner |
| 16 | Snapshot rubber-stamp | Bugs become baseline | Review every baseline change |
| 17 | Coverage target | Tests that touch lines, not rules | Invariants + mutation on core |
| 18 | Retry to green | Hides flakes and real races | Quarantine with owner and expiry |
| 19 | Test data cloned from production | Privacy risk, brittle, non-hermetic | Synthetic data through generators |
| 20 | Order-dependent tests | Pass alone, fail in suite | Isolate state; randomize order in CI |
| 21 | Test asserts implementation detail | Refactor breaks the suite | Assert visible outcome |
| 22 | Async fire-and-forget assertion | Asserts before the work completes | Await the completion signal |
| 23 | Testing private helpers via reflection | Couples to internals, hides design smell | Move the rule behind a public seam |
| 24 | One test file for the whole app | No ownership; merge conflicts | Mirror the source tree |
| 25 | Duplicated fixtures per module | Drift; two "valid users" | One generator home |

---

## 10. Rules of thumb

Short enough to remember in review, specific enough to act on.

1. **Test invariants, not counts.** Usefulness per test beats number of tests.
2. **Every test must be able to fail for exactly one reason.** If you cannot name it, the test is
   not finished.
3. **Assert the behavior, not the calls.** If the assertion names a method, ask who cares.
4. **A test with no assertion is a smoke test wearing a lab coat.**
5. **If the test needs a comment to explain the number, the number needs a name.**
6. **Don't mock what you don't own; wrap it and fake the wrapper.**
7. **Prefer one real integration over ten mocked units** when the wiring is what breaks.
8. **A test you don't trust is worse than no test.** Delete or fix; never ignore.
9. **Sleep is a bug with a timer attached.**
10. **If it breaks on every refactor, it is a change detector, not a test.**
11. **The test is the first user of your API.** If it is awkward to call, the API is awkward.
12. **Test the seam where the bug can hide**, not the line the coverage report misses.
13. **A skip without a reason is a lie.** A skip without an owner is a permanent lie.
14. **Green means the rules held, not that the code is good.**
15. **Fixtures build the world; generators build the people in it.**
16. **Same meaning, same value; different meaning, different value.**
17. **If two tests cannot tell their users apart, neither can the bug.**
18. **The cheapest test to maintain is the one that asserts the contract and nothing else.**
