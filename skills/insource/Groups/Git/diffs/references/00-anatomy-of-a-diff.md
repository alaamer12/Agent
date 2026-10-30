# Anatomy of a diff — read the format, not the vibe

Every misunderstanding of a diff is usually a misread header. The hunks carry their own coordinates, and the
headers say what kind of change happened before a single line of content.

## The file header

```text
diff --git a/src/auth/token.py b/src/auth/token.py
similarity index 96%                            <- with -M/-C: this is a RENAME, not delete+add
rename from src/auth/token.py
rename to   src/auth/tokens.py
index 9c1f0a4..c4a8d1f 100644                   <- blob ids (abbrev) + mode
--- a/src/auth/token.py
+++ b/src/auth/tokens.py
```

What the header lines mean, and when they matter:

| Line | Meaning | Why you care |
|---|---|---|
| `new file mode 100644` / `deleted file mode 100755` | creation / deletion | a delete is where behaviour disappears |
| `old mode` / `new mode` | permission or type change | `100755` (executable), `120000` (symlink), `160000` (submodule) |
| `similarity index 96%` + `rename from/to` | rename detected (`-M`) | without `-M` this is a 400-line delete and a 400-line add |
| `copy from/to` | copy detected (`-C`) | a duplicated file is a maintenance debt, not a move |
| `Binary files … differ` | opaque change | require the source, or a regeneration path |
| `GIT binary patch` | `--binary` payload | only needed to apply, never to read |
| `Subproject commit abc…` → `def…` | submodule pointer | a dependency change hidden in one line |
| `\ No newline at end of file` | missing trailing newline | style only, unless a tool concatenates files |

## The hunk header — the arithmetic that matters

```text
@@ -41,7 +41,8 @@ def refresh(self, force=False):
   │   │  │   │  └── new side: 8 lines starting at new line 41
   │   │  │   └───── new start line
   │   │  └───────── old side: 7 lines starting at old line 41
   │   └──────────── old start line
   └──────────────── enclosing function / section, from the diff driver
```

Rules that prevent invented findings:

- **Counts, not lines.** `-41,7 +41,8` means one net line added in this hunk — not seven changes.
- A count of `1` is often omitted: `@@ -5 +5 @@`.
- **The sides drift apart.** After a hunk that adds 3 lines, old line 100 is new line 103. When you cite a line
  number, say which side (`new:103`) or the reader will look at the wrong code.
- **Two hunks can mean one change.** A rename of a variable often produces `-old +new` in five separate hunks —
  read them together before concluding "five changes".
- **Context lines are not changes.** Three lines either side by default (`-U3`); `-U0` to see only the edits,
  `-U10` when the surrounding code is what makes the change sensible.
- **`-U0` is a trap for review** — it hides the control flow that gives the changed line its meaning.

## Reading a hunk in the right order

1. Read the `@@ … @@` function context: *what* is this hunk inside?
2. Read the **all `-` lines first**, as a block: what did the code do before?
3. Read the **`+` lines** as a block: what does it do now?
4. Only then read them interleaved — the line-by-line diff of a rewrite is noise; the two blocks tell the story.
5. Ask the change question: is the *condition*, the *default*, the *order*, or the *error path* different?

## Special formats you will meet

- **Combined diff (merges):** `@@@ -a,b -c,d +e,f @@@` with **one column per parent** in the content lines
  (`- ` means removed relative to that parent, `+` added). It shows what the *resolution* introduced, not what
  the branch contained — see [`04`](04-merges-and-series.md).
- **Word diff:** `[-removed-]{+added+}` in `--word-diff=plain`; `--word-diff=porcelain` emits tokens on their
  own lines (parseable), `--word-diff=color` uses colour only.
- **Colour-moved:** moved blocks are coloured, not marked in text; piping drops colour unless `--color=always`.
- **`--stat`:** `path | 12 +++---` is a visualisation, not data; `--numstat` gives exact added/removed counts
  (and `-` `-` for binary).
- **`--name-status`:** `R100 old → new` — the number is similarity; `C` copy, `T` type change, `U`
  unmerged.

## Encoding and line endings — the silent diff corruptor

| Symptom | Cause | Fix |
|---|---|---|
| Every line of a file is `-`/`+` | line endings changed (`autocrlf`, editor) | `git diff --ignore-cr-at-eol`, then `-w` |
| Every line changed after a small edit | indentation converted (tabs ↔ spaces) | `-w`; check `.editorconfig` / formatter run |
| Non-ASCII filenames print escapes | `core.quotepath` default | `git -c core.quotepath=false diff` |
| A UTF-8 file reads as binary | NUL byte, or a misconfigured driver | `--text` to inspect, then fix the cause |
| BOM appears as a change | editor added/removed BOM | treat as a file-format change, not logic |
| A diff of a CRLF file is unreadable in a script | text-mode decoding rewrote CRLF | capture **bytes**, never decode (`scripts/diff_survey.py` does) |

## What the format cannot tell you

- Whether the code compiles, and whether the change *works* — a diff is not the system.
- Untracked files, stash contents, or anything outside the chosen baseline.
- Intent — the message claims it; the diff never does. The claim is verified in
  [`03-truthfulness-review.md`](03-truthfulness-review.md).
- What was moved versus rewritten when the move is below the similarity threshold; raise `-M` to 30% to see
  whether the "new" file is the old one moved.
