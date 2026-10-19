---
name: anti-patterns
description: Find and document evidence-backed anti-patterns in any software project. Inspect the actual codebase, research relevant patterns using reliable web sources and the bundled seed database, produce an editable checklist grouped by detected language, and turn user-selected items into project documentation with explanations and before/after diffs.
---

# Anti-Patterns — project-specific, evidence-first review

Run a broad, language-agnostic review to identify avoidable patterns that actually occur in the target project, then create a user-editable checklist and—only after user selection—a concise project wiki. This skill is not limited to tests, builds, deployment, or one technology. A pattern is a candidate, not a verdict: explain context, impact, and trade-offs, and accept a clean audit as a valid result.

## Contract and safety

- Inspect before judging. Database rows, web pages, static-analysis output, and familiar smells suggest searches; none prove a project instance.
- Every checklist finding must be supported by current, inspected project evidence. Cite repository-relative locations and explain the observable consequence. Do not present external references as evidence the code contains a pattern.
- Calibrate certainty and impact separately. Include a finding only when evidence and project context justify it; label severity and confidence using the rubric below. Avoid both speculative findings and false certainty.
- Review production source and project architecture broadly: boundaries, dependencies, data and state flow, resource lifecycle, errors, security, reliability, performance, maintainability, and language/framework idioms. Adapt to project context; do not force a concern where it does not apply.
- Preserve user work. Inspect destinations first. Never overwrite existing files or silently replace user edits. If a target exists, read and preserve it, then ask before merging or replacing when intent is unclear. Do not create a root `AGENTS.md` without permission.
- Audit is read-only unless the user explicitly asks for remediation. Do not modify source code as part of generating findings.
- Do not expose secrets in reports or excerpts. For a suspected credential, cite its location and type without reproducing its value; avoid broad scans or copying sensitive data into web searches.
- Respect repository instructions and excluded/generated/vendor/fixture areas. Do not send proprietary code to external services; web searches should use pattern concepts, not code excerpts or identifying project details.

## Workflow

### 1. Establish context and scope

1. Read applicable `AGENTS.md`, repository guidance, and relevant project documentation before scanning. Inspect the root structure and manifests/configuration to identify project purpose, active languages, frameworks, major components, generated code, vendored dependencies, fixtures, and known exclusions.
2. Establish practical scope from repository size. For large projects, sample the architecture and partition the review by non-overlapping components or concerns. Prefer targeted searches followed by opening and tracing the actual code; do not claim exhaustive coverage when only a sample was reviewed.
3. If there is no software source, explain what was inspected and offer an empty checklist or ask whether the user wants a different scope. A fresh project may legitimately have zero findings.

### 2. Discover and verify candidates

Use the adjacent `data.csv` as a compact discovery aid. Inspect its header and relevant rows; it is neither authoritative nor exhaustive. Search for structural indicators and trace behavior through callers, callees, configuration, and boundaries as needed. Search results and automated tools are leads only: open the relevant files, confirm the behavior, and consider intended design, mitigations, and counterexamples before including a finding.

If useful, research candidate concepts on the web. Search in a targeted way using the detected language/framework and the candidate pattern. Prefer primary specifications and official documentation for technical constraints, then maintainers' guidance, recognized books/papers, and reputable engineering sources. Verify the cited page supports the general claim; record title, URL, and access date. If sources disagree or applicability is uncertain, state that caveat. Do not copy another skill or checklist wholesale. If web access is unavailable, continue with code evidence and say that external research was unavailable rather than implying it was done.

Optional reference-skill review: if comparing existing Agent Skills is useful and a supported `skills` CLI is available, first inspect its current help/docs and use an isolated temporary directory outside the repository. Request only named skills, list before installing if the CLI supports it, and inspect downloaded `SKILL.md` files read-only. Do not install into the target project, modify agent skill directories, or claim skills were downloaded if only web pages were consulted. This comparison is optional and never replaces authoritative technical sources or code verification.

For each candidate, maintain a working evidence record:

- **Pattern:** stable, concise name; merge duplicate symptoms that share one cause or remediation.
- **Project evidence:** repository-relative file and line range, symbol, or short safe excerpt; for systemic claims cite multiple concrete locations or a traceable flow.
- **Why it matters here:** actual behavior/risk/cost and the relevant context; distinguish observed impact from plausible risk.
- **Severity:** `High`, `Medium`, or `Low`, based on project-specific consequence and reach—not how familiar or visually unpleasant the code is.
- **Confidence:** `High`, `Medium`, or `Low`, based on directness and completeness of evidence. Exclude low-confidence claims from the checklist; resolve them or mention them separately as unconfirmed questions only if useful.
- **Caveats:** intentional use, mitigating controls, acceptable trade-offs, or conditions that would invalidate the finding.
- **Sources:** optional verified external support for the general concept, never a substitute for project evidence.

### 3. Produce the editable checklist

