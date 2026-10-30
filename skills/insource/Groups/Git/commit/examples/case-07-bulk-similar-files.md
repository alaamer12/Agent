# Case 7 — twenty similar files in one sitting

**Situation:** a DSA tutorial repo. The task: write a `README.md` for each algorithm folder — `greedy/`,
`backtracking/`, `dp/`, `graph/`, … — plus a global `README.md` with the index. Twenty-one files, one sitting.

The tempting move is one commit named `docs: add readmes`. The other tempting move — twenty-one commits of
`docs: add readme` — is not more professional, it is noise. The decision is made by **intent granularity**, not
by file count.

## The test that decides

| Question | If yes |
|---|---|
| Does each file carry substantive, distinct content? | one commit per file |
| Were they authored in separate steps, possibly separate days or people? | one commit per file |
| Will different people own them later? | one commit per file — per-file blame and per-file revert survive |
| Are they boilerplate or placeholders ("Coming soon", title only)? | one bulk commit |
| Are they all the same template, produced in one sitting as one unit? | one bulk commit |

## Case A — real content, per-file commits

```bash
git add algorithms/greedy/README.md
git commit -m "docs(greedy): add README with overview of greedy strategies"

git add algorithms/backtracking/README.md
git commit -m "docs(backtracking): add README with explanation and example"

git add algorithms/dp/README.md
git commit -m "docs(dp): add README with top-down vs bottom-up comparison"

git add README.md
git commit -m "docs(root): add global project README with index and instructions"
```

Note the scope: the shared concern is *documentation of one algorithm family*, so the folder name is the scope
and the subject says what the reader gets. `docs: add readme` repeated twenty-one times teaches nothing.

## Case B — the same session produced scaffolding

```text
docs: add README stubs for all algorithm categories

Each file carries the standard section outline (problem, approach, complexity,
references) so contributors can fill them in. The global README indexes them.
Content is placeholder by design; per-folder authorship starts in follow-ups.
```

One commit, because it is one decision: *the repository now has a documentation skeleton*. The body says the
content is deliberately empty, so nobody mistakes the stub for finished documentation and closes the task.

## The mixed case, which is the common one

Four folders got real write-ups; sixteen got stubs. That is **two commits**, not seventeen:

```bash
git add algorithms/greedy/README.md algorithms/dp/README.md \
        algorithms/backtracking/README.md algorithms/graph/README.md
git commit -m "docs(algorithms): write READMEs for the four core paradigms"

git add algorithms/*/README.md
git commit -m "docs(algorithms): add stub READMEs for the remaining categories"
```

`git add algorithms/*/README.md` is safe here only because the glob was written *after* the first four were
committed, so it cannot capture them — the ordering is the discipline, not the glob.

## What stayed uncommitted

The scratch notes file `planning/readme-outline.md` and a `drafts/` folder: personal working material, not
project documentation. Reported as deliberately left out rather than silently included or silently dropped.

## Report line

```text
COMMITTED : 2 - docs(algorithms): write READMEs for the four core paradigms (4 files)
            docs(algorithms): add stub READMEs for the remaining categories (16 files)
NOT STAGED: planning/readme-outline.md, drafts/  - personal working notes
WHY SPLIT : substantive content and placeholder scaffolding are different decisions
```
