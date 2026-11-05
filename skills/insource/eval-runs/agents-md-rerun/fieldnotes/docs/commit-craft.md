# Commit Craft

The `commit` skill reads this file before writing any commit message (AGENTS.md section 14).

- Subject: imperative mood, <= 72 chars, survives `git log --oneline` alone.
- Body: what changed and why - the effect, not a diff replay; wrap at 72.
- One commit = one atomic change; split mixed work before staging.
- Trailers: keep the repo's configured human author; add
  `Co-authored-by: Tidepool Agent <agent@tidepool.local>` for agent-made commits
  (identity rule: AGENTS.md section 16).
- Never commit with a failing pre-commit hook; fix the cause (`--no-verify` is forbidden).
