---
name: packages
description: 'One run, two jobs over a project''s dependencies, any ecosystem (JS/TS, Python, Go, Rust, JVM, .NET…) and any project shape. Job 1 — redundancy audit: classifies each dependency as explicit (imported) or implicit (needed without any import: toolchain binaries, native/link-time stubs, config plugins, entry-point-discovered packages, blank imports, peer deps, codegen, type-only), flagging for removal only what is neither. Job 2 — freshness: updates via the ecosystem''s first-class tooling when it exists (go mod tidy, bun update --latest, cargo upgrade, uv, dotnet-outdated…), else resolves latest via context7 or registry/web search — never memory; always a before/after report for approval, majors checked against migration guides and real project usage first. Both jobs close with a mandatory verification gate — resolve, typecheck/compile, build, tests, runtime — with commands discovered from the project''s scripts and CI, never invented. Use to audit, dedupe, clean up, update, or modernize dependencies in any stack.'
---

# packages

Two checks in one skill, answering *"do we still need all of this?"* and
*"is all of this still current?"*. They share the dependency manifests as
their surface, one verification loop (sync → static check → build → tests →
runtime where possible), and one rule: **nothing is removed, added, or
version-bumped on a guess.** When the user doesn't scope the run: job 1, then
job 2.

> **This skill is ecosystem-general.** Every command, tool name, and
> dependency kind here and in its references is an *illustrative example* of
> what its ecosystem provides — not a mandate, not a closed list; a hybrid or
> unlisted answer is always acceptable. Standing procedure: detect what this
> project actually uses, then **verify the current tooling by searching**
> (context7 if installed, else web) rather than answering from memory —
> dependency tooling turns over fast, and a remembered command or "best tool"
> is stale by construction.

Per-ecosystem facts (manifests, implicit proofs, native tidiers, updaters,
registry queries, verification chains) live in
`references/ecosystem-playbook.md`; scan recipes, the worked-example script,
and report templates in `references/audit-toolkit.md`.

## Step 0 — Detect the ecosystem and the project shape

