---
name: generalize
version: 1.0.0
specialized: none
description: 'Convert closed inventories into open patterns. Use when a spec, structure doc, API list, config catalog, or tree lists concrete items as if they are the complete set — rewrite as growth rules + shape + illustrative examples so a reader extends instead of replicating. Applies to any document type: file trees, endpoint registries, component catalogs, database schemas, route tables, feature lists, enum definitions.'
when_to_use: When a document presents a list or tree that implies nothing else should exist, when an agent is about to write a spec that enumerates concrete items without stating the rule for the next one, or when the user says "generalize", "make it a pattern", "not a closed set", "etc", "abstract the idea", or complains that a spec reads like an inventory.
argument-hint: "[the file or passage to generalize, or 'audit <path>' to scan a docs tree for closed-set anti-patterns]"
---

# generalize — teach the growth, not the snapshot

A document that lists files, endpoints, tables, or features as if they are the complete set tells a
future reader one thing: "these exist, add nothing." A document that states the RULE for how the next
item slots in tells them: "here is the shape, extend it." The first freezes architecture; the second
enables it.

This skill converts the first into the second. Universal: any doc type, any stack, any list.

## The cosmos rule: describe the pattern or you have generalized nothing

A `…` marker, an "etc.", or a list trimmed to "2–3 examples" is NOT generalization — it is decoration.
Generalization exists only when the **pattern is written down**: what the set contains, why it exists,
and what makes a candidate item belong. The reader must be able to look at a new, never-seen item and
decide from the pattern alone whether it slots here. If the pattern is not described, that decision is
guessing, and the list silently became a closed inventory again.

Every generalized section must carry a **pattern description** answering, in prose:

1. **WHAT** does this group contain — the class of things, not the instances.
   *"Route files, each defining the HTTP surface of one API domain group."*
2. **WHY** does it exist — the role it plays, the problem the grouping solves.
   *"One file per domain keeps the API surface navigable and reviewable per business area."*
3. **MEMBERSHIP** — what makes an item belong, and what disqualifies it.
   *"A group belongs here when it owns endpoints under one path prefix. Business logic does not —
   it lives in rules/. A shared utility does not — it lives in lib/."*
4. **EXTENSION** — what the Nth item must satisfy. *"A new domain adds a file exporting a Hono
   sub-app mounted at `/<group>`, containing only validate → call-rule → respond."*

The four answers ARE the pattern. Examples and `…` markers illustrate it; the description teaches it.
Without the description, adding an item requires the reader to infer the rule from instances — which
is exactly how closed sets enforce themselves.

## The test

Ask of any enumerated item: **does this list the rule, or the current instance?**

| Closed (bad) | Open (good) |
|---|---|
| `auth.ts # POST /auth/login` | One route file per domain group (examples: `auth.ts`, `funds.ts`) |
| 7 bullet points naming every endpoint | "Routes follow `METHOD /resource` — current groups listed as examples" |
| A tree with 12 files, no ellipsis | A tree with 3 files + `...` + a rule paragraph for adding the Nth |
| "Tables: users, funds, trades" | "One collection per domain entity; current: users, funds, trades, …" |

Detection heuristic: a closed set has no `…`/`etc.`/`e.g.` marker AND no sentence stating how to grow.
A pattern has both.

## What stays closed (the exceptions)

Not every list is an inventory anti-pattern. These are genuinely finite and must NOT be opened:

- **Security boundaries:** the exact allowed origins, the exhaustive list of forbidden imports,
  the closed set of trust levels. "No PB SDK in client" is a boundary, not a growth point.
- **Type-safety enumerations:** the exact union members, the exhaustive switch cases, the 8 error
  prefixes the boot gate validates. These are compiler/gate-enforced; opening them is wrong.
- **Contract obligations:** "all 3 layers must do X" — the layers are defined, not extendable
  by convention.
- **Settled decisions:** the chosen framework, the selected database. Not a pattern; a choice.

The test: if removing an item or adding an item changes the CONTRACT or the SECURITY posture, it stays
closed. If it just adds capability that follows the same shape, it opens.

## The rewrite method

For each closed section:

1. **Write the pattern description (mandatory, first).** Prose answering WHAT / WHY / MEMBERSHIP /
   EXTENSION for the group (the cosmos rule above). Place it as a "Patterns" subsection after the
   tree, or as expanded comments on the directory line. This is the generalization; everything else
   is illustration.
2. **Show the shape (tree or list) with markers.** Keep 2–4 concrete examples that teach the
   naming and structure. Add `…` or `...` to signal "this grows."
   ```text
   routes/
   ├── auth.ts        # POST /auth/login, /auth/refresh
   ├── funds.ts       # GET /funds, GET /funds/:id
   └── ...            # one file per new domain group
   ```
3. **Name the extension point.** Explicitly state how the Nth item is added and what it must
   satisfy. *"A new domain gets its own file here; it registers routes, never business logic."*
4. **Keep the hard rules verbatim.** Boundaries, prohibitions, and invariants stay as closed lists.
   Only the CONTENT inventory opens.

## Anti-patterns to avoid while generalizing

- **Marker without pattern (the worst one):** an "etc." or `…` with no prose describing what the set
  is, why it exists, and what belongs. The list LOOKS open and IS closed — the reader still cannot
  tell whether their new item qualifies. The cosmos rule above forbids this: no pattern description,
  no generalization.
- **Over-abstracting:** "files live in directories as appropriate" teaches nothing. The pattern must
  name WHAT the class is and the MEMBERSHIP test, not gesture at "flexibility."
- **Opening the wrong thing:** the 8 error prefixes are a closed contract. Do not write "e.g. TRD,
  XP, …" where the set is compiler-enforced and exhaustive.
- **Losing the current state:** a new agent joining needs to know what EXISTS today, not just the
  rule. Examples serve double duty: illustration AND status snapshot. Keep enough to orient.
- **Replacing the tree with prose:** trees are fast to scan. Put the pattern description in prose
  beside the tree (a "Patterns" section after the tree, or expanded comments); do not dissolve the
  tree itself.

## Audit mode

`generalize audit <path>` — walk every doc under the path, flag sections that pass the closed test
(no growth marker, no rule sentence, not a security/contract/type exception) AND, separately, flag
**open markers without pattern descriptions** — the `…` exists but WHAT/WHY/MEMBERSHIP/EXTENSION are
missing. Output: file, heading, one-line diagnosis, suggested rewrite shape. Report-only; no edits
until the user says apply.

## Done

A generalized section reads correctly to someone holding a NEW, never-listed item: the pattern
description tells them what the set is, why it exists, and whether their item belongs; the tree shows
the current shape with examples; they never wonder "am I allowed to add this?" A `…` with no pattern
prose is NOT done — it is a closed list pretending.