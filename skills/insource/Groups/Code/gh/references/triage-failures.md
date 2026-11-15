# Triage failing checks — classify before you touch anything

The failing-check loop: **classify → gather evidence → reproduce locally
→ plan → fix (after approval) → push → recheck.** The classification is
the whole step; agents that skip it debug the wrong thing — editing
application code while the workflow file itself is what broke.

## Step 0 — auth, then scope the failure set

```bash
gh auth status
gh pr checks [pr]                       # current branch PR if omitted
gh run view <run_id> --json name,conclusion,status,event,url,headBranch
```

The bundled one-shot does steps 0–2 and prints failure snippets:
`python <skill-root>/scripts/inspect_pr_checks.py --repo . --pr <n|url>`
(`--json` for machine-friendly output; exits non-zero while failures
remain, so the same command is the post-fix recheck).

## Step 1 — classify each failing check

| Signal | Class | First move |
|---|---|---|
| run shows **"This run likely failed because of a workflow file issue"**, **zero jobs started** | workflow YAML rejected | it never ran — no logs exist; go to `authoring-workflows.md` (quoting/expression traps, actionlint) |
| a job ran and a named step failed | real failure | read that step's log (Step 2) |
| failure is in setup/checkout/network/runner provisioning | infra | `gh run rerun <id> --failed` once; if it clears, report as infra, do not "fix" code |
| test failed here, passed on other jobs or an earlier commit | suspect flaky | rerun first — rerunning to hide a real flake is forbidden; if it reproduces, treat as real and note the rate |
| state `action_required` | fork PR waiting for a maintainer's approval | not a failure; tell the user where to approve |
| state `cancelled` | concurrency group or a human stopped it | check `concurrency:` config and who cancelled (run metadata) |
| `detailsUrl` points outside GitHub (Buildkite, Jenkins…) | external provider | out of scope: report the URL only, do not chase their API |

A PR can hold several classes — take the cheap part of each.

## Step 2 — read the log like it's evidence, not noise

```bash
gh run view <run_id> --log-failed          # only failed steps
gh run view <run_id> --log --job <job_id>  # whole job when context is needed
# run still in progress and the aggregate log refuses:
gh api "/repos/<owner>/<repo>/actions/jobs/<job_id>/logs" > file
```

- Jump to the failing step's headers; the tail (`Process completed with
  exit code 1`) is the reporter, not the cause — the first real error
  above it is the neighborhood.
- Actions annotations (`::error::`, `::warning::`) are pre-extracted
  failures; grep them before the raw stream.
- Distinguish the layer that broke: dependency install vs build vs lint
  vs test vs the action itself (an action stepping on its own bug has a
  totally different fix than a test failing).
- Missing logs are a finding, say so — never paraphrase unseen output.

## Step 3 — reproduce locally, then plan

Run the failing command locally (same image/OS when it matters, e.g. a
`runs-on` difference). Only then draft the fix plan: failing check, run
URL, log snippet, root-cause sentence, proposed change, blast radius —
and **implement only after the user's approval**. The plan may route
through a plan skill if the project has one; inline is fine.

## Step 4 — fix, push, recheck loop

1. Apply the approved fix (if it touched `.github/workflows/`: the
   `workflow` scope and the quoting/actionlint rules of
   `authoring-workflows.md` apply — validate **before** pushing, CI on
   the workflow file is exactly what was broken).
2. Run the project's own test/build gate locally.
3. Push; watch: `gh pr checks --watch` or re-run the bundled script.
4. New symptom → this is the loop, iterate from Step 1 with the new
   evidence; after three fixes that did not take, the classification is
   wrong — stop and re-classify, don't repeat harder.

## Gates — ask the user, never self-serve

- Rerunning until green while the failure reproduces locally.
- Editing a workflow to **remove or skip** a failing check/job "so CI
  passes" — deleting a gate is the user's call.
- Bumping/relaxing a dependency to clear a failure without knowing why
  it was pinned.
- Anything on another repo, `main` history, or org settings.
