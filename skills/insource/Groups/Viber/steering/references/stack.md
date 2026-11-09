# stack

> This document defines the `stack` steering folder: what the project is built with, stated as "we use X". It is one of six folders; see the [index](index.md) for the set.
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).
> Structure: holds, does not hold, the test, why it has its own folder, why a folder and not a file, then an example.

**Holds.** What the project is built with: languages, frameworks, libraries, databases, hosting, infrastructure choices, external services. For each item, one line saying what it is for, and the version if it matters.

**Does not hold.** How to use the tools (`playbook` for a specific task), mandated usage for a specific part (`doctrine`), or how a feature behaves with the tool (the feature's own documentation or the steering function folder). A stack file states what is in use; it does not carry the reasoning for the choice. That reasoning is a decision record, which lives outside this taxonomy (see [placement.md](placement.md)).

**The test.** If a line says "we use X", it is stack. If it says "do this with X" or "never do that with X", it belongs elsewhere. For the tests that separate stack from the other folders, see the boundary tests in [placement.md](placement.md).

**Why it has its own folder.** "What we use" is a different question from every other folder, it changes at its own pace (a dependency swap), and it is the first thing a newcomer or agent needs.

**Why a folder and not a file.** "What we use" is several topics that each grow on their own: frontend, backend, database, infrastructure, external services. One file would become a long list. A small project may start with a single `stack` file and split it once it has three or four distinct sections.

**Example (`stack/frontend`).** "We use a cross-platform client framework with a component library on top. The component library provides the native UI components. Versions are listed in the package manifest." No usage guide: that is a `playbook` pointer.
