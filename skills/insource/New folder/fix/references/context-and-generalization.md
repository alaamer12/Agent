# Context-Aware Generalization

## Local context (required)

After fixing the discovered instance, inspect:

- The immediate surrounding implementation (same function, same component, same module).
- Sibling or equivalent instances that follow the same pattern or belong to the same visual/logical block.

Examples of justified local generalization:
- Three cards that share the same icon layout → fix alignment in all three.
- Several endpoints that share the same validation pattern → close the same gap in each.
- Multiple places that construct the same domain object with the same incomplete check.

## Boundary rule

Generalize only when there is a **reasonable relationship** to the discovered problem or the change being made.

Do **not**:
- Scan the entire codebase for “similar looking” code.
- Apply a back-end insight to an unrelated front-end component (or vice versa) without a clear dependency.
- Turn every fix into a broad refactor.

If the relationship is ambiguous, prefer the smaller, safer scope and note the potential broader issue for the user.

## Consequences of the change

A correct fix can still leave the system inconsistent. After the code change, ask:

- What statements, documents, or configurations are now false?
- What other code assumes the old behavior?
- What duplicated values or names will now diverge?

Update those artifacts in the same change when they are discoverable through explicit or implicit reference.