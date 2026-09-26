---
name: dbug-regression-testing
description: Turn every real bug into a permanent regression test — use when a failure is confirmed and about to be fixed (or was just fixed and has no test). Drives the fail → fix → pass loop, picks the lowest test layer that actually exercises the broken path, and decides honestly when a test is NOT reasonable (needs disproportionate infrastructure, lives only in production, is inherently flaky) so verification happens another way. The core dbug idea: "every bug is a chance to test."
---

# dbug-regression-testing — every bug is a chance to test

A bug is the cheapest source of *real* test cases the project will ever
get. The output is not just "problem removed" but "problem removed **and
proven removed**, with a tripwire left forever."

## The loop

```
Confirmed failure (from investigation — cause known, evidence ≥ level 3)
   ↓
Reproduce the ACTUAL failure as a test        ← real user path/data/shape,
   ↓                                             not an invented look-alike
Run it: it must FAIL for the right reason     ← red proves the test bites
   ↓
Apply the fix (investigation §5 design)
   ↓
Same test: PASSES                              ← green proves the fix bites
   ↓
Full local suite still passes                  ← the fix broke no neighbour
   ↓
KEEP the test — permanent regression protection
```

The failing-first step is the whole point: a test written after the fix
proves only that current code satisfies it, not that it catches the bug.
If the fix is already applied (e.g. user patched it by hand), *revert it
temporarily* to watch the test fail, or state explicitly in the commit/PR
that red-first was skipped and why.

## Choosing the layer — lowest layer that exercises the broken path

| Bug lives in… | Test at layer | Why |
|---|---|---|
| pure function / calculation / parser | unit | fastest, no deps |
| handler/service logic with dependencies | integration (real DB in txn w/ rollback, or harness per `backend/`) | the seams ARE the bug |
| API contract (request→response correctness) | API/route test against app, no browser | catches serialization, auth, validation layers |
| DB state / schema / migration | verification script or migration test (`database/`) | asserts catalog truth, not app opinion |
| component render logic, client state machine | component/unit test with jsdom or framework test utils | cheaper than e2e by an order of magnitude |
| cross-system user journey (browser→server→DB really wired) | e2e (Playwright-class) | **intensive — ask first** |
| only reproduces in production | no test yet → `production/` observability + manual verify; a synthetic repro if one can be built | honesty over theatre |

Rules:
- Reuse the project's existing test layout, runner, fixtures, CI hooks.
  Find them first (`ls` the test dirs, read one existing test) — mirror it.
- One bug → one focused test; a broad breakage → one test per distinct
  failing layer, not a mega-test.
- Test named after the *failure*: `test_user_order_survives_refund_retry`
  beats `testOrder3`. A future reader must see the tripwire's purpose.

## Fail-for-the-right-reason check

The red run must fail with the bug's actual signature (same assertion,
error, or wrong value), not because the harness itself is broken (missing
env, unrelated exception, flaky seed). If it's red for the wrong reason,
the test is worthless before the fix and misleading after.

Also demand **determinism**: same result every run, no wall-clock sleeps
standing in for synchronization (that's a flaky test, i.e. no test).
Probabilistic bugs → convert to a measurable condition first (loop N,
stress with fixed seed) — see escalation ladder L1 reproduction hierarchy.

## When NOT to auto-write the test

Skip — with a one-line explicit reason in the summary to the user — when:

1. **Disproportionate infrastructure**: needs a fresh e2e stack, browser
   automation, seeded external services the repo doesn't have. → That's a
   *proposal*, not a solo build: state cost, offer, let the user decide
   (dbug gate #2). A manual verification script in `.debugging/tmp/` plus
   careful human check may be the honest answer.
2. **Genuinely unreproducible outside production**: instrument instead
   (`production/`), so the *next* occurrence is captured as evidence; then
   the test can be written from the capture.
3. **Non-deterministic by nature** and no way to pin the inputs (pure
   third-party timing). Documented manual verify + monitoring is truth;
   a flaky committed test is a liability.

Skipping the test never skips verification — something must still prove
the fix works; say which method and why sized to the risk.

## After the fix

- [ ] Regression test committed, passing, wired into normal suite (CI runs it)
- [ ] The bug's *shape* checked at other layers (same defect via another
      caller?) → `investigation/` stance 3
- [ ] If reproducible-by-procedure emerged (e.g. "how we test write-skew
      fixes"): capture via **how-to-do**

---
**Related:** building the repro script first lives in
[`../instrumentation/SKILL.md`](../instrumentation/SKILL.md) (tmp/) — the
script is scaffolding, the committed test is the keepsake. ·
[`../investigation/SKILL.md`](../investigation/SKILL.md) — when cause must
be proven before writing the test.
