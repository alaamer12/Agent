# Anatomy of a good commit

## What a commit is actually for

Four readers consume your message, and none of them is you-right-now:

| Reader | What it needs | What breaks it |
|---|---|---|
| A reviewer, `git log --oneline` branch-wide | one line per change that says what changed | subjects describing files ("update handler.py"), 95-character lines that wrap into mush |
| Whoever runs `git bisect` in an outage | a commit that is one coherent change, so "this commit broke it" is actionable | blobs mixing a fix with a rename; commits that don't build |
| Whoever runs `git blame` on a strange line | *why* the constraint exists, and what the alternative was | bodies that restate the diff ("changed if to switch") |
| A changelog generator or release tool | typed/structured metadata, or nothing at all | half-followed conventions, `BREAKING CHANGE` written in prose |

A commit is also **the smallest unit the project can ship, revert, or credit**. Design the boundary
accordingly ([`03`](03-atomicity-and-staging.md)).

## The parts of a message

```text
1  subject        one line; the whole change summarized; what git log and merge output display
2  blank line     mandatory separator - without it, tools read your body as the subject
3  body           what and why, in prose, wrapped at 72; context a diff cannot carry
4  blank line
5  trailers       structured key: value lines a human or a bot parses (issue links, co-authors,
                 sign-offs, review credit, BREAKING CHANGE)
```

`git` itself treats the first line as the summary and everything after the first blank line as the
description; that is the whole reason the blank line is not cosmetic. `git log --oneline`, `git revert`'s
default subject, `git format-patch`'s cover text, GitHub's commit list, and most release tooling all read
those positions.

## Why imperative mood, specifically

Not style snobbery. It is the mood that composes with git's own generated messages:

```text
git merge x   ->  "Merge branch 'x'"        (imperative: Merge)
git revert x  ->  "Revert "Add retry""      (imperative: Revert)
you           ->  "Add retry to the client"  (imperative: Add)
```

They read as one consistent voice in `git log`. Past tense does not: "Added retry", "Merge branch 'x'",
"Revert …" is the sound of a log written by four authors. The trick that resolves the doubt every time: the
subject must complete the sentence **"If applied, this commit will ___"**. *will prevent duplicate webhooks*
✓; *will prevented* / *will preventing* ✗.

## Why the length budgets exist

- **50 characters** on the subject is a classic budget (it is what `git log --oneline` shows comfortably on
  an 80-column terminal, and it matches the `git shortlog`/`format-patch` subjects that get quoted in mail).
  Treat it as a target, not a wall.
- **72 characters** for the body is about readability in a wrapped 80-column view with indentation, and
  survives quoting in email and terminal panes.
- Modern caveat, and it is a real one: GitHub's UI and web-based tools display far more than 50, so teams
  with scoped types (`feat(auth):` eats 11) commonly allow 60-72 on the subject. Pick one number, note it in
  the repo's contributing guide or lint config, and do not mix. Length is a signal of compression: if you
  need 90 characters, you have two facts and one of them belongs in the body.

## The one thing that separates professional from amateur messages

Amateurs describe the **activity** ("update", "fix", "wip", "cleanup"). Professionals describe the
**result in the tree** ("reject tokens after expiry instead of caching them", "reduce p99 by dropping the
synchronous metadata fetch"). One tells a reader what was done; the other tells a reader what is now true.

Then the body adds the only thing the code cannot show: the reason this result was worth obtaining, the
alternative that was rejected, and the risk that was accepted ([`02`](02-body-what-why-not-how.md)).

## Truthfulness, the rule underneath all the others

Every claim in the message must be verifiable from the commit or from what you actually did. No "all tests
pass" unless you ran them and can name them; no "fixes the race" unless you identified the race; no
"refactor, no behavior change" unless you can defend that reading. A wrong message is worse than an empty
one — it sends the next reader toward a conclusion you did not earn. If you are unsure, write what you
observed instead of what you concluded.
