# Report Template

Use this structure for both outputs: the compact in-chat report (default) and the `TREAT.md` file (only when the
user asks). Same fields, same order; the chat version may omit sections that would be empty instead of pasting the
skeleton.

```markdown
# TREAT Report — <Tool or Tools>

**Scope:** <feature / module / project area>
**Date:** <YYYY-MM-DD>

## 1. Tools under review

| Tool | Installed version (lockfile) | Docs source and version used | Mode | Verdict |
|------|------------------------------|------------------------------|------|---------|
| …    | …                            | …                            | Empirical / Physical | fits cleanly / partial mismatch / significant mismatch |

No lockfile: say so, state the manifest range instead, and lower the confidence of every finding that depends on
the version. Mixed versions installed: report the migration as unfinished rather than picking a side.

## 2. Tool Model Summary

Per tool, from documentation **for the installed version or its major**:

- **Core concepts & terminology**
- **Paradigm / execution model**
- **Natural boundaries the tool expects**
- **Result / error model**
- **Official structural guidance** (quote or paraphrase; name the docs version it came from)

## 3. Project Side Snapshot

- Current organization of the relevant area
- How the tool is imported and used (Physical) or how the area is currently structured (Empirical)
- Existing naming and module conventions that touch the tool

## 4. Diagnosis

Per tool.

### Respectful aspects
What already aligns with the tool's model.

### Gaps and mismatches
For each finding:

- What the tool's model expects
- What the project currently does
- Why it matters (complexity, hidden concepts, mixed responsibilities, brittle usage)
- **Confidence:** high / medium / low — and the reason whenever lowered (indirect version evidence, no docs found
  for the installed major, code path only partially read)
- **Version note** when the mismatch is a previous-major idiom still in use, or a migration that stalled partway

### Over-structuring risks
Where adding structure would be pure bureaucracy.

## 5. Recommendations

Only what restores or preserves respect for the tool's model. Each one:

- **What** to change (structure, naming, boundaries, explicitness)
- **Why** (link back to a concrete part of the tool model)
- **Proportionality** (the smallest change that achieves respect)
- **Do not change** (what should stay as-is)

No patches and no file edits — describe the target shape only. If the structure already respects the model, say so
and recommend no change.

## 6. Decision Summary

| Concept / concern | Current state | Recommended action | Rationale |
|-------------------|---------------|--------------------|-----------|
| … | … | Keep / Adjust / Introduce | … |

## 7. Sources

Per tool: the primary documentation consulted, with its version and, where useful, the page.
```

## Writing rules

- **In chat, lead with the verdict per tool**, then the findings, then the recommendations. Omit empty sections.
- **`TREAT.md` only on request** — "save it", "export", "write TREAT.md", or a named path. It is the only file this
  skill may ever write.
- Be concrete. Name files, modules, and concepts that exist or should exist.
- Prefer the tool's own terms over project-local translations when diagnosing.
- State the reviewed version and the docs version per tool; when either is uncertain, say so and lower confidence
  rather than presenting a guess as fact.
- Do not produce code diffs, do not edit source, configs, lockfiles, or package files. The report is the deliverable.
