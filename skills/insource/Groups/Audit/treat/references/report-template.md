# TREAT.md Report Template

Write the report to `TREAT.md` (project root or user-specified path). Use this exact section order. Keep language precise and diagnostic.

```markdown
# TREAT Report — <Tool or Tools>

**Mode:** Empirical | Physical  
**Scope:** <feature / module / project area>  
**Date:** <YYYY-MM-DD>

## 1. Tool Model Summary

For each tool under review:

- **Core concepts & terminology**
- **Paradigm / execution model**
- **Natural boundaries the tool expects**
- **Result / error model**
- **Official structural guidance** (quote or paraphrase primary sources)

## 2. Project Side Snapshot

- Current organization of the relevant area
- How the tool is currently imported and used (Physical) or how the area is currently structured (Empirical)
- Existing naming and module conventions that touch the tool

## 3. Diagnosis

### Respectful aspects
List what already aligns with the tool's model.

### Gaps and mismatches
For each mismatch:
- What the tool's model expects
- What the project currently does
- Why it matters (complexity, hidden concepts, mixed responsibilities, brittle usage)

### Over-structuring risks
Note any places where adding structure would be pure bureaucracy.

## 4. Recommendations

Only recommendations that restore or preserve respect for the tool's model.

For each recommendation:
- **What** to change (structure, naming, boundaries, explicitness)
- **Why** (link back to a concrete part of the tool model)
- **Proportionality** (smallest change that achieves respect)
- **Do not change** (explicitly list what should stay as-is)

Never include implementation patches or file edits. Describe the target shape only.

## 5. Decision Summary

| Concept / concern | Current state | Recommended action | Rationale |
|-------------------|---------------|--------------------|-----------|
| … | … | Keep / Adjust / Introduce | … |

## 6. Sources

Primary documentation and examples consulted.
```

## Writing rules

- Be concrete. Name files, modules, and concepts that exist or should exist.
- Prefer the tool's own terms over project-local translations when diagnosing.
- If the current structure is already respectful, say so clearly and keep the recommendations section short.
- Do not produce code diffs or apply changes. The report is the only deliverable.
