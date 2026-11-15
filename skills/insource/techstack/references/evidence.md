# Ground every judgment: current version + real-world proof

Two failures silently corrupt a recommendation, and both look like reasoning while they are actually guessing:

1. **Judging a stale version.** The agent states what a candidate can or cannot do based on how it behaved in training data, an old blog post, or a comparison written two releases ago. The capability may have been added, removed, or reworked since. A "no" that was true last year is a wrong "no" today, and it can eliminate the right candidate.
2. **Declaring a capability awkward without looking for proof it is done.** The agent infers "relationships are awkward here" or "this needs a workaround" from the shape of the API, while a real production application is doing exactly that thing. The inference is not evidence; the real application is.

This reference is the discipline that prevents both. It applies in **both modes**, at Step 0 (verification) and whenever a capability claim is made in Step 3/4 or in the capability matrix (`capability-matrix.md`). It is not optional polish — a recommendation built on stale-version or unproven negative claims is not verified, however confident it sounds.

## Part 1: Find the actual latest version, then judge against it

**Never state a capability from memory of a version. Pin the claim to the candidate's current latest stable release, found from an authoritative source, and verify the capability against *that* release.**

### Find the latest — actually look, do not recall

For each serious candidate, reach the source that authoritatively states its current release. The source depends on the ecosystem; these are illustrative reaches, not a closed list — use whatever is authoritative for the candidate at hand:

- **The package registry native to the ecosystem**, which usually exposes a machine-readable "latest" record — for example the npm registry JSON (`/ <package>` → `dist-tags.latest`), PyPI's JSON API (`/pypi/<package>/json` → `info.version`), crates.io, NuGet, the Go module proxy, pub.dev, Packagist, Maven Central. A registry query returns the real current version, not a remembered one.
- **The project's releases / tags page** on its repository host, when the tool is not on a registry or to confirm the registry matches the source of truth.
- **The official changelog / release notes / release blog**, which also tells you *when a capability changed* — the fact that corrects stale memory.

Record three things per candidate: the **version number**, its **release date**, and the **source URL**. This triple is the anchor for every capability claim about that candidate and the honest content of the recommendation's "Verified as of" line.

### Stable vs pre-release

Pin to the latest **stable** release by default. If the newest version is a release candidate, beta, or nightly, say so and do not silently credit its unreleased capabilities to the stable product. If a capability the project needs exists *only* in an unreleased version, that is a real finding: name the version it lands in and the risk of depending on it, rather than counting it as available today.

### Judge against that version, and correct the record

- Verify each capability against the **current** docs and changelog for the pinned version — not a cached summary, not an old comparison article.
- When a capability was **added or changed recently**, the changelog says so. That is precisely where memory and old "X vs Y" posts are wrong; flag the correction explicitly ("this was added in `[version]`; older comparisons that say it is missing are out of date").
- A capability claim whose only source predates the pinned version is **unverified** until re-checked against the current release. Re-check it or mark it unknown — do not carry it forward as fact.
- If the latest version cannot be established (no registry, no releases page, docs silent), say so plainly and lower confidence; do not substitute a remembered version number.

## Part 2: Real-world proof before any negative capability judgment

**Before calling a capability awkward, limited, impractical, workaround-heavy, or impossible in a candidate, search for real-world evidence that it is done in practice.** A negative capability claim is a strong claim — it can disqualify a candidate — so it carries a burden of proof that an inference from API shape does not meet.

### What counts as real-world proof

Look for the capability actually exercised by real users, not described in marketing:

- a real application or open-source project that does the thing (a `[real app]` built on the candidate, whose repo or write-up shows the capability in use),
- a case study, production user story, or "built with `[candidate]`" showcase,
- a conference talk, engineering blog, or detailed Q&A thread where someone reports doing it in production, with the mechanism they used.

Search the capability plus the candidate plus terms like "example", "built with", "case study", "in production", "real world", and the ecosystem's own showcase tags. The proof must be **version-pinned** too (Part 1): a `[real app]` on an old release proves the capability class exists, but check whether the current release still works the same way.

### What the proof changes

- **If a real application does the thing, the capability is proven possible.** The honest claim is no longer "awkward / impractical / no" — it becomes "**possible — proven by `[real app]`; the cost is `[specific mechanism]`**." Record both the proof and the actual mechanism cost. A real app doing it does not make it *easy*; it makes it *possible*, and the remaining question is the cost, which you now describe from evidence instead of inferring.
- **A disqualifying "no" in the capability matrix must pass this check before it is allowed to eliminate a candidate.** If real apps do the thing, flip the cell to a qualified yes and write the mechanism. A false "no" is the exact failure that wrongly drops a viable option.
- **Absence of proof is not proof of absence.** If no real-world example surfaces, say "no production example found" — that is weaker than "impossible", and the cell should read as unproven/unknown rather than a hard no, unless the docs or source affirmatively rule it out.
- **Ground positive claims too.** A "yes" rests on the current docs plus, where it exists, a real user — not on the candidate's own feature page alone. Marketing says everything is supported; the mechanism and a real user say how.

### The shape of the corrected claim

> Before: "`[candidate]`'s relationships are awkward; you cannot really do joins."
> After: "Possible — `[real app]` (a `[kind of app]` on `[candidate]` `[version]`) does relational queries in production. The mechanism is `[how]`, and the cost is `[what is harder than in a full SQL engine]`. Verified against `[version]`, `[date]`, `[source]`."

The second claim is usable: it keeps the candidate alive, names the real cost, and is checkable. The first is a guess that could have eliminated the right answer.

## How this feeds the rest of the skill

- **Step 0** (`process.md`): the version triple and the real-world check are part of verifying each candidate, not a separate later pass.
- **The capability matrix** (`capability-matrix.md`): every cell is a version-pinned, evidence-grounded yes/no; every disqualifying "no" has passed Part 2.
- **Mechanism** (`dimensions.md` §Mechanism): real-world proof and the public source record are how a mechanism is established; this reference supplies the version pin and the proof burden that mechanism probing assumes.

A worked illustration of both failures and their correction — including a real application overturning an "awkward" verdict — is in `examples/capability-matrix-example.md`. It is illustrative; verify any named tool fresh before repeating it as current.