# Stress test: am I confused about where this goes?

> This document is a self-check for placing a document. It lists the signs that you are confused, says which rule in [placement.md](placement.md) resolves each, and records how 30 representative files land. It does not define the rules; [placement.md](placement.md) owns them. The folders are listed in the [index](index.md).
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).

## How to use this

1. Run the document through the ordered decision flow in [placement.md](placement.md).
2. If one folder fits, place it there. You are not confused.
3. If two folders fit, apply the boundary test for that pair in [placement.md](placement.md).
4. If it is still unclear, or the file mixes several concerns, split it by role (the golden rule in [placement.md](placement.md)) and place each part separately.
5. If a part still fits nowhere, check whether it is outside the taxonomy before you invent a folder.

## Signs you are confused

| Sign | What it usually means | Rule that resolves it |
|---|---|---|
| The file fits two folders | Two roles in one file, or a scope question | Boundary test for that pair, then split by role |
| The file is about one feature but also reads as system-wide | A feature, or a capability the whole application is built around | Feature-deletion test and the whole-application check |
| A mandate reads as general, but names one part (the API, logging, tests) | Scope: system in general versus one specific part | Scope test between the steering function folder and `doctrine` |
| The file explains why a technology was chosen | A decision record | Outside the taxonomy; `stack` only states what is used |
| The file lists what data exists or what an interface exposes | Reference documentation | Outside the taxonomy |
| The file is about naming | Folder and file names, or identifiers inside code | Folder and file names: `structure`. Identifiers inside code: outside the taxonomy |
| The file is a list of steps and also states a policy | Two roles | Split by role: steps to `playbook`, policy by scope |
| The file is for newcomers, a glossary, a roadmap, or an incident record | General or reference content | Outside the taxonomy |
| You want to create a seventh folder | A missing rule or an outside document | Re-check the outside list in [placement.md](placement.md) first |

If none of these resolves it, the gap is in these docs, not in your file. Record the file, the two folders that fit, and the test that failed to decide, and raise it with whoever owns the taxonomy. Do not pick silently.

## The 30 test files

These files were used to test the taxonomy. The names are generic. "Outside" means outside the steering folders; see [placement.md](placement.md). Where a file has two parts, it is split by role.

| # | File | Destination | Deciding rule |
|---|---|---|---|
| 1 | `video-upload` | outside (feature documentation) | One feature |
| 2 | `recommendations` | outside (feature documentation) | One feature |
| 3 | `live-streaming` | outside (feature documentation) | One feature |
| 4 | `error-ux` | steering function folder | Errors in general |
| 5 | `client-lifecycle` | steering function folder | The whole application |
| 6 | `notification-delivery` | steering function folder if it is the system's shared way of delivering notifications; the feature's documentation if it exists for one feature | Whole application versus one feature |
| 7 | `payment-provider-integration` | steering function folder if the whole application relies on it; otherwise the feature that owns it | Whole application versus one feature |
| 8 | `media-transcoding-integration` | steering function folder if media processing is a capability of the whole application; otherwise the feature that owns it | Whole application versus one feature |
| 9 | `tech-stack-overview` | `stack` | What is used |
| 10 | `module-layout` | `structure` | Where things live |
| 11 | `code-naming-conventions` | outside if it covers identifiers inside code; `structure` if it covers folder and file names | Naming split |
| 12 | `database-schema` | outside (reference documentation) | Reference documentation |
| 13 | `api-reference` | outside (reference documentation) | Reference documentation |
| 14 | `test-quality` | `doctrine` | One specific part |
| 15 | `data-deletion` | `doctrine` | One specific part |
| 16 | `api-error-format` | `doctrine` | The API is one part |
| 17 | `pii-logging-rules` | `doctrine` or steering function folder | What it describes and its range |
| 18 | `accessibility-standards` | steering function folder | Accessibility in general |
| 19 | `auth-and-security` | split by role: steering function folder (how the whole system is authorized) and `doctrine` (how auth is to be written) | Golden rule |
| 20 | `release-process` | `playbook` | How to operate a release |
| 21 | `database-choice-reasoning` | outside (decision record) | Decision record |
| 22 | `content-moderation` | outside | Detail beyond the product overview |
| 23 | `run-in-docker` | `playbook` | How to operate |
| 24 | `seed-100-videos` | `playbook` | How to operate |
| 25 | `onboarding-guide` | outside | General guidance |
| 26 | `product-vision` | `product` | Product-level overview |
| 27 | `monetization-and-business-goals` | `product` | Business objectives |
| 28 | `roadmap` | outside | Roadmap |
| 29 | `glossary` | outside | Glossary |
| 30 | `outage-postmortem` | outside (incident record) | Incident record |

## Caveats

The 30 files are a constructed test, not real documents. The boundary between the steering function folder and `doctrine` is a judgment of scope and has not been tested on real documents (see the caveat in [placement.md](placement.md)). If real files land differently, update [placement.md](placement.md) and then this table.
