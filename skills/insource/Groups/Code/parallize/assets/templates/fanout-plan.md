# Fan-out plan (state this in chat before launching)

```markdown
## Fan-out plan — <goal in one line>

**Why parallel:** <the seams: which chunks are independent, and what it saves>
**Snapshot:** <commit / branch / file versions every brief is planned against>

| # | Slice | Output (deliverable) | Owns (paths) | Depends on | Risk | Wave |
|---|-------|----------------------|--------------|------------|------|------|
| 1 | <name> | <file / module / test suite> | <paths> | — | low | 1 |
| 2 | … | … | … | 1's interface | med | 2 |

**Main agent keeps:** <interfaces / sensitive code / destructive steps / shared files / integration>
**Waves:** <wave 1: slices 1,3,4 · wave 2: slice 2 · cap: N>
**Verification:** <commands, per-slice done-when, end-to-end check>
**Out of scope:** <what this run will not touch — the scope fence>
```

Rules for the plan itself:

- Every slice has owned paths and a verification. A row without either is not a slice yet.
- No two rows share an owned path. Shared files appear only under "main agent keeps".
- Waves are justified by dependencies, not by the cap.
- If the table has one row, say "not worth fanning out" and do it directly.
