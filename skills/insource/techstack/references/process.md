# Tech Stack Recommendation — Full Process

This is the complete process for this skill. Read this in full every time the skill triggers — it is short by design so it can stay in context for the whole task.

## Core principles (non-negotiable)

1. **No recommendation from memory alone.** Never recommend a technology purely because it was strong, standard, or popular in training data. Ecosystems move fast — a library considered best-in-class a year ago may now be stagnant, superseded, or have a serious known issue; a newer option may have matured past what memory suggests.
2. **Popularity and "it works" are not sufficient justification.** Widespread adoption or general capability doesn't make something the right fit for a specific project. Every project has different requirements, and every problem has an appropriate tool — the right tool follows from the requirements, not from what most people choose.
3. **Requirements come before options**, and requirements include the *specific feature list*, not just the project category. This is the single most important part of the whole process — see Step 1.
4. **Multi-dimensional, balanced evaluation.** No technology is evaluated on a single characteristic. A technology can be an excellent recommendation despite being weak on a dimension that doesn't matter here, and a poor one despite being strong on a dimension that doesn't matter here.
5. **Honest trade-offs, always.** Every real recommendation carries a cost somewhere. State what is being given up, not just what is being gained.
6. **Existing-project awareness.** If there's an existing codebase/stack, understand exactly what kind of change is being asked for before proposing anything.
7. **The agent decides.** This skill's job is to think it through and land on an answer for the user, not to lay out a neutral menu of options and leave the decision to them.

---

## Step 0: Verify before recommending — always {#step-0}

Before naming any technology, verify its current state via search. Do not rely on how well-regarded, standard, or capable something seemed historically. At minimum, check per serious candidate:
- Current maintenance status and release cadence (is it still actively developed, or has it stagnated / been deprecated / superseded?)
- Recent significant changes (major version shifts, breaking changes, notable regressions, migration of the community away from it)
- Recent independent commentary/comparisons — is current sentiment consistent with what memory suggests, or has something shifted?

This applies to every candidate under consideration, not just the one being leaned toward — an option dismissed from memory as "too immature" or "not preferred" deserves the same current-state check as the frontrunner, since that judgment might also be stale. This is a multi-search task by design: run several targeted searches per serious candidate, not one generic search for the whole comparison. Under-researching a candidate defeats the purpose of this step.

This verification feeds a decision the agent is making on the user's behalf — it is not neutral research for the user to weigh themselves. Once verified, move to forming and stating an actual recommendation, not a side-by-side dossier.

---

## Step 1: Establish the project's actual priorities AND its specific features {#step-1}

Do not skip to recommending. Two separate things need to be established here, and neither substitutes for the other:

**A. Priorities** — what the project optimizes for (speed of delivery, native feel, long-term maintainability, cost, team skill fit, performance under a specific load, etc).

**B. The specific feature list** — not just "what kind of app/system is this" but the actual concrete list of things it needs to do. This is often the detail that actually decides the recommendation, more than the high-level project category. A feature can be:
- natively/easily supported by one technology,
- technically possible but awkward in another (requiring an extra layer, a plugin, a workaround, or non-trivial custom work),
- or effectively impractical in a third.

Pay close attention to every feature the user mentions, in passing or explicitly. See `feature-fit-examples.md` for worked examples of this pattern across mobile, web, and backend. When a named feature's difficulty across the candidate stacks isn't already obvious, research it the same way Step 0 requires — "does X support Y" is exactly the kind of claim that needs verification, not assumption.

### Finding this out: look before you ask

**Actively look for context before asking the user to repeat themselves.** Documentation, an existing codebase, specs, a design file, or earlier messages in the conversation may already state the priorities and/or the feature list. Check what's available (read files, search the existing project, re-read the conversation) before opening with questions — asking for information that's already discoverable wastes the user's time and signals the agent didn't look.

**If genuine gaps remain after checking available context, formulate targeted questions** shaped by the actual project in front of you — not a memorized checklist. See `question-method.md` for the underlying method: it teaches the universal axes to check (dominant constraint, concrete capabilities, existing footprint, scale, team/ops reality, hard constraints) and how to turn whichever ones are genuinely open into natural questions in that domain's own vocabulary, for any kind of project, including ones not anticipated in advance. Keep the question count reasonable (a handful of the highest-value ones, not an exhaustive interrogation). Prefer a structured choice tool when a short set of concrete options is natural (e.g. a timeline bracket, a priority ranking).

**If the user declines to give more detail or brushes past the questions**, don't block — fall back to a general, priority-labeled recommendation and say plainly that it's general because specifics weren't available. Example shape (for mobile):
- If the priority is fastest possible development: something like Ionic + Capacitor, because it lets a single web codebase ship across platforms with minimal native-layer work.
- If the priority is native feel: something like React Native or Flutter, which render true native (or near-native) UI components rather than running inside a WebView.

