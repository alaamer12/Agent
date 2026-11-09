# The knowledge model

This file is about judgment, not formatting.

There is no template. No required fields, no fixed order, no ID scheme, no mandatory table. The writer chooses the shape. What this file fixes is the judgment behind the choices: what must be answerable, when two pieces are the same knowledge, how evidence is marked, and how a correction stays visible.

## The floor

Every piece of knowledge — a paragraph, a section, a table, a diagram, a set of notes — must make these answerable somewhere, in whatever form fits:

1. **The claim.** What is known, stated plainly enough that a reader can disagree with it.
2. **The mechanism.** How it works, why it is that way, and what it trades away.
3. **The evidence.** Where it came from: file, section or line, and the exact words.
4. **The epistemic status.** Whether the source stated it or the writer inferred it, and how far the source actually reached.
5. **The limits.** What it does not establish, where it stops, what would contradict it.
6. **The connections.** What related knowledge it depends on or supports, named, in this file or another.

The floor is about content, never about headings. A writer who covers all six in three dense paragraphs has done the job; a writer who fills six labeled boxes with thin restatements has not.

## Naming and linking

A knowledge base is read by pieces, so each piece needs a stable way to be pointed at. The writer chooses the form: a heading, a short name, a slug, a descriptive phrase. It only has to be unique across the whole base and stable once written.

Links use that name and, when the target lives in another file, the file. Links go both ways: the piece that depends on another says so, and the piece being depended on says what builds on it. A link that resolves nowhere is a defect, not a stylistic choice.

Names should describe the knowledge, not the source that happened to supply it first. `Tenant isolation enforced in the database`, not `Atlas section 4`.

## When two pieces are the same knowledge

Same knowledge requires all three:

1. the same subject,
2. the same scope,
3. an equivalent assertion.

The kind of knowledge — pattern, decision, failure mode, metric — is a thinking aid and a navigation aid. It is not a gate: a decision and a pattern can describe the same artifact from different angles, and they are still different pieces of knowledge. Keep them distinct and link them.

Apply the ladder, in order:

| Situation | What the writer does |
|---|---|
| All three match | **Merge.** One piece, all evidence together. Keep the richer account; keep every limit. Raise confidence only for independent evidence. |
| Same subject, different scope | **Keep both.** Link them as variants. The broader piece names its variants. |
| Same subject, incompatible assertion | **Keep both side by side.** Write what each claims, what evidence stands behind it, and what turns on the difference. |
| Different subject, related | **Keep both.** Add the link. |

Never merge across a real difference in scope to make the base look tidier. Never merge two claims whose evidence conflicts; that is a contradiction, not a duplicate.

## Evidence and lineage

Evidence is written next to the claim, in the writer's own form. At minimum it names the source file, the section or line, and reproduces the exact words. A paraphrase belongs in the explanation, never in the evidence.

Every piece of evidence is one of two kinds:

- **independent** — it comes from a different raw source, or a different mining run.
- **derived** — the file it comes from was itself built out of evidence already cited.

Within one run, almost everything in `distillation/` is derived: it was written from the checkpoints. If a checkpoint and its distillation both state a claim, that is one observation restated, not two corroborations. Counting it twice inflates confidence and hides how thin the evidence is.

Across runs, the same claim from two independent mining runs is genuinely independent. Mark it honestly and let confidence follow.

## Confidence

Confidence is a property of the evidence, not of the prose. Say how sure the claim is and why, in whatever words fit the piece. When a label helps, `high` / `medium` / `low` are enough:

- **high** — an independent source states it within the reach it measured; or two independent sources agree.
- **medium** — one source states it with partial reach; or it is inferred from two or more independent observations.
- **low** — one source infers it; or the only support is derived; or the sources disagree and the disagreement is unresolved.

Never raise confidence because the distillation repeats the claim. Never lower it because the source hedged; write the hedge down instead.

## Corrections

Nothing is deleted.

When later evidence corrects an earlier reading, the earlier piece stays, marked as corrected: what was believed, what replaced it, and why. The reader sees both the current claim and the path that led to it. This is how a misunderstanding is fixed without pretending it never happened.

The same applies at the level of a whole file: a superseded framing stays visible, with a note on what changed. A knowledge base that shows only its final state is less trustworthy than one that shows its corrections.

## Operations during the fold

While folding, the writer is doing one of these. They are actions, not formats, and each one that affects more than the current file is recorded in `merges.md`.

- **add** — new knowledge, no match.
- **merge** — same subject, scope, and assertion; combine the evidence.
- **vary** — same subject, different scope; keep both and link.
- **contradict** — incompatible assertions; keep both and write the disagreement.
- **supersede** — later evidence corrects an earlier piece; keep the old one visible and explain the change.
- **link** — related but distinct; add the connection.
- **answer** — a file resolves an open question; close it and say which knowledge answered it.
- **raise** — a file opens a question; write it down.

## Gaps and open questions

The knowledge base is as valuable for what it says is unknown as for what it asserts.

A gap records what the corpus does not establish, what it would take to settle it, and which file raised it. "Not measured" from a source becomes a limit or a gap, never a blank. A pre-plan run produces a candidate dossier, and the dossier says so at the top.

Open questions live in the folder knowledge file while the fold is running. At delivery, the unresolved ones become gaps; the resolved ones stay in the merge log.

## What does not belong

- A summary of a file. The base holds knowledge, not abstracts.
- A claim with no source. If the writer reasoned it, say so and name the pieces it follows from.
- A product detail that carries no lesson. It belongs only if the corpus uses it as an example of something larger.
- Two pieces for the same knowledge. Merge or link; never duplicate.
- A correction with no trace of what was corrected.
- Confidence language that the evidence does not support.

## Writing quality

The same standards as the skill body:

- Lead with the claim.
- Carry the mechanism and the cost.
- Quote exactly; paraphrase elsewhere.
- Separate observation from inference.
- Prefer measured numbers to adjectives.
- No filler, no marketing, no performance of thoroughness.
- Say when the corpus is thin.
- Do not average away disagreement.
