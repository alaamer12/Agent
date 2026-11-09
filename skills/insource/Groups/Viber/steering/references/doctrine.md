# doctrine

> This document defines the `doctrine` steering folder: guidelines, and mandated behavior, for one specific part or task. It is one of six folders; see the [index](index.md) for the set.
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).
> Structure: holds, shape, does not hold, the test, how to write it, then two examples.

**Holds.** Guidelines for one specific part or task: how to write high-quality tests, how data deletion is handled, the error format of the API, and similar. A part is a specific component, layer or activity (the API, tests, data deletion), as opposed to the system in general. It covers code, tests, and whatever else should be done a certain way. Where a part has mandated behavior (a fact with nothing to argue), that is written here too, in the same folder and the same plain-text style. Think of the folder as the project's jurisprudence: accumulated, reasoned guidance that people apply to new cases.

**Shape.** One flat folder of topic-named files (`test-quality.md`, `data-deletion.md`). There are no subfolders for kinds of content and no marker separating guidelines from mandates.

**Does not hold.** Tool lists (`stack`), how the platform works as a whole, or a concern that applies to the system in general such as accessibility (the steering function folder), step-by-step recipes (`playbook`), or general project-wide procedures, how documentation itself is written, and decision records (the last three are outside this taxonomy; see [placement.md](placement.md)). Doctrine holds guidelines for specific parts and tasks, never the decision records themselves.

**The test.** Is it a guideline, or mandated behavior, for one specific part or task? Then it is doctrine. For the tests that separate doctrine from the neighboring folders, see the boundary tests in [placement.md](placement.md).

**How to write it.** The general writing principles are in [documentation-conventions.md](documentation-conventions.md). Applied to doctrine: do not use SQL-like syntax (`ON DELETE CASCADE`) or per-table lookup lists. If the enforcement mechanism (database constraints versus application code) is worth recording, it is a separate lower-level fact and belongs in `stack` or `structure`.

**Example (`doctrine/test-quality`).** "Do not write tests that only check for null or undefined. Test critical functions for their invariants: properties that must hold across all valid inputs. A pagination function's invariant is not that it returns something, but that pages never overlap and that concatenating all pages recovers the full set exactly once."

**Example (`doctrine/data-deletion`).**

> Every table that holds data owned by a user (content items, replies, sessions, and anything else scoped to that user's account) must cascade on delete when the user is deleted. If a user deletes their account, nothing that belonged exclusively to them should be left behind as an orphaned row.
>
> Attached files are the one deliberate exception. Deleting a content item must not cascade into deleting its attached files, because files live in storage, not just the database. Files must be explicitly detached before the content item they belong to can be deleted, and the system should refuse the deletion rather than silently drop the files.
>
> The general standard: ownership relationships cascade, storage-backed relationships do not. When in doubt about a new table, decide which side of that line it falls on before choosing its deletion behavior.
