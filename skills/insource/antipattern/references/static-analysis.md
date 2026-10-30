# Static analysis and measurement

Metrics provide objective evidence. They never settle the question alone.

## Contents
- Principles
- Workflow
- Tool matrix
- What metrics can and cannot indicate
- Recording evidence
- Limitations

## Principles

1. **Use what exists.** Run `scripts/detect_tooling.py` and prefer installed analyzers, the project's own lint/type configs, and standard tools. Write a custom script only for a narrow question no tool answers (for example counting a specific suppression pattern), and keep it throwaway.
2. **Read-only.** No autofix flags, no config edits, scratch output under `/tmp/antipattern/`.
3. **Choose metrics that fit the language and the candidate pattern.** Do not collect every metric.
4. **Relative before absolute.** Compare a unit against the project's own distribution (outliers above roughly the 95th percentile) and cite published guidance only as a secondary reference. Fixed thresholds copied from blog posts mislead.
5. **Separate fact from reading.** Every significant finding states the measurement, the interpretation, and the uncertainty separately.

## Workflow

1. `python scripts/detect_tooling.py <root>`: languages, manifests, analyzers available and missing.
2. Run the relevant installed tools on the in-scope paths only, excluding vendored, generated, and build output.
3. If a needed tool is missing, install it in an isolated environment outside the repo (venv or temp prefix) when network access exists. If it does not, say so and fall back to narrower checks or manual inspection.
4. Save raw outputs in `/tmp/antipattern/` and summarize in the findings.
5. Cross-check at least the top findings by reading the code. A tool can flag generated code, tests, or intentional design.

## Tool matrix

Examples, not a mandate. Verify names and flags against the installed version.

| Need | Cross-language | Python | JS / TS | Go | Rust | JVM | .NET | Ruby | PHP |
|---|---|---|---|---|---|---|---|---|---|
| Size / inventory | `cloc`, `tokei` | | | | | | | | |
| Complexity, LoC per function | `lizard` | `radon` | `eslint` complexity rules | `gocyclo` | `clippy` | PMD, Checkstyle | Roslyn analyzers | `flog`, `reek` | `phpmd` |
| Duplication | `jscpd` | | | | | PMD CPD | | | |
| Types and contracts | | `mypy`, `pyright` | `tsc --noEmit` | `go vet` | compiler | compiler | compiler | | `phpstan` |
| Dead / unused code | | `vulture` | `knip`, `ts-prune` | `staticcheck` | `cargo-udeps` | IDE/compiler warnings | analyzers | | |
| Dependency graph, cycles | | `pydeps`, `import-linter` | `madge`, `dependency-cruiser` | `go list -deps`, `go mod graph` | `cargo tree` | ArchUnit, jdepend | NDepend or analyzers | | |
| Security patterns | `semgrep` | `bandit` | `eslint-plugin-security` | `gosec` | `cargo-audit` | SpotBugs | analyzers | `brakeman` | |
| Structural search | `ast-grep` (the `sg` alias collides with the Linux `sg` command), `rg` | `ast` module | | | | | | | |

## What metrics can and cannot indicate

| Metric | May indicate | Check before concluding |
|---|---|---|
| Very long function or class | Mixed responsibilities | Does it change for several unrelated reasons? Is it generated or a table of cases? |
| High cyclomatic complexity or deep nesting | Hard-to-test branching, missing decomposition | Is the branching inherent (parser, state machine)? |
| Many parameters or boolean flags | Missing abstraction or a function doing several jobs | Are callers actually passing different combinations? |
| Duplicate blocks | Copy-paste logic that may diverge | Have copies already diverged? Are they in unrelated domains? |
| Import cycles, many afferent/efferent edges | Poor layering or a hub that knows too much | Is the hub an intentional composition root? |
| Unused declarations | Dead code, leftover scaffolding | Reflection, DI, or public API usage that tools cannot see |
| Many suppressions or casts | Superficial compliance | Where are they concentrated, and are they justified? |

## Recording evidence

For each significant finding keep three labelled parts:

```
Measured:      lizard on app/services/order_service.py: process_order = 212 LoC, CCN 38 (project p95 CCN = 11).
Interpreted:   Probably mixes validation, pricing and persistence (read lines 40-210).
Uncertainty:   Medium. Git blame shows hand-written over 14 commits; no generated header.
Reproduce:     lizard app/ -l python --csv > /tmp/antipattern/lizard.csv   (lizard 1.17, 2026-10-26)
```

## Limitations

State these in the report's methodology when relevant: unanalyzed languages, excluded paths, dynamic dispatch or DI hiding dependencies, tools that could not be installed, partial runs on large repos, and generated or vendored code that was excluded.
