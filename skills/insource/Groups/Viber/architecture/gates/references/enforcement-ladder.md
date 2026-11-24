# The Enforcement Ladder

A rule can be enforced at six places. They differ in what they can see, how fast they run, how
often they are wrong, and who pays when they fail. Choosing the rung is the first design decision of
a gate, and choosing it badly is why teams end up with a review checklist that checks import order
while the type errors pile up.

The ladder is ordered by **distance from the author**, not by prestige:

```text
0  types            the value cannot be written
1  compiler + lint  the syntax or AST is rejected
2  contract check   the project-specific pattern is found
3  conformance test the cross-file fact is asserted
4  runtime guard    the bad value is stopped at the boundary
5  review           a person notices
```

The rule is simple: **use the earliest rung that can see the fact completely**. "Completely" is the
hard word. A type can see a shape but not a string literal; lint can see a string but not a design
token's meaning; a project check can see a token but not whether the catalog is complete; a test can
see the catalog but not the value that arrives in production. When the earliest rung can be escaped,
you do not abandon it — you add the rung that covers the escape.

---

## 1. Rung 0 — Types

The type system is the only rung that prevents a value from existing. Everything else detects a
value after someone wrote it. That asymmetry makes types the cheapest gate per violation and the
most expensive one to retrofit.

What types are good at:

- **Illegal states.** `type Session = { kind: "anonymous" } | { kind: "authenticated"; userId: UserId }`
  makes "authenticated without a user" unrepresentable. A boolean pair (`isLoading`, `isError`) can
  represent four states, one of which is nonsense (`loading` and `error` at once); a union can
  represent exactly the real ones.
- **Identity.** Branded or nominal types (`UserId`, `TenantId`, `OrderId`) stop a function from
  accepting the wrong string. In TypeScript, `type UserId = string & { readonly __brand: "UserId" }`;
  in Python, a `NewType`; in Go, a defined type; in Rust, a newtype.
- **Exhaustiveness.** A discriminated union plus an exhaustive switch turns "we forgot the new
  status" into a compile error. Without it, the default branch silently absorbs the future.
- **Boundary parsing.** Parse, don't validate: `parseUser(json): User` at the edge, and the rest of
  the program receives a value it can trust. A cast (`as User`) is not parsing; it is a promise the
  runtime does not keep.

What types cannot see:

- string contents (`"#ff0000"`, `"localhost"`, `"ar"`), file names, and docs;
- cross-file architecture (who may import whom);
- catalogs and counts ("every route has a page");
- values that enter through `any`, `unknown` casts, reflection, or generated code;
- behavior under time, locale, network, and concurrency.

Use types when the rule is **"this combination must not exist"**. Do not use a runtime check for a
fact the compiler can prove, and do not use a comment for a fact a union can encode.

---

## 2. Rung 1 — Compiler Flags and Lint

This rung sees syntax and AST shape: unused names, forbidden calls, import order, complexity, naming
conventions, deprecated APIs. It is fast enough to run on save and precise enough to block a commit.

The most important configuration decision is not which rules to enable; it is what happens to
warnings. A warning is a finding that does not block, which means it competes with every other
warning for attention. One study of static-analysis warnings found that **35–91% were
non-actionable** across projects (Heckman and Williams; the figure is still the standard citation).
Google's response is instructive: aim to never issue a compiler warning — either enable it as an
error or do not show it. A codebase that tolerates 400 warnings has already trained everyone to
ignore the output, including the warning that mattered.

Practical rules:

- **Zero warnings at the boundary.** `-Werror`, `--max-warnings=0`, `-D warnings`, or the
  equivalent. If a warning is not worth failing on, delete the rule; do not keep it as decoration.
- **Ban the escape hatches, or count them.** `any`, `@ts-ignore`, `# type: ignore`, `eslint-disable`,
  `# noqa`, `//nolint`, `#[allow(...)]`. A ban with a reason-required exception is better than a ban
  with a silent comment. If a ban is too strict for the migration, ratchet the count down.
- **Keep lint out of semantics.** A lint rule that needs to know the design system, the route
  catalog, or the database schema is a project contract check wearing a lint plugin's uniform.
- **Formatting is not a gate.** Run the formatter and rewrite the file. A blocking check that says
  "this line should have been wrapped" spends trust on an argument a tool can end.
