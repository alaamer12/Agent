# Steering Files: The Six-Folder Documentation Taxonomy

> This is the entry point and map of the steering taxonomy: what steering files are, the six steering folders at a glance, and where each part is documented. Every other document in this set owns one concern in full; start here to find it.
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).

This document set defines how project knowledge is organized into six **steering folders**, how those folders relate to the rest of the documentation (feature documentation and other documentation), and the conventions that keep the wiki accurate for both humans and agents.

You must update this file whenever a document is added, removed, or moved.

## Documents

| Doc | What it answers |
|---|---|
| [`index.md`](index.md) | What the taxonomy is for, what is in and out of scope, and where each part lives |
| [`doctrine.md`](doctrine.md) | How should one specific part or task be done, and what is mandated for it? |
| [`stack.md`](stack.md) | What is the project built with? |
| [`structure.md`](structure.md) | How is the project organized? |
| [`product.md`](product.md) | What is the product, for whom, and why? |
| [`function.md`](function.md) | How does the system work as a whole, beyond any one feature or part? Also holds the terminology rule for the steering function folder |
| [`playbook.md`](playbook.md) | How do I operate this specific task? |
| [`placement.md`](placement.md) | Which folder, or which non-steering home, does a document belong in? |
| [`stress-test.md`](stress-test.md) | Am I confused about where this goes, and how did 30 representative files land? |
| [`layout.md`](layout.md) | How is the steering tree laid out, indexed, split into areas, and entered by agents? |
| [`migration.md`](migration.md) | How are the legacy docs moved into this taxonomy? |
| [`documentation-conventions.md`](documentation-conventions.md) | How are steering files written and edited? Read it before writing or changing any steering file |

## Purpose and scope

The documentation wiki belongs to a web platform. It already holds files such as `external-provider-integration`, `personalization`, `client-lifecycle`, and `error-ux`. The goal of this taxonomy is to make sure that:

- a newcomer or an agent can find what they need without re-reading everything;
- operational know-how (how to run the containerized setup, how to test inserting 100 records) is not lost as the project grows;
- a fact has exactly one home, so documents do not drift apart;
- guidelines, system-wide functionality, and step-by-step recipes are not mixed.

"Steering files" is the project's term for the six reference folders described here. They are usually placed inside a `.steering/` directory. The project is expected to contain other documentation folders as well (feature documentation, and others such as decision records or incident records), so the steering folders are not the whole wiki. They are the cross-cutting reference layer.

**In scope:** the definition of each steering folder, placement rules, writing conventions, navigation, and migration of legacy docs.

**Out of scope:** the content of any specific document, and tooling that would enforce the rules automatically. Where feature documentation and other documentation live is covered in [placement.md](placement.md). The physical layout of the documentation in a given repository, including how many apps or areas the project has and what they are called, is covered in [layout.md](layout.md).

## The six folders at a glance

| Folder | Question it answers | One-line definition |
|---|---|---|
| [**doctrine**](doctrine.md) | How should this specific part or task be done, and what is mandated for it? | Guidelines for a specific part or task (test quality, how data deletion is handled), including mandated system behavior, with the reasoning behind them |
| [**stack**](stack.md) | What is this project built with? | Languages, frameworks, libraries, databases, hosting, stated as "we use X" |
| [**structure**](structure.md) | How is the project organized? | How the project is laid out and where each kind of thing is defined: architecture, modules, boundaries, folder layout (for example, how styles are structured) |
| [**product**](product.md) | What is the product, for whom, and why? | The product-level overview: purpose, target users, key features at a high level, business objectives |
| [**steering function folder**](function.md) (`function`) | How does the system work as a whole, beyond any one feature or part? | System-wide functionality shared across features and parts (error handling in general, accessibility, lifecycles, shared integrations) |
| [**playbook**](playbook.md) | How do I operate this specific task? | Step-by-step recipes for operating one subject or task (check the database tables, seed test data, run the containerized setup, release a new version) |

Each folder answers a different question and changes for a different reason. A library swap touches `stack` only. A module reorganization touches `structure` only. A new guideline touches `doctrine` only.

General, project-wide, rarely updated guidance on how to do things (how to develop here, how to debug, how to run commands) is not a steering folder. It is outside this taxonomy; see [placement.md](placement.md).

## Inspiration

Agents need steering folders: stable, predictable reference files that tell them what the project is, what it is built with, how it is organized, and what rules to follow, so they do not have to rediscover this on every task. The idea comes from the foundational steering files used by tools such as Kiro, extended here with more folders and placement tests.

## Writing conventions

The conventions for writing and editing steering files live in [documentation-conventions.md](documentation-conventions.md). They are not repeated elsewhere, so there is one owner for them. If that file is missing or renamed, every pointer to it leads nowhere.

## References

- Kiro steering guide (community write-up describing `product.md`, `tech.md`, and `structure.md`): https://dev.to/sienna/kiro-steering-guide-ae7
- Kiro official steering documentation: https://kiro.dev/docs/steering/
