# Agenda Index

Directory of language/framework agenda folders. Each folder's own `index.md` maps `../decision-spectra.md`'s universal trade-offs onto that ecosystem's idiom. Each `examples/` file argues one specific point through a real, redacted case.

Not a roadmap — lists what exists now, says nothing about what's next.

## Directory

| Language | Framework / context | Path |
|---|---|---|
| JavaScript (TypeScript as its typing layer, not a separate branch) | Plain — no UI framework | `javascript/plain/` |

## When the project's stack has no matching folder

1. `../decision-spectra.md` always applies — it isn't language-scoped.
2. Check other agenda folders' examples for a case whose *shape* transfers (same kind of duplication risk, same kind of boundary question) even if the ecosystem doesn't match — weight it as a borrowed hypothesis, weaker than a native example, and say so in the output.
3. Say plainly no dedicated agenda backs this stack; ask whether to proceed on that basis or wait for one to be written.

## Adding an agenda

New folder: `agendas/<language>/<framework-or-plain>/index.md` + `examples/`. One row here. Nothing else.
