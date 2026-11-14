# Decision Spectra — Universal Structural Trade-offs

## Contents
- How to use this file
- Repo boundary: single repo ↔ many repos
- Deployable boundary: what gets its own top-level slot
- Shared-ground threshold: when a decision earns a dedicated home
- Cross-engine query/decision duplication
- Test-tree organization
- Isolation cost: when process/container isolation earns its keep
- Naming: role vs. type

---

## How to use this file

None of the spectra below have a fixed correct point in the abstract. Each one is a line between two valid extremes, and where a given project should sit on it is answered by that project's evidence — **and a stated requirement is the strongest form that evidence can take.** If the user has already said, in their own words, where a project sits on one of these spectra (a specific deploy platform, a language constraint, a scope boundary), that statement resolves the spectrum outright for this project; the spectrum stops being a question to weigh and becomes an answered one. The spectra exist for the cases evidence is inferred, incomplete, or silent — not to be re-litigated against something the user already settled. See `principles.md`'s requirement-fidelity check.

This is the shared reasoning every agenda folder points back to — an agenda's job is to say how a specific ecosystem's idiom expresses a chosen point on a spectrum, never to re-derive whether the spectrum itself is real. If an agenda's `index.md` is re-explaining *why* a shared package is sometimes warranted, that reasoning drifted out of its single ground and belongs back here.

---

## Repo boundary: single repo ↔ many repos

**The spectrum.** One repository holding every deployable and shared package, versus separate repositories per deployable, versus something in between (a repo per team boundary, a repo per release cadence).

**What moves a project along it.** Shared-decision surface area pulls toward one repo — the cheaper it is to share a decision (an import vs. a published, versioned dependency), the more single-ground stays mechanically enforceable rather than aspirational. Independent release cadence, independent ownership (separate teams meant to be decoupled on purpose), or a piece that's a standalone product in its own right (published for consumption outside this project) pull toward separate repos.

**What this is not about.** Team size, company convention, or which is currently fashionable. A one-person project and a fifty-person org both ask the same question: does anything here need to share a ground truth with anything else, and how much does drift between them cost if they don't.

---

## Deployable boundary: what gets its own top-level slot

**The spectrum.** A structure where every unit that runs as an independent process gets a distinct top-level location, versus a structure where things are grouped by domain/feature regardless of what actually deploys independently.

**What moves a project along it.** The deployable-boundary end wins whenever "what changed" and "what needs redeploying" need to map cleanly — the fewer surprises about blast radius, the better. A useful invariant-level test, independent of any specific ecosystem's folder names: *if this unit were deleted, does something stop being deployable, or does something merely stop compiling?* The former belongs at the top-level "runs independently" tier; the latter belongs at the "gets imported" tier, no matter how large or central it feels.

**What this is not about.** Size or perceived importance. A small independently-deployed worker still belongs at the top-level tier; a large, heavily-used library that nothing runs on its own still belongs at the imported tier.

---

## Shared-ground threshold: when a decision earns a dedicated home

**The spectrum.** Every decision (a threshold, a validation rule, a computation) implemented locally where it's first needed, versus every decision immediately extracted to a shared, single-owner location the moment it's written.

**What moves a project along it.** The threshold is duplication of a *decision*, not duplication of *code*. Two independently-implemented pieces of code that happen to look similar is usually harmless, sometimes even desirable for decoupling. Two independently-implemented answers to the same business question — a threshold, a scoring rule, an eligibility check — is dangerous, because each answer can look locally correct and still silently diverge from the other. The extraction earns its cost the moment a second consumer needs the *same answer*, not the same code shape. Extracting before that point is complexity added on spec, justified by nothing in evidence yet.

**The exception worth naming precisely.** A single-consumer decision that is nonetheless fragile or high-stakes (a financial rounding rule, a security-relevant check) can justify isolation into its own module even with one consumer today — but the justification there is *isolation for scrutiny and testability*, a different reason than *preventing drift between two consumers*. Don't collapse the two justifications into one just because the resulting file placement looks the same.