- **Scope is part of the rule.** A linter configured only for `src/**/*.ts` does not protect
  `scripts/`, `docs/`, `*.mdx`, SQL, or configuration. If the rule matters everywhere, the gate must
  see everywhere.

Use lint when the rule is **"this syntax or shape is forbidden"** and the fact is visible in one
file. Do not write a custom lint plugin for a project convention that changes with the design
system; that is rung 2.

---

## 3. Rung 2 — Project Contract Checks

This is the rung most projects are missing, and the one that catches the failures generic linters
cannot: raw design tokens, the wrong component primitive, an import that crosses an architectural
boundary, a hardcoded locale, a brand color outside the token module, an emoji in a README.

The check reads source (and often non-source files) and applies project-specific rules. Two
implementations dominate:

| Approach | Sees | Strengths | Weaknesses |
|---|---|---|---|
| **Source scan** (line/regex/string) | text, including docs, SQL, templates, config | trivial to write, fast, whole-repo | false positives in comments/strings; no context |
| **AST / structured parse** | element names, imports, call arguments, JSX props | context-aware, fewer false positives | parser per language, slower, more code |

Start with the source scan when the pattern is unambiguous (`#rrggbb` outside the token module,
`localhost` in a non-test file, `http://` in a production config). Move to the AST when context
matters (`<button>` as a JSX element, not the word "button" in a sentence; an import from
`features/*` inside `shared/*`, not a string that looks like a path). Do not build a parser for a
problem a line scan solves, and do not ship a line scan for a problem that needs to know whether
the token is in a comment.

This is the rung where **the rule lives outside the framework's release cycle**. A project can add
twenty contract checks in an afternoon without waiting for an ESLint plugin, a new compiler
release, or a vendor feature. The author's `chekr` project is a reference implementation of this
rung: plain JavaScript functions over source files, with a report contract that carries severity,
impact, a stable logical id, and occurrences. The lesson is not the tool; it is that the rule set is
a project asset, versioned with the project.

Design rules for rung 2:

- **Narrow the rule until false positives are rare at the blocking tier.** A contract check that
  cries wolf is worse than a missing check, because it teaches suppression.
- **Include the files the linter forgot.** Docs, README, SQL migrations, HTML templates, config,
  scripts, and generated-file headers. The Unicode-icon rule is the canonical example: an agent
  obeys "no icons in code" and writes one in the README, because the linter never looked there.
- **Give every finding a stable identity** (rule id + file + normalized context), so baselines and
  deduplication survive line drift. See
  [baselines-ratchets-and-exceptions.md](baselines-ratchets-and-exceptions.md).
- **Keep the check deterministic and offline.** A contract check that needs the network is a flaky
  gate with a dependency.
- **Version the rule set.** A rule change is a code change: review it, test it, and observe it
  failing before trusting the new version.

Use rung 2 when the rule is **"this project-specific pattern must not appear"** and a generic linter
cannot know the project's vocabulary.

---

## 4. Rung 3 — Conformance Tests

A conformance test reads the repository as data and asserts a fact that spans files: every route in
the router has a page, every table in the schema has a reference row, every documented setting
appears in the settings catalog, every binding rule in the architecture docs appears in the gate
register. This is the rung that makes documentation executable and turns "we have a catalog" into
"the catalog is complete."

Conformance tests are the executable form of an architecture fitness function: an objective,
automated measure of how well the system satisfies a characteristic. They are slower than lint and
should not run on every keystroke, but they are cheap compared with end-to-end tests and they catch
a class of drift no other rung can see:

- a new route added without its loading, error, or empty state;
- a new translation key added in one language only;
- a new table added without a generator default;
- a new gate added without an owner or an evidence date;
- a documented rule that no gate enforces.

Design rules:

- **Assert the census, not a sample.** "Every route" means enumerated from the router, not a
  hand-maintained list that drifts.
- **Have a sanity floor.** If the scanner discovers zero files because a path moved, the test must
  fail, not pass vacuously. `expect(files.length).toBeGreaterThan(50)` is not paranoia; it is the
  difference between a green suite and a green nothing.
- **Fail with file:line and the rule id.** A conformance failure that says "catalog mismatch" costs
  an investigation; one that says `settings/catalog: src/settings/registry.ts:42 missing "theme"`
  costs a fix.