This example is illustrative of the *shape* of a good fallback (a small number of options, each tied to a named priority) — refresh the actual technology choices and their trade-offs via Step 0 before stating them, since these go stale too.

---

## Step 2: Existing-project awareness {#step-2}

If the project already has code and an established stack, do not propose a stack in a vacuum — the best technology for a greenfield project is not necessarily the best choice inside an existing architecture. First determine what kind of change is actually being asked for:

- **Replace/update the existing stack** — a full or partial migration; evaluate against the existing codebase's constraints (migration cost, team retraining, data/API compatibility), not just greenfield criteria.
- **Add a new part to the existing project** — e.g. a new service or module — evaluate for fit within the existing architecture (can it interoperate cleanly, does it introduce redundant tooling, does it fight existing conventions).
- **Add a new, mostly-separate application** — e.g. a companion mobile app for an existing web backend — more freedom exists here, but still weigh integration points (shared auth, shared APIs, shared data models) against the existing stack.
- **Add a new feature** — often best served by staying within the existing stack unless there's a concrete reason it can't reasonably support the feature; don't recommend a new technology for a feature the existing stack can already do well.
- **Something else** — the ask may not cleanly fit any of the above (e.g. spinning out a shared library, evaluating a build-tool swap, adding a data layer). Don't force it into one of the four categories above if it genuinely doesn't fit — identify what's actually being changed and apply the same underlying question: does this need to work *with* the existing stack, or is it independent of it?

If it's unclear which of these applies, ask — the right technology answer genuinely differs across these cases, and guessing wrong wastes the whole exercise. Once clear, fold this context into Steps 1, 3, and 4 as just another set of priorities/constraints/dimensions.

---

## Step 3: Identify the dimensions that matter here {#step-3}

See `dimensions.md` for the full checklist (ecosystem, maintenance, API design, abstraction level, quality, performance, fit-to-requirements, design/architecture, user-specific dimensions) and guidance on when each one matters.

Not every dimension applies to every kind of decision, and not every dimension matters equally for a given project — weigh the ones this project's priorities (Step 1) actually make relevant. State which dimensions are driving the recommendation, so the reasoning is visible rather than asserted.

---

## Step 4: Weigh, decide, and present trade-offs honestly {#step-4}

This is where the agent does the actual thinking — weighing dimensions against each other and against this project's priorities and feature list to reach its own conclusion, not compiling a balanced write-up for the user to decide from.

- Do not let a single strong dimension (popularity, familiarity, "industry standard" status) override an otherwise-poor fit — and do not let a single weak dimension disqualify an otherwise strong fit if that dimension doesn't matter here.
- Reach an actual recommendation — a clear judgment, not just a list of considerations. Lead with it plainly ("Given what you've described, X is the right choice here") rather than making the user extract a decision.
- State explicitly what is being traded away by the recommendation. Naming a downside is part of the deliverable, not an optional caveat. Example: recommending Ionic/Capacitor for speed means naming the cost plainly — it runs inside a WebView rather than compiling to fully native UI, so the app won't have a fully native feel, and anything requiring deep native/hardware access may need plugins, workarounds, or extra native-layer work rather than being natively supported.
- If a specific feature the user mentioned is hard, awkward, or requires an unusual workaround in the recommended technology, say so directly rather than glossing over it.
- A close call is the one case where naming multiple real contenders is appropriate — and even then, don't stop at listing them: say which way the evidence leans and exactly what fact or priority would settle it, so the response still ends in guidance rather than an open question handed back to the user.

---

## Anti-patterns to avoid

- Recommending a technology because it's popular, standard, or well-known, without connecting that to this project's actual stated priorities
- Skipping requirements-gathering (Step 1) and jumping straight to a recommendation
- Treating the high-level project category as the whole picture and ignoring specific named features
- Not looking for available context before asking the user to repeat information
- Presenting a technology's strengths without its trade-offs, or vice versa
- Judging a candidate on one dimension and ignoring the rest
- Treating memorized knowledge about a technology's maturity/quality/popularity as current without verifying it (Step 0)
- Proposing a stack for an existing project without first clarifying what kind of change is wanted (Step 2)
- Asking an exhaustive, generic checklist of questions unrelated to the specific type of project being built, or reciting a memorized question list instead of formulating questions fresh from `question-method.md`'s axes
- Silently blocking on missing information instead of falling back to a clearly-labeled general recommendation when the user declines to elaborate
- Producing a neutral side-by-side comparison and leaving the actual choice to the user when the user asked for a recommendation
