# structure

> This document defines the `structure` steering folder: how the project is organized and where each kind of thing is defined. It lives exclusively in the **tech tier** (`tech/structure/`); see [`index.md`](index.md) for the taxonomy overview.

**Scope rule.** Default to `tech/<area>/structure/`; use `tech/shared/structure/` only after the [Universal Scope Test](layout.md#universal-scope-test) passes. Area files link to shared facts and contain only their delta.

**Holds.** The static technical shape of the project: monorepo boundaries, package boundaries, directory trees, file placement conventions, and naming rules for folders and files. It answers where things live, which placement rules are normative, and how new members join the structure. A structure file pairs a scannable snapshot with extensible placement patterns; it is not an exhaustive census or a mandate to reproduce example paths.

**Does not hold.**
- Business domain concepts, module breakdowns, or product functional areas (which belong in [`domain.md`](domain.md) or [`capabilities.md`](capabilities.md)).
- What technologies are used ([`stack.md`](stack.md)).
- How components behave at runtime (the steering function folder, [`function.md`](function.md)).
- Data schemas, table columns, or API route payloads (which belong in reference documentation outside the taxonomy).
- In-code identifier naming (variables, types, classes), which belongs in coding standards or linter configurations outside the taxonomy.
- Example or proposed paths presented as mandatory homes without an explicit approved rule.

**The test.** Does it describe static file/directory layout and code organization?
- *"Where do UI views live versus UI components?"* -> `tech/web/structure/client-tree.md`
- *"How are shared backend packages split from application workspaces?"* -> `tech/<area>/structure/repo-layout.md`
- *"What entities exist in the business domain?"* -> `perception/<area>/domain/`

**Anti-Assumption Rule.** An agent must never unilaterally guess or invent directory layouts. Confirm the technical structure with the user through its directory interview; reflecting actual files does not replace that interview.

### Pattern-First Authoring Rule

Write structure files so a reader can extend them without running a separate generalization pass:
1. **Label the tree's authority.** Mark each tree as **Observed current snapshot**, **Approved target**, or **Illustrative example**. An illustrative path teaches the shape; it does not require that exact location. Separate current and proposed trees rather than blending them.
2. **Make growable groups visibly open.** Use `...` or `…` for groups that accept future members. Add a compact rule inline or beside the tree stating what belongs and what the next item must satisfy. Include the purpose and disqualifiers when they are not obvious. A marker alone is decoration; a formal essay or template is not required.
3. **Preserve orientation without freezing the inventory.** Keep enough real examples to show naming and relationships, but never imply that unlisted items are forbidden.
4. **Keep true closed sets closed.** Do not add ellipses to the steering taxonomy roster, security or trust boundaries, forbidden-import lists, compiler/gate-enforced contracts, or explicit settled decisions.
5. **Apply the new-item test.** A reader holding a new, never-listed item must be able to tell whether it belongs, where it goes, and whether the shown path is an example or a rule. If not, the structure file is unfinished.

**Interview before authoring.** Complete the [Tech Directory Interview and Authoring Gate](documentation-conventions.md#mandatory-tech-directory-interview-and-authoring-gate) for this directory. Ask or explicitly confirm:
- What repository roots, workspaces, packages, applications, and area boundaries exist, and which layout is current versus proposed?
- Which parts of the documented tree are observed facts, approved targets, or merely illustrative examples?
- Which groups are intended to grow, what belongs in each, what disqualifies an item, and what must the next item satisfy?
- Which naming and placement conventions are intentional, and which existing paths are legacy or temporary?
- Which dependency directions and security or contract boundaries must remain closed?
- Which facts pass the [Universal Scope Test](layout.md#universal-scope-test) for steering `shared/`, which area owns the rest, and what local delta must each area document?

Record the confirmed boundary map, normative placement rules, illustrative or current snapshots, growable groups with their extension rules, shared-scope justification, local deltas, closed boundaries, and migration status in the directory's ledger row. Do not turn an example path into a requirement.

**Illustrative example (`tech/web/structure/client-tree`) — shape, not mandated paths.**

Pattern: `features/` groups code by user-facing capability so each area can evolve independently. A new capability gets one feature folder when it owns a distinct boundary; generic cross-feature code belongs in the code-level `shared/` instead. This code-level `shared/` is unrelated to the steering taxonomy's `.steering/<tier>/shared/` scope rule.

```text
apps/web/src/
  features/
    auth/           # one approved feature area
    portfolios/     # another approved feature area
    ...             # one folder per new feature area that meets the rule above
  shared/           # only code used across feature areas
```
