# Logic in scripts, wiring in YAML — the organizing practice

Standing question while writing any step: **"can I push this YAML
complexity into a script?"** — if yes, do it. The workflow file stays a
declarative map; the doing lives in files.

## Why embedded programs break (the four measured failure classes)

1. **Block scalars mutate code.** `run: |` hands the interpreter what
   YAML decided about indentation and blank lines — Python
   `IndentationError`s and off-by-one heredocs that never existed in the
   original file.
2. **Two error languages in one blob.** A shell line and an embedded
   Python line fail in the same step: the traceback says Python, the
   exit trap says bash, and diagnosing which language broke means
   reading the YAML like a script.
3. **Untestable, unlintable, undebuggable outside CI.** No local run,
   no editor diagnostics, no unit of reuse; iteration cost is one push
   and one queued runner per experiment.
4. **Copy-paste divergence.** The same 15-line block in four workflows
   becomes four subtly different bugs.

## The split, exactly

| Lives in YAML | Lives in the script file |
|---|---|
| triggers, filters, `concurrency`, `permissions` | every actual operation |
| job graph: `needs`, `matrix`, `outputs` | loops, conditionals over data, retries |
| `if:` conditions that gate a step/job | — keep few, keep named |
| mapping secrets/vars/inputs → `env:` | reading `env` values |
| `uses:` pinned actions; one-line `run:` calling the script | the program itself |

Contract: YAML gives the script an **environment** and a **reason to
run**; the script returns an **exit code** and **one line on stderr**
when it fails. `${{ }}` never gets string-concatenated into script text
(pass values through `env:` — this is simultaneously the injection
defense and the language firewall: the script is one language, the shell
stays two lines).

## File discipline

```
scripts/ci/          # or .github/scripts/ — one entry point per concern
├── test.sh          # invoked: run: bash scripts/ci/test.sh
├── check-api.py     # invoked: run: python scripts/ci/check-api.py
└── deploy.ps1       # invoked: shell: pwsh, run: ./scripts/ci/deploy.ps1
```

- Invoke with the **explicit interpreter** (`bash x.sh`, not relying on
  shebang + exec bit across platforms); if calling directly, make it
  executable in git: `git update-index --chmod=+x scripts/ci/x.sh`.
- `actions/checkout` precedes any step that touches these files;
  `defaults.run.working-directory` sets the base instead of per-step
  `cd` chains.
- Scripts are locally runnable with the same env they'll get in CI —
  that is what makes "reproduce before pushing" cheap.
- Each file self-describes its inputs (a 3-line header: what env it
  reads, what exit codes mean) — no archaeology through the workflow to
  learn the contract.

## Where conditions belong

- **Gating** (run this job/step only for PRs, only on main, only when a
  file changed): declarative — `on:` filters + `if:`. Visible in the
  map, cheap to review.
- **Decision logic** (skip work when data says so, choose a path from
  inputs): inside the script, with `exit 0` and a message. A 40-line
  `run:` block that early-exits around nothing is the anti-pattern both
  rules exist to ban.

## Concise feedback

- Default output: the tool's own summary + the exit code. CI answers one
  question — pass/fail, why, where.
- `$GITHUB_STEP_SUMMARY` only for a small human table (counts, links,
  versions); annotations/`::error::` only where a human must act.
- PR comments from CI: post once, edit the same comment thereafter, cap
  the length. Transcript dumps train reviewers to ignore the bot.

## Reuse ladder — when a script outgrows itself

`[repeat 3+ lines in one file]` → helper function in the script ·
`[same steps in 2+ workflows]` → **composite action** (local,
`.github/actions/<name>/` — inputs/outputs in its own file) ·
`[whole pipeline shared]` → **reusable workflow** (`workflow_call`) ·
`[shared across repos/teams]` → versioned action, SHA-pinned.
Illustrative shapes: stay on the lowest rung that removes the
duplication — a composite action for one workflow's private step is
over-engineering, exactly like the embedded block was under-engineering.

## Before/after — the canonical breakage

```yaml
# BEFORE — 18 lines of Python wearing a YAML coat: indentation roulette,
# ${{ }} pasted mid-code, zero local testability
- name: Label check
  run: |
    import os, json
    pr = json.loads("""${{ toJSON(github.event.pull_request ) }}""")
    labels = [ l["name"] for l in pr.get("labels", []) ]
    # ... 15 more lines, one of which starts with a tab

# AFTER — YAML wires, script does, feedback is one line
- name: Label check
  env:
    PR_PAYLOAD: ${{ toJSON(github.event.pull_request) }}
  run: python scripts/ci/check-labels.py   # exits 1: "missing kind/* label"
```

Same shape in any language the stack uses — the point is the boundary,
not the interpreter.