Read the repo root (and workspace globs) for manifests/lockfiles —
`package.json` + locks/`pnpm-workspace.yaml`, `pyproject.toml` (+ uv/poetry),
`go.mod`/`go.work`, `Cargo.toml` (`[workspace]`), `pom.xml`/`build.gradle`,
`*.sln`/`*.csproj`, `Gemfile`, `mix.exs` — full table in the playbook. The
shape falls out of what's found: **single module** (one manifest),
**workspaces/monorepo** (root workspace config: npm/bun, Cargo, uv, Gradle
settings, Maven reactor), or **multi-manifest/polyglot** (independent projects
in one repo — run the jobs per subtree; never let one ecosystem's tooling
stand in for another's).

## Job 1 — duplicate/redundancy audit

### Explicit vs implicit usage — the distinction that decides everything

**Explicit** = code references it (`import`, `require`, `use`, blank import).
**Implicit** = the project needs it installed *though nothing imports it* —
where naive audits delete working builds. Named kinds (pattern: *"installed
IS the usage"*):

- **Toolchain invoked by name** — compilers/transformers a config or script
  calls (`oxc`/`swc`/`esbuild`; `maturin`/`cmake`; JVM annotation processors;
  .NET analyzers). Proof lives in config and scripts, not source.
- **Native/runtime stubs & link-time packages** — zero code references,
  runtime demands them (`react-native-screens`-class; `-sys`/cgo/JNI links;
  provider gems). Compile clean without them, crash at launch → *runtime*
  verification mandatory.
- **Plugins registered in config** — listed in a plugin/preset array (ESLint/
  Metro/Tailwind-style; pytest plugins in `pyproject`/`pytest.ini`).
- **Entry-point / metadata-discovered plugins** — installing *is* activating
  (Python entry_points/pluggy, Ruby gem discovery, .NET analyzers, Gradle
  plugin markers). Text search can never find these; metadata is the only
  proof — the most-deleted-by-mistake class, everywhere.
- **Side-effect / blank imports** — `import 'x'`, Go `_ "x"`,
  register-on-import modules: referenced, but never used as a value.
- **Peer / provided-scope deps** — satisfied by being installed (React
  peers, Maven `provided`, Cargo feature-required deps).
- **Install-time codegen** — postinstall/prepare scripts (`prisma generate`),
  `build.rs`, pre-commit hooks, generators whose *output* is imported.
- **Type-only/stub packages** — compiler-consumed (`@types/*`, PEP 561
  `types-*`); nothing imports them at runtime.

**A package is a removal candidate only when it is neither explicitly nor
implicitly used.** Uncertain status (is that gem metadata-discovered? does
the SDK demand that stub?) → check its docs (context7/web), don't assume:
implicit removals typically fail at *runtime* — the one layer static checks
can't see.

### Workflow

1. **Scope** — the manifests found in step 0 (all workspaces, or the subtree
   the user named).
2. **Native detector first, script fallback.** Several ecosystems ship
   authoritative tooling — `[go mod tidy]` prunes unreferenced deps itself;
   `[cargo machete]`/`[cargo-udeps]`, `[knip]`/`[depcheck]`,
   `[mvn dependency:analyze]` report candidates — verify what's current, use
   it where it exists, cover the rest with the universal scan recipe in the
   toolkit. Never audit from internal knowledge of the codebase; always run
   something against actual files. (Native *analyzers* are
   candidate-generators: blind to exactly the implicit kinds above.)
3. **Redundancy (shared-abstraction check).** Umbrella/kit packages and
   central version catalogs (`[pnpm catalog]`, `[workspace.dependencies]`,
   `[Gradle version catalogs]`, Maven BOMs, .NET central package management)
   make direct deps duplicative or per-manifest pins redundant. "Likely"
   isn't verified — confirm the kit re-exports it / the catalog covers it
   before removing.
4. **Categorize** — **explicit** (keep) · **implicit** (keep; record *which
   kind* proves it) · **unused** (neither, all checks negative → removal
   candidate) · **redundant** (kit/catalog-covered → candidate) ·
   **misplaced** (build/test-only use declared as runtime dep → move to the
   ecosystem's dev/tool scope: `devDependencies`, `dev-dependencies`,
   poetry groups, Gradle test scope…).
5. **Report, then implement** — categorized table to the user; remove only
   approved candidates; re-sync each lockfile (`bun install`, `poetry lock`,
   `go mod tidy`, …).
6. **The verification gate — mandatory after EVERY change, ecosystem-native,
   in order.** No removal or move is "done" until this ladder passes; it is
   the closing step of the job, not optional polish:

   1. **Resolve** — lockfile syncs cleanly (`bun install` / `poetry lock` /
      `go mod tidy` / `cargo build` / `bundle install` / `dotnet restore`…).
   2. **Static gate** — the ecosystem's type/lint checker: `tsc --noEmit` /
      `mypy`/`pyright` / `go vet` / `cargo check --all-targets` /
      `javac`-compile / `dotnet build` (analyzers fire here) / `rubocop` /
      `mix compile --warnings-as-errors`.
   3. **Full build / package** — the real build, not just the type pass:
      bundlers, linkers and annotation processors surface implicit-usage
      mistakes the static gate cannot see.
   4. **Tests** — unit/integration suites.
   5. **Runtime smoke** where feasible — mandatory for native-stub /
      link-class / entry-point-plugin removals: that class compiles clean
      and fails at launch.

   **Discover the exact commands from the project, don't invent them** — the
   authoritative list is the project's own scripts: `package.json` scripts,
   `Makefile`/`justfile`, `Cargo.toml` aliases, Gradle tasks, `pyproject`
   tool sections, and **CI workflow files** (CI already encodes what
   "verified" means for this repo — run what CI runs, locally, in its order).
   Polyglot repos run each subtree's ladder. **A failing gate ends nothing
   silently: fix the cause, or revert that change and record why — never
   declare done on a red gate, never skip a rung because it "should be
   fine".**

## Job 2 — are the deps up-to-date?

1. **The ecosystem's own updater beats a hand-rolled diff.** Report-vs-apply
   pairs by stack — `[bun update --latest]`, `[npm-check-updates]`,
   `[pnpm outdated]`; `[go list -m -u all]` + `[go get @latest]`;
   `[cargo outdated]` + `[cargo upgrade]` (`cargo update` alone = the
   semver-respecting safe default); `[poetry show --outdated]` /
   `[uv lock --upgrade]`; `[dotnet-outdated]`;
   `[mvn versions:display-dependency-updates]` / `[gradle dependencyUpdates]`;
   `[bundle outdated]`; `[mix deps.update]`. Where the stack ships a
   *coordinated* updater that knows inter-package constraints
   (`expo install --check/--fix` pinned to the SDK being the JS example),
   prefer it over per-package "latest" — "latest on the registry" and
   "correct for this stack" are different answers.
2. **No tool for it — resolve latest externally, never from memory.**
   context7 if installed (version-matched docs arrive with the number, which
   step 4 needs) → else **the registry itself is the search**: one call each
   (`npm view`, `pip index`, Go module proxy `@latest`, `cargo search`,
   NuGet/Maven/rubygems/hex APIs). A remembered version is not evidence.
3. **Always the before/after report BEFORE applying.** Per dependency:
   current vs latest, grouped **patch / minor / major**, each row naming
   *where "latest" came from* (updater / context7 / registry call) — an
   unverified "latest" is memory wearing a table. Template in the toolkit;
   the user approves the set or a scope ("minors only", "skip that major").
4. **Majors: check breaking changes before updating, not after.** Fetch the
   migration guide/release notes (context7, then the project's own
   changelog) and answer per major what breaks *in this project* — removed
   APIs actually called here, config-format changes, constraint shifts.
   Nothing findable → mark "unknown breakage — extra verification on
   apply", never "safe by default". Patch/minor skip this unless release
   notes say otherwise.
5. **Apply, then run the FULL verification gate** (job 1 §6) — it is not
   optional after updates any more than after removals: resolve → static
   check → build → tests → runtime smoke, per group, with the gate re-run
   after each package family lands. A green `install` is not verification;
   the ladder is. Land majors by package family (SDK-coupled together, UI
   libs together), never one 40-package sweep; keep job-1 removals and
   job-2 bumps as separate changes — a broken gate after "removed 6 and
   updated 30" can't bisect. If a gate fails on a major: fix forward if the
   migration is small and documented, otherwise revert that family cleanly
   and record it as "blocked on migration" — never leave a repo half-upgraded.

## Best Practices

- **Peer/provided scoping serves both jobs** — shared deps are dedup
  candidates *and* version-coordination points during updates.
- **Re-export barrels/umbrellas** — public exports can reference a dep no
  local import shows; check what the package exports outward.
- **Metadata-discovered & blank imports are the classic false "unused"** —
  the kinds table exists for them; run it before any removal list.
- **Ecosystem idioms outrank this skill's tables** — a convention this file
  doesn't list (a monorepo tool, a metapackage, a platform BOM) wins over
  anything here.
