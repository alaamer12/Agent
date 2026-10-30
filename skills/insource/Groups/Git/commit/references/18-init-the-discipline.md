# Init — write this repository's commit discipline, with the user

Mode 2 exists because guidance decays. A guide makes *this* commit better; a written discipline makes the next
six months of commits in this repository describable by one document the team agreed on — including the commit
written at 23:40 by someone who never read the guide.

**Init writes one document and installs nothing.** No `commit-msg` hook, no `git config`, no CI file, no
`.githooks/` directory. Whether the repository enforces the discipline with a hook, a linter, a forge rule, or
nothing but review is a decision the maintainers make in their own stack — and it is a *separate, explicit*
change if they want one.

There is no script for this on purpose: the valuable part is the interview, and the answer to "what should this
project's rule be" is not in the repository. The repository only tells you what it currently does.

## Step 1 — read the room (facts, not decisions)

```bash
git log --oneline -40                        # shape: Conventional? sentence-style? ticket-prefixed?
git log -40 --format='%s' | awk '{print length}' | sort -n | tail -3   # what length the team actually writes
git log -40 --format='%s' | grep -oE '^[a-z][a-z-]*(\([^)]*\))?!?:' | sort | uniq -c | sort -rn
git branch -a && git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null   # which branches are real
git config --get core.hooksPath; git config --get commit.template
ls .githooks .husky .pre-commit-config.yaml lefthook.yml* .commitlintrc* .gitmessage 2>/dev/null
ls .git/hooks/commit-msg 2>/dev/null         # a local hook nobody versioned
ls CONTRIBUTING.md .github/CONTRIBUTING.md docs/ AGENTS.md 2>/dev/null
```

Report what you found in one short block before asking anything: how many of the last N subjects look
Conventional, the types and scopes actually in use, the median and max subject length, whether ticket keys sit
in the subject or a footer, which branches exist, whether anything already checks messages, which doc could hold
the policy. **Never ask the user a question the repository can answer** — but do flag where history is mixed,
because mixed history means no decision was ever made, which is exactly what this session settles.

## Step 2 — the questionnaire

Ask these seven, one at a time, with the detected default proposed so the user only has to disagree. Keep the
stakes attached to each: every one has a silent failure mode.

| # | Ask | Propose from the repo | Why it matters (the failure) |
|---|---|---|---|
| 1 | **Message shape** — keep what the history does, or change it? | the majority style in the last 40 | changing it silently converts the project; the next person's `git log` becomes two dialects. Keeping sentence style also means *no type list*, so a Conventional linter would reject every existing commit |
| 2 | **Types** — which vocabulary, and is an unknown type a rejection or a shrug? | the types in use, not the standard fourteen | a list nobody uses is decoration in the doc and a CI wall in review. If the repo has no types, say so in the doc — that is a rule too |
| 3 | **Subject budget** — 50, or 72? | median if it is tight, max minus overrun if scoped types are normal | over-budget subjects get truncated in `git log --oneline` and in forge UIs, which is where a reviewer stops reading |
| 4 | **Which branches are named branches** — the ones that must not carry `wip:`/`temp:`/`debug:`? | `origin/HEAD` if set, else the trunk-named local branch, else ask outright | a wrong list blocks nothing and *looks like it works*. Never guess this one silently — say how you detected it |
| 5 | **Ticket keys** — subject prefix, footer, or untracked here? | whatever the last 40 show | a key in the subject eats the length budget; a key only in the body is invisible to the board |
| 6 | **Body policy** — required when the *why* is non-obvious, or required always? | whether existing commits have bodies at all | "always" produces filler bodies; "when non-obvious" needs the doc to name what counts as non-obvious |
| 7 | **Enforcement** — document only, or do you want a check wired up too? | report what already exists and ask whether to extend it | a policy with no check decays within a quarter; a check with no documented escape hatch teaches people to bypass everything |

Two extra prompts worth their cost: *"what would make you break this rule?"* (that answer becomes the escape
hatch sentence) and *"who owns this document?"* (an unowned policy file is a suggestion).

## Step 3 — write the document

One document, seven sections, each stating a rule and the reason in the same breath. A rule without its reason
gets re-litigated in every review; a reason without a rule gets ignored.

