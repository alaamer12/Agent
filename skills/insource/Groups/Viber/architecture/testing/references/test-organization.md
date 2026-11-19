# Test Organization

A suite's directory shape is an architecture decision. It tells every future contributor where a new
test belongs, which tests may share a database, which lane runs on a pull request, and what "the
tests for this module" means. Left undecided, the answer becomes "somewhere in `tests/`", and the
suite grows into a junk drawer with a green checkmark.

---

## 1. Organizing principles

1. **Mirror the source tree.** `src/billing/invoice.ts` is tested by
   `tests/billing/invoice.test.ts`. The mapping gives every module an owner, makes drift visible
   (a source folder with no tests is a question; a test folder with no source is a smell), and lets
   a contributor find the tests without a search engine.
2. **One subject per file.** A file named after a unit tests that unit. A file that tests five
   things has no name that tells the truth.
3. **Folder = lane.** The folder a test lives in declares its size and its dependencies: unit,
   integration, contract, end-to-end, live. The runner can then select a lane without parsing test
   names, and reviewers can see the cost of a change.
4. **Support code is not a second production layer.** Helpers, generators, and harnesses live under
   `support/` and are imported by tests, never by production. If production needs the helper, it is
   production code and belongs in `src/`.
5. **Fixtures are data, support is code.** A recorded response, a golden file, or a case table is a
   fixture. A function that starts a server or builds a user is support. Mixing them makes both
   hard to find.
6. **Tests are compiled, linted, and reviewed** under the same strictness as production. A test
   suite that only executes is a suite with type errors waiting to become false passes.

**Colocate or centralize?** Colocate (`src/billing/invoice.test.ts`) when the team works
module-by-module and the runner supports it. Centralize (`tests/billing/invoice.test.ts`) when tests
need a shared harness, a corpus, or per-language tooling, or when the deployable excludes test files
by directory. Both are valid; pick one and state it. Do not mix two conventions in one repository —
that is how a test is written twice because nobody found the first one.

---

## 2. Canonical layout

```text
tests/
├── tsconfig.json                 # tests are typechecked as a project (or the language equivalent)
├── setup/                        # global lifecycle and guards, loaded by the runner
│   ├── no-egress.*               # blocks network/fetch/DNS by default
│   ├── pinned-environment.*      # timezone, locale, deterministic ids
│   └── database.*                # engine, migrated template, teardown
├── support/                      # shared code, imported only by tests
│   ├── generators/               # one file per aggregate: user, order, tenant, session
│   ├── scenarios/                # named business situations
│   ├── harness/                  # server, container, app-in-process, temp project
│   └── from-docs.*               # reads the docs the conformance tests assert
├── fixtures/                     # small, test-owned data
│   ├── recordings/               # archived responses used by contract tests
│   ├── golden/                   # approved outputs
│   └── cases/                    # parameterized case tables (JSON/YAML/CSV)
├── contract/                     # consumer/provider contracts across a boundary
├── db/                           # schema, migrations, engine parity, repository behavior
├── e2e/                          # a handful of real user journeys
├── <module>/                     # mirrors src/<module>/
│   ├── <subject>.test.*
│   └── <subject>.<profile>.test.*
└── conventions.spec.*            # executable architecture (see §5)
```

Some projects keep the large conformance corpus at the repository root (`fixtures/`) because capture
scripts, seeders, and tests all read it. That is fine and often better: the corpus is shared
infrastructure, not test-owned data. The rule is not "everything under `tests/`" — it is **one home,
documented, with a manifest**.

---

## 3. Lanes and profiles

| Lane | Folder / tag | What runs | Environment | Timeout |
|---|---|---|---|---|
| **Unit (small)** | mirrored module folder | pure logic, no I/O | hermetic, in-process | seconds |
| **Integration (medium)** | `<module>` or `db/` | real DB, real HTTP handler, local container | localhost only | tens of seconds |
| **Contract** | `contract/` | consumer expectations against a provider, real gateway in-process | fake externals, real wiring | tens of seconds |
| **End-to-end (large)** | `e2e/` | a few user journeys through the real stack | full stack | minutes |
| **Live** | `<profile>.test.*` | real third-party service, real network | explicit opt-in | minutes |
| **Stress / adversarial** | `<subject>.stress.test.*`, `.adversarial.test.*` | pathological inputs, concurrency, load | non-blocking lane | bounded |

Rules:

- The default command runs hermetic lanes only. A developer must never need a network connection, a
  populated shared database, or someone else's credentials to get a green suite.
