# Testing Architecture Pillar

## 1. Overview & Philosophy

A test suite is a second implementation of the product's rules, written in a language the compiler
cannot check for meaning. Left undesigned, it decays into three familiar shapes: a thousand
assertion-free smoke tests that prove nothing, a mock theatre that turns every refactor red, and a
graveyard of hardcoded `"test@test.com"` values that no one dares change. Each shape is a data
architecture failure before it is a testing failure. This pillar decides the harness, the fixtures,
the generators, the data vocabulary, and the organization once, so every later test inherits them.

The pillar's doctrine:

- **Test invariants, not counts.** Usefulness is the metric, not the number of tests, the coverage
  percentage, or the green badge. A hundred tests that cannot fail for the right reason are worth
  less than ten that pin the rules the product actually depends on. Coverage measures lines walked,
  never understanding earned.
- **A test is a claim with a failure message.** Every test names the invariant it protects and fails
  with text a stranger can act on. A test whose failure requires opening the debugger to interpret
  has not finished being written.
- **Behavior-sensitive, structure-insensitive.** Refactoring must not turn the suite red; a behavior
  change must. A test that breaks on both is a change detector, and a change detector is deleted
  within a quarter.
- **Determinism is constructed, not hoped for.** Clock, randomness, identifiers, locale, ordering,
  network, and filesystem are seams. `sleep` is a bug with a timer attached; a retry that hides a
  flake is the same bug wearing a disguise.
- **Every test has one reason to fail.** One behavior per test, arranged once, asserted with
  specific messages. Assertion roulette — ten bare expectations in one test — turns every failure
  into an investigation.
- **Test data has exactly one home.** Domain values come from generators, never from literals
  scattered across test bodies. This is the **No-String Rule** (§6): a test body names intent; the
  generator supplies value.
- **Generators are the product's test vocabulary.** `UserGenerator`, `OrderGenerator`,
  `SessionGenerator` carry sensible defaults, explicit special states, and derived identity, so
  adding a required field to the domain is one edit, not a suite-wide hunt.
- **Fresh fixture by default.** Shared mutable state is the root of order-dependent failures. Share
  only what is expensive and read-only (an engine, a container, a compiled schema); isolate
  everything a test can write.
- **Mock at the boundary you do not own.** Wrap third-party services in an adapter and fake the
  adapter. Mocking what you own couples the test to today's call graph and calls it a contract.
- **The size ladder is a budget.** Small tests carry logic, medium tests carry wiring, large tests
  carry a handful of journeys users actually make. The ice-cream cone — mostly end-to-end, almost
  no unit tests — is the expensive way to learn this.
- **A suite you do not trust is worse than no suite.** Quarantine flaky tests with an owner and an
  expiry date; never retry-to-green, never mute a failing test without a tracked reason.

Boundary map. The `language` pillar owns types and compiler strictness; this pillar requires test
code to compile under the same settings and adds only what the compiler cannot see. `error` owns
failure payloads; tests assert them but never re-invent their shape. `db` owns schema and
constraints; this pillar owns how a test world is seeded, isolated, and torn down. `plugin` owns the
extension contract; every declared extension point earns a test here. `cross-platform` owns platform
seams; platform-conditional tests belong to the platform lane, never to a shared test that silently
skips. This pillar owns the harness, the data vocabulary, and the organization — nothing else.

## 2. Directory Structure & Assets

```text
testing/
├── method.md                                            # this file — doctrine, workflow, DoD
├── assets/templates/
│   └── testing-architecture-template.md                 # binding document skeleton
├── references/
│   ├── testing-principles.md                            # desiderata, sizes, determinism, invariants, mistakes
│   ├── fixtures-and-generators.md                       # fixture lifecycle, isolation, generator design, sessions
│   ├── test-data-and-the-no-string-rule.md              # data SSOT, semantic identity, enforcement
│   ├── test-organization.md                             # layout, naming, lanes, corpora, meta-tests
│   └── discovery-interview.md                           # targeted questions + the decision each drives
└── examples/
    └── testing-walkthrough.md                           # polyglot pass: generator, session, DB, contract, meta-test
```

## 3. Workflow

1. **Recon (read first, never ask what the repo answers).** Inventory: test runner and config,
   existing directory shape, naming conventions, fixture and factory modules, seed scripts, global
   setup files, CI lanes and timeouts, skip/quarantine markers, coverage and mutation tooling,
   database strategy, and every hardcoded literal in test bodies (grep for `@example`, `test`,
   `123`, `user_`, `2024-`). Count the tests that cannot fail: no assertion, assertion on a mock
   call only, or a snapshot nobody reviews.
2. **Interview** ([references/discovery-interview.md](references/discovery-interview.md)): ask only
   what the code cannot answer — which behaviors are contractual, which environments must be
   hermetic, who owns flaky tests, whether test data may resemble production data, and which
   documentation rules must become executable.
3. **Decide per lane,** reading the reference that owns it:
   - principles, size budget, determinism and flake policy →
     [testing-principles.md](references/testing-principles.md);
   - fixture lifecycle, isolation strategy, generators and sessions →
     [fixtures-and-generators.md](references/fixtures-and-generators.md);
   - data ownership, semantic identity, the No-String Rule and its enforcement →
     [test-data-and-the-no-string-rule.md](references/test-data-and-the-no-string-rule.md);
   - layout, naming, corpora, guards, meta-tests and CI lanes →
     [test-organization.md](references/test-organization.md).
4. **Author** `<docs>/testing-architecture.md` from the template. It is binding for every test in
   the project, including tests written later by agents.
