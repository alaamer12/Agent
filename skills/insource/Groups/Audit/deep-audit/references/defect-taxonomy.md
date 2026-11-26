# Defect taxonomy — the classes a census hunts

Each class: what it looks like, how to PROVE it, where the content belongs, and the decoy that is
NOT this defect. Cite file:line for every hit.

## 1. Boundary violation (content in the wrong home)

- **Signature:** a tier meant to be general (architecture, principles, shared) carries project
  specifics: binding "must/never" lists, inventory tables, config blocks, operational steps, tool
  tables, command lines.
- **Proof:** read the section and ask which of its four kinds it is — mandate (→ doctrine),
  mechanism (→ function folder), runbook (→ playbook), structure/path (→ structure doc). If not
  design intent, it is a violation.
- **Decoy:** a general principle stated with one concrete example is fine. An example that IS the
  only content is the violation.

## 2. Contradiction (same fact, two values)

- **Signature:** two homes assert incompatible values for one fact — identifiers, numbers, units,
  counts, paths, package names, enum members.
- **Proof:** grep the fact across the corpus; two distinct values = contradiction, name both
  witnesses and the likely authority.
- **Decoy:** a decision recorded as revised (strikethrough, changelog, "superseded") is history,
  not contradiction. Only live claims conflict.

## 3. Invention (asserted, never defined)

- **Signature:** a concept gates or rejects or prices — but no domain rule, table, page, test, or
  definition anywhere defines it.
- **Proof:** search every possible definer (schema, policy, UI, code, config). Zero hits = invented.
- **Decoy:** a deliberately deferred decision marked with the structured `Pending (Drafting)` marker is not an invention; an unmarked assertion is.

## 4. Stale marker (answered, still marked open)

- **Signature:** "pending — not assumed", "TODO", "not decided yet", open questions in ledgers —
  while the answer exists elsewhere in the corpus or in a recorded decision.
- **Proof:** compare marker date against the decision's date and the current content state.
- **Decoy:** honest open ends (genuinely unknown at DR) stay. Only resolved-but-unmarked items are
  stale.

## 5. Never-decided-but-asserted

- **Signature:** many docs state a concrete choice (a library, a number, a symbol, a limit) that no
  decision record contains. Consensus without authority.
- **Proof:** check the decision ledger for the claim; absent = the corpus voted without the owner.
- **Action:** either ask the owner or write `Inferred from <evidence>` when evidence supports the inference. After explicit deferral, use the structured `Pending (Drafting)` marker. Never leave an assumption label as fact.

## 6. Terminology drift

- **Signature:** one meaning, several names (entity vs label vs code identifier), or one name,
  several meanings.
- **Proof:** build the drift table: meaning | names in use | locations | ruling needed.
- **Decoy:** synonyms in prose that name no entity/field/endpoint are voice, not drift.

## 7. Duplicate home (one fact, N copies)

- **Signature:** the same table, list, path, or rule present verbatim in 2+ files; one will drift
  first.
- **Proof:** diff the copies; identical = pick the owner, convert others to pointers; diverged =
  contradiction #2 waiting with a fresh number.
- **Decoy:** a deliberate multi-home fact with an update-all rule (a sync block) is legitimate.

## 8. Marker-without-pattern

- **Signature:** an "etc./…/for example" on a list with no stated rule for membership or extension.
  Looks open; behaves closed.
- **Proof:** can a reader place an unseen item into the set using only what is written? No =
  decoration. The pattern (what/why/membership/extension) must be described.
- **Decoy:** genuinely closed sets marked CLOSED with the reason are correct, not missing patterns.

## 9. Falsified belief (training vs project reality)

- **Signature:** what a competent outsider's memory assumes, contradicted by this project's
  records (the stack, the platform, the framework the "obvious" answer implies).
- **Proof:** check against the ledger and the actual artifacts; on conflict, the project wins and
  the belief gets recorded as a dated fact so the next agent does not re-learn it.
- **Decoy:** general industry truth the project agrees with needs no fact entry.

## 10. Migration tombstone

- **Signature:** living guidance contains `Moved to`, `Moved from`, or a `retired` block preserving outdated content instead of stating the current rule.
- **Proof:** classify the file as living or historical. In living files, quote the migration label and the current owner or replacement.
- **Repair:** replace wrong living content directly and use an ordinary reference to the current owner. Keep history only in its explicit historical home.

## 11. Assumption label

- **Signature:** living content uses `assume`, `assumed`, or `Assumption` as an epistemic label instead of evidence, a decision, or an explicit drafting deferral.
- **Proof:** identify the claim and ask whether evidence supports `Inferred from <evidence>`, the user must decide, or the text is simply wrong and should be replaced.
- **Repair:** write the evidence-backed inference, ask immediately, or use structured `Pending (Drafting)` after explicit deferral.

## Reporting format per census agent

```
## <class name>
| file:line | finding | class | destination | reason |
...
## Statistics
files scanned: N | findings: total + per-class | consensus/solitary/conflict marks
## FINE (do not churn)
file:line ranges with one-line reason why they belong where they are
## Questions for the owner (never assumptions)
- question | why the corpus cannot answer | options if known
```