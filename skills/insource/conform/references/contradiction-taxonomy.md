# Contradiction Taxonomy

Classify what disagrees before proposing a repair. Cite exact `file:line` evidence for every finding. Options below are repair directions, not automatic answers.

## D1 — Direct Value Conflict

**Signature.** Two live documents assert incompatible values for the same fact: names, numbers, units, paths, enum members, defaults, or limits.

**Proof.** Normalize scope and terminology, quote both values, and verify that both claims are live and apply to the same subject.

**Repair.** Identify the facet owner or recorded decision. Update every dependent copy; convert duplicate homes to links.

**Decoy.** Superseded ADRs, changelogs, and explicitly historical comparisons are not live conflicts.

## D2 — Relational Contract Mismatch

**Signature.** Each document is internally coherent, but their assumptions cannot both hold at a boundary. Example: a language contract requires typed exhaustive failures while an error contract exposes untyped strings.

**Proof.** Compare producer and consumer expectations for the same boundary: vocabulary, data shape, failure behavior, lifecycle, security, and ownership.

**Repair.** Preserve both facet owners. Conform one facet to the other's constraint, or add an explicit integration contract such as a mapping, adapter, validation boundary, or shared invariant.

**Decoy.** Different internal and external representations are valid when the translation boundary is explicit and tested.

## D3 — Ownership Gap

**Signature.** Every document describes one part of a behavior, but no document owns the hand-off or combined outcome.

**Proof.** Trace the behavior across documents and name the missing transition, producer, consumer, or accountable owner.

**Repair.** Put the integration rule in the document that owns the boundary; link the participating facets. Do not duplicate the whole behavior into every file.

## D4 — Scope Mismatch

**Signature.** A universal rule conflicts with a local exception, or a claim for one area is applied to another.

**Proof.** Write the scope of each claim explicitly: area, layer, environment, actor, time, and modality.

**Repair.** Narrow the universal claim, split the fact, or record the authorized exception with its exact scope. Recheck whether the remaining shared claim is still universal.

## D5 — Duplicate Drift

**Signature.** The same normative fact has multiple homes whose copies have diverged.

**Proof.** Diff the passages and compare meaning, not just wording. Identical copies are a drift risk; diverged copies are a contradiction.

**Repair.** Choose one canonical owner, convert other homes to pointers, and update all links. Preserve deliberate mirrors only with an explicit update rule.

## D6 — Stale Decision Propagation

**Signature.** A later decision exists, but one or more live documents still assert the prior rule.

**Proof.** Compare decision date, status, and supersession links against each live claim.

**Repair.** Update every affected document in one pass and mark the prior decision as superseded rather than deleting its history.

## D7 — Terminology Collision

**Signature.** One name denotes different concepts, or one concept has names that hide a contract mismatch.

**Proof.** Build a meaning-to-names table with locations and decide whether the difference is semantic or merely stylistic.

**Repair.** Rename at the owning boundary and update references. Do not churn harmless prose synonyms.

## D8 — Documentation-versus-Reality Mismatch

**Signature.** Live documentation conflicts with implemented code, schema, configuration, or observed behavior.

**Proof.** Name the implementation evidence and determine whether the doc states intent, current state, or an approved target.

**Repair.** Ask whether the implementation or the document is authoritative for that facet. Never silently rewrite docs to match a bug or code to match an unapproved draft.

## D9 — Migration Tombstone

**Signature.** Living content says `Moved to`, `Moved from`, or `retired` instead of stating the current rule and an ordinary reference.

**Proof.** Classify the file as living or historical. In living content, quote the migration label and identify the current owner or replacement.

**Repair.** Replace wrong living content directly, remove the tombstone, and use a normal cross-reference. Preserve history only in its explicit historical home.

## D10 — Assumption Label

**Signature.** Living content uses `assume`, `assumed`, or `Assumption` as a label instead of evidence, a user decision, or an explicit drafting deferral.

**Proof.** Identify whether evidence supports `Inferred from <evidence>`, the user must decide, or the claim is wrong and should be replaced.

**Repair.** Write the evidence-backed inference, ask immediately, or use structured `Pending (Drafting)` after explicit deferral.

## False-Conflict Checks

Before reporting, rule out:

- **Different scope:** internal diagnostics versus public payloads; development versus production; one area versus all areas.
- **Different time:** a historical decision versus the current decision.
- **Different modality:** advisory guidance versus a binding mandate.
- **Illustration:** an example is not a normative claim.
- **Intentional layering:** separate facets agree through an explicit integration contract.

Record dismissed candidates briefly so the audit shows what was checked and avoids repeated churn.

## Evidence Record

```text
ID | Class | Impact | Confidence | Claim A + file:line | Claim B+ file:line | Scope comparison | Facet owners | Joint invariant | Decision needed
```

Impact describes what the conflict blocks: **Blocking**, **Material**, or **Local**. Confidence describes evidence quality, not severity.