- **Keep them in the same language as the project.** A conformance test that needs a second runtime
  is a gate with a second failure mode.

Use rung 3 when the rule is **"these facts must agree across files"**. Do not use an end-to-end test
for a fact a repository scan can prove, and do not use a conformance test for a behavior that
requires the application to run.

---

## 5. Rung 4 — Runtime Guards

Some facts only exist when the program runs: the shape of a request body, the tenant that owns a
session, the invariant that a payment is captured once, the permission check on a route. Types and
tests approximate these; the runtime is where the value actually arrives.

Runtime guards are not a substitute for static gates. They catch only the paths that execute, they
fail in production rather than at the boundary, and they are expensive to debug when the message is
poor. Their job is to **stop the bad value at the edge and fail loudly**, not to re-check what the
compiler already proved.

Design rules:

- **Parse at the boundary.** Validate the external payload once, produce a typed value, and pass
  that value inward. Do not scatter `if (!user) return` through the domain.
- **Fail with a domain error, not a crash.** The `error` pillar owns the payload; the guard raises
  it. A guard that throws a string is a guard nobody can handle.
- **Never swallow.** A `catch` that logs and continues turns a gate into a suggestion at runtime.
  If the operation cannot continue, stop it.
- **Assert invariants that would corrupt data.** Double capture, negative stock, a session without
  a tenant, a migration applied twice. These are worth a runtime assertion even when a test exists,
  because the test cannot prove the production path.
- **Guard the guard.** A runtime check that is disabled by an environment flag is a gate with a
  remote off switch; document who can flip it and why.

Use rung 4 when the fact is **"the value that actually arrived is valid"**. Do not use it to
re-validate constants the compiler knows, and do not use it as the only enforcement for a rule that
could be caught before deploy.

---

## 6. Rung 5 — Review

Review is the most expensive rung and the least reliable for mechanical facts. A person reading a
diff can judge naming, abstraction, product intent, and whether a test actually tests something.
A person reading 400 files cannot reliably notice a missing `aria-label`, a hardcoded locale, or a
duplicated type — and should not be asked to.

Use review for:

- **Judgment:** is this the right abstraction? does this belong in this module? is the feature
  correct?
- **Taste with a rubric:** naming, API ergonomics, error message tone, visual hierarchy.
- **Risk acceptance:** money, credentials, personal data, public contracts, migrations, destructive
  changes. These are the categories where a human decides, not because a machine cannot see them,
  but because the consequence is not reversible by a redeploy.
- **The residue:** the rules that genuinely cannot be automated. Mark them advisory, give them a
  review checklist, and revisit them quarterly — some become automatable later.

Do not use review for anything a script can check. Every mechanical item on a review checklist is a
gate that has not been built yet, and it is consuming the attention the judgment items need.

---

## 7. Choosing the Rung — Decision Table

| Rule class | Earliest complete rung | Why | Gate the escape with |
|---|---|---|---|
| Illegal state combination | 0 | the compiler can make it unrepresentable | — |
| Wrong id type passed | 0 | branding/nominal typing | lint on casts |
| External payload shape | 4 + 0 | only the runtime sees the bytes; parse produces the type | schema test + typed boundary |
| Forbidden syntax / unused name | 1 | AST, one file, fast | zero-warning policy |
| Project token or component substitution | 2 | project vocabulary; often JSX/AST | include docs/config; ban the primitive |
| Import / layer boundary | 1 or 2 | dependency graph or AST | generated/vendor exclusions |
| Whole-repo text rule (icons, secrets, forbidden URLs) | 2 | must see docs, SQL, config, scripts | scan scope test with a sanity floor |
| Catalog / route / schema completeness | 3 | cross-file census | sanity floor; fail on zero discovered |
| Behavior under time/locale/network | 3 + 4 | tests pin the seam; runtime validates | injected clock, pinned locale |
| Auth/session invariant | 3 + 4 | e2e proves the round trip; runtime enforces | e2e signup→refresh; route guard |
| Performance / accessibility budget | 3 (measurement) | needs a running build or page | budget in metric units, p75 |
| Migration safety | 3 + 5 | static diff check plus human approval | destructive-change detector |
| Naming, abstraction, taste | 5 / advisory | no objective oracle | rubric + quarterly review |
| "Is this the right feature" | 5 | product judgment | — |

