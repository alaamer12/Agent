# Truthfulness — does the diff do what it claims?

A diff can be perfectly readable and still not ship the change it advertises. This is the review that catches
"implemented X" where X is half-done, or a fix that quietly weakens the code around it.

## Build the claim ledger

Extract every claim, then point at the hunk (or its absence) that satisfies it.

| Claim (from message / PR / ticket) | Hunk | Verdict |
|---|---|---|
| "rejects expired tokens" | `auth/guard.py` new `if expired: raise` | satisfied |
| "adds a regression test" | `tests/test_guard.py` — new test asserts the raise | satisfied |
| "also fixes the retry loop" | no hunk in the retry path | **unshipped claim** — ask or drop the sentence |
| (none claimed) | `scripts/deploy.sh` permissions 100644 → 100755 | **unclaimed change** — why is it here? |

Unshipped claims are a message problem; unclaimed changes are a review problem. Both belong in the report.

## Tests: present, real, unweakened

- **Present** — a code change with no test hunk is not automatically wrong, but it is a finding; say "no tests in
  the diff".
- **Real** — does the new test exercise the new branch, or call the function and assert nothing?
- **Unweakened** — the expensive hunk: an assertion changed from `== 3` to `>= 1`, a test deleted, disabled
  (`.skip`, `xfail`, `@Ignore`, `t.Skip`), a mock added where a real dependency used to be asserted. A weakened
  test is how a red suite turns green without the bug being fixed.

```bash
git diff <range> | grep -nE '^\+.*(\.skip|xfail|@Ignore|t\.Skip|pytest\.mark\.skip)'
git diff <range> -- '*test*' '*spec*' | grep -n '^-[^-]'      # removed test lines
```

## Leftovers

| Leftover | Grep |
|---|---|
| debug prints | `^\+.*(console\.log|print\(|dbg!|fmt\.Println|System\.out)` |
| breakpoints / pauses | `^\+.*(debugger;|breakpoint\(\))` |
| artificial delays | `^\+.*(sleep|setTimeout|time\.Sleep)\(` |
| disabled code | `^\+.*(//|#|--)\s*(TODO|FIXME|XXX|HACK)` or large commented blocks |
| temporary flags | `^\+.*(DEBUG|DEV_MODE|SKIP_AUTH|BYPASS)\s*=\s*(True|1|true)` |
| broad catches | `^\+.*catch\s*(\([^)]*\))?\s*\{\s*\}` or `except\s*:\s*pass` |

These are questions, not verdicts — a `print` may be a CLI's output. The finding is that it was not mentioned.

## Partial staging and mixed concerns

```bash
git status --short
git diff            # worktree only
git diff --cached   # staged only
```

A diff that looks complete may be half the work if the rest sits unstaged. Conversely, a single commit can mix
concerns: check whether every file belongs to one change
([`../../commit/SKILL.md`](../../commit/SKILL.md) owns splitting; this skill only flags it).

## Generated artifacts

- Lockfile changed, manifest did not (or the reverse) → unreproducible or unexplained dependency change.
- `dist/`, `*.min.js`, `*.map`, snapshots (`__snapshots__`, `*.snap`) changed without the source or test that
  produces them.
- A generated file edited by hand — the next regeneration silently reverts it.

The question is never "is the generated file different"; it is "was it regenerated from the changed source, and
is that source in the diff".

## Secrets and personal data in added lines

```bash
git diff <range> | grep -nE '^\+.*(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'
git diff <range> | grep -nEi '^\+.*(password|secret|token|api[_-]?key)\s*[=:]\s*["'"'"'][^"'"'"']{12,}'
```

A hit is a rotation event, not a follow-up ticket — the value is already in the object database once committed.

## Scope: the hunks that do not belong

- Reformatting in a file that also has logic changes (the review hides the logic).
- Renamed variables/files inside a fix (the diff doubles).
- Unrelated dependency bumps, config tweaks, version strings, commented-out experiments.
- Whitespace-only files in a logic change.

These are not crimes; they are noise that makes the claim harder to verify. Flag them and, when the change is
yours, split it with the `commit` skill.

## Binary and opaque changes

A binary hunk cannot be reviewed, only **accounted for**:

- What is it, who produced it, and is the producer in the diff?
- For images/assets: is it the intended file (name, size, dimensions, format) — check with `file`/`identify`,
  not by trusting the diff.
- For compiled artifacts: they do not belong in a source diff at all.

## The report line for each finding

```text
finding:  <what is wrong or unverified>
evidence: <path:line at the new side, or the command + output>
impact:   <what could break, for whom>
ask:      <the one question the author can answer>
```

"Could you explain the 40-line change in `deploy.sh`?" is a complete finding. "Looks suspicious" is not.
