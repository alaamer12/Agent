# The subject line

The subject is the only part guaranteed to be read. It has one job: let a scanner predict what the commit
does, well enough to decide whether to open it.

## Rules, with the reason

| Rule | Reason |
|---|---|
| Imperative mood ("add", "fix", "prevent") | composes with git's own "Merge…", "Revert…" messages; completes "If applied, this commit will ___" |
| State the result, not the activity | "update handler" describes you; "stop retrying on 4xx responses" describes the tree |
| No trailing period | it is a summary line, not a sentence; the period wastes a character and looks wrong in generated lists |
| Cap the length (target 50, hard ceiling ~72; pick one and enforce it) | survives `--oneline`, `shortlog`, terminal panes, patch subjects |
| Capitalize consistently with the repo | consistency is the actual rule; `feat:` conventions want lowercase, sentence style wants uppercase |
| No issue numbers in place of words ("fix #123") | the reader of `git log` has no ticket context; put the reference in a trailer |
| No file lists, no "and" | "and" means two commits ([`03`](03-atomicity-and-staging.md)) |
| No `WIP`, `update`, `fix bug`, `changes`, `initial commit`, `stuff` | these are non-information; a stranger learns nothing |

## Shape options, in order of preference

Use whichever the repository already uses ([`04`](04-conventions-and-when-to-drop-them.md)).

```text
Conventional      fix(orders)!: reject expired tokens instead of caching them
Sentence style    Reject expired tokens instead of caching them
Ticket prefixed   APP-4821 reject expired tokens instead of caching them
Subsystem style   orders: reject expired tokens instead of caching them
```

All four are fine. All four, in the same repository, are a mess.

## Scope: what makes a good one

A scope is a **noun for the area affected** - module, subsystem, or file-without-extension. It answers "where"
before the reader opens the diff.

- Good: `(auth)`, `(orders)`, `(ci)`, `(api-client)`, `(db)`.
- Poor: `(code)`, `(all)`, `(misc)`, `(src)`, a scope that repeats the type `(fix)`.
- Omit it when the change genuinely spans the project, or when the repo's history has no scopes.
- One scope per commit. Needing two is a hint that the commit should be two.

## Bad → good, the useful part

| Bad | Why it fails | Good |
|---|---|---|
| `fixed bug` | which bug, in what | `fix(orders): stop double-charging retried payment webhooks` |
| `update README.md` | names the file, not the change | `docs: document the two-step local env setup` |
| `Adding tests` | progressive mood, no target | `test(cart): cover coupon expiry edge cases` |
| `refactor` | no information at all | `refactor(pricing): extract tax rounding into a pure function` |
| `Fix issue with user authentication when a token has expired and causes a crash in production` | 96 chars; two facts; body material | `fix(auth): stop crashing on expired tokens` + body |
| `feat: implement stuff for APP-1234` | ticket as substitute for meaning | `feat(search): add prefix suggestions to the search bar` |
| `1. bumped deps 2. fixed lint 3. updated tests` | a checklist, not a summary | three commits |
| `Merged branch main into feature` (hand-written) | git generates this better | let the merge tooling write it |
| `perf: optimizations` | what got faster, how much | `perf(list): avoid re-rendering rows on filter keystroke` |
| `chore: bump` | from what to what | `chore(deps): upgrade http client 2.4 -> 2.7` |

## Verbs worth having ready

`add`, `fix`, `prevent`, `reject`, `allow`, `remove`, `rename`, `extract`, `inline`, `cache`, `batch`,
`retry`, `skip`, `enforce`, `relax`, `guard`, `bump`, `drop`, `deprecate`, `restore`, `harden`, `split`,
`merge`, `document`, `cover`, `stub`, `seed`.

Pick the one that describes the effect. **Avoid**: `update`, `improve`, `change`, `modify`, `make`, `various`,
`misc`, `cleanup` — each of those outsources the real description to the diff. If `improve` is genuinely the
change, say *improved what, measured how*.

## Numbers help

If a change has a magnitude, put it in the body, not the subject - but a subject that can carry one honestly
is stronger:

```text
perf(search): halve cold-start index build (48s -> 21s)
fix(rate-limit): stop retry storms by honoring Retry-After
```

One caveat: only quote numbers you measured. A made-up "halves latency" in a log line becomes an assumption
someone else builds on.
