# Trailers and footers

Trailers are the structured part of a commit: `token: value` lines at the end, after the body and a blank
line, one per line. Humans skim them; tools parse them. Get the format exactly right, because a trailer that
is 90% right is just a paragraph.

```text
fix(orders): stop double-charging retried payment webhooks

<body>

Closes #4821
Co-authored-by: Jordan Lee <jordan@example.com>
Reviewed-by: Sam Ortiz <sam@example.com>
```

## Issue and work-item references

| Key | Effect | Use when |
|---|---|---|
| `Closes #123` | GitHub closes the issue when the commit lands on the default branch | the change completes the work item |
| `Fixes #123` | same closing behavior on GitHub, and the conventional "this commit is the fix" | a defect being fixed |
| `Resolves/Refs #123` | `Refs` links without closing | partial progress, or a design decision issue |
| `Fixes: 1f2e3d4 ("subject")` | kernel convention: names the commit that introduced the bug - the bisect shortcut | bug fixes in projects that use it |
| `Reported-by: Name <mail>` | credits who found it | security and user-reported defects |
| Tracker keys (`APP-4821`) | host-integration links (Jira, Azure DevOps) | wherever the project's integration expects them |

Put the reference in a trailer, not in the subject text, so the subject stays readable in `git log`.

## Attribution

```text
Co-authored-by: Full Name <email@example.com>     # GitHub and most forges parse this into avatars
Co-developed-by: Name <mail>                      # kernel-style, marks joint authorship
Signed-off-by: Full Name <email>                  # DCO: "I have the right to submit this under the project's license"
Reviewed-by / Acked-by / Tested-by: Name <mail>   # review and test credit
```

- `Signed-off-by:` is a legal statement of the Developer's Certificate of Origin. Use `-s` on the commit
  command only when the project requires it, and **only with the identity the user has configured**. Never
  sign on someone else's behalf, never invent an email.
- `Co-authored-by:` should list people who actually authored or lost work to this commit - not a courtesy
  mention of the reviewer (that is `Reviewed-by`).
- **Agent authorship is the project's decision, asked once.** Detect before acting:
  ```bash
  git log -20 --format='%(trailers:key=Co-authored-by)'                       # already used here?
  grep -niA4 'author\|co-author\|agent' AGENTS.md CONTRIBUTING.md 2>/dev/null | head -20
  git config --get alias.cm; ls .gitmessage 2>/dev/null                       # something appends one?
  ```
  Detected -> use that spelling verbatim, every time, and say where you read it from. Undecided -> ask one
  question (question 7 of `commit` init), and keep it consistent with the branch-name twin in
  [`branch`](../../branch/SKILL.md) so history and ref names never disagree. A trailer is a public claim
  about who did the work: adding one nobody asked for is as unauthorised as removing one the project
  expects. Never invent a name, address, or model string to fill it in - if the exact spelling is unknown,
  ask, because a plausible guess becomes permanent history people cite.
- Do not attach generated-by lines to a human's commit uninvited, and do not strip credit the project
  expects - including from commits made before the rule changed. History is evidence, not a preference.

## Breaking changes

Two spellings, and both should appear when the tooling reads either:

```text
feat(search)!: return { items, suggestions } instead of a bare array

The old shape forced every client to guess whether suggestions were present.

BREAKING CHANGE: /api/search responses are now objects. Consumers must read
.items; ?compat=1 restores the array shape until 2026-01-15.
```

Rules: `!` goes immediately before the colon, the footer keyword is `BREAKING CHANGE` (space, not hyphen),
and the footer states what breaks and how to adapt - a version bump alone is not a migration story. Semantic
release tooling reads this to produce a major bump, so a wrong claim here is a wrong published version.

## Revert commits

`git revert <sha>` generates `Revert "<original subject>"` and includes `This reverts commit <full sha>.`,
which is the machine-readable link you want to keep. Add one sentence for the why:

```text
Revert "feat(search)!: return { items, suggestions }"

This reverts commit 9f2c11ab7d0e4b5c8a1f0d3e6b9c2a4f5d8e1b3c.

Broke the mobile client, which parses the response as an array; 4.2% of sessions
hit an empty results list. Reverted to unblock the release - the fix is to ship
a versioned endpoint and keep the old shape there.
```

Re-apply later as its own commit that references the revert, so the pair reads as a story rather than churn.

## Writing them correctly, mechanically

Trailers are position-sensitive: they must be the last block, contiguous, each on its own line, with a blank
line before them and no prose after them.

```bash
git commit -m 'fix(orders): stop double-charging retried webhooks' \
           -m 'Retry of permanent-failure codes kept the queue hot.' \
           --trailer 'Closes #4821' \
           --trailer 'Co-authored-by: Jordan Lee <jordan@example.com>'

git interpret-trailers --in-place FILE          # add/edit trailers without rewriting the body
git interpret-trailers --if-exists doNothing --trailer 'Signed-off-by: …' FILE
git log --format='%(trailers:key=Co-authored-by)' -5   # confirm a trailer really parsed
```

`--trailer` (git 2.32+) handles the blank line and placement for you. It is the reliable way, especially for
multi-line messages, and it beats hand-pasting `-m "…\n\nCo-authored-by: …"` where an editor or shell can
mangle the layout.

## Reading history through trailers

```bash
git log --grep='BREAKING CHANGE' --oneline            # every contract break, for a migration doc
git log --format='%h %an %s' --trailer='Fixes'        # who fixed what
git log --all --format='%(trailers)' | sort -u        # which trailers this project actually uses
```

That last one is how you discover the incumbent trailer vocabulary before adding your own ([`04`](04-conventions-and-when-to-drop-them.md)).