Before creating a file, inspect whether `antipattern.md` already exists and check repository conventions for audit artifacts. Use the project root for `antipattern.md` unless the user or established convention specifies another path. If a file already exists, preserve it and ask before replacing or merging. Do not create it outside the target project.

Group findings under headings for each detected source programming language. Put genuinely cross-language, architectural, or repository-level findings in a `Shared / Architecture` section. Include only languages with findings; do not infer language solely from generated/vendor files. Every finding is exactly one bullet checkbox and includes title, description, severity, confidence, concrete code reference, and any relevant caveat/source. Keep it concise but specific:

```markdown
## Python

- [ ] **Swallowed errors** (`Medium`; confidence: `High`) — `service/client.py:42-49` catches a broad exception and returns success-shaped `None`, so callers cannot distinguish a failed request from an absent result. Caveat: none found. Source: [Python exception guidance](https://docs.python.org/3/tutorial/errors.html) (accessed YYYY-MM-DD).
```

Use repository-relative paths and real line ranges (or symbols where line numbers are unstable). Never make up line numbers, URLs, citations, severity, or impact. Avoid reproducing secret values. Every item uses `[ ]` initially; never preselect. For a zero-finding audit, state the reviewed scope, note that no evidence-backed anti-patterns were confirmed, and create no placeholder checkbox items.

After creating the checklist, stop and ask the user to select items by changing `[ ]` to `[-]` (the literal marker has a hyphen between the brackets), or to provide their selections directly. Explain that unmarked items will not be documented as selected. Do not proceed to selection parsing or wiki creation until the user responds or explicitly authorizes both stages.

### 4. Parse user selections

Re-read the checklist after the user's edit/response. Treat only a checkbox whose marker is exactly `[-]` as selected; `[ ]`, `[x]`, `[X]`, and other markers are not selections under this workflow. Match selected entries by stable title and evidence reference, not by line number alone. Preserve the user's text and markers. If an item was renamed, duplicated, or ambiguously marked, ask for clarification rather than guessing. If no item is selected, do not create a wiki of assumed choices; confirm that no wiki is needed or ask whether the user wants a general reference page instead.

### 5. Document selected patterns in project docs

Inspect existing documentation structure and naming conventions (for example, `docs/`, `doc/`, `documentation/`, or an established wiki). Choose the conventional location, not an arbitrary new folder. If no convention exists or several are plausible, ask the user where documentation belongs before creating it. Use an existing suitable anti-pattern page when safe; do not duplicate it. Ask before overwriting or merging conflicting existing content.

For every selected finding, document:

- **What it is:** a plain explanation of the pattern and why it is harmful or costly in this project's context.
- **Evidence:** verified code location(s), observed behavior, and limits of the claim; separate fact from inference.
- **How to fix:** a specific, practical remediation consistent with project conventions, including material trade-offs and any prerequisite decisions.
- **Before/after diff:** a small, idiomatic, language-appropriate diff that illustrates the fix. Base it on verified context where possible; otherwise label it explicitly as illustrative and do not claim it was applied. Preserve relevant behavior and avoid unrelated cleanup.
- **References:** meaningful source titles and URLs, with access dates when used.

Group wiki entries by the same language/shared headings when useful. Keep the checklist as the audit record and wiki as the selected-items guidance; do not silently rewrite checklist evidence. If documentation is created or updated, verify links and relative paths.

### 6. Link from root `AGENTS.md`

If a root `AGENTS.md` exists, inspect its conventions and add a concise link to the completed wiki without rewriting unrelated instructions. If none exists, ask before creating it unless the user explicitly authorized creation. Only add the link after the wiki exists, and verify it resolves. Do not add a reference for an empty or nonexistent wiki.

## Subagent use

For large projects, parallelize bounded, read-only audits by directory, component, or concern only when useful. If the `subagent` skill is available, read and follow it before delegation. Give each worker a non-overlapping scope and request candidate title, rationale, precise file/line evidence, caveats, confidence, and sources; prohibit edits and final inclusion decisions. Consolidate duplicates and independently verify every proposed item against current files. A subagent's conclusion is a lead, not accepted evidence.

## Completion checklist

- The reviewed scope and detected languages are explicit; coverage claims match work actually done.
- Each included finding has inspected project evidence, contextual impact, severity, confidence, caveats, and relevant language/shared grouping.
- External sources support general claims only, are verified, and are cited; unavailable research is disclosed.
- `antipattern.md` uses one `[ ]` bullet per finding, has no invented/duplicate claims, and handles zero findings honestly.
- Selection parsing recognizes only exact `[-]` markers and waits for the user's choices before documentation.
- Selected wiki entries explain what, how to fix, and a relevant before/after diff; examples are identified as illustrative when needed.
- Wiki location follows actual project documentation conventions; existing user content is preserved.
- Root `AGENTS.md` links only to an existing, verified wiki, and no source code was changed without authorization.

## Resources

- `data.csv` — seed taxonomy for discovery. Each row is a prompt to investigate, not a rule, diagnosis, or exhaustive catalog.