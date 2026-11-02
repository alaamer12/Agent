---
name: commit
description: "Professional git commits, in two modes. GUIDE (default, writes nothing): detect the repo's incumbent convention from its history, split work into atomic units, stage with git add -p, write an imperative subject that survives git log --oneline, a what/why body, readable trailers - plus scenario calls: when to commit, gray zones, a fix interrupting a feature, wip vocabulary, squash or not, repairing history behind a backup ref. INIT (/commit init): co-author this repository's written commit discipline - read what the history and existing tooling do, ask the eight questions the repo cannot answer (shape, types, budget, named branches, ticket keys, body policy, agent authorship (trailer + branch segment), enforcement), draft one document, merge never clobber existing prose, install nothing: no hook, no git config, no CI file - enforcement is the maintainers' choice. Rails: no --no-verify, no committing unread files, no claiming unrun tests, no rewriting pushed history."
when_to_use: The user asks to commit, to write or review a commit message, to split work into professional commits, or to tidy local history. Init mode when they ask to set up commit conventions here, write down the project's commit rules, or document a commit policy. Also /commit, /commit init.
argument-hint: "[init] — or a hint like 'split into atomic commits'"
---

# Commit

A commit is the interface to four readers who arrive later: `git log --oneline` in a review, `git bisect`
during an incident, `git blame` when someone asks *why does this line exist*, and the release tool that reads
your types. Write for them, not for the moment.

> One commit records **one decision**: small enough to understand, honest enough to trace, cleaned up before
> anyone else has to read it. The subject says **what** the tree now does; the body says **why** and what it
> cost. The diff already contains *how*.

Tool names in these pages are **examples in brackets**, never requirements. What a repository needs is a role
filled — a message checked at commit time, a structure offered while typing, a release step that reads the
types — and any stack can fill those roles.

## Two modes

| Mode | Trigger | Writes to the repo? | Use for |
|---|---|---|---|
| **Guide** | any commit request (default) | no — only the commit itself | making *this* change commit well, now |
| **Init** | `/commit init`, "set up commit conventions here", "write down our commit rules" | one document, after the user approves the text | making every future commit in this repository describable by a policy the team agreed on |

Guide never writes anything. Init writes **one discipline document and installs nothing** — no hook, no git
config, no CI file. It is a conversation: read what the repository already does, ask the user the seven
questions the repository cannot answer, then write the agreed rules down. Whether the team later wires a check
up to enforce them is their decision in their stack, and a separate change.

---

# Mode 1 — Guide

## The ten rules

1. **One commit = one logical change** — one unit of behavior that works and is verifiable.
2. **Commit after each logical change, never after a line count** — if you can describe it in one sentence,
   commit now.
3. **Follow the repository's message convention** — Conventional Commits where the repo uses it, sentence
   style where it does not ([`04`](references/04-conventions-and-when-to-drop-them.md)).
4. **Never mix concerns.** Feature + fix + formatting + CSS in one commit "is not one unit — that's a dump."
5. **Commit by intent, not importance.** No change is too small; ten "too small"s become one 200-line blob
   with no context.
6. **History is a record of decisions, not code snapshots.**
7. **Commit freely while developing; clean up before anyone else reads it** — squash/reword so the public
   history shows net-positive changes.
8. **Commits are personal checkpoints; a squash is a public statement.**
9. **Never rewrite pushed, shared history.** No amend, no force-push on branches others depend on — add an
   honest follow-up commit instead.
10. **Record clean intent, clean up later.** When a constraint forces a messy moment, label it truthfully
    (`wip:`, `wip-fix:`, `debug:`) so the cleanup pass can find it.

## The safety gate before any history rewrite

Rule 9 protects other people; this protects you from your own cleanup. Before `rebase -i`, `--amend` beyond
the last local commit, `reset` past `--soft`, `filter-*`, `gc --prune`, or any force-push:

```bash
git branch backup/pre-rebase-<name>             # 1. a named ref at the current tip
git rev-parse --short backup/pre-rebase-<name>  # 2. print it, so it is in the transcript
# … rewrite …
git log --oneline origin/main..HEAD             # 3. the shape you wanted?
git diff backup/pre-rebase-<name> HEAD          # 4. MUST be empty — content unchanged, history tidied
git push --force-with-lease                     # 5. never plain --force on a shared branch
git branch -D backup/pre-rebase-<name>          # 6. delete only after everything verifies
```

A branch, not the reflog: reflog entries expire (`gc.reflogExpire`, ~90 days) and `git gc` prunes unreachable
objects. If step 4 is **not** empty you changed code, not history — that needs its own commit and review.
Full decision tree: [`14`](references/14-repairing-history.md).

