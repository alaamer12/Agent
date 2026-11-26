# Documentation Conventions

> General conventions for authoring and editing steering files across the Two-Tier Steering Taxonomy. Read this document before writing or updating any steering file. See [`index.md`](index.md) for the master index.

1. **One fact, one file.** Every fact has exactly one canonical home, including across `shared/` and area copies. When two folders or tiers touch the same fact, the fact lives in its single owner file and related files link to it. Never duplicate a fact.
2. **One fact, one file ACROSS TIERS.** Do not restate a business policy in `tech/` or an engineering standard in `perception/`. A technical document links to the perception document it implements.
3. **Passage-level splitting.** Always split mixed source material by passage rather than assigning an entire file or prompt block to one folder. Evaluate each sentence or paragraph against the Tier Test and folder boundary tests.
4. **Cross-tier link direction (strict).**
   - Documents in `tech/` link to their governing concepts in `perception/`.
   - Documents in `perception/` **never link to `tech/`**.
   - *Rationale*: This guarantees that `perception/` remains strictly stable across technical rewrites, framework migrations, and refactoring without experiencing link rot.
5. **Describe behavior, not fragile mechanism.** Especially in `doctrine` files that state system behavior. The enforcement mechanism can change without making the document obsolete.
6. **Write general principles in free plain text.** Express rules and concepts as plain-language prose rather than fragile lookup tables unless the content is genuinely a key-value lookup.
7. **Keep rationale next to the thing it explains.** Record reasons that come from project requirements or maintainers. If a reason is inferred, state so clearly. Never invent history.
8. **Name files after the concern they hold.** File names should be obvious and descriptive (e.g., `user-tiers.md`, `non-negative-balance.md`) so an agent can locate them without opening every folder.
9. **Do not normalize formats across files.** Match the format to the concern: prose, table, checklist, diagram, or code block.
10. **Terminology rule for `function/`.** Inside the `tech/` tier, the directory `function/` is always referred to as the **steering function folder** in prose, headings, index files, and agent output. (Its business-tier counterpart in `perception/` is `capabilities/`, which has no naming ambiguity).
11. **Pattern-first `structure/` files.** Label trees as observed current snapshots, approved targets, or illustrative examples; never make an example path mandatory. Mark growable groups with `...` or `…` and add a compact inline or adjacent rule for membership and the next item. Keep enough examples for orientation, but keep taxonomy, security, contract, and other true closed sets closed. Apply [`structure.md`](structure.md#pattern-first-authoring-rule) directly instead of requiring a later `generalize` pass.
12. **Minimalist shared plus area delta.** Admit content to `shared/` only through the [Universal Scope Test](layout.md#universal-scope-test): every confirmed area must need the same fact without local qualification. Keep shared files free of area material and union summaries. Area files link to the shared owner and contain only their own delta; never copy, clone, shadow, or override it. Follow the [Minimalist Shared Contract](layout.md#minimalist-shared-contract) and [Area Delta Contract](layout.md#area-delta-contract).
13. **No silent drafting open topics.** During Draft [DR], announce every newly discovered question to the user immediately and offer resolution now or explicit deferral. Use only the structured `Pending (Drafting)` marker below; close every marker before declaring Draft [DR] complete.
14. **Living documents show current truth, not migration history.** Replace wrong living content directly during drafting; use ordinary cross-references after relocation. Never write `Moved to`, `retired`, `assume`, `assumed`, or `Assumption` as living-document or report labels. Use `Inferred from <evidence>` for evidence-backed inference and structured `Pending (Drafting)` for explicitly deferred decisions.

---

## Drafting Open-Topic Lifecycle

Pending is a valid Draft [DR] state because later steps reveal questions that earlier steps cannot answer. It is never permission to hide uncertainty.

### 1. Disclose on Discovery

In the same turn that a new unanswered question appears:

1. Stop the affected claim; do not invent an answer.
2. Tell the user immediately: **what is unknown, what it blocks, and where it appeared**.
3. Ask whether to resolve it now or explicitly defer it. If several topics appear, name all of them immediately, then use `close-topics` one at a time. Explicit deferral opens a structured marker; it does not close the topic.

Continuing unrelated drafting is allowed only after the disclosure. Silence, an internal note, or a future handoff is not disclosure.

### 2. Write Only a Structured Marker

When the user explicitly defers, write:

```text
Pending (Drafting) — <question>. Blocks: <claims or paths>. Discovered: <step>. Close before: Draft [DR] completion.
```

- Never write a bare `pending`, `not defined yet`, `not decided`, `TBD`, `TODO`, `to be decided`, `open question`, or empty placeholder.
- Keep interview-ledger statuses such as `Pending interview` and `Awaiting user` in conversation or planning artifacts; do not copy them into project documents.
- When Viber is active, record the question in `memory.md` and put its question ID in the marker. Update both when the answer lands; move the answered question to `settled.md` under Viber's rules.

### 3. Close Before Drafting Completes

Before declaring the full Draft [DR] phase complete:

1. Enumerate every `Pending (Drafting)` marker and every open/deferred Viber memory question affected by the drafting work.
2. Use `close-topics` to resolve them one at a time with the user.
3. Replace each marker with the settled content in its canonical owner, or remove the affected section when the user retires it.
4. Update the memory ledger, links, and agreement matrix where applicable.
5. Re-sweep for bare unresolved markers.

**Zero structured pending markers is the completion gate.** If the user cannot or will not answer, report the exact blockers and keep Draft [DR] incomplete; never silently carry them into implementation.

---

## Mandatory Tech Directory Interview and Authoring Gate

Apply this gate to **every existing or planned** `tech/<area>/stack/`, `structure/`, steering function folder (`function/`), `doctrine/`, and `playbook/` directory. `shared/` and each confirmed application area have separate rows. A folder is **Not applicable** only when absent and the user confirms no content is planned for it. Process one directory at a time, normally `stack/` → `structure/` → steering function folder → `doctrine/` → `playbook/`; dependencies may reorder the rounds, but no row may be skipped.

### 1. Interview Each Directory Separately

1. Read the folder's governing reference and gather evidence from code, configuration, current steering files, and legacy documentation.
2. Label every claim **Observed**, **User-stated**, **Proposed**, **Unknown**, or **Conflicting**; cite evidence for observed claims.
3. Ask the mandatory questions in the folder reference and all additional forks revealed by the evidence. For choices, use named options with pros and cons plus a recommendation; options are illustrative, and unlisted or hybrid answers are valid. A question may close with an explicit **not applicable** and reason; silence never closes it.
4. Present known facts for confirmation or correction. Existing code, a previous document, a successful lint, or the lack of an obvious fork never waives the interview.
5. Finish the directory with a decision recap and wait for the user's explicit confirmation or explicit delegation of that directory's decisions.

### 2. Maintain the Tech Directory Decision Ledger

Keep one row per directory in conversation or in a user-requested planning artifact:

```text
Directory | Scope | Evidence | Decisions and rationale | User answer/delegation | Open items | Status
```

Use only these statuses:
- **Pending interview**: evidence or mandatory questions are incomplete.
- **Awaiting user**: questions were asked but the directory recap is not confirmed.
- **Blocked**: a contradiction, missing authority, or dependency prevents a reliable answer.
- **Settled**: the user confirmed the directory recap or explicitly delegated its decisions, and no unresolved item affects the intended content.
- **Not applicable**: the folder is absent and the user confirmed no content is planned.

The agent may record a status but may never self-settle a directory. Deferred decisions remain unsettled. Approval of the whole project or the final topology does not settle rows that were never interviewed.

### 3. Block Examination and Design Authoring

For an unsettled directory, do not author its examination, technical design, distribution topology, mapping, steering documents, or speculative drafts. Read-only evidence gathering, questions, and the ledger are allowed. Do not disguise a proposed answer as a verified fact or hide it in an apparently final document.

A Settled directory may proceed independently. Before Phase 2 absorbs its content, Phase 3 presents the complete plan, or Phase 4 materializes files, recheck the ledger. New evidence that changes a settled decision reopens that directory's interview.
