# Tests vs Verifiers

## Distinction

| | Test | Verifier |
|---|---|---|
| Purpose | Promise about behavior / protection against regression | Proof that something currently works |
| Nature | Claim that can fail in the future | Observation of present success |
| Medium | Assertions on outcomes, state, or interactions | Concrete artifact (exit code, stdout, binary runs, screenshot, HTTP body, etc.) |
| Selectable | Yes (tagged / categorized) | No — always runs as a fast baseline |
| Speed | May be slower | Must be extremely fast |

A test *may* verify a final outcome (for example by asserting CLI output).  
A pure verifier *cannot* test a behavior; it only shows that the system looks good right now.

## When to write a verifier

Use a verifier for cheap, always-on “smoke” checks that answer:

- Does the main binary still compile and start?
- Does `my_cli --help` (or equivalent) exit successfully?
- Does the health / readiness endpoint respond?
- Do the core packages import without error?

These checks belong in a conventional location such as:

- `verify/`
- `smoke/`
- `scripts/verify.*`
- or the ecosystem’s idiomatic equivalent

They should not require tags, feature flags, or selection. The default test command (or a dedicated fast gate) runs them every time.

## Relationship to tests

- Verifiers give rapid confidence that the system is basically alive.
- Tests give confidence that specific behaviors remain correct under change.
- Prefer turning important behavioral claims into proper tests (with one reason to fail, factories, etc.).
- Keep verifiers minimal; anything that needs rich setup, multiple assertions about behavior, or slower execution belongs in the selectable test suites.

## Anti-patterns

- Treating a green verifier suite as evidence that behavior is protected.
- Making verifiers slow or dependent on heavy external services.
- Putting behavioral regression claims only in verifiers (they will not protect against future breakage as effectively as real tests).
- Tagging or making verifiers selectable — they lose their “always-on baseline” purpose.