## Step 1 — Know what changed before you describe it

Prefer the context you already have; if this session produced the work, don't re-read a 3,000-line diff to
rediscover it. Otherwise inspect cheaply and summarize, never dump:

```bash
git status --short          git diff --stat          git diff --cached --stat
git diff -- <path>          # read only the files that decide the message
```

If you cannot say what the change accomplishes, you are not ready to write its message. A message invented
from filenames is where "update code" comes from.

## Step 2 — Adopt the repository's convention, do not import one

```bash
git log --oneline -20                              # the style actually in force
git log -3 --format='%n--- %h ---%n%B'             # the shape of a real body
ls .githooks .husky .pre-commit-config.yaml .commitlintrc* commitlint.config.* 2>/dev/null
grep -rilE "commit message|conventional commit" CONTRIBUTING* README* docs/ .github/ 2>/dev/null | head
```

| What the repo shows | Do this |
|---|---|
| a message linter, hook manager, or release tool configured (any ecosystem) | obey it exactly; run its check before committing |
| history is Conventional (`feat(scope): …`) | use it, matching its type vocabulary and casing |
| history is sentence style (`Fix rounding in invoice total`) | use that; do not convert the project |
| ticket prefixes (`APP-1234 …`) | include the key as the project does — trailer, not subject |
| fresh repo, no history, no config | Conventional Commits as the default, and say you chose it |

A convention the surrounding commits don't use is noise in `git log`; a tool-enforced convention you ignored
is a failed CI job.

## Step 3 — Split into atomic, change-based commits

- Mixed concerns (`fix` + `refactor` + `formatting` + `dependency bump`) become separate commits
  ([`03`](references/03-atomicity-and-staging.md)).
- A change and the tests that prove it belong together; a test for work you haven't written does not.
- Formatting-only and lint-only edits ride alone, so a behavior change stays reviewable.
- Order them so each intermediate commit is sensible — the reader and `git bisect` walk them in sequence.
- Split when a reviewer would ask "why are these two things in the same commit?"

## Step 4 — Stage deliberately

```bash
git add <paths>            git add -p            # named paths; hunk-by-hunk for a mixed file
git restore --staged <p>   git diff --cached     # fix staging; READ the source of the message
```

- Never a blind `git add .`/`-A` with more than one concern present — it sweeps in `.env`, scratch files,
  build output, and someone else's in-progress edits.
- Scan the staged diff for secrets, keys, tokens, debug printers, commented-out blocks, large binaries.
- In a shared worktree, re-check `git status` immediately before committing; another agent's work stays theirs.

## Step 5 — Write it

```text
<type(scope)!: subject, imperative, <= 50 where possible>     <- or the repo's shape
<blank>
<body: what and why, wrapped at 72; the constraint that made this the right choice>
<blank>
<trailers: Closes #123, Co-authored-by:, Reviewed-by:, BREAKING CHANGE: …>
```

1. **Imperative mood** — it composes with git's own `Merge…`/`Revert…` output.
2. **What changes for the reader**, not which files you touched.
3. **Short enough to survive `--oneline`** — 50 is the budget, 72 the ceiling; the rest belongs in the body.
4. **No trailing period**, no filler (`WIP`, `update`, `fix bug`).
5. **Body when the why isn't obvious** — motivation, the alternative rejected, the risk accepted.
6. **Never fabricate** — no "all tests pass" you didn't run, no "fixed" for a cause you didn't find.

## Step 6 — Check, commit, report

```bash
python scripts/commit_lint.py --file MSG      # format + clarity; exit 1 on findings
python scripts/commit_lint.py --staged        # secrets / junk in what is staged
git commit -F MSG                             # multi-line safe
git show --stat --no-patch HEAD               # the intended files, and only those
```

If the project lints messages in a hook, let it run and **fix the message** — never `--no-verify`. Do not
push, amend a published commit, or rebase shared history as part of "committing" ([`07`](references/07-history-hygiene-and-hooks.md)).
Then report the short hashes, one line each, and anything deliberately left uncommitted.

## Guardrails

- Commit only when the user asked. Writing a message for review is a different request: produce the text, wait.
- Never commit files you have not read; never stage by wildcard with several concerns present.
- Never `--no-verify`, never sign or co-author on someone's behalf, never rewrite pushed history unasked.
- **Never decide authorship disclosure either way.** Whether an agent's `Co-authored-by:` trailer appears is the
  project's answer, not yours: read it from history/`AGENTS.md`; if undecided, ask once, then record it (and the
  matching branch-name rule in [`branch`](../branch/SKILL.md)). Adding attribution nobody asked for is as much an
  unconsented change as erasing the provenance of who did the work.
