# Hunks and splitting — two unrelated changes lived in one file

The file is not the unit of a commit. The **hunk** is, and `git add -p` is the tool that makes one file yield
two honest commits.

## Vocabulary first (p.22–24)

- **diff** — the whole set of changes between versions. The movie.
- **hunk** — one contiguous block of changed lines inside that diff. A scene. You stage one scene at a time.
  One file edited in two places = one diff, two hunks.

Etymology, because it helps people remember: `diff` is the 1970s Unix command for *difference*; *hunk* is
Git's own word for a chunk — Git's source has `apply_hunk()` and `parse_hunk()`.

## The keys inside `git add -p` (p.20)

| Key | Meaning | Daily driver |
|---|---|---|
| `y` | stage this hunk | ✓ |
| `n` | skip this hunk | ✓ |
| `q` | quit; stop reviewing the rest | ✓ |
| `a` | stage this hunk **and all remaining** | |
| `d` | skip this hunk **and all remaining** | |
| `s` | **split** this hunk into smaller ones | ✓ (the one people forget) |
| `e` | **edit** the hunk line by line — delete what you do not want staged | ✓ |
| `?` | help | |

`s` handles two changes that happen to be adjacent; `e` handles a single hunk that mixes them at line level.
`git add -e <file>` edits the whole patch directly.

## The worked case (p.14, p.16–19)

You added `generate_report_summary()` **and** fixed a docstring on the old `plot_graph()`, in one file,
uncommitted:

```bash
git status
git add -p report.py
# hunk 1 (docstring): Stage this hunk [y,n,q,a,d,s,e,?]?  -> n
# hunk 2 (new fn):                                       -> y
git commit -m "feat(report): add generate_report_summary function"

git add -p report.py      # now only the docstring hunk remains  -> y
git commit -m "docs(report): add docstring to plot_graph"

git log --oneline         # two clean commits from one file
```

## Already committed them together? (p.15, p.19)

```bash
git reset HEAD~      # undo the commit, KEEP the changes in the working tree
# then redo the git add -p split above
```

Rewriting history **before pushing** is always safe (p.15) — with one exception, and it is not this one:
see the backup rule in [`14`](14-repairing-history.md). `git reset -p` unstages by hunk when the staging itself
went wrong.

## The no-patch-mode fallback (p.14–15)

When interactive staging is unavailable (some shells, some harnesses, some terminals):

```bash
cp file.py file_backup.py
git restore file.py            # back to committed state
# paste ONLY change 1 from the backup -> git add file.py -> commit
# paste change 2                 -> git add file.py -> commit
rm file_backup.py
```

Crude, but it produces the same history. The backup file is scratch: delete it when finished, and never
commit it.

## What patch files are actually good for (p.41)

`git diff > my.patch` looks like a lightweight way to park work. It is the weakest option:

- untracked, so one cleanup pass deletes it forever;
- invisible in history — no `git log`, no blame, no restore;
- conflict-prone when re-applied after the branch moved.

Use them for emergencies and offline transfer only. If a project genuinely keeps patches around, they belong
in a **tracked** folder with a README beside them, applied with `git apply` — and the contradiction in the
source material (a folder told to be both tracked and gitignored, p.43) is exactly why you decide this per
project instead of copying advice.

## When splitting is not worth it

Three hunks that are one refactor with mechanical repetition across a file: one commit. Splitting is a means
to a reviewable, revertable, bisectable history — not a virtue in itself. The test stays the same
([`03`](03-atomicity-and-staging.md)): *would a reviewer ask about these separately?*
