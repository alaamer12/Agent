# Conventions - detect the incumbent, and know when a format hurts

The professional move is to match the repository. An imported format nobody else uses produces a history with
two dialects, which is worse than either dialect alone.

## Detect, in this order

```bash
git log --oneline -20                                  # the style that is actually enforced
git log -5 --format='--- %h ---%n%B'                   # body structure, blank lines, trailers
git log --format='%s' | grep -cE '^[a-z]+(\(.+\))?!?:' # how much of history is Conventional
ls .githooks/ .husky/ .pre-commit-config.yaml .commitlintrc* commitlint.config.* .czrc 2>/dev/null
grep -rilE "commit message|conventional commit" CONTRIBUTING* README* docs/ .github/ 2>/dev/null | head
```

The history is the real authority: a config that says `feat|fix|chore` while every commit says `Fix …` means
nobody enforces it, and matching the config gets you the outlier commit.

## Conventional Commits, in the form teams actually use

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

- Types are chosen by the project, not by the spec - Angular's set is the common default:
  `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- `!` before the colon, or a `BREAKING CHANGE: <explanation>` footer, marks an incompatible contract change.
- `fix:`/`feat:` drive semantic versioning in release tooling; other types are usually excluded from
  changelogs.
- The description follows the subject rules in [`01`](01-subject-line.md): imperative, no period, capped
  length. The type prefix does not license a vague summary.

```text
feat(search)!: add prefix suggestions to the search bar

BREAKING CHANGE: /api/search now returns { items, suggestions } instead of a bare
array. Consumers must read .items; a temporary ?compat=1 flag returns the old
shape until 2026-01-15.

Closes #4821
```

## Why teams adopt it, honestly

Real benefits: changelog and release automation, a shared vocabulary for "does this ship a version bump",
lintable history, and a mild guard against "update stuff".

Real costs, which is where the 2025-2026 criticism lands - and the criticism is worth taking seriously
rather than dismissing:

| Criticism | Fair? | What to do about it |
|---|---|---|
| Type-first ordering buries the useful information; scope is optional while area is what readers want | yes | put the meaningful noun in the description; consider subsystem-first style (`orders: reject expired tokens`) when scope discipline is weak |
| The type is often a guess, and a wrong `feat`/`fix` produces a wrong version bump | yes | if you use release automation, the type is a *release decision* - state it and let the owner confirm |
| It encourages one commit per type-label rather than per change, splitting logical work | yes | atomicity comes first ([`03`](03-atomicity-and-staging.md)); a label never justifies a bad boundary |
| `chore` becomes a landfill for anything uncategorizable | yes | define the project's `chore` meaning, or prefer a real type; a `chore:` subject still has to describe the change |
| Boilerplate noise on tiny or personal projects | yes | skip it: a two-person tool with no generated changelog does not need it |
| Machine-parsed metadata is the only way to get release notes | no | release notes can also come from the PR/issue side; some teams write user-facing changelogs by hand and keep commit messages for maintainers |

**The decision rule:** adopt it where it buys automation (public libraries, versioned services, multi-contributor
repos with release tooling) and where the team will actually lint it. In a monorepo of internal tools with no
generated changelog, plain descriptive subjects plus a `Closes:` trailer are perfectly professional. Never
argue for it on taste alone, and never force it on a repository that has chosen otherwise.

## Other vocabularies worth recognizing

```text
Sentence style        Reject expired tokens instead of caching them
                      (Linux kernel, many language runtimes; bodies are long and technical)
Subsystem prefix      net: fix checksum offload on vlan interfaces
                      (kernel, git itself, many C projects)
Ticket first          APP-4821 reject expired tokens
                      (Jira-driven teams; keep the key out of the summary text if the tooling links it)
Component + mood      [checkout] prevent double submit
Issue-only            #4821 (not a convention; a failure of one)
```

Sentence style has no type prefix, so length budgets are tighter and the body carries the classification. Its
bodies are often better - the format does not write the message for you.

## Changing a project's convention

That is a project decision, not a commit-level one, and it needs buy-in and enforcement in the same change
(a hook or CI lint) or the history ends up bilingual. If the user asks you to "start using conventional
commits", produce: the type list scoped to what the project needs, the lint config, the commit template, and a
note that old commits stay as they are.
