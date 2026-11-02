# Following the doc chain

The project tells you where its own truth lives. This pass is traversal, not review: read what
the docs say, record what they point at, and never silently drop a pointer.

## Starting files, in order

1. `AGENTS.md` — the designed entry point for agents. If it exists, it wins.
2. Otherwise: `README.md` (human entry), package/build manifests
   ([package.json], [composer.json], [pubspec.yaml], [.csproj/.sln], [go.mod], [Cargo.toml]),
   CI definitions ([.github/workflows], [.gitlab-ci.yml]), and root docs folders — order is
   whatever actually exists; say which one you started from.

Missing AGENTS.md is a recorded finding, not a failure: note it once and continue.

## What to follow from AGENTS.md

A well-kept AGENTS.md is a **pointer table**. Read every pointer it declares, in this priority:

| Pointer kind | Why it matters to the overview |
|---|---|
| Workflow/build/startup docs | define what the project claims to be and how it runs (read-only — never execute it) |
| Units catalog / component docs (UNITS.md, SYSTEM-COMPONENTS.md) | the module inventory the code sweep will check against |
| `# Glossary` or GLOSSARY.md | project vocabulary — reading code without it misreads domain terms |
| COMMITMENTS.md or a Commitments section | declared priorities; "does the project agree with itself" is judged against these |
| IDEA.md / design/spec docs | the intended behavior statements that become ledger claims |
| Decision records (`docs/decisions/`, `.iwts/*/decisions/`) | why non-obvious things are the way they are |
| Skills section ("whenever you use skill X, read source Y") | per-skill standing instructions — read the referenced sources before treating that area |
| Environment/config docs | variable *names*, ports, services — presence only; values of secrets are never read or reported |

## Traversal rules

- **Breadth-first, bounded.** Read the docs the entry doc points to; then follow pointers those
  docs make, to a second hop. Beyond that, list unread deeper docs by path in the report rather
  than reading everything — the chain is usually deeper than it is wide.
- **Broken pointer = finding.** Referenced file missing, empty, or a heading that no longer
  exists: record (pointer text, expected path, status). Never guess what it "probably" pointed
  to, never quietly skip.
- **Stale pointer = finding.** The doc exists but describes files/behavior the sweep already
  proved absent: record it with both sides.
- **Duplication = pick an authority.** Two docs claiming to define the same table: note which
  one the entry doc references, and flag the other as a drift risk.
- **Language stays the project's.** Read docs in whatever language they are written; report the
  overview in the language the user used.

## Extracting the intent ledger

While reading, convert prose into checkable claims. A claim is anything the docs assert about
structure or behavior that code could contradict:

```text
| # | Claim                                   | Source            | Check later against          |
| 1 | "auth lives in apps/api/auth module"    | docs/ARCH.md §2   | directory + imports          |
| 2 | "sync is retrying 3 times"              | GLOSSARY + spec   | constants in sync code       |
| 3 | "no direct DB access from UI layer"     | COMMITMENTS.md    | import scan                  |
```

Rules: only claims the docs actually make (no invented requirements); quote or cite the exact
section; prefer falsifiable phrasing. This ledger is what `/exmaine full` later checks pass by
pass — the code sweep knows where to look because the ledger says what should be there.