- **Always create a backup ref before a history rewrite**, prove it was content-neutral with
  `git diff backup/… HEAD` (must be empty), and delete it only after the result verifies.
- Never `git push --force`; `--force-with-lease` only, and only on a branch nobody else builds on.
- Never include secrets or scratch — and if a secret was ever committed, say out loud that rewording does not
  un-leak it: rotation is the fix.
- Respect the project's own build/test instructions; if you didn't run them, report "not run".

## Scenario router

| The situation | Read |
|---|---|
| Is it time to commit? too small? 500 lines of one thing? feature+docs+tests? N similar files? | [`09`](references/09-when-to-commit.md) |
| Two unrelated changes live in one file | [`10`](references/10-hunks-and-splitting.md) |
| Which type? which scope? CSS? chore vs refactor? perf? a fix needing a mini-feature? | [`11`](references/11-gray-zones-type-and-scope.md) |
| A fix interrupts the feature, and policy forbids `fix:` here | [`12`](references/12-fix-interrupts-feature.md) |
| WIP commits, checkpoints, dead-end fixes, squash or not, an 800-line diff | [`13`](references/13-wip-checkpoints-and-squash.md) |
| Something committed is broken or wrong | [`14`](references/14-repairing-history.md) |
| Version bumps, tags, `--follow-tags`, release commits | [`15`](references/15-releases-tags-bumps.md) |
| Need the answer fast | [`16`](references/16-decision-trees.md) |
| Need the exact command and its trap | [`17`](references/17-command-reference.md) |
| Write this repository's commit discipline down | **Mode 2**, then [`18`](references/18-init-the-discipline.md) |

---

# Mode 2 — Init

`/commit init` writes this repository's commit discipline **as a document, with the user**. It installs
nothing — no hook, no `git config`, no CI file, nothing to uninstall.

## Procedure

| Step | What you do | Output |
|---|---|---|
| 1. Read the room | history shape, types and scopes actually used, real subject lengths, branch names, anything that already checks messages, which doc could hold a policy | one short facts block — never ask what the repository can answer |
| 2. Ask the seven | the decisions below, each with its failure mode attached | the project's rules, chosen by its maintainers |
| 3. Draft | the seven-section skeleton, in the project's own vocabulary | text shown in the conversation **before** any file is touched |
| 4. Merge | read any existing commit prose, hook or linter; keep what still holds | a diff the user approves, not a rewrite |
| 5. Write | one document: a `CONTRIBUTING.md` section, or `docs/commit-conventions.md` | the path, plus what links to it |
| 6. Close it | write the maintenance duty in (`Last reviewed: <date>`, decisions recorded in the same change) and name an owner | a policy that outlives its author |

Questionnaire, section skeleton, merge rules, and the enforcement table:
[`18-init-the-discipline.md`](references/18-init-the-discipline.md).

## The eight questions

1. **Message shape** — keep the dialect the history uses, or change it? Changing it is a project decision made
   *before* init, not a default init applies.
2. **Types** — which vocabulary, and is an unknown type a refusal or a shrug? "This repo has no types" is a
   valid rule to write down.
3. **Subject budget** — 50 or 72, matched to what the team actually writes, not to the guide's preference.
4. **Named branches** — which ones must not carry `wip:`/`temp:`/`debug:`? State how you detected them; a wrong
   list blocks nothing and still looks like it works.
5. **Ticket keys** — subject prefix, footer, or not tracked here.
6. **Body policy** — required always, or when the *why* is not obvious — and what counts as non-obvious here.
7. **Authorship** — does an agent's involvement get a `Co-authored-by:` trailer (with what exact name and
   address), or is the human the sole author and the tool invisible in the history? Detect first
   (`git log -20 --format='%(trailers:key=Co-authored-by)'`, plus `AGENTS.md` - its Version Control section is the
   decided home for authorship - and any git alias or template that appends trailers); ask only what the
   repository cannot answer. The same decision has a twin in branch naming
   (an agent segment or none) — see [`branch`](../branch/SKILL.md); record both together so history and ref names
   do not contradict each other. Neither side may be decided silently: adding attribution nobody asked for and
   erasing provenance are the same mistake in opposite directions.
8. **Enforcement appetite** — document only, or a check too? Say plainly that a local check is a courtesy and a
   CI check over the commit range is the layer that survives `--no-verify`.

Two prompts pay for themselves: *"what would make you break this rule?"* — that answer becomes the documented
escape hatch — and *"who owns this document?"*, because an unowned policy file is a suggestion.

