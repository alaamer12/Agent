# Job B — Separate what the user names

The full procedure for "the architecture document and the state-machine document both explain transitions; the state machine gets its own document". SKILL.md routes here; load `references/restructuring-rules.md` alongside this file, and nothing from the other jobs.

The defining constraint of this job: **the user names the seam, you execute the cut.** The separation is their decision. Deciding it for them — splitting extra concepts because they look separable, or merging the seam back because one file seemed tidier — is the failure mode of this job, and nothing downstream catches it.

## 1. Understand the separation before touching anything

Establish, from the request and from the files:

- which subjects are involved;
- where each one is currently documented;
- what belongs to which subject;
- what each resulting document is expected to cover;
- which relationships between them must stay stated.

If the requested scope is unclear **and** the answer would materially change the result, ask one precise question. Otherwise proceed from the reading and state your interpretation in the plan (step 4) where the user can correct it cheaply.

## 2-3. Inspect, then map

Read every file containing either subject, fully. Then map the content: which passages belong to which subject, which are shared context that belongs to one home only, and which are duplicated explanations that will need to be merged rather than copied twice.

## 4. Plan the split

List the files that will change, what each resulting document owns, and which cross-references will connect them. Presenting this before writing costs nothing and is the last cheap moment to catch "that's not the seam I meant".

## 5-7. Extract, restructure, connect

Move content into its new home — **move, don't rewrite**, unless the separated document needs a proper identity of its own and the old text cannot serve it. Reshape each document around its own responsibility, then wire the real relationships as accurate cross-references. A relationship the prose implies but no link states is a reader losing the other half; a relationship stated in prose is not a reason for both files to carry the same specification.

## The independence bar

Each resulting document must read independently:

- its purpose stated at the top;
- its own terminology defined where it uses it;
- the rules and constraints that apply to it;
- enough context that the reader is not forced into another file to understand this one.

"Independent" does not mean "complete". It means a reader who needs only this subject gets a coherent document. When several separations are requested, each resulting document meets this bar on its own — not collectively.

## Ownership, not duplication

The separated document owns **its** full specification. The other document does not need that specification inside it; it needs a pointer. So:

- move the detailed content into the document that owns it;
- leave in the original document only what it genuinely needs to do its job;
- replace the rest with a reference;
- never leave the same detailed rules living in two places, because they will drift the first time one is edited.

## No silent resolution

Contradictions, duplicates that disagree, or a passage that plausibly belongs to either subject are **reported**, not resolved by preference. Silently picking one side of an ambiguity quietly changes what the documentation says.

## Respect what already exists

Follow the project's own conventions — file naming, formats, location, how its indexes and navigation work — for everything this job touches. The separation is the change; the surrounding style is not.

## Completion

Done when each subject the user named has its own document, each reads independently, neither carries the other's full specification, the surviving relationships are stated accurately in both directions, and existing navigation and references point where they should.
