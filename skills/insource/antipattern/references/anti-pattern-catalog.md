# Anti-pattern catalog (investigation candidates)

These are **candidates to test against the project**, not automatic violations. For each one, the entry gives signals worth searching for and cases that look similar but are fine. A finding needs project-specific evidence and consequences.

## Contents
- How to research
- 1. Superficial compliance
- 2. Types and contracts
- 3. Reinventing existing assets
- 4. Duplication and unnecessary abstraction
- 5. Overengineering and complexity
- 6. Coupling, cohesion, layering
- 7. Business rules and domain models
- 8. Integrations and error handling
- 9. Comments and generated code
- 10. Security and reliability
- 11. AI-generated code issues
- 12. Execution model and lifecycle

## How to research

1. Start from the project's stack: search `<framework> anti-patterns`, `<language> common pitfalls`, `<integration> reliability pitfalls`, not generic lists.
2. Prefer official documentation and language/framework guides, established catalogs (Fowler's refactoring and smell catalog, OWASP, CWE, SEI CERT, cloud well-architected reliability guidance), post-mortems, issue trackers, conference talks, and peer-reviewed or empirical studies.
3. Down-rank SEO listicles, vendor marketing, and unsourced claims. Tool and framework guidance ages: check dates and versions.
4. For each source used, note title, URL, and a one-line takeaway. The report cites them.
5. Add stack-specific candidates the list below misses (e.g. N+1 queries in ORM-heavy code, effect-dependency bugs in React, goroutine leaks in Go).
6. The general catalogs worth citing: Fowler's *Refactoring* smell catalog (code smells and their remedies), the OWASP Top Ten and CWE (weakness classes), the Twelve-Factor App (process, logging, configuration, state), language and framework official guides, and cloud well-architected reliability guidance. Cite title, URL, and the date you accessed it, so a later reader can tell whether the source still says that.

## 1. Superficial compliance

Changes that satisfy a checker without satisfying the requirement.
- **Signals:** unexplained `# type: ignore`, `@ts-ignore`, `eslint-disable`, `//nolint`, `#[allow(...)]`, `@SuppressWarnings`; skipped or deleted tests; assertions loosened to match output; mocks that assert nothing; blindly updated snapshots; special-casing test inputs; catch-and-ignore; lowered strictness in lint/type config.
- **Not a violation when:** the suppression is narrow, justified in a comment or issue link, and covers a genuine third-party typing gap or false positive.

## 2. Types and contracts

- **Signals:** casts to `any` / `unknown` / `as unknown as T`, `typing.cast`, `Any` leaking through APIs; types that disagree with runtime shapes; everything optional; stringly-typed fields; DTO and domain types conflated; API spec drifting from handlers; money as float; naive datetimes where time zones matter.
- **Not a violation when:** the cast sits at a validated boundary, or the loose type is deliberate at an untyped edge and narrowed immediately.

## 3. Reinventing existing assets

- **Signals:** reimplementing something a dependency or the framework already provides (date parsing, retries, validation, HTTP clients, auth, crypto); duplicating an internal utility; recreating logos, icons or brand assets by hand when official assets or the project's icon library exist; hand-rolled SDK wrappers beside an official SDK.
- **Not a violation when:** the dependency is unsuitable for a documented reason (size, licence, security, missing feature) or the in-house version predates and is being phased out.

## 4. Duplication and unnecessary abstraction

- **Signals:** copy-pasted logic that has begun to diverge; single-implementation interfaces and factories with no second consumer; pass-through wrapper layers; "utils/helpers/common" dumping grounds; abstraction that forces callers to pass flags to get different behavior.
- **Not a violation when:** duplication is cheaper than coupling (stable, tiny, unrelated domains) or the abstraction exists for a test double or planned second implementation recorded in the project.

## 5. Overengineering and complexity

- **Signals:** configuration for values that never vary; plugin systems with one plugin; speculative generality; god functions or classes; a routine long enough that it mixes several unrelated decisions and its intent has to be reconstructed; deep nesting; long parameter lists or boolean-flag parameters; patterns applied for their own sake; values whose meaning survives only as a magic number or an undocumented config key.
- **Not a violation when:** the complexity is inherent to the domain and localized.

## 6. Coupling, cohesion, layering

- **Signals:** domain code importing infrastructure or UI; circular dependencies; reaching into another module's internals; shared mutable globals; state whose owner and allowed transitions are nobody's responsibility; one database written by several services; feature envy; a change to one concept forcing edits in scattered unrelated files (shotgun surgery); modules that mix unrelated reasons to change.
- **Not a violation when:** the project's documented architecture permits the dependency direction.

## 7. Business rules and domain models

- **Signals:** the same rule implemented in several places with different thresholds or wording; invariants enforced only in the UI; unguarded state transitions; anemic models with rules scattered in services; inconsistent names for one concept; rules duplicated between SQL and code that have drifted.
- **Not a violation when:** variations are intentional (per-region rules) and named as such.

## 8. Integrations and error handling

- **Signals:** outbound calls without timeouts, retries with backoff, or idempotency; several layers each retrying the same failing call, so the load multiplies instead of stopping (retry amplification); swallowed exceptions; every failure collapsed to a generic 500; external payloads trusted without validation; multi-step writes without a transaction or compensation; log-and-rethrow duplication; partial failure leaving inconsistent state.
- **Not a violation when:** failure is truly acceptable (best-effort telemetry) and documented as such.

## 9. Comments and generated code

- **Signals:** comments that restate the code or contradict it; stale TODOs; commented-out code; boilerplate docstrings on every function; unused generated scaffolding; dead feature flags; placeholder bodies.
- **Not a violation when:** the comment records *why*, links an issue, or documents a non-obvious constraint.

## 10. Security and reliability

- **Signals:** secrets in the repo or logs; injection-prone string building; missing authorization checks at boundaries; overly broad CORS or IAM; unsafe deserialization; unbounded queues, loops, or payloads; race conditions on shared state; PII in logs.
- **Not a violation when:** the code is a documented local-only tool and the exposure is bounded. State the assumption.

## 11. AI-generated code issues

Verbosity and an "AI feel" are not findings. Describe the defect, not the suspected author.
- **Signals with real evidence:** imports of packages or APIs that do not exist (or exist under a near-identical name); features nobody asked for; over-defensive checks for impossible states; style that disagrees with the surrounding codebase; tests that restate the implementation; fixes that silence the symptom (see category 1).
- **Verification:** confirm the package exists and is the intended one, confirm the API in the pinned version's docs, and use `git blame` or history to judge how the code arrived.
- **Label as "AI slop" only** when the defect is concrete and the user's own wording uses the term. Otherwise use the plain defect name.

## 12. Execution model and lifecycle

The mistake is assuming a thread, a process, or a request is cheaper or more available than it is.

- **Signals:** a blocking call (disk, DNS, sleep, synchronous HTTP, console read) inside an async/event-loop path; a task or goroutine started and never awaited, cancelled, or joined; no cancellation or timeout propagated into a long-running operation; per-request state kept in a module-level or process-global cache; a background job holding a database connection across idle time; shutdown that skips cleanup of handles, files, or pools; unbounded queue or buffer growth behind a producer that outruns the consumer.
- **Not a violation when:** the runtime is explicitly single-threaded or one-shot (a CLI script, a migration), the blocking work runs on a dedicated pool the project documents, or the growth is bounded by a stated limit and tested at that limit.
