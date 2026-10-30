---
name: fix
description: After root-cause diagnosis with dbug, resolve the problem and improve the relevant implementation so the same or similar problems become easier to identify, understand, or prevent in the future. Use together with dbug whenever a problem has been understood and a fix is being applied. Covers immediate fix, local-context generalization, consequences, explicit and implicit references, and consistency. Not a standalone debugger.
---

# Fix

Dbug finds the root cause. Fix resolves it **and** leaves the system better equipped for the next similar problem.

These two skills are paired:
- Using dbug requires following with fix.
- Using fix requires having used dbug (or equivalent disciplined root-cause analysis).

The goal is continuous improvement: every properly fixed problem should make the affected implementation and its relevant surrounding context clearer, more consistent, and easier to diagnose next time.

## Scope of a fix (in order)

1. **Immediate problem**  
   Apply the minimal-but-complete root-cause fix identified by dbug. Make the bug structurally impossible where practical.

2. **Local context**  
   Inspect the surrounding implementation and equivalent instances that share the same pattern or block. Apply the same underlying correction when the relationship is clear (e.g. the same alignment issue in sibling cards, the same validation gap in sibling endpoints). Stay inside the relevant context; do not jump to unrelated modules.

3. **Consequences and dependencies**  
   Identify what becomes invalid, outdated, inconsistent, duplicated, or misleading because of the change. Update those artifacts.

4. **Explicit references**  
   Search for direct mentions of the changed concept (names, identifiers, keywords, values, regular expressions, symbols). Inspect and update what is affected.

5. **Implicit references**  
   Use conceptual understanding of the system to locate artifacts that depend on the changed behavior even when they lack an obvious textual match (policy documents, user-facing copy, configuration assumptions, related documentation, etc.).

6. **Consistency**  
   Ensure the change does not leave duplicated, contradictory, or outdated information elsewhere in the relevant context. Common examples include hard-coded values that represent the same concept under different names, outdated documentation, or configuration that no longer matches the new behavior.

Do not expand scope without a reasonable relationship to the original problem or the change being made.

## Forms of improvement

The improvement is whatever makes the next occurrence cheaper to diagnose or prevent. Examples (none is mandatory):

- More precise custom errors or exceptions that name the exact failure point and responsible component.
- Better logging, validation messages, or state handling.
- Clearer naming, structure, or separation of concerns in the affected block.
- Extraction or consolidation of duplicated hard-coded values when they represent the same concept (magic numbers are a common example that linters often flag).
- Updated documentation, terms, privacy statements, or configuration that would otherwise become false after the change.
- Structural changes that make the same class of defect impossible.

Choose the form that best serves future diagnosis and consistency; do not force exceptions, logging, or constant extraction when they are not the highest-leverage improvement.

## Incomplete-fix risks (examples)

A fix can still leave the system inconsistent. Typical signals (none is mandatory to chase in every case):

- The same meaningful value appears under different names or as a bare literal in multiple places.
- Documentation, policy files, or configuration still describe the old behavior.
- Sibling instances in the same contextual block still contain the original defect.

When any of these are reasonably related to the change, address them. Magic numbers are simply one frequent illustration of the broader consistency obligation.

## Relationship to other skills

- **dbug** — mandatory predecessor. Fix never starts without root-cause understanding.
- **test** — when the bug is reasonably testable, the regression test belongs with the fix (dbug already requires it).
- Do not use this skill for pure feature work or unrelated clean-ups.

## Anti-patterns

- Symptom patch that leaves the root cause intact.
- Fixing only the discovered instance while ignoring clear siblings in the same contextual block.
- Unjustified jumps to unrelated parts of the system.
- Leaving documentation, terms, or configuration that now state falsehoods.
- Leaving clear sibling instances of the same defect untouched.
- Treating “add a custom exception” or “extract every magic number” as the default answer for every problem.

For deeper guidance on context boundaries, consequence tracing, and search techniques see `references/`.  
For polyglot concrete illustrations see `examples/`.
