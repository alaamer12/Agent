# Worked example — two waves, main keeps the contract

**Job:** add CSV export of a resource across a service and its client, with tests and docs. Language-agnostic; the
shape is what matters.

## The plan stated in chat

```markdown
## Fan-out plan — CSV export for <resource>

**Why parallel:** the export format is one contract; the server endpoint, client button, and docs do not
depend on each other once the contract exists.
**Snapshot:** main branch at <commit>; export schema frozen in step 0.

| # | Slice | Output | Owns | Depends on | Risk | Wave |
|---|-------|--------|------|------------|------|------|
| 0 | export contract + serializer core | `export/format.*`, `export/writer.*`, unit tests | these paths | — | high | main, before wave 1 |
| 1 | server endpoint | `api/export.*` + handler tests | that folder | 0 | med | 1 |
| 2 | client download action | `client/export/` + component tests | that folder | 0 | med | 1 |
| 3 | docs page + changelog entry | `docs/export.md` | that file | 0 | low | 1 |
| 4 | wiring: route registration, index, dependency manifest | shared files | shared files | 1,2 | high | main, after wave 1 |

**Main agent keeps:** the format contract and serializer (0), all shared files (4), final integration.
**Waves:** wave 1 = slices 1, 2, 3 · then main merges 0, integrates 4.
**Verification:** each slice runs its own tests; main runs the project's full suite and a real export end-to-end.
**Out of scope:** other resources, UI restyling, performance tuning.
```

## What happened

1. **Before the wave**, the main writes the format contract (column order, quoting, encoding, empty-value rule)
   and the serializer, with tests. That is the sensitive part: two consumers will encode it differently if it is
   not fixed first. It is also the only part that cannot be re-run cheaply if wrong.
2. **Wave 1** launches slices 1–3 together, each brief quoting the contract verbatim and listing its owned paths
   plus the do-not-touch list (the serializer, the other slices' folders, shared files).
3. **During the wave**, the main finishes the serializer's edge-case tests — its own slice, not idle waiting.
4. **Slice 2 returns early** with the download action but a stub for "no rows" behaviour. It is not a failure; the
   main names the missing case and re-runs that slice alone with the extra done-when.
5. **Slice 1 and 3 return clean.** The main reviews each against its done-when list, then integrates in dependency
   order: contract → endpoint → client, then the shared files (route registration, index, manifest) written once.
6. **Duplication found:** slice 1 and slice 2 each wrote a tiny CSV line-joining helper. The main deletes the
   client's copy and imports the serializer — the normal fan-out failure, caught in the cross-slice read.
7. **Verification:** full test suite, a real export from the client path, docs example matches the actual output.

## The report

> Ran 3 subagent slices in one wave; main wrote the export contract and serializer and did all integration.
> Slice 2 was re-run once for the empty-export case. Deleted a duplicated CSV helper from the client. Full suite
> passes; end-to-end export verified against the docs example. Not parallelized: shared-file wiring (collision risk).

## Why it worked

- One contract, written by the main, before any consumer existed.
- Disjoint write sets, so the only shared file was the one the main owned.
- Waves sized by the dependency (one wave), not by the cap.
- The main's slice was the risky one, and it was done first.