The table is a starting point, not a verdict. The question is always: **what is the earliest place
that can see this fact without being fooled, and what is the cheapest way to make the escape
visible?**

---

## 8. Escapes — and How to Gate Them

Every lower rung has an escape. The escape is not a reason to skip the rung; it is a second rule.

| Escape | What it defeats | Countermeasure |
|---|---|---|
| `any`, `unknown` cast, `as` | rung 0 | ban or ratchet the count; parse at the boundary; `@ts-expect-error` with a reason |
| `@ts-ignore`, `# type: ignore`, `eslint-disable`, `# noqa`, `//nolint` | rung 1 | reason required; count ratchet; no file-level disables without approval |
| Generated code, vendor, minified bundles | rungs 1–3 | exclude explicitly, and gate the generator's output separately |
| Docs, README, SQL, templates, config | rungs 1–3 | include them in the scan scope, or accept that the rule is source-only |
| Dynamic import, reflection, string-built queries | rungs 2–3 | runtime guard + a conformance test on the registry |
| Cache / incremental scope | every rung | content + rule + tool version in the key; full scan above a diff threshold |
| Baseline / suppression | every rung | identity, expiry, owner, and a ratchet that shrinks |
| A gate the author can edit | the gate itself | protected paths, CODEOWNERS, protected pipeline configuration |

The practical test: **try to defeat the gate.** Add `any`, add a disable, move the file to `docs/`,
rename it, make the diff large, edit the config. If any of those passes silently, the gate is
incomplete.

---

## 9. The Two-Rung Rule

Important rules get two gates, not one:

- **A local rung** at T0/T1: fast, scoped to the changed file, ideally auto-fixing. Its job is to
  keep the author in flow and to make the boundary run unsurprising.
- **An authoritative rung** at T2/T3: full scope, no incremental lies, the same rule or a stronger
  one. Its job is to decide.

The local rung is a courtesy. The boundary rung is the gate. Teams get this backwards by making the
pre-commit hook the only enforcement, then discovering that hooks can be skipped, are not installed
on every machine, and do not run in the web UI or the agent's environment.

---

## 10. What Cannot Be Gated

Some rules should not be automated, and pretending otherwise produces a gate that measures the
wrong thing:

- **Novel design decisions.** "Is this the right abstraction?" has no oracle.
- **Product scope.** "Should this feature exist?" belongs to the product, not the pipeline.
- **Naming quality.** A linter can enforce a pattern; it cannot judge whether the name communicates.
- **Visual taste.** Contrast and spacing are measurable; "does this look professional" is a rubric.
- **Architecture fit.** A dependency rule can be checked; whether the new module belongs in the
  domain or the application layer is a review judgment.

Mark these **advisory** in the register, give them a review rubric and an owner, and revisit them.
An honest advisory row is better than a fake gate that everyone learns to ignore.

---

## 11. Worked Examples

### No raw color outside the token module

- **Rung:** 2, plus 1 if the project has Stylelint.
- **Why not 0:** a hex string is a valid string; the type system cannot distinguish it.
- **Why not 5:** 400 occurrences across TSX, CSS, HTML, and docs; review will miss them.
- **Gate:** scan every source and style file for `#rrggbb`, `rgb(`, `hsl(` outside `tokens/**`;
  exclude generated themes; report the nearest token when one exists.
- **Escape:** inline suppression with a reason; the brand-mark module is an approved exception.

### No raw `<button>` (use the design-system primitive)

- **Rung:** 2 (AST) or 1 if the lint stack supports `no-restricted-syntax` on JSX.
- **Why AST:** a regex also matches the word in a comment, a docs string, and a test name.
- **Gate:** JSX opening elements named `button`, `input`, `select`, `textarea` outside the
  primitive module. The primitive module is the only allowed home.
- **Escape:** the primitive module itself; generated form markup with a header comment.

### Import direction (`shared` must not import `features`)

- **Rung:** 1 or 2. Dependency-cruiser, `eslint-plugin-boundaries`, or a project check over the
  import graph.
- **Why:** the compiler does not know the architecture; a test that imports both sides proves the
  rule only for the tested path.
- **Gate:** every import specifier is resolved to a layer; `shared → features` fails, `features →
  shared` passes.
