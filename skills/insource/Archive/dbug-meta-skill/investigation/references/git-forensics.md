# Git forensics — when "it worked before" is in the frame

Source: `data/debug.txt` §2; `data/user.txt` §19; `data/grok.txt` §3,5;
`data/gemini.txt` §15. Trigger: the user confirmed (or evidence shows) the
behaviour was previously correct, or the failure began around a deploy/PR.
The question that drives everything here:

> **What changed between last known-good and first known-bad?**

## Establish the bookends first

```
known-good: tag/commit/date/user-reported "last worked" — pin a SHA
known-bad:  current failing state — pin a SHA
```

Ask for the date; `git log --until=<date>` converts memory into commits.
Vague bookends make bisect meaningless — if you cannot bound good/bad,
skip to hypothesis work and come back.

## The cheap moves, in order

```bash
git log --oneline -20 -- <paths in the failing area>   # what touched it
git log --since=<good-date> --oneline -- <suspect-path>
git diff <good> <bad> -- <path>                        # read the delta
git log --all --oneline --grep='<feature>'             # find the change story
git branch -a --contains <commit>                      # did it ship everywhere?
git log -p --follow <file> | less                      # when did this line appear
```

Reading the diff of the suspect window usually *is* the investigation: the
regression is nearly always inside the change set the user can describe.
Correlate with non-code changes too — lockfile diffs (dependency bump),
migration files added, config/env changes committed, feature-flag defaults.

## git bisect — when the window is large and the failure is deterministic

```bash
git bisect start
git bisect bad                  # current
git bisect good <sha>           # last known-good
git bisect run <test-command>   # script/exit-code that fails on bad
```

Requirements: (1) a command that decides good/bad automatically — if none
exists, *write the reproduction first* (`.debugging/tmp/repro.sh`, exit 1
on bug) — it becomes the regression test's twin anyway;
(2) every intermediate commit must be runnable (skip unbuildable ones).
~log2(n) steps; 1000 commits ≈ 10 builds. Manual bisect (checkout middle,
test, half) when automation can't wire up.

## Beyond commits: the same logic on every axis

| Axis | Bisect/diff instrument |
|---|---|
| dependency version | lockfile diff; `npm/pip install <pkg>@<ver>` binary search |
| config value | change one value at a time; diff env dumps |
| migration history | which migration first produces drift (see ../../database/SKILL.md) |
| deploy/release | compare artifacts between releases (staging↔prod, image digests) |
| dataset | halve the failing input — binary narrowing of data |

## Caveats

- Bisect finds the commit that *exposed* the bug, not always the one that
  *introduced* it (latent defect + new caller). After locating the exposing
  commit, ask "what was already wrong here before this change?"
- "Worked on another branch" = diff the branches on the failing paths
  (`git diff main..<branch> -- <area>`), don't bisect blindly.
- Squash-merged/force-pushed history breaks linearity — bisect against
  release tags instead of the messy middle.
- The endgame is still the pipeline model: a diff narrows candidates; the
  first invalid state proves the candidate. Don't stop at "this diff looks
  suspicious" (evidence Level 2) when the repro/bisect result can reach
  Level 4–5.
