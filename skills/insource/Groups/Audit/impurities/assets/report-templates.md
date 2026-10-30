# impurities — report templates

Copy into the project's convention if one exists; otherwise the reference
layout is:

```text
impurities/
  iteration-01/
    findings.md
    remediation.md
  iteration-02/
    ...
  summary.md
```

Keep reports concise enough to review and complete enough to reconstruct
the work. Never let a report claim more verification than actually happened.

## findings.md (written BEFORE fixes are applied)

```markdown
# Iteration <NN> — findings
Objective: <impurity type sought>     Scope: <components/behaviors covered>
Date: <YYYY-MM-DD> · agent: <main / sub-agent id + assigned slice>

## F-<NN>-<n>: <short title>
- **Classification:** confirmed defect | suspected defect | optimization
  opportunity | unresolved question
- **Description / observed behavior:** <what happens, concretely>
- **Affected:** <files, components, behaviors>
- **Root cause:** <established cause, or "not yet established">
- **Conditions:** <when it occurs — platform, config, load, timing>
- **Impact & severity:** <what it costs; blast radius>
- **Evidence:** <paths, command outputs, profile numbers, reproduction
  steps — each claim traceable>
- **Confidence:** <high/medium/low + why>
- **Recommended remediation:** <approach, expected change surface>

<Repeat per finding. Include a final "Negative results" section: what was
investigated and found clean, or suspicions that evidence killed — absence
of findings in an area is itself reportable work.>
```

## remediation.md (per iteration)

```markdown
# Iteration <NN> — remediation
Date: <YYYY-MM-DD> · commits: <hashes on the working branch>

## R-<n> — <fix title>  (resolves F-<NN>-<n>)
- **Change:** <what was modified and how it addresses the root cause>
- **Behavior preserved:** <implicit requirements checked before/after>
- **Verification:** <methods run; for performance changes state baseline →
  after with numbers; note anything NOT verified and why>
- **Final state:** fixed-and-verified | fixed-incompletely-verified |
  investigated-not-reproducible | confirmed-unresolved | deferred
  (<scope/authorization reason>) | determined-not-a-defect

## Shared-root-cause note
<Where several findings produced one coherent fix, link all of them.>

## Plan adjustments made from this iteration
<Added/split/merged/reordered iterations and the evidence that justified it.>
```

## summary.md (final)

```markdown
# Impurities — final summary
Project: <name/commit range> · branch: <working branch> · dates: <range>

1. **Investigation plan & iterations executed** — <table: iteration,
   objective, status, commits>
2. **Major defects and risks discovered** — <with severity; include the
   confirmed-unresolved ones, they are the honest headline>
3. **Changes implemented** — <grouped narrative or table>
4. **Verification performed** — <what was run vs reviewed vs blocked>
5. **Relevant commits** — <mapping iteration → hashes>
6. **Remaining findings & limitations** — <suspected/unreproducible/
   deferred items; environments or credentials that were unavailable>

Closing statement rule: this project was investigated responsibly and its
remaining uncertainty is reported — not "this project is defect-free",
which no honest report may claim.
```

## Sub-agent reports

When sub-agents investigate, give each its own findings/remediation file
named by scope (e.g. `iteration-03/concurrency-findings.md`,
`iteration-03/assets-remediation.md`); the parent deduplicates, resolves
overlaps, and writes the iteration-level truth. Parallel reports never get
concatenated without integration review.
