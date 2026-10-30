# Pre-delivery checklist

## Boundaries
- [ ] No application code, dependency, or project config was changed.
- [ ] Analyzers ran read-only; scratch output is outside the repo.
- [ ] Only the spec (or existing section) and, in Mode C, the report were written.
- [ ] No lint rule, hook, or CI gate was added.
- [ ] No secret value appears in the report, the spec, or a search query; generated/vendored/fixture paths were
      not treated as the project's own code.

## Scope
- [ ] Mode was chosen from the user's request, then existing docs, then default.
- [ ] A focused request was not widened into a full audit.
- [ ] No competing documentation was created.
- [ ] In Mode C, `/inquire` instructions were read first, and nothing was written to project docs before the user answered.
- [ ] If the audit was split across workers, their findings were re-verified against current files, and any
      sampling is stated as sampling rather than exhaustive coverage.

## Evidence
- [ ] Every finding names locations and separates measured from interpreted.
- [ ] Impact and confidence are rated separately, and confidence states what would raise or lower it.
- [ ] No low-confidence item became a finding or a rule.
- [ ] Intentional decisions (ADRs, comments) were checked before flagging.
- [ ] "AI slop" was used only for concrete, evidenced defects.
- [ ] Sources researched are cited in the methodology (Mode C), each with title, link, and the date it was read.
- [ ] A clean result is reported as a clean result: scope inspected and candidates rejected with reasons, no
      placeholder rules.

## Rules
- [ ] Every rule has Avoid, Instead, Applies when, Why it matters, Exceptions, Compliance check.
- [ ] Rules are specific, scoped, and checkable; none is a platitude.
- [ ] Every optional Example field holds a real before/after pair, labelled illustrative when it is not project code.
- [ ] Only user-selected recommendations appear in the final spec (Mode C).
- [ ] `python scripts/check_spec.py <file>` passes.

## Report (Mode C)
- [ ] Sections A to F are present and in order.
- [ ] Section E records both included and declined items.

## Reply
- [ ] Summary states what was investigated, what was written and where, limitations, and anything outside scope.
- [ ] Fix or enforcement requests are acknowledged and offered as a handoff, not performed.
