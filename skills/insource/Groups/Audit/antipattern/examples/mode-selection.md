# Mode selection: examples

| User request | Discovery result | Mode | Handling |
|---|---|---|---|
| "Find unnecessary type casts and suppressions and document rules for them." | Nothing | A | Investigate casts and suppressions only. Write `ANTIPATTERN.md`. No `/inquire`. |
| "What anti-patterns should we avoid in this repo?" | Nothing | C | Full research and investigation. `/inquire` for choices. Report plus spec. |
| "Update our anti-pattern rules." | `ANTIPATTERN.md` with 8 rules | B | Check the 8 rules against the code. Report violations and proposals. Edit only on agreement or explicit request to update. |
| "Check the payment integration for fragile error handling." | `ANTIPATTERN.md` exists | A | Investigate the payment integration. Add results to the existing file. |
| "Audit and then fix the anti-patterns." | Nothing | C | Do the audit and spec. Decline the fixing part: outside this skill, offer a handoff. |
| "Is this code AI slop?" (one file pasted) | n/a | A | Treat as a focused pattern check on that code. Name concrete defects, not authorship. No project-wide audit. |
| "Set up anti-pattern docs." | AGENTS.md has a "Pitfalls" section | B | Treat the Pitfalls section as existing documentation. Update it instead of creating a new file. |
| "Review my PR." | Nothing | none | Not this skill's job. Do a normal review, or offer an anti-pattern audit separately. |
