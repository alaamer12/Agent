# Pitfalls that change conclusions

The traps that make a reading wrong rather than merely slow — each row is a conclusion people reach and the
reality behind it. Check them before you report.

| Trap | Reality |
|---|---|
| "No diff" | merge commit, untracked file, wrong baseline, or path outside the range |
| Rename read as delete+add | you forgot `-M`; the "new" file is the same code |
| Whitespace noise hides a one-line change | `-w` before concluding "only formatting" |
| `git diff` shows nothing | the change is staged: `git diff --cached` |
| Huge generated file read line by line | the information is the regenerated diff, not the content |
| `autocrlf` rewrites every line | diff with `--ignore-cr-at-eol`; never review line endings as logic |
| Non-ASCII paths print as `\344\275\240` | `git -c core.quotepath=false diff …` |
| Piped output with no colour | `--color=always` when `--color-moved` matters |
| Diff agrees with the message, code does not compile | the diff is not the system; run it if the claim is behavioural |
| Whole diff loaded to answer one question | context spent for nothing — index first, `--hunks` then `--hunk --budget` |
| `git show <sha>` to see a deleted file | the commit prints the whole deletion — `--at <rev-before> --path F --lines/--grep` |
| Aggregate range read as the story | commits that cancel out are invisible: `--per-commit` exposes hidden churn |
| `blame` treated as authorship | it reports the **last touch** — a move or reformat reassigns the line; use `-w -M -C`, then `log -L` |
| "This file has no history" | `git log -- path` stops at a rename — add `--follow` |
| Topic hunt answered by dumping every patch | `git log -S topic -p` can run to tens of k tokens in a few-hundred-commit repo; the `--topic` dossier said more in ~600 - and covered the message channel too |
| `--range <single-sha>` treated as worktree | a single revision means **that commit's own diff**; use `--worktree`/`--staged` for local state |
