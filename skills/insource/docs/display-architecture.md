# manager.py — Display Architecture

Status: implemented in `manager.py` 2.0.0.
Scope: the terminal output layer only. Command behavior, fingerprints and the
hard-copy manifest are specified in `manager-migration.md`.

## 1. Goals

The manager prints four kinds of things: the command being run, what happened
per skill, an urgent sync warning, and a lint verdict. The display layer exists
so those four never compete for attention and never depend on one terminal
library.

- **One semantic event, one function.** Commands do not format strings; they
  call `display_table`, `display_banner`, `display_counts`, and friends.
- **Rich when present, plain when not.** `rich` is optional. Without it, every
  screen still renders with ASCII borders and no colour.
- **Warnings survive `--quiet`.** Quiet removes progress and result tables; it
  never hides a warning or an error.
- **Colour is decoration, not information.** Every coloured message also has a
  text prefix or a title, so a monochrome terminal loses nothing.
- **Deterministic in ASCII.** `--no-color` selects the ASCII backend, which
  makes output stable for tests, CI logs and diffs.

## 2. Layers

```
command code (cmd_skill / cmd_refresh / cmd_agent / cmd_lint)
        │  semantic events: rows, pairs, banners, counts
        ▼
display API (display_table, display_banner, display_kv,
             display_command_report, display_counts,
             display_info / ok / warn / error, display_sync_banner)
        │  one backend decision per call
        ▼
backend selector  ── rich available and colour enabled ──▶ rich Console
        │
        └──────── otherwise ─────────────────────────────▶ ASCII emitter
```

The command layer owns **what** is said. The display API owns **how** it is
laid out. The backend owns **which characters** reach the terminal.

## 3. Backend selection

`_rich_on()` returns true only when both conditions hold:

| Condition | Source | Effect |
|---|---|---|
| `rich` imported successfully | module import guard | otherwise ASCII |
| colour enabled | no `-C/--no-color`, no `NO_COLOR` env var | otherwise ASCII |

`--no-color` therefore means "plain output", not merely "no ANSI escapes". This
is deliberate: a single switch gives a stable, greppable format. `rich` itself
still drops ANSI when stdout is not a TTY; the manager does not try to detect a
TTY separately.

## 4. Primitives

| Function | Purpose | Quiet behaviour |
|---|---|---|
| `display_table(headers, rows, title=, always=)` | tabular results | suppressed unless `always=True` |
| `display_banner(title, lines, level=)` | attention box (warning/error/info/success) | never suppressed |
| `display_kv(pairs, title=, always=)` | two-column setting summaries | suppressed unless `always=True` |
| `display_command_report(command, settings=, flags=, implicit=)` | command and flag echo before work | suppressed |
| `display_counts(counts)` | result histogram after a deploy/refresh | suppressed |
| `display_info(msg)` | neutral progress line | suppressed |
| `display_ok(msg)` | success line with `[ok]` prefix | suppressed |
| `display_warn(msg)` | warning line with `[warn]` prefix on stderr | never suppressed |
| `display_error(msg)` | error line with `[error]` prefix on stderr | never suppressed |
| `display_sync_banner(issues)` | sync summary built from `SyncIssue` rows | never suppressed |

`always=True` is used by `lint` and `--list`: their output *is* the result, so
it must survive `--quiet`.

## 5. Data contract

- A table is `headers: Sequence[Any]` plus `rows: Sequence[Sequence[Any]]`.
  Every cell is converted with `str()` and newlines are flattened to spaces, so
  a path or an exception message cannot break the grid.
- Every row must have the same number of cells as the header. The ASCII
  renderer computes widths per column and pads with spaces; the rich renderer
  folds long cells instead of clipping them.
- Empty `rows` renders nothing. A caller that wants an explicit "none" row must
  add it.
- Cells must not contain ANSI escapes or pre-built table borders. Colour is the
  backend's job.
- `title` is plain text. Rich renders it as the table/panel title; ASCII prints
  it on the line above the grid.

## 6. Colour and levels

| Level | Rich border/title | ASCII equivalent |
|---|---|---|
| `warning` | yellow panel | `sync check` title above the box |
| `error` | red panel | `[error]` prefix |
| `info` | cyan panel | plain text |
| `success` | green panel | `[ok]` prefix |

A banner carries its own title, so the meaning survives without colour. The
same rule applies to `[ok]`, `[warn]` and `[error]` prefixes.

## 7. Command and flag reporting

Every command starts with one report unless `--quiet`:

