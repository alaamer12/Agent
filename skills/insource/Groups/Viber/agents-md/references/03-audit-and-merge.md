# Auditing and merging an existing `AGENTS.md`

Most projects do not need a new file; they need the existing one organized, fenced, and stripped of the
paragraphs that turned into documentation. agents-md's job in that case is **triage, not rewrite**. The user
wrote those rules, often after being burned. Deleting one because it did not fit my template is a real loss.

## The pass

1. Read the file in full. Note line count and where it is bloated.
2. Classify every rule, block, and table into one of the twenty-three sections - or into one of three exits:
   **move out**, **merge with** (duplicate rule elsewhere in the file), **drop only with the user's ok**.
3. Build the map table and show it before writing anything.
4. Ask the user about the moves that change meaning (see "conflicts" below).
5. Rewrite using the template, carrying the content in, then diff-check that no rule vanished.

## The map table

```text
existing content                                   | -> | action
---------------------------------------------------+----+------------------------------------------
"Read these 5 steering files at conversation start" | 2  | keep; add the excluded-scope column
"Current version is V1, ignore v2/"                 | 2  | merge into the active-context table
Version format + increment duty                     | 3  | keep, compress to 3 bullets
Tray icon / channel-isolation prose (34 lines)      | -  | MOVE OUT -> docs/channel-identity.md, pointer here
Units duty (read/reuse/update)                      | 4  | keep; add "same task, not follow-up"
Skills table + "state which you used"               | 1  | keep as a stable behavioral rule
Pool notation x->2x->4x + max 4 depths              | 10 | keep; add worker cap and failure handling
Subagent duties 1-5 + baseline block                | 10 | keep; regenerate block from final sections
"Prefer CMD over PowerShell"                        | 6  | keep, keep the reason
Shared blocks import table (@kit/shared)            | -  | MOVE OUT -> a tech conventions doc
Debugging escalation ladder                         | 8  | keep
```

## Move-out decisions

Content moves out when it **describes** rather than **obligates**, or when it duplicates a document that
already owns it. The test is not "is it long" - a five-line prohibition is fine here; a two-paragraph
explanation of an architecture is not.

When moving out, three options and only these:

1. **Pointer to an existing file** - best case; the content already lives somewhere and section 2 gains a row.
2. **Pointer to a file that does not exist yet** - then the rule is a dead reference: say so in the report and
   let the user decide whether to create it (not agents-md's job to create it) or keep the content inline.
3. **Keep inline anyway** - legitimate for short, high-frequency rules where a hop costs more than the drift
   risk. Write the reason in the map so the choice is visible later.

Never "move out" into silence: an unreported deletion is how a rule like *never commit to `main`* disappears.

## Conflicts and stale content

| Situation | Handling |
|---|---|
| Two rules contradict (one says squash-merge, another says preserve history) | **Ask.** Do not pick. This is a decision the user owns and probably does not know is open |
| A rule contradicts the codebase (says `v1` is current; `v3` exists) | Report the mismatch; propose the fence update; do not silently switch the scope |
| A rule references a path that no longer resolves | Move to the dead-reference list; do not delete the rule - the target may be deliberately pending |
| The file is written for a different harness (`.cursor/rules`, Copilot syntax) | Keep the paths that still exist; note which are harness-specific; the tool-neutral form is `AGENTS.md` |
| Two versions of the same rule (DRY violation) | Merge into the section that owns it and cross-reference; state which copy survived |
| The baseline subagent block disagrees with the body | **Body wins**, then regenerate the block. The block is a projection ([`05`](05-delegation-and-subagents.md)) |

## Foreign managed blocks

Other tools write their own regions into the instruction file - for example a pinned-skills block between two
HTML comment markers. Rules for those:

- Copy the region **verbatim**, markers included, in the same relative position (usually near the top).
- Never edit inside the markers; that region belongs to another tool's command, and its next `sync` will
  replace only what is between them.
- Count it in the report: `preserved the managed block on lines 12-24 (owned by theskills)`.
- If the foreign block is empty or broken (unbalanced markers), report it rather than fixing it.

## What a finished merge looks like

The user should be able to answer, from the report alone: what stayed, what moved and to where, what was
dropped with their approval, what is dead, what is pending, and how many lines it cost. If any of those is
missing, the audit was not conservative enough - the failure mode of this task is not ugliness, it is quiet
information loss in the one file every session depends on.
