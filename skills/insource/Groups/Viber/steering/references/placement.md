# Placement: where does a document go?

> This document decides which steering folder, or which non-steering home, a document belongs in: the ordered decision flow, the boundary tests between folders, what lives outside the taxonomy, and worked examples. The folders themselves are defined in [doctrine](doctrine.md), [stack](stack.md), [structure](structure.md), [product](product.md), [function](function.md) and [playbook](playbook.md); the [index](index.md) lists the set.
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).

## The ordered decision flow

Ask these in order and stop at the first match.

1. **Is it about exactly one feature?** It belongs with that feature's own documentation, which this taxonomy does not govern (see [Outside the taxonomy](#outside-the-taxonomy)).
2. **Is it general, project-wide, rarely updated guidance on how to do things** (how to develop here, debug, run commands, configure the environment, version, write docs, onboard newcomers)? It is outside this taxonomy.
3. **Is it a decision record, an incident record, reference documentation (a data schema, an API reference), a glossary, or a roadmap?** It is outside this taxonomy. Where it is written is not governed here.
4. Otherwise it is a steering document. What kind of knowledge is it?
   - Tools and technologies in use: **[stack](stack.md)**
   - How the project is organized and where each kind of thing is defined: **[structure](structure.md)**
   - What the product is, for whom, and why: **[product](product.md)**
   - How the system works as a whole, or a concern that applies to the system in general, across features and parts: **[steering function folder](function.md)**
   - A recipe for operating one specific task: **[playbook](playbook.md)**
   - A guideline, or mandated behavior, for one specific part or task: **[doctrine](doctrine.md)**

**Golden rule: if you are unsure where a file goes, split it by role.** A file that mixes several concerns is not placed as one unit. Split it by the role each part plays, then place each part with the flow above. Auth is the example: the part that describes how the whole system is authorized (for instance, how general auth works across services) goes in the steering function folder as `auth`, and the part about how auth is to be written goes in `doctrine`. The same applies to any mixed file.

A fact lives in exactly one file; the rule is owned by [documentation-conventions.md](documentation-conventions.md).

## The boundary tests

| Boundary | Test |
|---|---|
| steering function folder vs. feature | If feature X were deleted, would the document still be true? Yes: the steering function folder. No: the feature's own documentation. A capability the whole application is built around (such as media playback in a media platform) is the system, not a feature |
| doctrine vs. steering function folder | Is the concern the system in general (steering function folder) or one specific part or task (`doctrine`)? Errors in general and accessibility in general: steering function folder. The error format of the API, which is one part: `doctrine`. A fact that fits both is written once and linked |
| doctrine vs. playbook | What good looks like and what is mandated for a part: `doctrine`. Steps to operate (run) a specific task: `playbook` |
| playbook vs. general guidance | One specific subject or task: `playbook`. General guidance that would read the same for any task: outside this taxonomy |
| doctrine vs. general guidance | One specific part or task, changing with it: `doctrine`. General, project-wide, rarely updated: outside this taxonomy |
| stack vs. everything else | "We use X" is `stack`. "Do this with X" is a `playbook` recipe, or general guidance outside this taxonomy. "Never do that with X" is `doctrine` when it concerns one specific part, or general guidance outside this taxonomy when it applies project-wide (such as the one package manager) |
| structure vs. steering function folder | Static shape and organization: `structure`. How the platform works: the steering function folder |
| structure vs. reference documentation | Where things live and how they are laid out: `structure`. What data a thing holds or what an interface exposes (data schema, API reference): outside this taxonomy |
| structure vs. code naming | Naming of folders and files, as part of the layout: `structure`. Naming of identifiers inside code: not steering content, outside this taxonomy |
| product vs. feature | The whole product: `product`. One feature's detail: the feature's own documentation |

**Doctrine vs. playbook.** Doctrine says how a part should be built or handled and what is mandated for it ("test invariants, not null checks"). A playbook says how to operate something: which steps to run for a task ("how to check the database tables", "how to release a new version"). To operate means to run, not to implement. If the reader finishes knowing how to judge their work, it is doctrine. If they finish having run a task, it is a playbook.