**The over-correction to watch for.** "Everything must be shared" is the same reflex as "nothing should be shared," just pointed the other way — both skip the actual question, which is whether *this specific* decision has (or will soon have) more than one place that needs to agree with it.

---

## Cross-engine query/decision duplication

**The spectrum.** The same logical operation (a filter, a delta-pull, a sort) hand-implemented separately for each storage engine or client it needs to run against, versus expressed once as a small typed intermediate form and compiled per engine.

**What moves a project along it.** This is the shared-ground threshold applied specifically to query semantics — worth calling out on its own because "query code" doesn't read as a business decision the way a threshold does, so it tends to get hand-duplicated per engine without triggering the usual instinct to extract it. The moment two engines need to agree on what "the same query" returns, that agreement becomes exactly the kind of decision that drifts silently: each dialect's hand-built version looks locally reasonable, and nothing catches the divergence except a test built specifically to compare their outputs.

**What earns the extraction.** More than one storage engine or client genuinely needs to agree on the same logical operation's result, for the lifetime of the system — not "we might add a second engine later." If there's exactly one engine and no credible second one coming, this is complexity added on spec; hand-write the query directly.

---

## Test-tree organization

**The spectrum.** One flat test directory (or tests co-located per source file with no higher grouping), versus a test tree grouped by *what kind of thing each test protects* — interface agreement between independently-deployed pieces, correctness of a single decision, agreement between engines on the same logical operation.

**What moves a project along it.** A contract test (does this process's output match what the consuming process expects) and a unit test of a pure computation are protecting fundamentally different kinds of failure, and a flat structure erases that distinction. The grouped structure earns its cost once there's more than one deployable (contract tests become meaningful) or more than one engine/client that must agree (differential tests become meaningful). Below that scale, co-located unit tests are enough — don't create empty scaffolding for test categories that have no members yet.

---

## Isolation cost: when process/container isolation earns its keep

**The spectrum.** No isolation beyond the language runtime's own process model, versus full container-level isolation for every deployable.

**What moves a project along it.** Isolation is justified by a specific, checkable fact: multi-service local development that needs reproducible, coordinated versions across services (a database, a queue, an app, running together); a deploy target that specifically requires the isolation mechanism; a need to guarantee parity between development and production environments at the OS level. It is not justified by "this is what serious projects have." When a deploy target already builds directly from the project's own manifest/lockfile, adding a second build description (a container definition) doesn't add safety — it adds a second authority for how the build happens, which is itself a shared-ground violation: now there are two places that must agree on the build, and nothing stops them from drifting.

**What this is not about.** Perceived professionalism. The presence or absence of container tooling says nothing about a project's seriousness; it says something about whether the project's deploy mechanism and local-dev needs specifically call for that isolation mechanism.

---

## Naming: role vs. type

**The spectrum.** Naming a unit's home after *what kind of thing it is* (its implementation category — a component, a helper, a utility, a controller), versus naming it after *what role it plays in the composition* (what decision it owns, what it computes, what it decorates, what it validates).

**What moves a project along it.** This isn't really a spectrum with two defensible ends — role-based naming is close to a hard invariant, because type-based naming survives exactly until the type stops being the interesting fact about the thing. A folder named for its type (`utils/`, `helpers/`, `common/`) is where things go when nobody was forced to answer what the thing's role actually is — which is precisely why those folders tend to accumulate unrelated content: they were never organized around anything to begin with. A folder named for its role stays meaningful even as its implementation changes underneath it.

**Where this connects to a specific failure pattern.** An asymmetric ownership relation (X exists only because Y exists — a decoration that belongs to one specific component, not to components-in-general) rendered as two type-based siblings (both under a folder named for what they *are*, "components") hides the relationship entirely, because both satisfy the type label equally well. Naming by role forces the ownership question to be answered explicitly, because "what does this belong to" is part of stating its role.
