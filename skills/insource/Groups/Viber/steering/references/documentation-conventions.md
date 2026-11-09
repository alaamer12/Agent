# Documentation Conventions

> General conventions for authoring and editing steering files across the Two-Tier Steering Taxonomy. Read this document before writing or updating any steering file. See [`index.md`](index.md) for the master index.

1. **One fact, one file.** Every fact has exactly one canonical home. When two folders or tiers touch the same fact, the fact lives in its single owner file and related files link to it. Never duplicate a fact.
2. **One fact, one file ACROSS TIERS.** Do not restate a business policy in `tech/` or an engineering standard in `perception/`. A technical document links to the perception document it implements.
3. **Passage-level splitting.** Always split mixed source material by passage rather than assigning an entire file or prompt block to one folder. Evaluate each sentence or paragraph against the Tier Test and folder boundary tests.
4. **Cross-tier link direction (strict).**
   - Documents in `tech/` link to their governing concepts in `perception/`.
   - Documents in `perception/` **never link to `tech/`**.
   - *Rationale*: This guarantees that `perception/` remains strictly stable across technical rewrites, framework migrations, and refactoring without experiencing link rot.
5. **Describe behavior, not fragile mechanism.** Especially in `doctrine` files that state system behavior. The enforcement mechanism can change without making the document obsolete.
6. **Write general principles in free plain text.** Express rules and concepts as plain-language prose rather than fragile lookup tables unless the content is genuinely a key-value lookup.
7. **Keep rationale next to the thing it explains.** Record reasons that come from project requirements or maintainers. If a reason is inferred, state so clearly. Never invent history.
8. **Name files after the concern they hold.** File names should be obvious and descriptive (e.g., `user-tiers.md`, `non-negative-balance.md`) so an agent can locate them without opening every folder.
9. **Do not normalize formats across files.** Match the format to the concern: prose, table, checklist, diagram, or code block.
10. **Terminology rule for `function/`.** Inside the `tech/` tier, the directory `function/` is always referred to as the **steering function folder** in prose, headings, index files, and agent output. (Its business-tier counterpart in `perception/` is `capabilities/`, which has no naming ambiguity).