## Init rules

- **One document, no installation.** If the user wants a hook, a linter or a CI job, that is a separate change
  they approve line by line, built on whatever the repository already has — never layered on top of it.
- **Merge, never clobber.** An existing commit section or hook means someone already decided part of this: read
  it, quote it, keep what still holds, propose the rest as a diff. Do not delete a rule you merely disagree with.
- **One source of truth.** The same rule written in three files becomes two lies at the next change. `AGENTS.md`
  gets a pointer plus the agent-facing duties (staging hygiene, no `--no-verify`, backup before rewrite); the
  policy itself stays in one place.
- **Every rule carries its reason and its way out.** A rule without a reason gets re-litigated in every review;
  enforcement without a stated escape hatch gets bypassed wholesale.
- **Write the rules in the project's vocabulary.** If they say "trunk" rather than `main`, or "story key" rather
  than issue, use their words — a policy in borrowed words reads as imported and gets ignored.
- **Init never rewrites history and never converts the project.** It records the convention the maintainers
  chose; existing commits stay exactly as they are.
- **Verify anything that claims to enforce.** If a check was wired up because the user asked, run the probes and
  report what it printed. A check nobody has seen refuse something may not be running at all.

## References

| File | Owns | Read when |
|---|---|---|
| [`00-anatomy-of-a-good-commit.md`](references/00-anatomy-of-a-good-commit.md) | What commits are for (log, bisect, blame, changelog), the parts of a message, the reasoning behind each rule | Always, once |
| [`01-subject-line.md`](references/01-subject-line.md) | Imperative mood and why it wins, length budgets by tool, casing and punctuation policy, scope choices, 30 bad→good rewrites | Writing any subject |
| [`02-body-what-why-not-how.md`](references/02-body-what-why-not-how.md) | Body content: motivation, rejected alternatives, accepted risk; wrapping; prose vs lists; when a body is required | Non-trivial changes |
| [`03-atomicity-and-staging.md`](references/03-atomicity-and-staging.md) | Change-based splitting, `git add -p`, bisectability, ordering, tests-with-code, formatting-only isolation, shared-worktree caution | Mixed work in the tree |
| [`04-conventions-and-when-to-drop-them.md`](references/04-conventions-and-when-to-drop-them.md) | Detecting the incumbent style, Conventional Commits in full, the real criticisms and when the format hurts, other vocabularies, changelog tooling | Step 2, and any "should we adopt…" question |
| [`05-trailers-and-footers.md`](references/05-trailers-and-footers.md) | `Closes` vs `Fixes #`, `Co-authored-by:`, `Signed-off-by`/DCO, `Reviewed-by`/`Tested-by`, kernel `Fixes:`, `BREAKING CHANGE:`, revert metadata, `git interpret-trailers` | Anything beyond the subject |
| [`06-scenario-recipes.md`](references/06-scenario-recipes.md) | Bug fix with root cause, refactor, perf, feature flag, dependency bump, generated code, migration, docs-only, CI, security fix | A specific shape you are stuck on |
| [`07-history-hygiene-and-hooks.md`](references/07-history-hygiene-and-hooks.md) | Amend rules, pushed history, rebase-to-tidy, squash-merge policy, the roles enforcement fills per stack, the reference hook | Before amending, or before writing a hook by hand |
| [`08-sources.md`](references/08-sources.md) | Where each convention claim came from, dated; the 2025-2026 pushback on type-first formats; provenance of the scenario material and its known source errors | Citing or re-checking a rule |
| [`09-when-to-commit.md`](references/09-when-to-commit.md) | Cadence by sentence not line count, intent over importance, the "too small" trap, feature+docs+tests cohesion, 500-line single functionality, bulk work across N files | Deciding whether this is one commit, several, or none |
| [`10-hunks-and-splitting.md`](references/10-hunks-and-splitting.md) | diff vs hunk, the full `git add -p` key set (`s`/`e` included), the worked two-changes-one-file case, repairing a merged commit, patch-file caveats | One file holding two intents |
| [`11-gray-zones-type-and-scope.md`](references/11-gray-zones-type-and-scope.md) | Scope styles and the multi-file rule (name the concern, never concatenate, or drop it), subject conventions, and the resolved answers for CSS, `chore` vs `refactor`, `perf`, staticmethod, prints, formatter sweeps, fix-needs-a-feature, mixed diffs | Naming anything ambiguous |
| [`12-fix-interrupts-feature.md`](references/12-fix-interrupts-feature.md) | Separate concerns even while interrupting; `fix/*` branch policy with cherry-pick; the cannot-switch ladder (`wip/` branch → named stash → `wip-fix:` label); commit-now-reorganize-later | A fix appears mid-feature |
| [`13-wip-checkpoints-and-squash.md`](references/13-wip-checkpoints-and-squash.md) | The `wip:`/`temp:`/`debug:` vocabulary, three-phase discipline, multi-day checkpoint patterns, when squashing is right and when it destroys value, big-diff verdicts, squash-merge "one commit on main" | Cleaning up before sharing |
| [`14-repairing-history.md`](references/14-repairing-history.md) | **The backup-ref gate**, broken feature commits, wrong fix with a feature on top, dead-end fix attempts, duplicate fixes vs duplicate messages, regression-from-fix, revert safety | Anything already committed is wrong |
| [`15-releases-tags-bumps.md`](references/15-releases-tags-bumps.md) | One bump per release not per commit, version commits and where the bump command lives per stack, tag pushing (`--follow-tags` vs `--tags`), `-S` vs `-s`, the `-am` untracked-file trap, pre-release checklist | Releases and version files |
| [`16-decision-trees.md`](references/16-decision-trees.md) | Every decision as a fast path: when to commit, which type, which scope, one commit or N, squash or not, broken-and-pushed, the safety gate | Mid-task, no time to read |
| [`17-command-reference.md`](references/17-command-reference.md) | The command set with the trap annotated per command, including the backup sequence and recovery commands | Typing a git command you're unsure about |
| [`18-init-the-discipline.md`](references/18-init-the-discipline.md) | The detection commands, the eight questions with their failure modes, the discipline document's section skeleton, merge-never-clobber rules, enforcement as roles (not products), the maintenance duty, what init refuses to do | Mode 2, before writing anything |

