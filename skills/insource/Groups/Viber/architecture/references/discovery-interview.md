# Discovery Interview & Web Research Scripts

Full question scripts for the `architecture` skill's §3 workflow. When invoked, the agent inspects
the repository to formulate an initial hypothesis, engages the user with these targeted questions,
and runs targeted web searches for the chosen versions before authoring any specification.

### Step 1: Language & Compiler Hygiene
> *"I detect [e.g. TypeScript / C# / Python / Go]. Which target runtime version are we building for (e.g. .NET 10, Python 3.12, TypeScript 5.6)? Would you like to establish binding compiler flags (zero-warnings), typing rigor tiers, and defensive collection boundaries for this application?"*
- If confirmed:
  1. **Mandatory Live Research:** Perform search queries:
     - `"<language> <version> new language features and best practices"`
     - `"<language> <version> breaking changes compiler strict flags"`
  2. Consult `architecture/language/` to draft the specification.

### Step 2: Error Architecture & Failure Contracts
> *"How should failure contracts and diagnostics be shaped across this application (e.g. monadic Result types, typed domain exceptions, or hybrid contracts)? Who consumes them (end-user UI, APM logs, REST clients)?"*
- If confirmed:
  1. Consult `architecture/error/` to agree on contracts and payload structures.

### Step 3: Visual UI & Design Contracts (Activation Gate)
> *"Does this application feature a visual user interface (Web, Mobile, Desktop GUI)? Or is it a headless service / CLI / daemon?"*
- If visual UI:
  1. **Live Research:** Search for latest idioms in the UI framework (e.g. `"Next.js 15 layout server components"`, `"MAUI 9 desktop responsiveness"`).
  2. Consult `architecture/ui/` to draft layout stability, zero CLS skeletons, and bidi/RTL rules.
  3. Consult `architecture/accessibility/` to establish visual adaptation tiers (high contrast, warm-cream/slate presets), typographic personalization (multi-font, dyslexia-friendly fonts), cognitive density controls, and permission hygiene.
  4. Consult `architecture/display/` to set the surface-class pairing table - notation level (exact / grouped / compact / prose) per reader question, container budgets with fallback ladders, the Intl/ICU locale pipeline (numerals, separators, calendars, Arabic plurals, bidi isolation), and the voice-typeface coherence roster. Accessibility user-choices always override its defaults.
  5. Consult `architecture/media/` (imgery) to fix the media stack: format pipeline, declared LCP candidate and loading posture, space reservation, icon system + brand-mark sourcing ledger, fonts delivery, embed facade/consent policy, caching and budgets in metric units.
- If headless: skip UI, accessibility, display, and media architectures.

### Step 4: Relational Data & Database Standards
> *"Does this service interact with a database (PostgreSQL, SQLite, MySQL)? Would you like to establish Dumb-Store conventions, relational modeling strategies, and an application table reference?"*
- If confirmed:
  1. **Live Research:** Search for engine-specific best practices (e.g. `"PostgreSQL 17 performance UUIDv7 indexing"`).
  2. Consult `architecture/db/` to establish schemas and DDL standards.

### Step 5: Plugin & Settings Extensibility
> *"Does this application have a settings screen, configuration catalog, feature flags, per-tenant or per-platform preferences, or any extension modules? Should settings and plugins share one extension contract so adding the Nth item never edits shared code? Must extensions load at build time or after release?"*
- If confirmed:
  1. **Live Research:** Search for stack-specific patterns (e.g. `"<framework> plugin architecture dynamic loading"`, `"<platform> app store downloadable code policy"`, `"<framework> configuration descriptor pattern"`).
  2. Consult `architecture/plugin/` to run the Open/Closed growth gate, choose build-time versus runtime per axis, and draft descriptors, contributions, composition, scope and storage.
  3. When the product has settings but no third-party plugins, author `settings-architecture.md`; otherwise author `plugin-architecture.md`.