- Live tests are selected explicitly (`TEST_PROFILE=live`, a tag, a separate script) and never
  silently included. Their failures are reported in a separate lane so a third party's outage does
  not block a merge.
- Every lane has a timeout. A lane without a timeout is a hang waiting for a Friday afternoon.
- Randomized order in CI is a cheap way to expose order dependence; keep it off locally when a
  developer needs a stable repro, on in the nightly lane.
- Tests that genuinely cannot run in an environment **skip loudly with a reason**, never pass
  silently. Better still, make the dependency required in CI and let the local machine skip.

---

## 4. Naming contract

| Pattern | Meaning | Example |
|---|---|---|
| `<subject>.test.*` | Behavioral test for one subject | `invoice.test.ts` |
| `<subject>.spec.*` | Conformance/meta test: asserts a documented rule, not product behavior | `conventions.spec.ts` |
| `<subject>.<profile>.test.*` | Same subject, specific engine/profile/lane | `smoke.sqlite.test.ts`, `youtube.provider.test.ts` |
| `<subject>.adversarial.test.*` | Hostile inputs, boundary abuse | `cardinality.adversarial.test.ts` |
| `<subject>.stress.test.*` | Volume, duration, concurrency | `orchestrate.stress.test.ts` |
| `support/`, `setup/`, `fixtures/`, `scenarios/` | Non-test modules by role | `support/generators/user.ts` |

Some ecosystems use `.spec` for all tests and `.test` for unit tests, or the reverse. The names
matter less than the distinction: **behavior tests** and **meta tests that assert the project's own
rules** are different jobs, and a reader should be able to tell them apart from the filename alone.
If the project already uses one convention everywhere, keep the meta tests in a named folder instead
(`tests/conformance/`); do not rename the world.

**Test names state the claim.** The file names the unit; `describe` names the behavior group; `it`
names the rule:

```text
invoice.test.ts
  describe("refunds")
    it("rejects a refund after the settlement window")
    it("allows a partial refund below the captured amount")
```

Not `it("works")`, not `it("test refund 2")`. A failure should read as a sentence about the product.

**Declare what the test protects.** A short header comment linking the test to the rule it enforces
turns a failure into an argument:

```ts
/**
 * Protects: docs/conventions/language.md §10.1 — pure modules import no I/O.
 * Failure here means the documentation and the code disagree; fix one, not the test.
 */
```

Keep it to the invariant and its home. A test file that explains its own existence in ten lines is
compensating for a bad name.

---

## 5. Meta-tests: executable architecture

Every binding rule that a compiler cannot see needs a test, or it is a preference. This is the
highest-leverage organizational pattern in a mature suite: the documentation names the test, and the
test reads the code.

A conformance test has four properties:

1. **It reads source, not memory.** Parse the AST (or the schema, or the docs) on every run; never
   keep a hand-maintained list of "known good" files that drifts.
2. **It can fail for the right reason.** Each rule is its own test with its own failure message
   naming file and line, so a red run says which rule broke — not "conventions failed".
3. **It cannot pass vacuously.** Assert a **sanity floor**: the number of discovered files or rules
   must be at least the known minimum. A path typo that discovers zero files must fail loudly, not
   produce a green suite that checked nothing.
4. **It is offline and deterministic.** Read files and parse; do not execute the module under test,
   hit the network, or depend on the clock.

```ts
// tests/conventions.spec.ts — sketch
const files = discover(PURE_MODULES);          // real discovery, no hardcoded list of results
it("discovers the pure set", () => {
  expect(files.length).toBeGreaterThan(20);    // sanity floor: a path bug cannot pass
});
for (const rule of RULES) {
  it(rule.title, () => {
    const hits = scan(files).filter((v) => v.rule === rule.id);
    if (hits.length) throw new Error(format(hits));            // file:line + rule meaning
  });
}
```

Two more meta-test shapes worth adopting:

- **Docs-to-code census.** Read the authoritative table (schema reference, route list, settings
  catalog) and assert the code declares exactly what the document declares. The document has
  probably been wrong once already; the test is the only form of the rule that can mean anything.
- **Differential / parity.** Run the same operation through two implementations (two SQL dialects,
  two adapters, old and new parser) and assert they agree on the *observable* result: same bound
  values in the same order, same fields, same error kind. Parity is a behavior claim, not a string
  comparison.

Meta-tests must themselves be reviewed. A scanner with a broken regex is worse than no scanner: it
manufactures confidence. Test the scanner against a known violation fixture at least once.

