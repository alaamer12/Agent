# Agreement Protocol

Use this protocol to compare documents without collapsing distinct layer responsibilities.

## 1. Extract Atomic Claims

For every normative or descriptive claim, record:

```text
subject | predicate | value | scope | modality | source file:line
```

- **Subject:** the fact, entity, boundary, or behavior.
- **Predicate:** what is asserted about it.
- **Value:** the concrete requirement, choice, state, or relationship.
- **Scope:** area, layer, actor, environment, time, and applicability.
- **Modality:** required, permitted, forbidden, observed, proposed, or unknown.

Keep examples separate from normative claims. Keep historical claims separate from live claims.

## 2. Build the Agreement Matrix

Create one row per concern that crosses document boundaries:

```text
ID | Concern | Participating documents | Facet owners | Joint invariant | Claims and evidence | Status | Decision reference
```

Use these statuses:

- **Aligned:** all participating claims satisfy the joint invariant.
- **Scoped non-conflict:** apparent disagreement is explained by explicit scope or layering.
- **Open:** intent or authority is not yet known.
- **Blocked:** a required decision or dependency prevents resolution.

The matrix points to canonical documents; it must not become a duplicate home for their rules.

## 3. Compare Every Shared Boundary

For each pair or group of documents, ask:

1. Do they name the same concept with incompatible definitions?
2. Does a producer create a value the consumer forbids or cannot interpret?
3. Does one layer require a failure behavior another layer cannot represent?
4. Are lifecycle, ordering, consistency, or cancellation assumptions compatible?
5. Are security, privacy, and observability assumptions compatible?
6. Does every hand-off have an owner?
7. Are exceptions scoped and authorized?
8. Is the same normative fact duplicated with an update rule?

For architecture suites, always check the language/type contract against error/failure contracts, then check both against API/schema boundaries, UI/display consumers, testing, and enforcement gates.

## 4. Classify Before Repair

Apply the contradiction taxonomy. A candidate is real only when both claims are live and their scopes overlap. When scopes differ, record **Scoped non-conflict** and the boundary that makes them compatible.

## 5. Resolve Jointly — No Single Winner

Authority belongs to a facet, not automatically to an entire file. Choose the repair that preserves legitimate responsibilities:

- **Conform the dependent facet:** one document clearly owns the disputed fact; update the other to comply.
- **Add the missing integration contract:** both facets are valid but their mapping, adapter, validation, or hand-off is absent.
- **Narrow or split the claim:** the conflict came from universal wording masking a local exception.
- **Create a shared invariant:** several facets must obey one outcome while retaining different mechanisms.
- **Ask the user:** intent, product behavior, risk acceptance, or authority cannot be derived from artifacts.

Never resolve by newest file, most files, longest document, or silent deletion. Never turn a hybrid answer into a forced either/or.

## 6. Ask Decision Rounds

When the corpus cannot settle a conflict:

1. Quote both passages with `file:line`.
2. Name each facet owner and the joint invariant at stake.
3. Present concrete options with pros, cons, and downstream impact. Include a hybrid or unlisted-answer path.
4. Recommend one option with a reason tied to the user's stated goals.
5. Ask only the blocking questions, at most four per call. Use open-ended questions when the answer is not a known choice set.
6. Record the answer, its scope, and whether it is explicit, delegated, provisional, or deferred.

A deferral is not consent. Keep dependent claims open or blocked.

## 7. Reconciliation Plan

Before `fix` mode edits anything, present:

```text
Conflict ID | Canonical owner | Exact edit | Other affected docs | Decision authority | Verification
```

Require explicit approval. Then:

1. Edit canonical owners first.
2. Replace duplicate homes with links.
3. Update every affected facet in the same pass.
4. Record the decision in the project's decision home.
5. Re-run the matrix and the falsified-claim sweep.
6. Report unresolved items honestly.

## 8. Incremental Recheck

After any decision or document changes:

1. Find every matrix row citing the changed document or fact.
2. Recheck those rows and all downstream consumers.
3. Add newly discovered agreement rows.
4. Stop completion while a blocking row remains open.
