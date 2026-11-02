# Rules binding the restructuring jobs (B reorganize, C separate)

Load this with `references/reorganize.md` or `references/separate.md`. Neither the write job nor the summarize job needs it.

- **Preserve what the user wrote.** Inspect the destination first; never overwrite existing files or silently replace user edits; merge rather than clobber when it is unclear whether content is redundant.
- **Follow the project's conventions** — where its docs live, how it names them, which file is the map. The incumbent convention outranks any layout this skill prefers.
- **Move, don't rewrite**, unless rewriting is required to give a subject its own identity. Meaning, terminology and design rationale survive the move.
- **Plan before writing**: the files read, the content mapped to each destination, the links that change. Then execute.
- **Validate afterwards**: no lost information, no specification owned by two files, every link and relative path resolves.
- **Ambiguities and contradictions are surfaced, not silently resolved.** Ask, or record them as open.
- **Scope stays where the user put it.** A messy corner does not become a whole-docs rewrite; a named separation does not become extra separations because more concepts *look* splittable.
- **Length is not a defect.** A long file that stays on one subject is healthy; splitting it into pieces the reader hops between is a regression. Split on concern findings, never on line counts.