### Step 6: Multi-Platform & Multi-Form-Factor Scope
> *"Does this application target multiple operating systems (iOS, Android, Windows, macOS, Web) or form factors (phone, tablet, desktop)? Should we enforce View Barrels, zero `#if` conditionals in shared code, and multi-axis isolation?"*
- If confirmed:
  1. Consult `architecture/cross-platform/` to author decoupling and isolation specifications.
  2. Who may *know* the platform SDK behind a View Barrel is not this pillar's concern — follow up with Step 7 (Seams).

### Step 7: Seams & Third-Party Boundaries (Activation Gate)
> *"Which third-party capabilities does this app consume — frameworks, vendor SDKs, platform hardware APIs, generated API clients, service integrations? Which of them are named today outside one project-owned file? Should every capability pass through a seam you own, with import and markup walls keeping that claim true — 'date it, don't marry it'?"*
- If third-party capabilities exist (nearly always, except a dependency-free tool):
  1. **Live Research:** Search boundary idioms of the confirmed stacks: `"<framework> auto-import component resolution"`, `"anti-corruption layer <ecosystem> pattern"`, `"vendor lock-in adapter module <language> best practices"`, `"<platform> native module wrapper pattern"`.
  2. Consult `architecture/seams/` (read its `method.md` first) to author `seams-architecture.md`: the seam register, composition ladders, the two walls and the build-probe result, severity and baselines, the adopted-component intake ledger, exemptions, and the gates handoff.
  3. Reconcile with the other pillars: `cross-platform` barrels are framework seams; `plugin` extension points must pass the one-file swap test; `testing` fakes stand at seams (determinism points); `language` contract seams keep vendor types out of public APIs; every wall rule earns a `gates` register row or is marked advisory.
- If the app consumes no third-party code (rare, pure-stdlib): skip the seams architecture and record why.

### Step 8: Testing & Test Data Architecture
> *"How is the suite organized today, and what must it protect? Should we establish a size ladder and lane budget (hermetic by default, live opt-in), one fixture and generator vocabulary (`UserGenerator`, `SessionGenerator`), a single source of truth for test data under the No-String Rule, and conformance tests that make the project's documentation enforceable?"*
- Always applicable (every application has tests, even if the answer is "too few"):
  1. **Live Research:** Search for current idioms of the confirmed runner and assertion stack (e.g. `"<runner> fixture scope isolation"`, `"<language> property-based testing library"`, `"<framework> contract testing"`).
  2. Consult `architecture/testing/` to author `testing-architecture.md`: lanes and budgets, fixture lifecycle and isolation per resource, the generator registry with identity rules, the No-String Rule and its enforcement, determinism seams, and the conformance-test list.
  3. Reconcile with the other pillars: the `language` strictness applies to test code, `error` payloads are asserted not re-invented, `db` constraints are what generators must satisfy, `plugin` extensions each earn a test, `seams` are where doubles stand, and `cross-platform` dispatch lives in a platform lane.

### Step 9: Gates & Enforcement Architecture
> *"Which rules must be impossible to ship broken, and which are only advice? Where does each one get enforced - types, lint, a project contract check, a conformance test, a runtime guard, or review - and at which tier (pre-commit, pull request, merge, nightly)? Who owns the gate, what is its budget, and how does a failure get fixed or excepted?"*
- Always applicable (every application has a delivery path, even a manual one):
  1. **Live Research:** Search for current enforcement idioms of the confirmed stack and platform (e.g. `"<runner> fail closed exit code"`, `"<lint tool> baseline ratchet"`, `"<platform> branch protection required checks"`, `"<agent harness> completion hook exit code"`).
  2. Consult `architecture/gates/` to author `gates-architecture.md`: the enforcement ladder and the rung per rule class, the tier table with commands and p95 budgets, the gate register (rule → gate → tier → owner → evidence → exception), the fail-closed and exit-code contract, the baseline/ratchet policy, the suppression syntax, the agent contract, the bypass policy, and the inventory census.
  3. Reconcile with the other pillars: `testing` owns test design and conformance tests, while this pillar owns where they run, how long they may take, and what failing means; `language` owns types, while this pillar owns the zero-warning and type-escape gates; `error` owns the payloads that runtime guards and gate messages use; `seams` designs and arms its walls' rules, while this pillar registers where they bite; every binding rule in every other pillar must name a gate here or be explicitly marked advisory.
