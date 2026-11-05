# The preference line - shape, boundaries, examples

Options in [brackets] are illustrative, not a closed menu.

## The shape

```text
[where it applies]: [required behavior]; [avoided/forbidden] - [exception boundary]
```

A line is done when an agent can act on it WITHOUT asking, and the first legitimate exception
does not break it. Test both halves: does it kill the question? does it survive the exception?

## Worked good vs bad

| User statement | Bad line | Good line |
|---|---|---|
| "I like bun and bunx" | `user likes bun` (transcript) / `prefer modern JS tooling` (answers nothing) | `JS work: bun/bunx; never npm/npx - unless the repo's config names another manager or the user orders otherwise in the session` |
| "PowerShell annoys me" | `avoid PowerShell` (avoid-whom? when?) | `Shell: use [cmd] on Windows; PowerShell hangs on long commands here - if the project dictates another shell, the project wins explicitly` |
| "Don't run typecheck every time" | `testing is optional` (destroys a duty) | `Do not run typecheck/build by default; the user runs them at session end or asks for them explicitly` |
| "Answer me shortly" | `be concise` (vague; unfalsifiable) | `Answers: the result first, one line what changed; details only when asked - unless the task's own skill requires a report shape` |
| "I always commit with the /commit skill" | `use skills` (noise) | `Before any commit: invoke the commit skill (guide mode); skip only when the user says "just commit"` |
| "no global pip installs" | `careful with pip` | `Python deps go in the project's .venv; never the global interpreter - unless the project has no Python env and the user approves creating one` |

The bad column fails in one of four ways: reported speech, vagueness, a missing boundary, or
scope creep (a rule wider than the statement that produced it).

## Exception-boundary patterns

Pick the boundary the preference actually needs; "unless told otherwise" alone is not a boundary:

- **repo-evidence escape** - `[the lockfile / manifest / project AGENTS.md names another answer]`
- **current-order escape** - `[the user orders it differently in the session]` (this one is
  implicit in the ladder below, worth naming on cage-prone rules)
- **explicit-project-override escape** - `[a project that states this rule differently in its own
  AGENTS.md wins for that project - overrides must be visible, not silent]`

## The precedence ladder (what every line lives under)

```text
1. the user's current prompt            (wins for this task, silently)
2. the project's AGENTS.md              (respects the global by default; may override a
                                         preference ONLY explicitly, with its reason stated)
3. this global preference file          (the standing default)
```

Global lines are load-bearing everywhere EXCEPT where a project has overtly said otherwise. The
project file respecting the global means: a project that wants different behavior writes the
override into its own AGENTS.md ("project rule narrows global: [X here, because Y]"); an agent
that quietly lets a project rule contradict the global - with nothing written - is the silent-drift
failure, and `/personalize` audits exactly that when promoting (below).

## Promotion mode - "section X of the current AGENTS.md into global"

A project section can hold one person's settled preference wearing project clothes. Promotion reads
the named section and sorts EVERY line:

- **personal default** (holds in other projects too: tooling, answer style, commit habits) →
  distilled into a global line; the project line may then retire (copy unless told "move").
- **project decision** (branch model, docs root, this-repo's secret strategy) → stays; promotion
  says so line by line - it does not leave the project file thinking global absorbed everything.
- **machine-specific** (paths, hardware, local tools) → routes to `AGENTS.local.md`, not global.
- **contradicts an existing global line** → stop and ask which one the user actually lives by;
  promotion never silently wins a fight between two files.