## Examples

Full messages, before and after, one scenario per file — read the one that matches your change:

| Case | Situation | The point |
|---|---|---|
| [`case-01-bugfix-root-cause.md`](examples/case-01-bugfix-root-cause.md) | a real defect being fixed | naming the cause, not the symptom, and the regression test |
| [`case-02-formatting-then-behavior.md`](examples/case-02-formatting-then-behavior.md) | one file, two concerns | the two-commit split that keeps the review readable |
| [`case-03-kitchen-sink-split.md`](examples/case-03-kitchen-sink-split.md) | eight files, four unrelated concerns | partitioning, ordering, and what stayed unstaged |
| [`case-04-breaking-api-change.md`](examples/case-04-breaking-api-change.md) | public contract changed | `!`, `BREAKING CHANGE:`, migration notes, and the consumer-facing line |
| [`case-05-dependency-bump.md`](examples/case-05-dependency-bump.md) | a routine upgrade | when a body is required, and what belongs in it |
| [`case-06-agent-committing-unknown-work.md`](examples/case-06-agent-committing-unknown-work.md) | "commit this" with no session context | reading to understand first, and refusing to invent claims |
| [`case-07-bulk-similar-files.md`](examples/case-07-bulk-similar-files.md) | 20 README files in one sitting | one bulk commit vs per-file commits, decided by intent |
| [`case-08-fix-under-branch-policy.md`](examples/case-08-fix-under-branch-policy.md) | a fix appears mid-feature, and `fix:` is banned on feature branches | the `wip/` branch → named stash → `wip-fix:` ladder, and the cherry-pick back |
| [`case-09-history-rewrite-with-backup.md`](examples/case-09-history-rewrite-with-backup.md) | three dead-end "fix" commits to squash before the PR | the backup ref, the empty-diff proof, and deleting it after |

## Scripts

- `scripts/commit_lint.py` — the checker both modes use: subject length and mood, vague starts, trailing
  punctuation, casing consistency with the repo's history, body presence where a *why* is implied, 72-column
  wrapping, blank line, type/scope shapes, trailer formats, secrets and junk in the staged diff.
  `--history [--shared REF]` learns the repo's style and flags staging vocabulary
  (`wip:`, `temp:`, `debug:`, `try:`, `checkpoint:`, `save:`, `wip-fix:`) and duplicate subjects — "don't
  worry about duplicate fixes, avoid duplicate messages". Exit 0 clean, 1 findings, 2 usage error; no argument
  runs the self-test (18 fixtures). Windows: `python`, not `python3`; output is ASCII.
- **Mode 2 has no script, on purpose.** Writing a repository's discipline is an interview, and the answers are
  not in the repository — they are in the maintainers' heads. The commands it uses are plain `git`/`ls`
  (detection) and the file it produces is prose. [`18`](references/18-init-the-discipline.md) holds the
  questionnaire and the document skeleton.
