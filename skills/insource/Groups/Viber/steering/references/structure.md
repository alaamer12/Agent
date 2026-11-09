# structure

> This document defines the `structure` steering folder: how the project is organized and where each kind of thing is defined. It is one of six folders; see the [index](index.md) for the set.
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).
> Structure: holds, shape, does not hold, the test, then an example.

**Holds.** How the project is organized and where each kind of thing is defined: architecture, modules, boundaries, directory layout (usually drawn as a tree), and the naming of folders and files. It tells the reader where to put something and how it is laid out once it is there.

**Shape.** One flat folder of files named after what they organize. Each file covers one area of the project, for example how styles are structured, and typically shows the layout as a tree.

**Does not hold.** What technologies are used (`stack`), or how the system behaves at runtime (the steering function folder). It also does not hold what data a thing contains or what an interface exposes: a data schema or an API reference is reference documentation, outside this taxonomy (see [placement.md](placement.md)). And it does not hold naming of identifiers inside code (variables, functions, classes). That is not steering content: it is usually enforced by tooling, and it is outside this taxonomy.

**The test.** Structure describes the static shape. If the answer is "where does this live, where do I define it, and how do the parts relate", it is structure. If the answer is about what the thing contains or how it behaves, it is not. For the tests that separate structure from the neighboring folders, see the boundary tests in [placement.md](placement.md).

**Example (`structure/styles`).** Styles are organized into folders by kind, so a new style has an obvious place:

```
styles/
  abstracts/    shared variables, mixins, helpers
  base/         resets and global element styles
  components/   one file per component
  layouts/      page-level arrangement
```

The file says where each kind of style is written and how the styles folder is laid out. It does not say what any individual style looks like.