**Doctrine vs. the steering function folder.** The deciding question is scope. The steering function folder covers the system in general: how the platform works as a whole and the concerns that apply across it (`error-ux`, accessibility, lifecycles, shared integrations). Doctrine covers one specific part or task, meaning a component, layer or activity such as test quality, data deletion or the API. So errors in general belong in the steering function folder, while the error format of the API, which is one part, belongs in `doctrine`. Accessibility in general is the steering function folder. A fact that fits both is written once and linked from the other.

**Caveat.** The boundary between the steering function folder and `doctrine` is a judgment of scope: the system in general versus one specific part or task. It was not tested against real documents.

## Outside the taxonomy

The six steering folders are the reference layer. Other documentation sits alongside them and is not governed here. Where and how it is written is each project's choice, and steering files do not hold it.

**Feature documentation.** Documentation about a single feature (what it does, how it behaves, how it is built) sits outside the steering folders. This taxonomy does not prescribe where it lives, how it is split into files, or what the files are called.

- Whatever is true of only one feature belongs with that feature's documentation, not in a steering folder.
- Steering files refer to features only in general terms: the product overview names key features at a high level, and the steering function folder holds what spans several features.
- The boundary test is the same everywhere: if feature X were deleted, would the document still be true? If yes, it is a steering document. If no, it belongs to the feature.

**General guidance, decisions, incidents, and everything else.** General project-wide guidance on how to work in the project (including onboarding guides for newcomers), decision records (such as ADRs), incident records (postmortems), reference documentation (a data schema, an API reference), a glossary, a roadmap, and similar content are outside this taxonomy.

## Worked examples

### Classifying existing files

| File | Destination | Why |
|---|---|---|
| `personalization` | that feature's own documentation | It belongs to one feature; deleting the feature makes it untrue |
| `error-ux` | steering function folder | It spans features; it stays true if any single feature is deleted |
| `client-lifecycle` | steering function folder | System-wide runtime behavior of the client application |
| `external-provider-integration` | steering function folder if the integration serves the application as a whole; otherwise the feature that owns it | Decided by scope, not by a count of dependents |
| `media-transcoding-integration` | steering function folder if media processing is a capability of the whole application (as playback is for a media platform); the feature's own documentation if it exists for one feature | Same scope test as the integration above |
| `api-error-format` | `doctrine` | The API is one specific part; errors in general would be the steering function folder |
| `accessibility-standards` | steering function folder | Accessibility in general, not one part |
| `release-process` | `playbook` | How to operate the release of a new version |
| `auth-and-security` | split by role: steering function folder (`auth`, how the whole system is authorized) and `doctrine` (how auth is to be written) | One file, two roles |
| `styles-layout` | `structure` | Where styles are defined and how they are organized |
| `database-choice-reasoning` | outside this taxonomy (decision record) | The reasoning behind a choice is a decision record; where it is written is not governed here |
| `content-moderation` | outside this taxonomy | Not `product`: product holds only the product-level overview, and moderation is detail beyond it |
| `pii-logging-rules` | steering function folder or `doctrine`, decided by what it describes and its range | If it covers the system in general, it is the steering function folder. If it covers one part (logging), it is `doctrine`. If it mixes both, split it by role |

### Items that are not steering documents

| Item | Destination |
|---|---|
| "Read the docs, understand the codebase, then start writing code" | outside this taxonomy |
| "How to write commands and which package manager to use" | outside this taxonomy |
| "How steering files are written" | outside this taxonomy (it lives in [documentation-conventions.md](documentation-conventions.md)) |
| An onboarding guide for newcomers | outside this taxonomy |
| A data schema reference, an API reference | outside this taxonomy (reference documentation) |

Everyday items that do belong in a steering folder are shown in each folder's own document: recipes in [playbook](playbook.md), guidelines and mandates in [doctrine](doctrine.md), the "we use X" line in [stack](stack.md), the whole-product overview in [product](product.md).