```markdown
# Commit discipline          <- or a section inside CONTRIBUTING.md

## What a commit is for here   one logical change; works alone; readable in --oneline later
## Message shape               the exact subject form, mood, length budget, type/scope vocabulary,
                               and the two or three gray-zone rulings this project has hit (CSS,
                               chore vs refactor, perf) with the answer, not the debate
## Body and trailers           when a body is required, the 72-column wrap, ticket footer shape,
                               BREAKING CHANGE shape, attribution rules
## Staging hygiene             named paths / git add -p, no blind git add ., formatting commits alone,
                               tests travel with the code that needs them
## Cadence and vocabulary      commit after a logical change; the checkpoint words; which branches
                               reject them and why public history shows net-positive changes only
## History rules               never rewrite pushed history; the backup ref before any local rewrite
                               and the empty git diff proof; --force-with-lease only
## Enforcement                 which roles are filled by what (or explicitly "review only, on purpose"),
                               the escape hatch, and who owns the doc
```

Write it in the repository's own vocabulary. If the project says "trunk" not `main`, says "story key" not
issue, calls the folder `src/` something else — use their words; a policy in borrowed words reads as imported.

## Step 4 — merge, never clobber

| The doc situation | Do this |
|---|---|
| `CONTRIBUTING.md` / `docs/*` already has a commit section | quote its rules back to the user, propose the replacement text as a diff, keep everything that still holds. Do not delete a rule you merely disagree with |
| a hook, linter or forge rule already exists | that tool *is* the current policy — write down what it actually enforces (read it), then note where the document is stricter or looser, and ask which one wins |
| no doc exists | create the smallest file the team will actually open (`docs/commit-conventions.md` is usually better than a new root file), and link it from the PR template or `CONTRIBUTING.md` |
| `AGENTS.md` is where the project keeps rules for agents | put a pointer plus the agent-facing duties there (staging hygiene, no `--no-verify`, backup before rewrite) — the full policy stays in one place, not two |

**One source of truth.** If the same rule lands in three files, the next change updates one and the other two
become lies. Everything else points at the document.

## Step 5 — enforcement is roles, not products

The document describes four roles. Any stack fills them; none is required.

| Role | Who fills it (examples in brackets, never requirements) |
|---|---|
| the message is checked as it is written | a `commit-msg` check — bare `.githooks/` + `core.hooksPath`, or [lefthook], [pre-commit], [husky], [simple-git-hooks] |
| the structure is offered while typing | a commit template (`git config commit.template`) — no dependency, works in every editor |
| junk never enters a commit | a staged-diff scan for credential files, secret shapes, oversized blobs |
| the policy survives a bypass | a CI check over the commit range — **the only layer that survives `--no-verify`** |

If the user asks for one wired up, that is a *separate change they approve line by line*: the check prints
**what failed / why it matters / do: the next action**, names the escape hatch in its own header, and matches
the manager already present rather than layering a second system (`core.hooksPath` set to `.husky/` twice
means one of them silently stops running).

Every rule needs a stated way out. Enforcement with no documented exit teaches people to reach for
`--no-verify` on everything, including the checks they should have met — and an unexplained refusal is also
unarguable when the rule turns out to be wrong.

## Step 6 — verify, then hand it over

- **Verify by failing.** If a check was wired up, run the probes in a scratch repo or on an empty commit and
  report what it printed: a `wip:` subject on a named branch must fail, a conforming subject must pass, and a
  too-long subject must fail with the number in the message. A check nobody has seen refuse anything is a
  check that may not be running — unset `core.hooksPath`, missing executable bit (Windows: git runs hooks
  through its bundled `sh`, and a copy that drops the bit does nothing silently), or a GUI commit that skipped
  the CLI.
- **Show the document, then write it.** Draft the text in the conversation, get the seven answers confirmed,
  and only then touch a file. Report which path it landed at and what links to it.
- **Set the maintenance duty in the same change.** The doc carries `Last reviewed: <date>` and one sentence:
  a decision about commits — a new named branch, a new type, a different budget — is recorded *in this file, in
  the same change* that makes it. Without that line the document is a snapshot of today's agreement.

## What init does not do

- **Install anything.** No hooks, no git config, no CI file, no `.githooks/` directory, nothing to uninstall.
- **Rewrite history.** The discipline governs what happens from now on; existing commits stay as they are.
- **Convert the project.** It writes the convention the maintainers chose. Moving a sentence-style repo to
  Conventional Commits is a project decision made *before* init, by whoever owns the history.
- **Replace Mode 1.** A document says what good looks like; the guide is still what makes this particular
  commit good — including whether it should have been three commits, which no message check can tell you.
