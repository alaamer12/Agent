# playbook

> This document defines the `playbook` steering folder: step-by-step recipes for operating one specific subject or task. It is one of six folders; see the [index](index.md) for the set.
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).

**Holds.** Step-by-step recipes for operating one specific subject or task: how to check the database tables (`db-tables.md`), how to seed test data and verify it, how to run the containerized setup, how to release a new version. To operate means to run it, not to implement it: a playbook never describes how to build something. How to build or handle a part well is `doctrine`.

**Does not hold.** General guidance on how to write commands, use the package manager, onboard newcomers, or work in this project in general (outside this taxonomy; see [placement.md](placement.md)). A playbook file does not restate any of that. It also does not hold descriptions of how the system behaves (the steering function folder) or guidelines for a part (`doctrine`). Incident-response content is not included by default, and the name leaves room to add situational procedures later.

**The test.** If the reader finishes the document having run something specific, it is a playbook. If they finish knowing something, it is another folder. If the document would read the same for any task in the project, it is general and belongs outside the steering folders. For the tests that separate playbook from `doctrine` and from general guidance, see the boundary tests in [placement.md](placement.md).

**Why it exists.** This is the information that is easy to remember while a project is small and easy to lose once it grows. Putting it in one predictable place prevents the "I have to re-read everything" cost.
