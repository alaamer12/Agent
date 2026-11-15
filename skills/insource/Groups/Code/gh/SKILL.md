---
name: gh
description: 'All GitHub CLI/Actions work in one router: fix failing CI/PR checks (gh pr checks, gh run view --log-failed, bundled inspect_pr_checks.py; classify workflow-file vs job vs flaky vs infra vs external), auth and tokens (gh auth scopes, GITHUB_TOKEN permissions, 401/403 causes, never paste a token into chat), author or edit .github/workflows YAML (valid YAML is not a valid workflow: the space-hash comment trap, quoting expression scalars, actionlint gate), keep workflows thin (wiring not logic - move run: bodies into checked-in script files, conditions stay declarative, scripts return exit codes and one-line feedback; embedding programs in YAML breaks block-scalar indentation and mixes shell with language errors), and harden (SHA-pinned actions, least-privilege permissions, script-injection defense via env mapping, fork-PR rules, OIDC, concurrency, timeouts). Also gh run rerun, workflow dispatch, artifact/release inspection. Not for GitLab CI, Azure Pipelines, Jenkins, or application YAML unrelated to Actions.'
when_to_use: 'Anything with gh, GitHub Actions, workflows, CI, or PR checks in it: the user says "fix CI", "the workflow failed", "write a workflow", pastes a run URL, a run says "This run likely failed because of a workflow file issue", a gh command answers 401/403, or a run: block you are writing grows past a couple of lines.'
argument-hint: "[pr number | run URL | workflow file | task description]"
license: 'Apache-2.0 (covers bundled scripts/inspect_pr_checks.py; see LICENSE.txt)'
---

# gh — GitHub CLI & Actions, one task router

Every gh/workflow task shares this entry point. The task decides which
reference to load (routing table below); read only what the task needs —
the laws here are the whole mental model, details live one file deep.

## Laws that hold in every task

1. **A workflow is wiring, not logic.** YAML declares triggers, jobs,
   ordering, conditions, secrets→env mapping, and calls checked-in
   scripts; behavior lives in files that lint, test locally, and diff
   cleanly. A multi-line program pasted into `run: |` is the failure
   class this skill exists to stop: block scalars silently change
   indentation, shell errors and language errors mix in one blob, and
   nothing is testable outside a push-and-watch cycle.
   → `references/logic-in-scripts.md`
2. **Valid YAML ≠ valid workflow.** GitHub Actions rejects files that
   `yaml.safe_load` happily accepts — the run loads with **zero jobs**
   and says *"This run likely failed because of a workflow file issue"*.
   The space-then-`#` comment trap truncates expression scalars; the
   authoritative check is `actionlint`, run before committing any
   workflow edit. → `references/authoring-workflows.md`
3. **Least privilege by default.** Top-level `permissions:` block
   (baseline `contents: read`), actions pinned to full SHA with a
   version comment, secrets and untrusted inputs reach scripts only
   through `env:` — never interpolated into script text.
   → `references/hardening.md`
4. **Auth first; the token never leaves the machine.** `gh auth status`
   before anything else. Interactive `gh auth login` is the user's
   command to run, never the agent's to execute or to ask for a token
   value. Pushing `.github/workflows/` changes needs the `workflow`
   scope on top of `repo`. → `references/auth-and-tokens.md`
5. **CI feedback is one answer.** Exit code = verdict; one-line stderr =
   reason; a step summary/annotation only for what a human will act on.
   Never dump transcripts into PR comments.
6. **Reproduce locally before pushing a fix.** Run the same command the
   runner runs. A "fix" that only exists as a push-and-watch cycle is a
   guess wearing a plan.

## Task router

| The task is… | Load |
|---|---|
| first run, auth error, 401/403/404, "what token does this need" | `references/auth-and-tokens.md` |
| PR checks or a run failed; "fix CI" | `references/triage-failures.md` (+ `scripts/inspect_pr_checks.py`) |
| write or edit any `.github/workflows/*.yml` | `references/authoring-workflows.md` |
| a `run:` block is growing; a fat workflow to refactor | `references/logic-in-scripts.md` |
| review, audit, or harden workflows; "is this safe" | `references/hardening.md` |

## Bundled helper

`scripts/inspect_pr_checks.py --repo . --pr <number|url> [--json]` —
fetches failing checks, pulls Actions logs (with the job-log fallback for
runs still in progress), extracts the failure snippet, exits non-zero
while failures remain, so it doubles as the recheck command after a fix.
Manual command equivalents are in the triage reference.
