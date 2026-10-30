# Case 6 - "commit this" when you did not write it

**Situation:** a fresh session. The user says: *"commit this"*. The tree has twelve modified files from work
this agent has not seen. This is where a professional commit turns into a fabrication, because the tempting
shortcut is to write the message from `git diff --stat`.

## The order of work

```bash
git status --short                      # what exists, including untracked
git diff --stat                         # unstaged shape
git log --oneline -10                   # the repo's actual message style
git branch --show-current
```

Then **read the diff**, by area rather than by line count:

```bash
git diff src/import/parser.ts | head -120
git diff --stat test/         # does this look like tests were written to prove it?
git diff src/import/parser.ts src/import/queue.ts    # pairs that suggest one concern
```

Twelve files is not "read all of it or none of it" - read the parts that decide the sentence. Filenames tell
you *where*; only the diff tells you *what is now true*.

## What the read produced, and what it did not

From the diff: the CSV importer now rejects rows whose date column is unparseable instead of coercing them to
epoch, and there is a new `src/import/fallback.ts` that adds nothing to that story.

Unknown, and therefore not claimable:

- whether the change is finished (the TODO in `queue.ts:88` says "handle quoted newlines" - is that part of
  it?)
- whether anything was run (`test/import/csv.spec.ts` was modified; nothing here proves it passed)
- what `fallback.ts` is for (it is imported by nothing in this diff)

## The correct message for what is known

```text
fix(import): reject CSV rows with an unparseable date instead of coercing to epoch

A malformed date became 1970-01-01, so bad rows imported silently and the
damage showed up months later in the aging report. The parser now raises a
field-level error and the row goes to the rejects file.

The rejects-file path already existed for the amount column; this reuses it.
```

and then the report to the user, which is the part that makes this professional rather than guessy:

```text
COMMITTED : 1 commit, 41f2c9a - the parser change and its error path
NOT STAGED: src/import/fallback.ts   - imported by nothing in the diff; unclear what it is for
UNANSWERED: queue.ts:88 TODO "handle quoted newlines" - in scope for this change or not?
NOT RUN   : the modified csv.spec.ts - I did not execute it; say the word and I will
SUGGESTED : separate commit once you tell me what fallback.ts is for
```

## What was refused, and why

| Temptation | Why it is wrong |
|---|---|
| `fix(import): handle date parsing and add fallback logic` | "and" plus a component you cannot explain; it asserts the two belong together |
| `test(import): cover malformed dates` as a second commit | the test file exists, but the change was not made to be tested separately - and the tests were never run; splitting them off also breaks the tests-with-code rule ([`03`](../references/03-atomicity-and-staging.md)) |
| `fix(import): resolve date handling issue` | activity language, zero information |
| Adding `BREAKING CHANGE:` because coercion changed | plausible and unverified; a false version bump is worse than no footer |
| Staging all twelve files to be helpful | `fallback.ts` and the queue TODO are not understood, and a commit is a claim about them |
| Committing the modified spec file silently inside the fix | hides that the tests were never run, and muddles two concerns |

## The rule underneath

A commit message is a claim about code. If you have not read enough to back the claim, the professional output
is a smaller commit plus an explicit list of what you did not understand - never a confident summary of a
filename list.
