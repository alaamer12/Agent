---
name: conform
version: 1.0.1
author: Amr
specialized: none
description: 'Audit live project documentation for direct contradictions, cross-layer contract mismatches, scope conflicts, duplicate drift, and stale decisions. Build an evidence-linked Agreement Matrix, distinguish real conflicts from different scopes or history, ask the user when intent or authority is unclear, and reconcile affected facets jointly instead of picking a single winner. Use for "find contradictions", "check these docs agree", architecture consistency audits such as errors versus typing, after separate sessions change a decision, or /conform. Default audit is read-only; fix requires an approved reconciliation plan.'
when_to_use: The user wants documentation checked for contradictions or cross-layer disagreement, wants architecture documents to agree without flattening distinct responsibilities, or invokes /conform.
argument-hint: "[audit|fix] [docs path]"
---

# conform — make documents agree without flattening them

Different layers may own different truths. Conform tests whether their contracts fit together; it does not force every document to say the same thing.

## Non-Negotiables

- **Prove every finding.** Quote the conflicting passages with `file:line` evidence and state the scope of each claim.
- **Authority is per facet, not per file.** A later date, a majority of documents, or a more authoritative-sounding filename never wins automatically.
- **No single-winner default.** Preserve legitimate layer responsibilities and add or repair the integration contract between them.
- **Ask when intent is unclear.** Never invent the user's decision to make the report look complete.
- **Audit is read-only.** In `fix` mode, present the exact reconciliation plan and wait for explicit approval before editing.
- **Do not commit unless asked.** Verification and reporting do not grant git-write authority.

## Modes

| Mode | Behavior | Stop condition |
| :--- | :--- | :--- |
| `audit` (default) | Read live docs, build the Agreement Matrix, report contradictions and open questions | Evidence-backed report; no edits |
| `fix` | Audit, ask blocking questions, propose exact edits, apply only after approval, then re-audit | Zero unresolved blocking conflicts, or an explicit deferred list |

## Boundary with Other Skills

| Need | Skill |
| :--- | :--- |
| Documentation meaning and cross-layer agreement | **conform** |
| Whole-corpus plus code/config drift and wave-based remediation | `deep-audit` |
| Blind orthogonal discovery with independent scouts | `crosscheck` |
| Project orientation before work | `exmaine` |

## Workflow

### 1. Scope the Corpus

1. Confirm the requested documentation root. If scope is ambiguous, ask which docs, areas, and document types are in play.
2. Inventory live documents: README and agent guidance, `docs/`, `.steering/`, architecture and specification files, API/schema references, decision records, and other requested text formats.
3. Mark each file **live**, **historical**, **generated**, or **vendored**. Exclude history and vendored material unless the user includes it or a live document cites it as current.
4. For generated documents, locate the source. A source/output mismatch is stale generation, not a product decision.
5. Record the corpus map before comparing claims. Use code and configuration only as evidence of implemented reality; report doc-versus-reality mismatches without silently changing either side.

### 2. Extract Claims and Build the Agreement Matrix

1. Break prose into atomic claims: **subject → predicate → value → scope → modality** (required, permitted, observed, proposed).
2. Group claims that share a fact, boundary, contract, or lifecycle.
3. Create one matrix row per agreement concern using [`assets/agreement-matrix-template.md`](assets/agreement-matrix-template.md).
4. Name the **facet owner** for each participating document and the **joint invariant** all facets must satisfy.
5. Read [`references/agreement-protocol.md`](references/agreement-protocol.md) before comparing layers.

### 3. Detect and Classify

Apply every class in [`references/contradiction-taxonomy.md`](references/contradiction-taxonomy.md):

- direct value conflict;
- relational contract mismatch;
- ownership gap;
- scope mismatch;
- duplicate drift;
- stale decision propagation;
- terminology collision;
- documentation-versus-reality mismatch;
- migration tombstone or retired label in living content;
- assumption label used instead of evidence, a decision, or structured drafting deferral.

Check decoys before reporting: different scopes, superseded history, illustrative examples, and intentional internal/external distinctions are not contradictions. Use [`assets/contradiction-report-template.md`](assets/contradiction-report-template.md) for the report.

### 4. Resolve Without Choosing One File as Winner

For each real conflict:

1. Identify which facet each document legitimately owns.
2. If one document owns the disputed fact, make dependent documents conform to it.
3. If both own different facets, preserve both and write the missing integration rule, mapping, adapter, or shared invariant in the correct owner document.
4. If the documents use different scopes, narrow or split the claim instead of deleting either meaning.
5. If intent or authority remains unclear, ask the user with both excerpts, concrete options, trade-offs, and a recommendation. Accept hybrid or unlisted answers.
6. Keep unresolved items **Open** or **Blocked**; never disguise a proposal as settled.

### 5. Fix Only After Approval

In `fix` mode:

1. Present the contradiction report and a reconciliation plan with exact files, passages, and intended outcomes.
2. Show every affected document, not only the first witness.
3. Wait for explicit approval of the plan or explicit delegation of the named decisions.
4. Edit the canonical owner, convert duplicate homes to links, and update all affected facets in the same pass.
5. Record the decision in the project's existing decision home. If none exists, ask where the decision belongs; do not invent history.
6. Re-run the audit and report each matrix row as **Aligned**, **Scoped non-conflict**, **Open**, or **Blocked**.

### 6. Recheck After Mid-Flight Changes

Whenever a decision or document changes, re-run every agreement row that cites it and every downstream consumer. When one session authors multiple architecture documents, run this gate before calling the set complete.

## Done Gates

- Every finding has exact evidence and a classified conflict or decoy.
- Every cross-layer concern has facet owners and a joint invariant.
- No conflict was resolved by file date, majority vote, or silent deletion of a legitimate facet.
- Every blocking ambiguity has a user answer or an explicit blocked/deferred status.
- `fix` mode has approval, synchronized edits, and a clean re-audit.
- A clean audit reports "no contradictions found" and makes no edits.

## Resources

| File | Purpose |
| :--- | :--- |
| [`references/contradiction-taxonomy.md`](references/contradiction-taxonomy.md) | Conflict classes, proofs, decoys, and repair directions |
| [`references/agreement-protocol.md`](references/agreement-protocol.md) | Claim extraction, matrix checks, joint resolution, and decision rounds |
| [`assets/contradiction-report-template.md`](assets/contradiction-report-template.md) | Evidence-backed audit report shape |
| [`assets/agreement-matrix-template.md`](assets/agreement-matrix-template.md) | Cross-document agreement register |
| [`examples/errors-and-typing.md`](examples/errors-and-typing.md) | Relational contradiction and hybrid reconciliation example |
