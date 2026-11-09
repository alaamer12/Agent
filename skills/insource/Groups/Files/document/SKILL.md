---
name: document
description: 'Markdown documents: five jobs, the default entry whenever a task produces, restructures, shortens or rewords a document - self-invoked, not only when /document is typed. WRITE a new document (normal/comprehensive/concise) matching the user''s purpose and evidence rules. REORGANIZE a messy doc set into one-concern-per-file with a README per directory as the map. SEPARATE the subject the user names into its own readable document. SUMMARIZE without losing meaning (normal/extreme): TL;DR, executive summary, digest, recap. REPHRASE sentence by sentence - improve grammar, flow and word choice only inside each sentence, preserving structure, boundaries, claims, certainty and the author''s voice; return the reworded text alone. Triggers: ''write a report about X'', ''refactor these docs'', ''separate X from Y'', ''summarize this'', ''rephrase this''. Each job loads only its own method; modes are named in the request. Restructuring pair: separate first, then reorganize. Not for code, slides, or spreadsheets.'
when_to_use: Any task that produces, restructures, shortens or rewords a Markdown document — writing one, reorganizing a doc set, giving a named subject its own document, summarizing/condensing a source, or rephrasing sentences without touching structure — whether or not the user names this skill.
argument-hint: "[what to write, the docs to reorganize, the seam to cut, the source to summarize, or the text to rephrase]"
---

# Document

Five jobs on Markdown documents. Use this skill on your own whenever a task produces, restructures,
shortens or rewords a document — the user rarely names the job.

## Which job

| The request looks like | Job | Load |
|---|---|---|
| "write a document/report about X", "give me a transcript of what we did", "document this investigation" | **A — write** | `references/write.md` |
| "refactor these docs", "reorganize the docs folder", "these files are a mess", "our docs keep repeating the same stuff", "give this folder a proper structure" | **B — reorganize a set** | `references/reorganize.md` + `references/restructuring-rules.md` |
| "separate the state machine from the architecture doc", "give X its own document", "X shouldn't live inside Y's doc", "this file documents two things" | **C — separate the named seam** | `references/separate.md` + `references/restructuring-rules.md` |
| "summarize this", "condense", "distill", "TL;DR", "executive summary", "digest", "recap", "shorten this" | **D — summarize** | `references/summarize.md` |
| "rephrase this", "word these sentences better", "fix the awkward phrasing" — same length, same structure, better sentences | **E — rephrase** | `references/rephrase.md` |
| "split this doc up", no subject named | One question: **which subject must stand alone?** Named → C. Only "it's too big / unfocused" → B. | |
| Both restructuring complaints at once | **C first, then B** — reorganizing first moves content around a seam you then cut again | both |
| Removing AI-flavored writing specifically | **E** only when the fix is per-sentence within the source's voice; otherwise `humanizer` does the de-AI job | — |

The line between B and C: in **B you find the boundaries** by reading the whole set; in **C the user has already named the boundary** and your work is to cut exactly there. Inventing a seam in C is a failure even when the result is tidier.

The line between D and E: **D makes it smaller** (selects what survives, may restructure); **E keeps everything** and improves only inside each sentence — never merges, splits, or trims. "Rephrase" is not a euphemism for "summarize".

## Translation is not a job

Agents translate natively - no method file, nothing to load. When a request is "translate this document", just do it, under four general rules:

- the source's Markdown skeleton survives exactly as job E preserves it: same headings, lists, blocks, order, and sentence boundaries where the target language allows them;
- code, commands, paths, numbers, ids and quoted literals stay **verbatim** - they are not prose;
- a term the project's glossary defines translates **as that term** consistently (see `glossary-md`); an undefined contested term is asked once, not improvised per occurrence;
- the output is the translated text alone - same discipline as E: no preface, no commentary, no change log.

## Load exactly one job

The five jobs share nothing operational. The table above names one job file per job; load that file and nothing else.

- A summarize request never reads the writing, reorganizing, separation or rephrasing material, and a write request never reads the restructuring rules. Each job file is self-sufficient. A rephrase job reads nothing about compression or structure changes — its whole discipline is staying inside the sentence.
- Modes belong to their job and are named in the request. **Write:** normal (default), comprehensive, concise. **Summarize:** normal (default) or extreme, plus reserved vs. custom output structure. A mode selects a reference *inside* that job's file — it never pulls in another job.
- Only the two restructuring jobs share one file (`references/restructuring-rules.md`), and only they load it.

## The jobs, one line each

### A — write · `references/write.md`

Produces a document that does not exist yet, matching the user's purpose, audience, scope and detail; never invents evidence; loads one style reference (normal, comprehensive, concise).

### B — reorganize a set · `references/reorganize.md`

Turns a messy set of existing docs into one concern per file with a README per directory as the local map. Read everything, map concerns, design the tree, get the plan approved, then migrate. Its full procedure — including when to load the structuring conventions, the plan template and the self-check — is in the file.

### C — separate the named seam · `references/separate.md`

Gives the subject the user named its own independently readable document while the real relationship survives as accurate cross-references. Full procedure, independence bar and ownership rules are in the file.

### D — summarize · `references/summarize.md`

Reduces a longer source without losing the meaning the reader needs: read for the point, select per mode, compress ideas rather than sentences, verify against the source. Its reference set, templates, examples and the size-report script are all listed in the file.

### E — rephrase · `references/rephrase.md`

Improves the saying, never the said: sentence-by-sentence work on grammar, naturalness, word choice, flow and concision, with structure, sentence boundaries, claims, certainty and the author's voice preserved, and a final skeleton pass that restores any drift back toward the source. Output is the rephrased text and nothing else.

## What this skill is not

| Not this | Go instead |
|---|---|
| Code, scripts, implementation artifacts | the project's own conventions |
| Slides, spreadsheets, PDF or Word output | the dedicated format skills |
| A new project's README | `readme-md` |
| Incident reports and postmortems | `postmortem` (with this skill's write job for the prose) |
| Reorganizing code, modules, or source file layout | `senior-refactor` |
| Deciding what a system *should* be | `detailsup`, `dtb` |
| Prose review for AI-sounding writing | `humanizer` (job E rewords within the author's own voice; removing AI tells is a different goal) |

## Layout

```
document/
├── SKILL.md                              this file — job choice and the one-file loading rule
├── references/
│   ├── write.md                          job A procedure + mode table
│   ├── guidelines.md                     write mode: normal
│   ├── comprehensive.md                  write mode: comprehensive
│   ├── concise.md                        write mode: concise
│   ├── reorganize.md                     job B procedure
│   ├── separate.md                       job C procedure
│   ├── restructuring-rules.md            the rules binding B and C only
│   ├── structuring-conventions.md        job B structure and naming principles
│   ├── example-readme.md                 job B worked README and opening contract
│   ├── summarize.md                      job D procedure + reference/template index
│   ├── rephrase.md                       job E procedure + preserve list + skeleton check
│   └── 01-…07-*.md                       job D detail, loaded from summarize.md
├── templates/                            B: plan + self-check; D: tldr, executive summary, digest, recap, extreme, conversation
├── examples/                             B: concern-mixing cases; D: normal-vs-extreme, reserved-vs-custom
└── scripts/                              D: size_report.py + fallback
```
