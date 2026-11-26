# Rules binding the restructuring jobs (B reorganize, C separate)

Load this with `references/reorganize.md` or `references/separate.md`. Neither the write job nor the summarize job needs it.

- **Preserve what the user wrote unless the task authorizes a correction.** Never overwrite user edits silently; when the user asks to fix or override content during Draft [DR], replace the wrong living text directly instead of preserving it as retired history.
- **Follow the project's conventions** — where its docs live, how it names them, which file is the map. The incumbent convention outranks any layout this skill prefers.
- **Relocate without rewriting unless the destination needs its own identity.** Keep meaning, terminology and design rationale, but do not add `Moved to` banners or migration notes.
- **Plan before writing**: the files read, the content mapped to each destination, the links that change. Then execute.
- **Validate afterwards**: no lost information, no specification owned by two files, every link and relative path resolves.
- **Ambiguities and contradictions are surfaced, not silently resolved.** Ask immediately; use a structured `Pending (Drafting)` marker only after explicit deferral, never an assumption label.
- **Scope stays where the user put it.** A messy corner does not become a whole-docs rewrite; a named separation does not become extra separations because more concepts *look* splittable.
- **Length is not a defect.** A long file that stays on one subject is healthy; splitting it into pieces the reader hops between is a regression. Split on concern findings, never on line counts.
