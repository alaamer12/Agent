# Integration and verification

Fan-out ends with one codebase, not N. Integration is the main agent's job and the part that decides whether the run was worth it.

## Merge in dependency order

1. **Main's own slice first** when other slices consume its interfaces — the contract must exist before the consumers land.
2. **Independent slices next**, in any order.
3. **Dependents last**, so they are reviewed against the real upstream result rather than a stub.
4. **Shared files at the end**, written once by their owner (usually the main): indexes, registries, lockfiles, generated output.

## Resolving conflicts

- The interface decided before launch wins over any slice's interpretation. If a slice changed the contract unilaterally, the contract wins and the slice is corrected.
- A conflict in a shared file is not a merge problem, it is an ownership problem — fix the ownership table, not just the file.
- Two slices implementing the same helper is the normal failure mode: keep one, delete the other, and note it.
- Never resolve a conflict by keeping both versions "to be safe". That is how duplication ships.

## Verify per slice, then together

For each slice, against its brief:

- done-when checks actually ran, with output;
- writes confined to its owned paths;
- no cross-slice imports that were not agreed;
- no leftover TODOs or stubs unless they were declared in the return.

Then for the whole run:

- the project's own build, test, and lint commands (not the slices' private ones);
- the end-to-end path the plan was meant to deliver;
- the diff read as a whole — a fan-out often produces consistent-looking parts that do not compose.

## The review pass

One final read-through with the whole picture, by the main agent or a single reviewer subagent that sees every slice's diff and the plan. A reviewer may fix integration wiring and missing tests; it must not rewrite architecture or re-open settled decisions. Report its findings rather than silently patching judgement calls.

## Final report

State, in chat:

- the planned slices and which ran in which wave;
- what the main agent did itself;
- what each slice returned, and anything re-run or reclaimed;
- duplicate or discarded work, and why;
- verification results (commands, pass/fail);
- what remains open, and what was not parallelized on purpose.

The report is also the audit trail for the next fan-out: it shows whether the cut was right, which is what improves the next plan.
