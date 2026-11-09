# steering function folder

> **Terminology rule (read first).** The steering folder whose directory name is `function` is always called the **steering function folder** in prose, headings, index files, commit messages, and agent output. Never write just "function" or "the function folder" for it, because in code "function" means a single function. The bare directory name `function/` appears only in file paths and layouts. Anyone, human or AI, reading or writing these docs must use this exact term.

This document defines the steering function folder: system-wide functionality that belongs to the whole application, not to one feature or one part. It is one of six folders; see the [index](index.md) for the set. This file owns the terminology rule above; every other document in the set carries a one-line reminder that points here.

**Holds.** System-wide functionality: how the platform works as a whole, and the concerns that apply across the system in general, not owned by a single feature or a single part. Examples: `error-ux` (errors in general), `accessibility-standards` (accessibility in general), `client-lifecycle`, and shared integrations. A core capability that the whole application is built around, such as media playback or media processing in a media platform, is the system itself and not a feature of it.

**Does not hold.** The behavior of one feature, or guidelines for one specific part or task (`doctrine`), such as the error format of the API, which is one part. A feature's own mechanics and behavior belong with that feature's documentation (see [placement.md](placement.md)).

**The test.** If you deleted feature X, would this document still be true? If yes, it belongs in the steering function folder. If no, it belongs to the feature. A document that represents the whole application's way of handling something (how video playback works across the system) passes this test even if it sounds like a feature; a document that exists for one feature (a transcoding integration used only by that feature) does not. A second test is scope: if the concern is the system in general (errors in general, accessibility in general), it belongs here; if it is one specific part (the error format of the API), it is `doctrine`. For the tests that separate this folder from `doctrine` and `structure`, see the boundary tests in [placement.md](placement.md).

**Why it exists.** Per-feature behavior lives with the feature, so behavior that spans features needs its own home. Keeping the two apart makes it clear which scope a file describes.

**Naming note.** In code, "function" usually means a single function, so this folder is always called the **steering function folder**. Its `index.md` should also define it in one line, for example: "System-wide functionality shared across features and parts." If misfiling still shows up in practice, revisit the name.
