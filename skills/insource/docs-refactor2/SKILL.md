---
name: docs-refactor2
description: 'Execute a documentation SEPARATION the user specifies: concepts or systems documented together that must each exist independently get their own document, identity, scope, definitions, and constraints; their real relationship stays documented through accurate cross-references. The user decides what separates — never split extra concepts just because they look separable. Move content rather than rerewrite; each resulting document reads independently; no subject owns another''s full specification; meaning, terminology, and design rationale are preserved; ambiguities and contradictions are surfaced, not silently resolved. Follow project doc conventions, keep scope to the requested separation, validate for lost information, duplicated specs, broken links. Distinct from docs-refactor (reorganizing messy doc sets one-concern-per-file): use when the user names which concepts to pull apart. Triggers: separate these concepts, give X its own document, X shouldn''t live in Y''s doc, split this system''s docs out.'
---

# docs-refactor2 — the user names the seam, you execute the cut

**The user defines what must be separated; the skill makes the separation
happen.** Example shape: a framework document holds both the framework's
architecture *and* a state-condition system the framework uses — and the
user decides that system deserves its own documentation. Result: each
subject is independently defined with its own responsibilities, even while
they continue to interact. (Reorganizing a whole messy docs folder is
`docs-refactor`, a different job.)

## 1. Understand the requested separation

Before touching anything, establish exactly what the user wants split:

- the concepts/topics involved · where their documentation currently lives ·
  which content belongs to which subject · what each resulting document is
  expected to cover · which relationships should survive the split · any
  stated boundaries or constraints.

The user's instructions are the source of truth for the intended seam.
**Do not introduce additional separations because other concepts appear
capable of being split.** If the requested boundaries are unclear *and*
would materially change the result, ask — one precise question, not an
audit.

## 2. Execute the workflow (only the steps the task needs)

1. **Understand** — §1.
2. **Inspect** — read the relevant documents; locate every passage involved.
3. **Map** — decide which existing content belongs to each subject.
4. **Plan** — define the resulting documents and the changes that create
   them.
5. **Extract** — move relevant content into its independent document
   (moving, not rewriting from scratch, unless rewriting is required to
   give the subject a proper identity).
6. **Restructure** — update the original document to its new, narrower
   responsibility.
7. **Connect** — re-establish the relationships that still matter.
8. **Validate** — check for lost information, duplicated specs, broken
   links, inconsistent definitions.
9. **Report** — summarize what was separated, which documents changed, and
   anything unresolved.

Never expand scope without a reason.

## 3. Each resulting document's bar

Every separated subject's document must have: a clear identity; a defined
purpose and scope; its own relevant definitions and terminology; the rules
and behavior belonging to that subject; its own constraints and applicable
design decisions; enough context to be understood independently. When
several subjects are requested, each gets a clearly defined responsibility —
"its own document" is not the finish line, *independently readable* is.

## 4. What independence means (and doesn't)

Separation means neither subject is **conceptually owned** by the other's
documentation. In the framework/state-condition example:

- the state-condition document defines the system itself;
- the framework document explains how the framework *uses* that system;
- the framework doc does not need the system's full specification inside it;
- the system keeps its identity as the framework evolves around it.

Independence does **not** mean zero dependencies or interactions — their
definitions, responsibilities, and documentation are separated along the
user's boundaries while real coupling stays documented accurately.

## 5. Preserve necessary relationships

Keep what still matters after the cut: dependencies · integration behavior ·
shared terminology · relevant constraints · links to related specifications ·
references explaining how the subjects interact. The framework doc may
reference the state-condition spec when describing integration.

Cross-references are optional where they add no meaningful value — never
create decorative links or imply relationships that don't exist.

## 6. Avoid duplicate ownership

Each separated subject has exactly **one authoritative location** for its
full specification:

- move detailed definitions and rules into the new document;
- leave only what the original document needs for its own purpose;
- replace leftover duplication with a concise explanation and/or a
  reference;
- keep integration details that genuinely belong to the original subject.

The goal is separated responsibility without lost context.

## 7. Preserve existing meaning

Through the whole restructuring: keep the original meaning and intent;
retain important rules, constraints, exceptions, and examples; preserve
design decisions with their rationale; maintain consistent terminology;
never silently drop information; never invent requirements or alter a
concept's behavior without authorization.

If the existing docs contain **ambiguity or contradictions: identify them
and report** — do not silently decide what the user "probably meant."

## 8. Respect documentation conventions

Follow the project's existing conventions where appropriate: file naming,
directory organization, document formats, heading structures, internal
links, navigation and indexes, referencing style. Choose names that
accurately represent the separated subjects. Do **not** reorganize
unrelated documentation or make broader structural changes than the
requested separation requires.

## Completion criteria

Done when: the user's named subjects are separated · each has its own
documentation identity · neither unnecessarily owns the other's full
spec · surviving relationships are accurate · existing information is
preserved · references and navigation are updated · the result reflects the
user's intended structure.

> Docs Refactor2 does not decide what the user should separate. It takes
> the separation the user wants and implements it — independently defined,
> clearly scoped, maintainable — while preserving the relationships that
> still matter.
