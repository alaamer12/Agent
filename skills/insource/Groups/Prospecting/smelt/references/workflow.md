# The smelt workflow

The sequence is fixed because each step depends on the state the previous one leaves behind:

```
inventory → fold file by file, folder by folder → reconcile all folders globally → package
```

Do not parallelise the fold. One agent, one running state, is what keeps the vocabulary consistent and the deduplication honest.

## 1. Resolve and inventory

Before reading anything:

1. Confirm the source is a mining run. A run has `experience/`, `distillation/`, or at least `sources/` with a plan. If it has none of these, say what it actually is and stop.
2. List the folders and files with sizes. Write the first version of `sources.md` in the destination: every file, its role, and whether it will be read or skipped.
3. Establish the read order. The default is scope → experience → distillation → witness → tools. If the request names a starting folder, start there and continue with the rest afterwards; a partial order is still an order.
4. Read the plan before the first checkpoint. It supplies the vocabulary and the questions the run was built to answer, so the first knowledge file does not invent its own frame.
5. Sweep the corpus for every URL it references — checkpoint closing ledgers, the distillation bibliography, inline citations, and `scratch/` URL lists if the run kept them — and write `provenance/links.md` with one row per unique URL: the URL, the files citing it, status `unchecked`. Mining runs accumulate references precisely because they were alive when touched; by smelt time they may not be, and only checking says which. The check pass itself runs before delivery (§5); nothing sampled. The sweep is grep-level reading of files for URLs — it does not contradict "read only knowledge folders for content."

### Folder order and nested folders

Every folder that carries knowledge gets its own knowledge file, including nested folders. Walk the tree **deepest first**:

- Enter the deepest folder that still has unprocessed files. Fold its files into its own knowledge file, close it, and move up.
- A parent folder's own files are folded **after** its child folders are closed.
- Never fold a child's knowledge into the parent's file. The child file stands on its own; the global pass is the only place folder files meet.
- Name each fold file after the folder's relative path, not its bare name, so two nested folders with the same name cannot collide: `provenance/fold/experience__atlas.md`.

This order matters because a nested folder is often where the concrete evidence lives, while the parent holds the summary or the index. Reading the concrete layer first gives the parent's files something real to be checked against.

If the run is pre-plan — candidates only, no checkpoints — produce a candidate dossier instead of a knowledge base: one account per candidate with why it was selected, what was verified, and what is still unknown. State plainly that no knowledge was mined yet.

## 2. Fold one file

For each file, in the order recorded in `sources.md`:

### Read it in full

Read the whole file before writing anything. For a file too large for one pass, read it by section and keep the section names and line ranges; never sample it and never substitute a summary for the read.

While reading, note:

- claims the source asserts outright
- claims the source infers, and its evidence
- numbers, with their unit and measure
- decisions, with the alternative they displaced and the cost
- things the source tried and could not establish
- places where it contradicts something already in the knowledge file

### Open the folder knowledge file

The folder knowledge file is the only artifact edited during the fold. After the first file it already exists; integrate into it rather than writing a new one. Read its current contents before deciding anything, so the comparison is against what is actually known, not against memory.

### Integrate, one piece at a time

For each candidate, find whether the knowledge file already contains it. Compare on meaning, not wording: same subject, same scope, equivalent assertion.

| Finding | What happens |
|---|---|
| Nothing similar | Add it, in the form the material suggests |
| Same knowledge | Combine the evidence; raise confidence only if the new evidence is independent |
| Same subject, different scope | Keep both, and link them as variants |
| Same subject, incompatible assertion | Keep both side by side, and write what turns on the disagreement |
| New evidence shows an earlier reading is wrong | Mark the earlier piece corrected, with the reason; write the current account |
| Related but distinct | Keep both, and add the connection |

Do not touch pieces the file does not implicate. Do not rewrite the whole knowledge file on every pass; edit surgically. A full rewrite per file is how detail erodes.

Write each piece as prose, notes, a table, or whatever shape carries it best. There is no required structure. What matters is that a reader can answer the six floor questions from `knowledge-model.md` without opening the source.

### Record the file

Append to the knowledge file's source note: file path, what it contributed, and anything it raised that is still open. Append the same line to `sources.md`.