---

## 6. Global setup and guards

Guards are the difference between a hermetic suite and a suite that happens to be offline today.

| Guard | What it blocks | Proof it works |
|---|---|---|
| **No egress** | `fetch`, HTTP(S) clients, raw sockets, TLS, DNS | A positive-control test *tries* each and requires a named refusal |
| **Pinned time** | Wall-clock date/time zone leaking into assertions | Assert the runner's zone and a fixed instant in setup |
| **Pinned locale** | Host locale changing number/date formatting | Assert the locale and a formatted sample |
| **Schema** | Untracked ad-hoc DDL drifting from migrations | Apply the authoritative migration path, never a test-only `CREATE TABLE` copy |
| **Database state** | Rows leaking across tests | The isolation test from [fixtures-and-generators.md](fixtures-and-generators.md) §2.2 |
| **Test-only code** | `.only`/`.skip` reaching CI | Lint rule or a conformance test over test sources |

Two cautions, both learned the hard way:

- **A guard is not a sandbox.** Monkey-patching `fetch` and `http.request` stops an accidental call
  in a well-behaved module; it cannot stop a native binding that opens a socket underneath. Say so
  in the guard's own comment, and put the authoritative isolation in the CI runner (a network
  namespace, a container with no route out) where it sits below every module object.
- **Prove the guard fires.** A guard that has never been observed blocking something is a
  superstition. The positive-control test is small, runs with the suite, and is the only evidence
  that the guard is real.

---

## 7. The corpus, when the world is not reproducible

Some suites replay archived reality: captured HTTP responses, scraped pages, market data, third-party
API payloads. This is the right answer for sources that change without notice, but only if the
corpus is self-describing.

```text
fixtures/
├── manifest.json               # every payload: digest, byte count, media type, source, captured_at
├── payload/<hh>/<sha256>.gz    # content-addressed, stored once, N pointers
├── captures/<run>.json         # what was seen, per line/URL; points into payload
├── expected/<table>.json       # the machine-readable conformance table
├── golden/                     # approved outputs for golden-master tests
├── _incoming/                  # staged captures, not trusted until promoted
└── README.md                   # layout + the rules below
```

The rules that make it trustworthy:

1. **A digest that disagrees with its bytes voids every claim above it.** A test recomputes
   `sha256(decompress(file))` for every payload and asserts it equals the manifest. Without that,
   "archived" is a word, not a property.
2. **No orphan payloads.** Every blob is cited by a capture row; every capture row points at a blob.
   An orphan is a corpus that no longer describes itself.
3. **Nothing asserts a value the world owns.** If a bank's price moved between capture and review,
   a value assertion fails for a reason that is not a regression. Assert structure, shape, presence,
   and absence; assert a value only where the value is the contract.
4. **Staging is not truth.** `_incoming/` is where a human or script drops salvage; promotion into
   `payload/` is a reviewed act with a manifest entry.
5. **Re-capture is deliberate.** New bytes are a new digest, never an overwrite. That is how a
   changed upstream becomes visible instead of silently absorbed.
6. **The README states the rules, not just the layout.** The next person needs to know what a digest
   mismatch means, not only where the folder is.

The same discipline applies to golden files and snapshot baselines: content-addressed or versioned,
reviewed on change, normalized for volatile fields, never regenerated blindly.

---

## 8. CI lanes and the budget

A practical split that keeps feedback fast without pretending the expensive tests do not exist:

| When | Runs | Budget |
|---|---|---|
| Pre-commit / watch | unit lane for touched modules | seconds |
| Pull request | unit + integration + contract, hermetic, randomized order | minutes |
| Merge / nightly | end-to-end, stress, mutation on core modules | tens of minutes |
| Release | live smoke against real providers, migration rehearsal | as needed |
| Always | conformance tests, guard positive controls | seconds |

Rules:

- **Fail the lane, not the suite.** A live-provider outage does not fail the pull request; it fails
  the live lane and notifies its owner.
- **Quarantine is visible.** A quarantined test is reported in a non-blocking job and fails the
  nightly once its expiry passes. Silent exclusion is how a suite loses coverage without anyone
  deciding to.
- **Time is a metric.** Track the blocking lane's p50/p95. A suite that takes 40 minutes is a suite
  people stop running, and a suite people stop running is a suite that rots.
- **Test code is part of the build.** Typecheck and lint the test tree in CI (a separate tsconfig or
  project reference is enough). Untyped tests are how a refactor leaves broken tests that still pass.

