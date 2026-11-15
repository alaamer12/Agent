# Auth and tokens — getting access without leaking it

Two different credentials exist and they are never interchangeable: the
**gh CLI login** (the user's identity, on their machine) and
**`GITHUB_TOKEN`** (an ephemeral per-run token, inside Actions). Most
"authorization" questions are about which of the two is wanted.

## The agent-safe flow

1. Check, don't assume: `gh auth status` — shows account, host, and
   granted scopes.
2. If unauthenticated, hand the interactive step to the user: they run
   `gh auth login` (the device flow waits for input — an agent running
   it deadlocks). In a chat session the user can run it in place with
   the `!` prefix; otherwise point them to their terminal.
3. Confirm scopes only after they logged in. Missing a scope is fixable
   without a re-login: `gh auth refresh -s workflow` (repeat `-s` per
   scope).

Scopes that matter for this skill's tasks:

| Scope | Needed for |
|---|---|
| `repo` | reading private repos, checks, logs, pushing fixes |
| `workflow` | pushing any change under `.github/workflows/` — the classic silent 403 when a CI fix edits the workflow itself |
| `read:org` | org-owned repos, team queries |
| `gist` | never needed here |

GHES (Enterprise Server): `gh auth login --hostname <host>` — same rules,
wrong host is a common cause of "works on github.com, 404 here".

## Failure code → actual cause

| Symptom | Cause | Move |
|---|---|---|
| 401 | expired/revoked login | user re-runs `gh auth login` |
| 403 on pushing a workflow file | missing `workflow` scope | `gh auth refresh -s workflow` |
| 403 on PR merge/approve | the token's role lacks that permission, or branch protection | it is a permissions question, not an auth one — see below |
| 404 on a private repo | no access at all (GitHub hides private as 404) | the user decides who has access; say so and stop |
| rate limit | anonymous API use or a burst | authenticate, back off, never "rotate" by asking for someone's token |

## Never do

- Ask the user to paste a token value into chat, or print `gh auth token`
  into output, logs, or a scratch file. If the agent lacks access, the
  answer is a login the user performs, not a token the agent receives.
- Put a secret in a CI log to "debug why auth fails" — masking exists
  but a printed secret is still exposure. Print scope names and codes,
  never values.
- Use a personal token where the platform offers a short-lived
  credential (OIDC for cloud, `GITHUB_TOKEN` for API calls in Actions).

## Inside workflows: GITHUB_TOKEN

Every Actions run gets one automatically; nothing to store. Its power is
set by the `permissions:` block (see `hardening.md`), and
*"Resource not accessible by integration"* means exactly that: the
role holding the token lacks the permission the step attempted — fix the
`permissions:` entry, do not swap in a personal PAT to "make it work".
For cloud providers (AWS/Azure/GCP) use OIDC role assumption instead of
stored keys.

When a workflow itself must run `gh` (e.g. commenting a PR):
`GITHUB_TOKEN` exposed as `GH_TOKEN` env **after** its permissions were
narrowed is the default; a fine-grained PAT stored as a secret is the
fallback when the job legitimately needs more than the default role —
least scope first, per `hardening.md`.
