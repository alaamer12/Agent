# packages — ecosystem playbook

Per-ecosystem facts for both jobs: what files to read, where implicit usage
leaves its proof, which native tools detect-unused or update versions, how to
query "latest", and the verification chain. **Every entry is illustrative of
its ecosystem's current tooling, not a closed mandate — verify what exists
today by searching (context7 / web / the ecosystem's own docs) before
running; remembered tool names and commands go stale fast.** Verification
labels: `verified` = actually run in this environment; `typical` = standard
ecosystem knowledge, not re-checked here.

The repo may mix shapes — a single manifest (everything applies once),
workspaces/monorepo (apply per member against the root config), multi-manifest
(polyglot repo: run each subtree independently, never share conclusions
across ecosystems).

---

## JS / TS (npm · bun · pnpm · yarn; Expo as a coordinated stack)

- **Detect:** `package.json` (+ `workspaces`, `pnpm-workspace.yaml`,
  `bun.lockb`/`bun.lock`, `package-lock.json`, `pnpm-lock.yaml`,
  `yarn.lock`).
- **Source to scan:** `.ts .tsx .js .jsx .mjs .cjs`; configs: babel/metro/
  metro/tailwind/postcss/eslint/vite/next, `tsconfig.json`, `app.json`,
  `package.json` scripts.
- **Implicit proofs:** plugin names in config arrays; `import 'x'`
  side-effect imports; native runtime stubs (react-native-*) — **runtime-only
  failure class**; `@types/*` consumed via tsconfig; peer deps; postinstall
  codegen (`prisma generate`).
- **Native unused detection (typical):** `knip`, `depcheck`, `npx
  npm-check`-class tools; workspace-aware ones for monorepos. *(Verify which
  are current before relying on one.)*
- **Updaters (verified in-repo: `bun install`):** `bun update --latest`,
  `pnpm outdated` / `pnpm update --latest`, `npx npm-check-updates [-u]`
  [--target minor], Expo: `npx expo install --check` / `--fix` (SDK-pinned —
  the coordinated-updater example), `npx expo fix`.
- **Registry query:** `npm view <pkg> version` / `… versions --json`.
- **Verify chain:** `bun install` → `bun run typecheck` per workspace →
  build (`turbo`/task runner) → tests → device/emulator runtime for
  native-stub removals.

## Python (pip · uv · poetry · pdm)

- **Detect:** `pyproject.toml` (+ `[tool.uv.workspace]`, poetry sections),
  `requirements*.txt`, `Pipfile`, `pdm.lock`, `uv.lock`, `poetry.lock`.
- **Source to scan:** `.py` (+ `.pyi`); configs: `pyproject.toml`,
  `setup.cfg`, `pytest.ini`/`tox.ini`, pre-commit config, `conftest.py`.
- **Implicit proofs (the big classes here):** **entry-point plugins** —
  installed *is* used (pytest plugins via `project.entry_points`/pluggy,
  flake8/ruff plugin family); build backends (`maturin`, `setuptools`
  extensions) named in `pyproject` `[build-system]`; PEP 561 `types-*` stub
  packages; `import x  # noqa: F401` registration side-effects; extras.
- **Native unused detection (typical):** no universal standard — per-file
  unused-import linters (`ruff`, autoflake) catch code references but are
  blind to entry-point installs; pair any tool's output with the implicit
  table before removing. `pip cache`/resolver tools don't do project-unused
  analysis.
- **Updaters (typical):** `uv lock --upgrade` / `uv sync`, `poetry show
  --outdated` + `poetry update`, `pip list --outdated` (+ `pip-review`),
  `pdm update`; constraint files (`requirements` pins) updated by re-resolution,
  not per-package commands.
- **Registry query:** `pip index versions <pkg>`; PyPI JSON API
  `pypi.org/pypi/<pkg>/json`.
- **Verify chain:** lock sync → `mypy`/`pyright` if configured → build/install
  the package → `pytest` → runtime import smoke (entry-point breakage shows
  at test-collection, not type-check).

## Go

- **Detect:** `go.mod` (+ `go.work` for multi-module).
- **Source to scan:** `.go` — including **blank imports** `_ "x"` (drivers,
  `embed`, pprof) — explicit in Go's own syntax; build-tag'd `tools.go`
  pattern pins binary tools as module deps.
- **Implicit proofs:** `tools.go`/`internal/tools` imports; `go:generate`
  invocations referencing an installed binary; cgo/purego packages linked at
  build; test-scope deps.
- **Native unused detection:** `go mod tidy` — the authoritative pruner, it
  *removes* what's unreferenced (typical, universal); read its diff rather
  than trusting a hand-audit. *(Verified concept; run with care on a branch.)*
- **Updaters:** `go list -m -u all` (report) → `go get <mod>@latest` /
  `@vX.Y.Z` (apply) → `go mod tidy` (sync); `govulncheck` for the security
  slice.
- **Registry query:** module proxy — `go list -m <module>@latest`;
  proxy.golang.org `…/@v/list`.
- **Verify chain:** `go mod tidy` → `go vet ./...` → `go build ./...` →
  `go test ./...`. (No separate typecheck; vet+build is the static gate.)

## Rust

- **Detect:** `Cargo.toml` (+ `[workspace.dependencies]` catalog) /
  `Cargo.lock`.
- **Source to scan:** `.rs` — plus `use` in `lib.rs`/`mod` re-exports;
  `build.rs` scripts; proc-macro usage in attribute position
  (`#[derive(...)]` counts as explicit use of the macro crate).
- **Implicit proofs:** `-sys`/link crates (LLVM/OpenSSL bindings — absence
  fails at *link* time, a different error class than compile); proc-macros
  pulled in via derive attributes; feature-gated deps invisible unless the
  feature set is enumerated (`cargo tree -e features`); `build-dependencies`;
  workspace members depending on the catalog pin instead of a local version.
- **Native unused detection (typical):** `cargo machete`, `cargo-udeps`
  (nightly-era caveats — verify current status); `cargo tree` for the
  transitive picture before calling a direct dep redundant.
- **Updaters:** `cargo outdated` (report) + `cargo upgrade` (apply, from
  cargo-edit) or `cargo add <crate>@latest`; `cargo update` = semver-respecting
  lock refresh (patch/minor), the *safe default* separate from `--latest`-style
  major jumps.
- **Registry query:** crates.io API / `cargo search <crate>`.
- **Verify chain:** `cargo check --all-targets` (catches feature-gated
  omissions) → `cargo clippy` → `cargo build` (link-time class surfaces
  here) → `cargo test`.

## JVM (Maven · Gradle)

- **Detect:** `pom.xml` (reactor `<modules>`, parent/BOM imports),
  `settings.gradle(.kts)` + `build.gradle(.kts)` (version catalogs in
  `gradle/libs.versions.toml`).
- **Source to scan:** `.java`/`.kt`; build files themselves; annotation usage
  (`@Override`-class deps appear only as decorators).
- **Implicit proofs:** annotation processors / KAPT-KSP plugins (compile-time
  only, zero runtime imports); `provided`/`compileOnly` scope; BOM-managed
  versions (a per-module pin duplicating the BOM = redundancy candidate);
  Gradle plugins declared only in `plugins {}` blocks; service-loader
  (`META-INF/services`) registrations.
- **Native unused analysis (typical):** `mvn dependency:analyze` (reports
  "unused declared" / "used undeclared" — with known false positives on
  exactly the annotation-processor/serviceloader classes above; treat its
  "unused" as candidate-list, not verdict); Gradle has no built-in —
  dependency-analysis plugins exist, verify current ones.
- **Updaters:** `mvn versions:display-dependency-updates` /
  `versions:use-latest-releases`; `gradle dependencyUpdates` (beneficial
  plugin — typical); version-catalog projects update the catalog file once,
  not every module.
- **Registry query:** Maven Central search API; Gradle Module Metadata.
- **Verify chain:** compile → `dep:analyze` diff → full build (annotation
  processor breakage appears *here*) → tests.

## .NET

- **Detect:** `*.csproj`/`*.fsproj` + `*.sln`; `Directory.Build.props` and
  central package management (`ManagePackageVersionsCentrally` — the
  single-source-of-versions pattern, i.e. a catalog: redundancy = a project
  pinning what the central file already governs).
- **Source to scan:** `.cs`/`.fs`; `.csproj` itself (`PackageReference`);
  `global.json`; EF migrations folder.
- **Implicit proofs:** analyzers/source-generators (`*.Analyzer`,
  `*.Generator` packages — build-time, no imports); EF Core design packages;
  NativeAOT/trimming-sensitive libs; satellite-resource packages.
- **Native / updaters (typical):** `dotnet package search`; `dotnet-outdated`
  tool for the report; `dotnet add package X --version` to apply; restore =
  `dotnet restore`.
- **Verify chain:** restore → `dotnet build` (analyzers/generators fail here)
  → `dotnet test`.

## Ruby & Elixir (compact — same six questions apply)

- **Ruby:** `Gemfile`/`Gemfile.lock`; implicit = Bundler groups (test-only
  gems), railtie/middleware auto-activation (metadata-discovered), native
  extension gems (compile-time class); detector: `bundle-audit`-class /
  per-gem usage greps; updater: `bundle outdated` (report) → `bundle update
  <gem>` (apply, group-semver aware); verify = `bundle install` →
  `rubocop`-static → `rake test`.
- **Elixir:** `mix.exs`/`mix.lock`; implicit = application-level
  `extra_applications` deps (boot, never imported), compilers/plugins in
  `mix.exs`; updater: `mix deps.update --all` / `mix deps.audit`; verify =
  `mix deps.get` → `mix compile --warnings-as-errors` → `mix test`.

## Anything not listed

Work the six questions like any other ecosystem: where the manifest lives,
what text-proves usage, what *installs-are-uses* mechanisms exist (plugin
discovery is the universal trap class), which native tidier/updater the
community uses (search — don't remember), what the registry queries look
like. Prefer the ecosystem's own `tidy`-class command if it has one — Go and
Bundler prove several ecosystems already solved pruning natively. Add the
ecosystem to this file after the first real run, with verification labels
honest.
