# Searching in and around diffs

When the question is "where did this come from / when did it disappear / which commit introduced it", you are no
longer reading a diff — you are searching history that happens to contain diffs.

## Pickaxe: `-S` versus `-G`

| Flag | Matches | Answers | Does not find |
|---|---|---|---|
| `git log -S'<string>'` | commits where the **number of occurrences** of the string changed | "when was this added or removed" | a commit that changed the surrounding line but kept the count |
| `git log -G'<regex>'` | commits where an added or removed line **matches the regex** | "when did any line mentioning this change" | a pure move where the line is both removed and re-added identically |
| `git log --pickaxe-regex -S'<regex>'` | occurrences of a regex whose count changed | broad pattern hunts | nuanced matches |

```bash
git log -S'RETRY_LIMIT' --oneline -p -- src/            # when the constant appeared/changed count
git log -G'^\s*return\s+None' --oneline -- src/         # commits touching lines that return None
git log -S'feature_x' --all --oneline                    # include every branch
git log -S'x' -p --follow -- path/one_file.ts            # one file across renames
```

The classic failure: searching `-S` for a string that was *edited in place* — the count never changed, so nothing
is found. If `-S` is empty, retry with `-G`, then with `git log -p | grep`.

## The topic dossier — "give me everything about one word, cheaply"

The question "extract every reference to **Sentry** (or any topic) in code *and* commit messages" is not one
search — it is **four channels**, and the naive answer (dump every patch: `git log -S topic -p`) is the most
expensive thing you can do. One deterministic command runs the whole ladder:

```bash
python scripts/diff_survey.py --topic Sentry            # + --cwd <repo> --rev <snap> --budget KB --max-rows N
```

The four channels, in the order that keeps the bill small:

```bash
git log --grep='Sentry' -i -F --format='%h %ad %s' --date=short   # MESSAGE level - the channel -S/-G never see
git grep -Ic -F -i 'Sentry' HEAD                                  # CODE now: per-file counts (cheap map first)
git log -S'Sentry' --format='%h %s'                               # CODE history: occurrences added/removed
git log -G'Sentry' -i --format=%h | wc -l                         # touched-mentioning-lines count (refactors/moves)
```

Then, and only then, spend content: `git show <sha> -- <one file>` or `--at <rev> --path <file> --grep` for the
two or three items the map says matter.

Measured on a mid-size mobile-app repo (a few hundred commits, hundreds of files): `git log -S Sentry -p` ran to
**~50 k tokens**; the full dossier (a message hit, a per-file mention map, pickaxe history, follow-ups) fit in
**~600 tokens** — roughly 80× cheaper, and it *contains more*, because the naive dump had no message-level
channel and no code-at-HEAD at all.

Dossier rules that generalize:

- **`--grep` is its own channel.** Commit messages mention topics that code never does (decisions, incidents,
  reversions); `-S`/`-G` scan *diffs*, never messages. A "Sentry history" answer without the message channel is
  missing the merge that explains the whole thing.
- **`-G` > `-S` is information, not noise**: commits that touched lines mentioning the topic while keeping its
  occurrence count — refactors, renames, file moves. Report both numbers.
- **Counts before lines, lines before patches.** `-Ic` (per-file count) is ~600 bytes for a whole repo; the same
  repo's `-n` lines are ~4 KB; `-p` patches are the 173 KB. Always ask the cheaper question first.
- **Case-insensitive by default** (`-i`): a topic is `Sentry` in code, `sentry` in prose, `SENTRY` in config
  keys. Exact case is what `--at --grep` is for.
- **Truncate subjects** (`clip`): squash histories put whole changelogs in one subject line; 120 chars is an
  honest budget, full message via `git show --format=%B <sha>` when chosen.

## A function's history, not a file's

```bash
git log -L :compute_totals:src/billing.py -p        # history of one function (by name)
git log -L 40,80:src/billing.py -p                  # a line range, following its movement
git log -L :/def compute_totals/:src/billing.py -p  # by regex when the name repeats
```

