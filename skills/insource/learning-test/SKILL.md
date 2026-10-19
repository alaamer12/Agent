---
name: learning-test
description: Write and run a "learning test" (term coined by Jim Newkirk, popularized by Robert C. Martin/Uncle Bob in Clean Code ch.8 "Boundaries") to empirically discover how a third-party library/framework/API actually behaves, instead of guessing, relying on stale training knowledge, or trusting docs that may be incomplete, outdated, ambiguous, or missing the exact case. Use whenever the Agent or the user is uncertain about real behavior/limits of an external dependency — "how does X actually behave", "what happens if...", "does X support...", "what's the limit of...", docs contradict themselves or don't cover the scenario, or before writing production code against an unfamiliar API. Also trigger on "write a learning test for X" or "figure out the limits of X". The test is small, real, executable code calling the actual API the way production code would, to characterize true behavior — not a mock or doc summary. Trigger this instead of guessing at or fabricating claims about library behavior.
---

# Learning Test

A learning test is a small, real, executable test written **not to verify your own code, but to verify your own understanding of someone else's code** (a library, framework, API, service, or runtime). The term comes from Jim Newkirk and is described by Robert C. Martin in *Clean Code*, Chapter 8 ("Boundaries"):

> "Instead of experimenting and trying out the new stuff in our production code, we could write some tests to explore our understanding of the third-party code... In learning tests we call the third-party API, as we expect to use it in our application. We're essentially doing controlled experiments that check our understanding of that API."

**The "third-party code" is not limited to production/runtime libraries.** It applies equally to any dependency whose real behavior is uncertain, including build tools, linters, CLIs, and — notably — testing frameworks and libraries themselves. If the behavior of Jest (or pytest, or any test runner/assertion library) isn't well understood — how a matcher actually compares values, how mocks reset between tests, what a hook actually guarantees about ordering — that uncertainty is itself a legitimate learning-test target. In that case the "third-party code under test" is Jest, and the learning test is simply a small Jest test (or script) written to observe Jest's own real behavior, not to verify any application logic.

## When to use this skill

Use a learning test — instead of guessing, instead of trusting memory, and instead of taking documentation at face value — whenever:

- The Agent (or the user) is not confident how a library/API/framework actually behaves in a specific scenario
- Documentation exists but doesn't cover the exact case at hand, is ambiguous, contradicts itself, or is plausibly outdated for the installed version
- There are too few real-world examples/answers available (thin community knowledge, new or obscure library, internal/private package)
- The behavior needs to be pinned down before writing production code against it, especially for something load-bearing (data integrity, concurrency, error handling, edge cases)
- The user explicitly asks "what happens if...", "does X support...", "what's the limit/behavior of...", or asks to "figure out" or "test the limits of" something
- The Agent notices itself about to state a claim about third-party behavior it hasn't actually verified in this environment/version

**Do not** use a learning test as a substitute for reading available, trustworthy, version-matched documentation first — check the docs, but treat "the docs say X" and "we verified X actually happens" as different confidence levels. A learning test is for closing the gap between the two, not for skipping the first step.

## What a learning test IS and IS NOT

- IS a small, real, runnable piece of code that calls the actual third-party API the way production code would — no mocks, no stubs, no guessing.
- IS a controlled experiment: change one variable at a time, observe the real result, record it.
- IS disposable by default — its job is to produce an answer, not to become permanent test suite coverage (though the user may choose to keep it — see "Step 4" below).
- IS NOT tied to any particular kind of dependency — it applies just as well to a testing library/framework (e.g. learning how Jest actually behaves) as to a production library, a CLI tool, a database driver, or a web API.
- IS NOT required to use a test runner, assertion library, or any formal testing framework at all. The "test" is whatever small, real, runnable thing answers the question — a single script, a one-line REPL/console command, a throwaway file executed directly. Reach for a test runner only when it's the natural way to call the real API being studied (e.g. studying Jest itself, or the project already has one wired up and using it is the path of least friction) — never because "test" implies a framework is required.
- IS NOT a way to test the Agent's own/the project's code — it targets the boundary (the external dependency), not internal logic.
- IS NOT a substitute for checking existing documentation first, when trustworthy docs are available.
- IS NOT free-form exploration with no record of what was learned — the whole point is to walk away with a concrete, written answer.

## The three shapes of a learning test

A learning test can aim at any of these, depending on what's actually uncertain:

1. **Understanding behavior** — "What does this function actually return/do in this situation?" (e.g. does a method mutate its argument, is a callback sync or async, what does an empty/null input actually produce)
2. **Forcing the limit** — deliberately push a boundary condition to see where/how it breaks or changes behavior (e.g. max payload size, rate limit threshold, max nesting depth, concurrency ceiling, timeout behavior)
3. **Figuring out the limit** — the limit's existence is known/suspected but its exact value or shape is not (e.g. binary-search a size limit, sweep a parameter range, vary types/formats until behavior changes)

State up front which shape applies — it changes what "done" looks like (a single confirmed fact vs. a swept range vs. a located threshold).

## Step 1: Scope the question precisely

Before writing any code, write down (briefly, in the conversation, not necessarily in a file) the exact question the test needs to answer. Vague uncertainty ("not sure how retries work") produces a vague, inconclusive test. A good scoped question looks like: "When the client's default timeout is exceeded mid-stream, does it raise `TimeoutError` or return a partial response object?"

If genuinely uncertain what to scope, or if there are several plausible candidate questions, ask the user rather than guessing which one matters most — this is cheap to clarify and expensive to redo.

Check existing, trustworthy, version-matched documentation for the question first. Note explicitly what the docs do and don't answer — that gap is exactly what the learning test needs to close. If the docs fully and reliably answer the question already, say so and skip writing a test.

## Step 2: Write and run the test

- Pick the lightest vehicle that actually answers the question: a single script, a one-liner run directly (e.g. `node -e "..."`, a REPL command, `python -c "..."`), or a full test-runner file — all are valid learning tests. Default to the simplest option that works; only use the project's test framework/runner when that's genuinely the easiest way to call the real API (it usually is when the API under study is a test/assertion library itself, or the project already has one wired up).
- Call the real dependency exactly as production code (or real usage) would — same import paths, same setup, same auth/config — a learning test that doesn't match real usage risks teaching the wrong lesson.
- Isolate one variable per test/assertion where possible. Multiple confounded changes in one run make the result ambiguous.
- Assert on the *actual observed* result, not the expected one — the test's purpose is discovery, so let it tell you the truth rather than writing the assertion you assume will pass.
- For "forcing/figuring out a limit" tests, iterate systematically (binary search, parameter sweep, or boundary-value steps) rather than a single guess-and-check.
- Actually execute the test and capture real output/errors — do not simulate or narrate a plausible-sounding result. If execution isn't possible in this environment (no network access, missing credentials, sandboxed), say so plainly rather than presenting a guessed result as if it were observed.
- Iterate: if the first result raises a new question, write the next small test rather than speculating about the answer.

## Step 3: Record the answer clearly

Once the test(s) produce a real answer, state it plainly and concretely before anything else — the specific behavior/limit/fact discovered, with the evidence (the actual output, error message, or measured value) that backs it. This is the deliverable; the test code is secondary. Note any caveats (version-specific, environment-specific, may differ under different config).

## Step 4: Ask what to do with the test — always

**This step is mandatory and must not be skipped or assumed.** Once the learning test has produced its answer, explicitly ask the user what to do with the test artifact. Do not default to any of these — the disposition is the user's call:

1. **Delete it** — the answer is now known and recorded in the conversation/commit message/comment; the test itself isn't needed going forward.
2. **Document it** — turn the finding into a comment, doc note, or ADR-style record near the relevant code so the team doesn't have to rediscover it, without necessarily keeping the test executable long-term.
3. **Keep it as a real, permanent test** — if the behavior being verified is worth guarding against regressions (e.g. "this library's retry behavior must stay X or our error handling breaks"), promote it into the permanent suite, typically under a clearly-named `learning-tests/` or similar directory/tag so it's distinguishable from tests of the project's own logic.
4. **Package it for later** — zip/archive the test and its findings so it can be revisited without cluttering the active codebase now.

Ask this as a real question with these options rather than picking one silently, even if one option seems obviously best — the user may have team conventions (e.g. "we always keep these in `tests/learning/`") that aren't visible from context.

## Anti-patterns to avoid

- Answering "how does X behave" from memory/training data alone when the question actually warrants verification, and presenting that guess with unearned confidence
- Treating documentation as ground truth without noting it wasn't actually verified against the running code/version
- Writing a learning test but not actually executing it, or narrating a plausible result instead of a real one
- Skipping Step 4 and silently deleting, keeping, or discarding the test without asking
- Confounding multiple variables in one test run, making the result hard to attribute
- Using a learning test to validate the project's own code/logic — that's a regular unit test, not a learning test
- Assuming a testing framework/runner is required just because the word "test" is in the name, or assuming a learning test can only target production libraries and never a testing tool itself (e.g. Jest, pytest)
