# The five axes — what to actually look at, and the briefs

Review order within the Spec & Quality axis: **context → tests first →
implementation → verification**. Tests reveal intent and coverage
before the code can argue about it; a reviewer who reads tests first
reads the implementation knowing what "correct" means.

## Axis checks

### 1. Correctness — does it do what it claims?

- Matches spec/task requirements (quote the spec line per finding).
- Edge cases: null/empty/boundary values; error paths, not just the
  happy path.
- Off-by-one, race conditions, state inconsistencies.
- Tests exist and test the right things — behavior, not implementation
  details; would they catch a regression?

### 2. Readability & Simplicity — understandable without the author?

- Names clear and consistent with project conventions (`temp`, `data`,
  `result` without context fail).
- Control flow straightforward: no nested ternaries, deep callbacks,
  "clever" tricks.
- Fewer lines where fewer suffice — 1000 lines where 100 do the job is
  a failure; abstractions must earn their complexity (not before the
  third real use case).
- Comments only for non-obvious intent; never narrating obvious code.
- Dead artifacts: `_unused` vars, compat shims, `// removed` comments.
- **A new conditional bolted onto an unrelated flow is a design smell,
  not a nit** — push the logic into its own helper/state/policy.
- Repeated conditionals on the same shape = missing model or
  dispatcher; a "temporary" branch is usually permanent debt.

### 3. Architecture — does it fit the system?

- Follows existing patterns, or justifies the new one it introduces.
- Module boundaries intact; duplication that should be shared;
  dependencies flowing the right way (no cycles).
- Abstraction level neither over-engineered nor too coupled.
- **Does the refactor reduce complexity or relocate it?** Count the
  concepts a reader must hold; if the "cleaner" version keeps the count
  the same, it isn't cleaner. Prefer the shape where whole branches,
  modes, or layers *disappear* over one that re-centralizes the same
  logic. Prefer deleting an abstraction to polishing it.
- Feature logic leaking into shared/general modules: keep logic in its
  owning layer; reuse the canonical helper, not a near-duplicate;
  don't normalize architectural drift.
- Type boundaries explicit — question gratuitous `any`/casts and
  silent fallbacks that paper over an unclear invariant; making the
  boundary explicit often deletes the branching around it.

### 4. Security — what breaks if this is hostile input?

- Input validated and sanitized at boundaries; outputs encoded (XSS);
  queries parameterized, never string-concatenated.
- Secrets out of code, logs, version control, and artifacts.
- Authn/authz checked where needed; external data (APIs, logs, config
  files, user content) treated as untrusted until a boundary says
  otherwise.
- New dependencies from trusted sources, no known vulns (see
  `remedies.md` §dependency discipline).
- Deep security audits belong to the security-scan-style tooling —
  review flags suspicious patterns and says so rather than half-auditing.

### 5. Performance — what explodes at 10× the data?

- N+1 patterns; unbounded loops or fetches; missing pagination on list
  endpoints.
- Sync work that should be async; needless re-renders in UI.
- Large objects in hot paths.
- Quantify when possible: "this query adds ~50ms per list item" beats
  "this could be slow".

## Subagent briefs (Standards axis material lives in `smells.md`)

**Standards sub-agent** — prompt carries: diff command + commit list,
the standards-source file list, the smell baseline pasted **in full**
(the subagent has no other access to it), and this brief:

> Report per file/hunk where relevant: (a) every place the diff
> violates a documented standard — cite the standard (file + rule);
> (b) any baseline smell spotted — name it and quote the hunk.
> Documented-standard breaches can be hard violations; baseline smells
> are always judgement calls ("possible Feature Envy"), and a
> documented repo standard overrides the baseline. Skip anything
> tooling enforces. Under 400 words.

**Spec sub-agent** — prompt carries: diff command + commit list, the
spec path or fetched contents, and this brief:

> Report: (a) requirements the spec asked for that are missing or
> partial; (b) behaviour in the diff that wasn't asked for (scope
> creep); (c) requirements that look implemented but where the
> implementation looks wrong. Quote the spec line for each finding.
> Under 400 words.

If no spec exists, skip the Spec subagent and report *"no spec
available"* under its heading.

## Verification the review itself must check

- All **Critical** resolved; all **Required** resolved or explicitly
  deferred with justification and a filed bug.
- Tests pass; build succeeds; the verification story is documented —
  what changed and how it was proven (tests run, manual passes,
  screenshots for UI, before/after for performance).

## Presumptive blockers

Surface and propose the simpler design for each of these; escalate to
Required only when the change actively makes structure worse:

- a refactor that relocates complexity instead of reducing it;
- a change that pushes a file past a healthy size with no decomposition;
- feature logic added to a shared module;
- a near-duplicate of an existing canonical helper;
- a silent fallback hiding an unclear invariant.

## Red flags on the process itself

PRs merged without review; review that only checks tests; "LGTM" with
no evidence; security-sensitive change without a security pass;
"too big to review" PRs (split, don't squint); bug-fix PRs with no
regression test; unlabelled severity on comments; accepting "I'll fix
it later"; a refactor that moves code without reducing the concept
count; scattered new conditionals; bespoke helpers duplicating
canonical ones.

## Common rationalizations

| Says | Reality |
|---|---|
| "It works, that's good enough" | Unreadable/unsafe-but-working code is compounding debt. |
| "I wrote it, so I know it's correct" | Authors are blind to their own assumptions. |
| "We'll clean it up later" | Later never comes — require cleanup before merge, or a filed bug. |
| "AI-generated code is probably fine" | Confident and plausible — needs *more* scrutiny, not less. |
| "The tests pass, so it's good" | Tests don't see architecture, security, or readability. |
| "The refactor made it cleaner" | Relocated complexity isn't reduced: count the concepts. |
| "It's only a small addition to this file" | Small diffs still push files past healthy size and bolt branches onto unrelated flows. |
