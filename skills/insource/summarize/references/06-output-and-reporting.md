# Output location and size reporting

Content and structure are decided by the other reference files. This one governs *where the summary goes* and *what gets reported alongside it* — mechanical rules, applied the same way regardless of mode.

## Where the summary goes

**Source was a file the agent read from disk:**
- Write the summary to the **same directory** as the source file.
- Name it with the prefix `summarized_` followed by the original filename (preserve the original extension unless the user asked for a different format): `report.docx` → `summarized_report.docx`; `notes.md` → `summarized_notes.md`.
- If the user specified a different output location or filename, honor that instead — the prefix rule is the default, not an override of an explicit instruction.
- Present the file to the user per the standard file-delivery mechanism; do not just describe it.

**Source was pasted or typed directly into the conversation (no file):**
- Deliver the summary **inline, in the chat reply**.
- Only write it to a file instead if the summary itself is long enough that a file is the better delivery mechanism (a genuinely long digest or detailed recap), or if the user asks for a file. Short-to-medium summaries of pasted content stay in the chat — do not create a file by default just because summarization happened.
- If writing to a file for this reason and no source filename exists to prefix, use a short descriptive name (e.g. `summarized_notes.md`) rather than inventing an unrelated one.

## Reporting size, before vs. after

For any file-based summarization task (source read from disk, output written to disk), report the size reduction alongside the delivered summary: lines, words, and characters for both source and summary, plus the percentage reduction on each metric.

Use `scripts/size_report.py` — pure standard library, no dependencies:

```bash
python3 scripts/size_report.py <source_path> <summary_path>
```

If Python is unavailable in the environment, use the bash or PowerShell equivalents in `scripts/size_report_fallback.md` — same three metrics, same shape.

For pasted-content summaries delivered inline, still give a one-line reduction note if it's easy to compute (e.g. "≈420 words → ≈60 words, an 86% reduction") — full multi-metric table formatting is optional here, but *some* size signal should accompany the summary so the user can gauge how much was cut.

## Quality checks

- [ ] File-sourced summaries were written next to the source, prefixed `summarized_`, unless the user specified otherwise.
- [ ] Pasted-content summaries were delivered inline unless length or an explicit request called for a file.
- [ ] A before/after size report (lines, words, characters, % reduction) accompanied any file-based summary.
- [ ] Pasted-content summaries carried at least a brief size signal.
