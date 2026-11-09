# Documentation conventions

> General conventions for writing and editing steering files. They are project-wide and rarely change. Read this file before writing or changing any steering file. The folders these files live in are listed in the [index](index.md).
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).

1. **One fact, one file.** When two folders touch the same fact, the fact lives in one file and the others link to it. Do not restate it.
2. **Describe behavior, not mechanism.** Especially in doctrine files that state system behavior. The mechanism can change without the document becoming wrong.
3. **Write general principles in free plain text** where a principle exists, so it applies to cases not yet listed. Use a lookup list only when the content is a lookup.
4. **Keep rationale next to the thing it explains**, but only the reasons that come from the sources or the team. If a reason is inferred, say so. Never invent history.
5. **Name files after the concern they hold**, so someone can guess the name without opening the folder.
6. **Do not normalize formats across files.** A file's format fits its concern: prose, table, checklist, diagram, code block.
7. **Cross-reference instead of duplicating.** A line that needs "because..." to make sense points to the file that explains it.

For quick tests on where a document belongs, use the boundary tests in [placement.md](placement.md).