---

## 9. What two real suites teach

Both reference suites are worth studying because they made the same decisions independently, in
different stacks and domains.

**From a scraped-data pipeline (TypeScript, Vitest, offline corpus):**

- The test tree mirrors `core/` module-by-module (`acquire/`, `parse/`, `read/`, `store/`, `ui/`),
  so "where do the tests for this parser live?" has one answer.
- `tests/conventions.spec.ts` reads source with the compiler API and enforces nine rules the
  documentation declares but the compiler cannot see — including a sanity floor so a discovery bug
  cannot pass. The documentation names the test that enforces it.
- `tests/setup/noEgress.ts` blocks five egress paths, and an in-suite positive control tries each
  one and requires a refusal; the comment is honest that this is a guard, not a sandbox, and names
  the stronger CI isolation.
- The offline corpus is content-addressed with a manifest; a replay test recomputes every digest and
  an orphan check keeps the corpus self-describing. The corpus README states the four rules that
  make it trustworthy, not just the folder map.
- Nothing asserts a value the upstream world owns; structure, shape, and absence are the claims.
- Fixtures are small and local (`tests/fixtures/`), while the shared corpus lives at the repository
  root because capture scripts also read it.
- `conventions` rules live in a `*.spec.*` file, separate from behavior tests — the naming does real
  work.

**From a mobile/media client (TypeScript, Bun, real gateway in-process):**

- `tests/contract/` holds the harness: a real PocketBase binary, the real orchestrator, an injected
  prober, driven over the app's own `fetch`. Contract tests hit the same gateway and pipeline as
  production while staying deterministic.
- The harness starts infrastructure, waits for a health signal with a bounded poll (never a fixed
  sleep), and tears it down; a missing binary **skips with a clear reason** instead of silently
  passing.
- `tests/db/differential.test.ts` runs the same query builder through both dialects and asserts
  parity on bound values, order, fields, and table — a behavior claim, not a string comparison.
- The test project has its own `tsconfig.json` and is typechecked (`tsc -p tests --noEmit`) as part
  of the build, so refactors cannot leave type-broken tests behind.
- Test names describe the protected contract
  (`Protects: Docs/v1/OW/structure.md — "every sugar = one file + BOTH engines"`), not the function
  called.

The shared lessons: mirror the tree, separate behavior tests from meta tests, keep a shared harness
in `support/`, make the corpus self-describing, prove the guards, and typecheck the tests.

---

## 10. Anti-patterns

| Pattern | Symptom | Correction |
|---|---|---|
| `tests/` junk drawer | Files named `misc`, `temp`, `test2` | Mirror the source tree; one subject per file |
| One test file per app | Merge conflicts; no ownership | Split by module/subject |
| Mirror drift | Source folders with no tests; test folders with no source | A coverage map / conformance check, reviewed monthly |
| Helpers imported by production | Test code shipping in the bundle | Move to `src/` or invert the dependency |
| Tests importing other tests | Order and state coupling | Extract support code; never import a test file |
| Fixtures with absolute paths | Passes on one machine | Path from the test root / temp dir |
| Committed snapshots nobody reviews | Bugs become baseline | Review every baseline diff; normalize volatile fields |
| `.only` / `.skip` drift | Half the suite never runs | Lint rule; quarantine with owner and expiry |
| Environment-dependent default lane | Needs a shared DB or a network | Hermetic default; live behind a profile |
| Support code that mirrors production | A second implementation to maintain | Keep helpers thin; generators build data, they do not re-implement rules |
| Global mutable state in setup | Cross-test surprises | Fresh per test; pass state explicitly |
| Corpus without a manifest | "Archived" bytes nobody can verify | Digest test, orphan check, documented rules |

---

## 11. Checklist

- [ ] The test tree has a stated mapping to the source tree.
- [ ] Every lane has a folder and a tag; the default run is hermetic.
- [ ] Behavior tests and conformance/meta tests are distinguishable by name or folder.
- [ ] Support code lives in one place and is never imported by production.
- [ ] Generators, scenarios, harnesses, and fixtures each have one home.
- [ ] Global setup pins timezone, locale, and determinism; guards have positive controls.
- [ ] The shared corpus has a manifest, a digest test, and an orphan check (if one exists).
- [ ] Tests are typechecked and linted in CI under the production settings.
- [ ] Quarantined tests have an owner, a reason, and an expiry that fails the build.
- [ ] Every binding documentation rule names the conformance test that enforces it.
