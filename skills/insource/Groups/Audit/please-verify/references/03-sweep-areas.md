# The sweep — ten areas, with concrete checks

Work the areas in this order: expectations, then the project, then the change. Each area ends with the same
question: **what evidence level did this area reach, and what did not get checked?** Commands shown are
placeholders - use the project's own (`[build]`, `[test]`, the runner in its docs).

## 1. Requirements coverage

- Take the baseline list from `01-expectation-baseline.md`; for each item, name the artifact(s) that
  implement it.
- Missing artifact = INCOMPLETE. Artifact existing but unproven = the item's evidence level, not more.
- Cross-read: does IDEA.md / the plan / the conversation each list requirements the others don't? Record
  the union, flag the disagreements.
- Watch for **renamed or merged requirements**: the feature exists under a different name. That's coverage,
  not completion - the proof still has to happen.

## 2. Implementation completeness

- Search for the unfinished markers: `TODO`, `FIXME`, "not implemented", "coming soon", empty handlers,
  stubs returning fixed values, placeholder copy, hardcoded sample data standing in for real data.
- Check every route/entry point is wired: declared but unreachable is L0; reachable but empty is a bug.
- Check the promised branches exist: success, error, empty, loading. Count how many were implemented.
- Feature flags: is the promised behavior on by default in the state being delivered?

## 3. Bugs and issues

- Run the project's own gates in order: build, type check, lint, unit, integration, end-to-end. Capture
  command + output + exit code for each.
- Run the app and read the startup logs; runtime errors and warnings count as findings.
- Try the flow once as a user would, not as a developer would (see area 9).
- For each failure: is it in scope of the baseline, pre-existing, or environmental? The report separates the
  three - a pre-existing failure is still a fact about "done", but it is not attributed to this delivery.

## 4. Violations

- AGENTS.md rules and the project's standards: forbidden shells/commands, package manager, privacy list
  (a declared-private path committed is a violation), glossary terminology in user-facing copy.
- Secrets hygiene: keys/tokens in source or fixtures, `.env` example drift, sensitive data in test files.
- License and dependency policy, if the project states one.
- The project's structural conventions: files in the wrong layer, cross-layer imports the rules forbid.

## 5. Consistency

- One concept, one implementation: the same helper/logic written twice (or three times) in different places.
- Naming agrees across code, docs, UI copy - a renamed feature with stale names is a source of future bugs.
- Docs versus behavior: the README's commands and descriptions match what the code does.
- Configs versus code: the declared ports/paths/env names exist and are used.
- Versions and manifests agree: lockfile, package manifest, build config, CI.

## 6. Missing work

What "done" needs that nobody produced:

- tests for the promised behaviors (not for the happy path only);
- migrations, seed data, fixture updates for changed shapes;
- configuration, `.env.example` entries, deployment/build steps;
- documentation updates promised by the project's own conventions (AGENTS.md, README, changelog);
- assets, translations, error copy, empty-state design.

Each absence is a finding with an owner suggestion - not a reason to go build it now.

## 7. Proof of work

- Build the claim-to-evidence table: every statement of completion from the delivery, next to the artifact
  that proves it, next to the level that artifact reaches.
- Anything with no artifact: UNVERIFIED. Anything with only a summary: UNVERIFIED.
- Confirm the artifacts belong to the current state (hash/date/fresh run).
- If the delivery produced a diff, sample the diff against the claims - files changed for unrelated reasons
  are a scope note, not automatically a failure.

## 8. Integration behavior

- Start every component the baseline involves; check they talk: service boots, client connects, the
  promised path completes.
- Exercise the seams: real data shape (or the project's staging sample), malformed input, an empty store.
- For multi-part systems: does the contract between parts hold at runtime, not just in types?
- A component that "starts" but never serves the promised path is L3 without the integration claim.

## 9. Project-level correctness

- Run the flow as the user would, on the promised surface (the phone app on a phone or emulator, the CLI in
  the terminal) - not only through a development harness.
- Reproducibility: can the project's own documented commands take a clean checkout to the working state?
  If not, the README is a finding and the L3/L4 proof does not travel.
- Compare the delivered outcome to the definition of done one line at a time.
- Confirm the environment the proof ran in, and say what differs from the user's real environment.

## 10. Scope, time-box and what was not reached

- State the verification's scope and budget up front; keep a running "not reached" list.
- Sample evenly rather than deeply: every area gets at least one probe; areas central to the baseline get
  the full treatment.
- The final report lists what was verified, at which level, and what remains unverified - the honest map is
  the product of this skill.