5. **Migrate, do not big-bang.** Introduce the generator directory and the conformance test first,
   then convert one module per change. A suite-wide rewrite hides which test protected what.
6. **Verify the suite can fail.** Break a rule on purpose in a scratch branch and confirm the
   conformance test, the generator, and the boundary test each go red for the right reason. A guard
   nobody has watched fail is a guard nobody has built.

## 4. The Four Layers

Every suite needs four distinct things, and conflating them is the most common organizational
mistake. Naming them once removes most "where does this go?" questions.

| Layer | What it is | Examples | Lifetime |
|---|---|---|---|
| **Harness** | The process-level world: runner, container, server, temp root, database engine, browser | `startPostgres()`, `startPocketBase()`, `tmpProject()` | Session or file; expensive, read-only |
| **Fixture** | The seeded state a test world starts from: schema, reference catalogue, feature flags, clock | `migratedDb()`, `catalogue()`, `fixedClock("2026-01-01T00:00:00Z")` | Function, or session when immutable |
| **Generator** | One domain instance, built on demand with valid defaults and derived identity | `UserGenerator.create()`, `OrderGenerator.paid()` | Per call |
| **Scenario** | A named business situation composed from generators | `expiredSubscriptionFor(user)`, `tenantWithTwoAdmins()` | Per call |

Rules that follow from the split: a generator never owns lifecycle; a fixture never builds domain
instances the test will mutate (it would share them); a scenario reads like the requirement it
represents; a harness never leaks a handle the test can close. If a helper needs two layers at once,
it is a scenario, and it belongs in `tests/scenarios/`, not in a generator file.

## 5. Anti-patterns (the easy paths, each observed in real suites)

| The shortcut | The documented cost |
|---|---|
| Hardcoded `"test@test.com"` in a dozen files | one validation change becomes a suite-wide hunt; parallel runs collide on the unique index |
| One shared user seeded once for the whole suite | order-dependent failures; a test that edits the user breaks every later test |
| `sleep(500)` to wait for async work | flaky on slow CI, slow on fast machines, and wrong under load; poll a condition or advance a fake clock |
| Retrying failed tests in CI | flake rate goes to zero on the dashboard and stays in the product |
| Mocking every collaborator | tests assert the call graph; refactoring is punished, behavior bugs pass |
| A snapshot of a 500-line payload | nobody reads the diff; `-u` rubber-stamps the bug into the baseline |
| Assertion-free "does not throw" tests | 100% coverage, zero protection; a smoke test wearing a lab coat |
| `if`/`for` logic inside a test body | the test now has its own bugs and its own untested branches |
| Test data copied from production | privacy exposure, brittle assertions on values that move, and a suite that cannot run offline |
| A generator that calls the code under test | the oracle agrees with the implementation by construction; tautology with extra steps |
| Skipping a test silently when a dependency is missing | a green suite that never ran the assertion; skip loudly with the reason |
| A conformance test with nothing to scan | vacuous green: assert a minimum discovered count so a path typo fails loudly |
| Chasing a coverage number | Goodhart's law; lines executed, behavior unverified |
| Test names like `works` / `test1` | the suite stops being documentation; failures need archaeology |

## 6. The No-String Rule (summary)

A test body may not contain a literal that carries domain meaning. Identifiers, names, emails,
statuses, amounts, dates, tokens, and expected domain strings come from a named generator, a named
constant, or a value derived from an instance already built. The test names intent; the generator
supplies value.

```text
BEFORE (values invented per test)          AFTER (one vocabulary)
────────────────────────────────────      ─────────────────────────────────────────
user = { name: "Alice",                    user = UserGenerator.create()
         email: "alice@test.com",          admin = UserGenerator.admin()
         role: "admin" }                   session = SessionGenerator.forUser(admin)
expect(user.email).toBe("alice@test.com")  expect(session.userId).toBe(admin.id)
```

Three literal classes remain legal: **the value under test** (`0`, `-1`, `""`, a max integer), **the
malformed value whose wrongness is the point** (named, not inline), and **structural syntax** (a
route template, a regex). Everything else is a finding. Full rule, rationale, and enforcement:
[test-data-and-the-no-string-rule.md](references/test-data-and-the-no-string-rule.md).

## 7. Core Invariants

1. **Never let a test assert a value no generator owns.** If the expected value has no home, the
   test has invented a fact.
2. **Never share mutable fixture state between tests.** Share infrastructure; isolate data.
3. **Never wait with a fixed sleep.** Poll a condition with a timeout, or advance a fake clock.
4. **Never mock a module the project owns when a real instance is cheap.** Fake the boundary, not
   the middle.
5. **Never let a test depend on execution order, wall-clock date, host timezone, or locale.** Pin
   all four.
6. **Never leave a skipped test without a visible reason and an owner.** Silence is a false pass.
7. **Never claim coverage as evidence of correctness.** Name the invariant, or the mutation score,
   or the failing mutation the test catches.
8. **Never let the suite require the network by default.** Live tests are an explicit, opt-in
   profile with their own lane.
9. **Never let documentation rules live only in prose.** A binding rule a compiler cannot see gets a
   conformance test, or it is a preference.

## 8. Definition of Done

`testing-architecture.md` exists and names: the size ladder and its budget, the directory and naming
contract, the fixture lifecycle and isolation strategy per resource, the generator registry with
defaults and special states, the identity rule that makes instances semantically consistent, the
No-String Rule and its enforcement, the suite profiles and CI lanes, the conformance tests that make
documentation executable, the flake policy with an owner and an expiry, and open decisions listed —
never defaulted silently. Shared units (generators, harnesses, scenarios, guards) are registered in
UNITS.md; sync points are declared with their same-change duty.