`-L` follows the region as it moves; it prints one diff per commit, which is usually the fastest way to answer
"why is this function like this". It needs the function boundary to be detectable (diff driver / language
support); otherwise fall back to `git blame -L` plus `-S`.

## Searching a snapshot rather than the worktree

```bash
git grep -n '<pattern>' <rev> -- 'src/**'      # content search at a commit/branch/tag
git grep -n -e 'a' -e 'b' <rev>                # OR
git grep -n --and -e 'a' -e 'b' <rev>          # AND
git grep -n -E 'foo|bar' <rev> -- '*.sql'
```

`git grep <rev>` is the answer to "is the removed symbol still referenced in the *new* tree" — a question a diff
cannot answer by itself, because the referencing file may not have changed.

## Searching inside one diff's text

```bash
git diff <range> | grep -n '^+.*TODO'
git diff <range> -- '*.py' | grep -n '^-[^-]'            # removed lines only
git diff -U0 <range> | grep -c '^+[^+]'                  # how many lines were added, cheaply
git diff --word-diff=porcelain <range> | grep '^[-+]'    # token-level changes
```

For a huge stream, `grep -n` with line numbers keeps you oriented; `--no-color` guarantees the `^[+-]` anchors
work (a colour escape before `+` silently breaks the match).

## Comparing two versions of the same work

```bash
git range-diff origin/main...old-head origin/main...new-head
```

`range-diff` pairs commits between two series and shows only what changed between versions — the tool for
force-pushed branches and rebased PRs. Symbols: `=` unchanged, `!` modified, `+` added, `-` dropped, `>`,`<`
reordered. Without it, an interdiff of the two patches (`git diff old..new`) mixes the rebase with the edits.

## Comparing things that are not commits

```bash
git diff --no-index old/ new/            # two directories, no repo required
git diff --no-index --stat a.json b.json
```

Useful for "the generator output before/after", vendor drops, or comparing a downloaded release with the tree.

## Making a misleading diff readable

| Symptom | Cause | Command |
|---|---|---|
| "whole file changed" during a move | Myers aligning badly | `--diff-algorithm=histogram` (or `patience`) |
| hunks split in illogical places | default heuristic | `--anchored='^\s*(def|function|class|func)\s'` to anchor on declarations |
| important file buried in noise | huge diff | `-O orderfile` (paths in your order) |
| rename limit exceeded ("too many files") | default rename limit | `-l0` (no limit) or raise `diff.renameLimit`, then `-M` |
| only some files matter | — | `--diff-filter=AM` (added/modified), `--diff-filter=D` (deleted only) |
| a file is shown as binary | NUL byte or misdetection | `--text` to read, then fix the cause |

## Parsing diffs in a script

- Use `-z` with `--name-status` if paths can contain newlines; otherwise split on tabs, never on spaces.
- `--numstat` columns are `added<TAB>removed<TAB>path`; binary shows `-\t-`.
- `--no-color`, `--no-ext-diff`, `--no-textconv` for deterministic text; `--src-prefix=a/ --dst-prefix=b/` to be
  sure of the prefixes.
- Capture **bytes** and decode at the end: a diff of a CRLF or non-UTF-8 file is silently rewritten by a text-mode
  pipe. `scripts/diff_survey.py` reads bytes for exactly this reason.
- `core.quotepath=false` (or `-c core.quotepath=false`) for non-ASCII paths.

## Search strategy in one paragraph

Start narrow: the symbol or string you know, with `-S`. Empty result → `-G`, then `--all`, then a path-scoped
`git log -p | grep`. Found the commit → `git show <sha>` for the hunk, `-L` for the function's whole history, and
`git grep <new-rev>` to check what still references it. For a series, `range-diff` before reading commits one by
one. Never grep the worktree when the question is about history — the file has already moved on.