- **Escape:** none. If a shared module needs a feature, the abstraction is inverted.

### Default language hardcoded across files

- **Rung:** 0 for the type (`Language` union), 1 for the literal ban, 3 for the database fact.
- **Why:** the literal `"ar"` is legal; the problem is that it appears in twelve files and the
  translations table has no `default` column.
- **Gate:** one exported `DEFAULT_LANGUAGE`; lint bans the literal outside the config module; a
  conformance test asserts the translations table has exactly one default row.
- **Escape:** tests may pin a language explicitly; that is not a default.

### No Unicode icons anywhere, including docs

- **Rung:** 2, whole-repo text scan.
- **Why:** lint sees source only; the agent obeys in code and writes an emoji in the README.
- **Gate:** scan every tracked text file (code, Markdown, SQL, config, templates) for emoji and
  pictographic ranges; allow a tiny approved list (arrows in prose, if the project allows them)
  with a named exception file.
- **Escape:** the exception file, reviewed as a data change.

### Duplicate domain types

- **Rung:** 2 (cross-file AST) or 3 (a conformance test over exported type names/shapes).
- **Why:** the compiler allows two structurally identical interfaces; the duplication is a
  maintenance fact, not a type error.
- **Gate:** a check that reports exported type names with the same normalized shape in different
  modules, and a ratchet on the count.
- **Escape:** a declared equivalence (`type UserView = Pick<User, ...>`) is not a duplicate; a
  generated DTO is excluded by path.

### Signup → refresh → still signed in

- **Rung:** 3 + 4.
- **Why:** the bug is a session round trip, not a type; the runtime guard is what protects the
  route after the test passes.
- **Gate:** an e2e test that signs up, reloads, asserts the authenticated shell, and asserts the
  sign-in route redirects an authenticated user away.
- **Escape:** none; a skipped test is a failed gate.

### Ad-hoc toast bypassing the error catalog

- **Rung:** 2 (AST) + 3 (catalog test).
- **Why:** the code compiles and the toast looks fine; only the project knows the copy and severity
  must come from the catalog.
- **Gate:** ban direct calls to the toast primitive outside the notification adapter; the adapter
  accepts a catalog key, not a color and a string.
- **Escape:** a documented adapter exception for a third-party embed.

### Filters that affect the whole page

- **Rung:** 3 for ownership, 3 for one representative journey, 5 for the judgment.
- **Why:** "all widgets update" is partly a UX contract and partly a data-flow fact. A conformance
  test can prove that every widget reads the filter store; an e2e test can prove one dashboard's
  widgets all change; "the placement makes ownership obvious" is a design review item.
- **Gate:** the filter store is the only source for widget queries; the dashboard e2e asserts every
  registered widget reacts; the placement rule is advisory with a rubric.

### Timezone handling

- **Rung:** 0 for the branded instant, 1 for the banned call, 3 for the behavior.
- **Why:** both under- and over-application are mistakes. The rule is contextual: store UTC
  instants, render in the user's zone, use a local date only for a genuinely local event, and use a
  region/legal zone where the law requires it.
- **Gate:** domain code uses `Instant`, not `Date`; a lint ban on `Date.now()` in domain modules; a
  conformance test that the rendering layer receives a zone; a decision table in the doc for the
  exceptions.
- **Escape:** an explicit `LocalDate` type for a local event; an approved legal-zone exception.

---

## 12. Rung-Choice Anti-patterns

| The shortcut | Why it fails |
|---|---|
| Regex for a semantic fact | matches comments, strings, and generated code; false positives train suppression |
| AST for a style rule | a formatter should have rewritten the file |
| A cast where a parse belongs | the type says `User`; the runtime has a string |
| Runtime checks for what types can prove | noise in every path; the compiler was cheaper |
| Review for a mechanical fact | 400 files, 20 minutes, and the one that mattered is missed |
| A test for a compile-time fact | the test cannot run if the code does not compile; the type was the gate |
| A whole-program check at pre-commit | 90 seconds, then `--no-verify` |
| One custom lint plugin per project convention | plugin boilerplate and a release cycle for a rule that changes monthly |
| A rule enforced only in the prompt | a preference with good PR; the model complies until it does not |
| A gate that only scans `src/` | the icon in the README, the key in the SQL, the secret in the script |