```
manager skill
  Setting      Value
  Registry     F:\Projects\Agent\skills\insource
  Destination  global agents (all)
  Mode         symlink
  Skills       avatar, mine
  Flags        -c/--hard-copy, -i/--into, -d/--dry-run
```

- Settings are the facts that change the outcome: registry, destination, mode,
  skill selection, description limit.
- **Flags always show both forms** (`-c/--hard-copy`), and only flags that are
  active or non-default appear. `-v/--verbose` widens other reports; it does not
  add noise here.
- The default command is marked in the title (`manager skill (default command)`)
  so a user who typed only `manager.py avatar` knows how it was interpreted.
- `--quiet` removes this report entirely; warnings and errors still print.

## 8. Synchronization banner

`audit_all()` produces `SyncIssue(kind, skill, target, state, detail)` rows.
`display_sync_banner()` turns them into one banner before the command runs:

```
sync check
  15 entries need attention: 15 broken-link
  - scss [broken-link] C:\Users\...\skills\scss
  - ...
  - ... and 9 more; run `python manager.py lint` for the full report
```

- The banner is capped at six rows unless `-v/--verbose` is set, so a large
  drift does not bury the command output.
- The banner is shown for `skill`, `agent` and `lint`. For `lint` the detailed
  table follows; the banner is the short version of the same truth.
- States are stable identifiers (`broken-link`, `missing-target`,
  `source-changed`, `target-modified`, `both-changed`, `missing-locked`, ...),
  intended to be greppable and to map to an action in the detail text.

## 9. Lint report layout

Order matters: a reader should learn whether the run is healthy before reading
the inventory.

1. Command report (registry, extra roots, limit, flags).
2. Sync banner, if any.
3. Description warnings table (`Skill, Location, Chars, Limit, Over by, Issue`).
4. Synchronization issues table (`Skill, State, Target, Detail`).
5. Summary key/value block (roots, files checked, hard copies, warnings, issues,
   limit).
6. A single `[ok]` line when both counts are zero.

`-v/--verbose` inserts an "all checked skills" table before the summary, with
each skill's length, state and path.

## 10. Width and wrapping

- Rich uses the terminal width, folds long cells and wraps the path in the
  registry row. This can break a path mid-token; the value remains intact.
- ASCII does not wrap or truncate. Very long detail cells make wide tables; the
  terminal wraps them, which is acceptable for a local tool and keeps the output
  copy-pasteable.
- The ASCII width calculation uses `len()`, so wide CJK glyphs can misalign the
  border by a column. Skill names are ASCII in practice; the rich backend
  handles wide glyphs correctly.

## 11. Accessibility

- Meaning is always present as text (title or prefix), never colour alone.
- `--no-color` and `NO_COLOR` produce border-only output with no escape codes,
  which is also what screen readers and log collectors prefer.
- Rows are line-oriented; a table can be read as a list of records when the
  borders are stripped.
- Warnings go to stderr; results go to stdout, so a caller can separate them.

## 12. Testing

- Golden-output tests run with `--no-color`; the ASCII renderer is deterministic
  across platforms.
- Rich is smoke-tested separately (exit code plus a known title), because its
  layout depends on terminal width.
- Tests never assert on ANSI sequences or box glyphs. They assert on titles,
  prefixes, state identifiers and summary labels.
- `MANAGER_HOME` redirects every agent path, so display tests never touch the
  real home directory.

## 13. Extending the layer

To add a new report:

1. Add a `display_*` function only if the new screen is structurally different;
   otherwise reuse `display_table` with new headers.
2. Keep the data as rows/pairs. Do not build a formatted string in the command.
3. Decide its quiet behaviour explicitly: result screens pass `always=True`,
   progress screens do not.
4. If it reports a problem, give it a `[prefix]` or a titled banner so it
   survives the ASCII backend.

To add a backend:

1. Implement the same primitives behind `_rich_on()`.
2. Keep the data contract in section 5 unchanged.
3. Make the selector a pure function of capability and configuration; never let
   a command branch on `rich`.

## 14. Failure modes

| Failure | Behaviour |
|---|---|
| `rich` not installed | import guard sets `RICH_AVAILABLE = False`; ASCII is used |
| `rich` raises during import | same guard (broad `except`) |
| `NO_COLOR` set | ASCII backend, regardless of `rich` |
| stdout is not a TTY | rich still lays out; it drops ANSI on its own |
| terminal encoding cannot render a glyph | `sys.stdout`/`stderr` are reconfigured to UTF-8 with `errors="replace"` in `main()` |
| broken pipe on a closed pager | Python's default `BrokenPipeError` handling applies; no partial table is buffered by the manager |