Keep a **fold tally** while reading: the file's substantive knowledge units and their outcome — new, merged-into-existing (still represented), correction, noise/boilerplate (excluded from the denominator), derived-repeat. At record time write the file's **smelt yield**: the share of its substantive units now represented in the base — (new + merged + corrected) ÷ substantive. "80%" is a meaning-share, not a byte count, and it is honest arithmetic only if the tally was kept — a low yield gets the reason in one line (thin checkpoint, duplicate of an earlier file, pure navigation content). The numbers land in `provenance/yield.md`, sorted highest to lowest.

### Update the question ledger

The knowledge file keeps the open questions the fold is carrying. A file may answer a question raised three files earlier — close it and name the knowledge that resolved it. A file may raise a new one — add it. Unresolved questions become gaps at the end; they are not dropped.

## 3. Close the folder

When every file in the folder is folded or recorded as skipped:

1. Check that every file has a source note and appears in `sources.md`.
2. Leave the folder knowledge file exactly as the fold left it. Do not re-read it, regroup it, retitle it, or compress it.
3. Move to the next folder and repeat the same procedure.

The folder file is meant to be uneven at this point: pieces were corrected one file at a time, and duplicates that only become visible across the whole folder are still present. That is intentional. There is exactly one compression pass, and it happens after every folder is closed, over all the folder files together.

## 4. Reconcile globally

After every folder is closed, read all the folder knowledge files together. This is the run's only compression pass. Do not reopen the raw source files; the folder files are the input to this pass, and the raw corpus remains the evidence of record.

The global pass does five things:

1. **Merge across folders.** The same knowledge may appear in the experience file and the distillation file. Merge on meaning, combine the evidence, and apply lineage: distillation evidence is `derived` and does not corroborate the checkpoint it came from.
2. **Resolve cross-folder contradictions.** Two folders may hold incompatible claims about the same subject. Keep both, say what each claims and what turns on the difference. Do not choose a winner unless a source explicitly does.
3. **Reorganise the writing.** The delivered base is for a consumer who wants knowledge, not a tour of the run. Arrange it in whatever shape the material supports: by theme, by kind, by product, or as one continuous argument. It may be one file or several. Each delivered file owns a distinct body of knowledge; when two files would cover the same piece, one file owns it and the other links to it. Keep the folder files as provenance.
4. **Link the files.** The base is a graph, not a folder of orphans. Every delivered file names the files it depends on and the files that depend on it, and every cross-file reference resolves. `INDEX.md` is the hub, but sibling files link directly as well.
5. **Build the navigation layer.** The index, the topic routes, the term list, the contradiction list, the file map, and the gaps all come from what was actually written. So do the two accounting surfaces: the yield table (per-file smelted share, sorted, with the corpus-weighted total) and the link-status summary (alive / redirected / dead / recovered counts).

Compression here means deduplication and correction, never shortening a piece that carries unique detail.

## 5. Verify before delivery

This check has two halves, and they split on one line: **what can be measured is measured by a script; what needs judgment is walked by the agent.** A run that hand-rolls its own sweep, or samples what should have been swept, discovers neither the coverage gap nor the artifact that contradicts its own ledger.

`scripts/smelt_check.py` runs the measurable half — `package` for structure, `quotes` for verbatim spans against the cached corpus, `links --sweep` for live status with redirect chains and retained receipts. It is **advisory**: it prints findings with ids, and nothing is blocked by them. Every finding gets one of two answers before delivery — fixed, or waived with a written reason in the waivers file, in the same shape as the skill's other recorded decisions. An unwaived, unfixed finding at delivery is the failure; a green script is not a pass, because the script cannot tell a good base from a confidently written bad one. Point it at the destination *before* the cache folder it writes is declared, and re-run after any fix, since a correction moves a count.

Judged, by the agent, walked against the delivered files:

- **Evidence.** Pick a sample of claims across files. Open the cited file and confirm the quoted words are there at the cited location. A fabricated or drifted quote is a blocker, not a note. (The script's full-corpus span audit narrows *what* to look at; it does not decide whether a near-match is a quotation.)
- **Coverage.** Every file listed in `sources.md` is either represented by one claim or marked skipped with a reason. A file read but contributing nothing is recorded as confirming or as empty — not omitted.
- **Yield.** Every `read in full` file has a smelted percentage in `provenance/yield.md`, sorted top to bottom, low yields explained, the weighted total stated; percentages reconcile with the fold tallies recorded during the fold, not recomputed from memory at the end.
- **Uniqueness.** Two signals, and they are not the same claim. Near-verbatim text is a duplicate and gets fixed (`duplicated-finding`). Two passages resting on the same specific names is a **reading list**, not a verdict (`shared-evidence-review`): measured on a real package, four in ten such pairs restated one claim and the rest were one piece of evidence legitimately cited for two different claims — which no threshold separates, because the difference lives in the assertion, not the text. Read the list, merge what repeats a claim, and leave what shares evidence, naming the owner where a card borrows another's material. Judge the delivered knowledge *and* the files that describe the package: `README.md` and `INDEX.md` restate findings like anything.
- **Lineage.** Any evidence marked independent traces to a different raw source or a different run. Anything derived from a file already in evidence is marked derived.
- **Gaps.** Every unresolved question and every "not measured" from the corpus appears in the gaps.
- **Cold read.** `INDEX.md` plus the knowledge files answer the corpus's own questions without opening `experience/`.
- **Writing.** A reader who has never seen the source can follow the claim, the mechanism, the cost, and the evidence.

Measured, by the script:

- **Links — exhaustive, never sampled.** Check every `unchecked` row with a real request, and record what the request actually said: the final address after every redirect and whether it still supports the claim, the check date, and the recovery attempt where it is dead (archive snapshot, or an equivalent source the corpus itself names). Recovered → the knowledge cites live-and-archive; unrecovered → the supported claim's provenance is marked "reference dead as of <date>", its confidence lowered, and a gap line written. The counts must reconcile: unique *addresses* swept = rows with a status, with the non-addresses a regex caught stated separately. A single unverified row fails this check. Label the sweep's depth, and keep a tool's own failure in its own class rather than reporting it as a property of a source.
- **Quote fidelity** across the whole package, not a sample: every quoted span located in the cached primary bytes, in the run's own prose (consistency, not corroboration — say which), or nowhere.
- **File graph.** Every delivered file is linked from `INDEX.md` and from at least one sibling, every cross-file link resolves, no file is an orphan — and no directory is undeclared, empty, or heavier than the knowledge it supports.
- **Accounting integrity.** One measurement, one artifact: no two files classify the same set into different partitions without the delivered ledger naming its source; no count in prose disagrees with the tree.

Fix what fails before writing the final report line, and record a reason for anything deliberately left as found.

## Large files

A checkpoint of 30–40 KB is normal; a long-form synthesis can be 70 KB. Read by its own headings, and record the section range for every claim. If a section is pure repetition of an earlier one, add its evidence to the existing piece rather than writing a new one. If a section is noise (navigation, changelog boilerplate), record it as skipped with the reason.

Never chunk a file into summaries and then fold the summaries. The fold reads the file; the knowledge file accumulates claims. Summaries of summaries are the failure this skill exists to prevent.

## Resume

The state is on disk:

- `sources.md` says which files are done.
- `provenance/fold/<relative-path>.md` holds the accumulated folder knowledge.
- `provenance/merges.md` holds what changed and why.
- `provenance/links.md` holds the URL sweep — rows may still say `unchecked` until the verify pass; a resumed run never re-sweeps from zero, it continues the ledger.
- `provenance/yield.md` holds the per-file tallies as they were recorded.

On re-entry, read those three, announce where the run stands, and continue at the first unprocessed file. Do not rebuild a finished folder, and do not re-extract a file already represented unless a verification check failed.

## Edge cases

- **Thin checkpoint.** If a file states conclusions without evidence, keep the conclusion but mark it as inferred and write a gap for the missing support. Do not re-mine the source.
- **Contradictory sources.** Keep both; the disagreement is a finding about the corpus, not a defect to smooth away.
- **A source the run could not reach.** Record it in `sources.md` and in the gaps. Unreachable is knowledge about the corpus.
- **A source that is a duplicate.** Cache pairs, copied notes, retold postmortems: fold the richer copy and record the other as a duplicate in `merges.md`.
- **A folder with no knowledge.** Record it as skipped with the reason. Do not manufacture pieces to justify reading it.
