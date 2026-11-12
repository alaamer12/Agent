# Waves and limits

## The concurrency cap

Every harness has a maximum number of agents it will run at once — commonly around [20]. Treat it as a hard ceiling, not a target:

- Verify the actual cap when you do not know it; do not assume the ceiling is higher than it is.
- Never plan a wave larger than the cap. Excess agents either fail to start or start late and read stale state.
- The cap governs a moment in time. Waves let you exceed it across the whole job without ever exceeding it at once.

## Sizing a wave

| Work shape | Wave size | Why |
|---|---|---|
| Independent slices, uniform difficulty, cheap review | Up to the cap | Merge cost is low; the cap is the only limit |
| Coupled slices (shared interface, overlapping reading) | [3–5] | Coordination and review dominate |
| Each slice needs the previous wave's output | 1 wave of dependents at a time | The dependency defines the wave |
| Slices with a shared-file edit at the end | Wave, then main-only integration | Shared files cannot be parallel |

Default to the smallest wave that keeps the main agent busy, then grow only while the evidence says it is faster.

## Diminishing returns

Each added agent adds merge work, review work, and context duplication. Stop growing when:

- integration time per wave is longer than the work a wave adds;
- two slices need the same files;
- the review of a wave's output takes longer than doing a slice yourself.

That is the "as possible" rule: parallelize while the job benefits, not until the cap is full.

## Launching

- State the fan-out plan in chat first (`assets/templates/fanout-plan.md`), then spawn the wave.
- Launch a wave's members together so they read the same snapshot; a late starter on a moving tree is the classic drift.
- If the user asked for `with staggering ...`, launch simultaneously is replaced by computed delays: every member still reads the same snapshot, but its own first read is deferred by the schedule. State the delay table with the plan, recompute it per wave (the clock resets), and never let a delay stand in for a dependency. Grammar and safety rules: `06-staggering.md`. With no stagger requested, keep the simultaneous launch.
- Give each brief the exact snapshot (commit hash, file version) it was planned against.
- If the harness isolates agents in worktrees or branches, prefer it for write-heavy waves; the merge rules are in the `branch` skill.
- Anything the main must do before the wave reads it (interfaces, schema, index files) is done before launch, not during.

## Monitoring a wave

- **Progress:** each slice should report a first result early — a created file, a failing test, a diff. Silence past the first checkpoint is a signal, not patience.
- **Stuck agents:** ask for current state instead of waiting longer. A slice with no progress and no clear blocker is mis-scoped; re-brief or reclaim it.
- **Drift:** if a slice starts editing outside its owned paths, stop it — the ownership table is the contract.
- **The main agent's own slice is a task too:** budget its time inside the wave, not after it.

## Failures and re-runs

- A failed slice is re-run **alone**, with its failure evidence appended to the brief. Restarting the wave throws away good work and re-reads a tree that changed.
- Two failures on the same slice means the cut is wrong: fold it back into the main's work or re-cut it.
- A blocked slice is not a failed slice: if it waits on a file another slice owns, the main unblocks it or reorders the wave.
- Never let a slice fix another slice's file to get unblocked. That is how two agents write the same path.

## Ending the run

Stop when every planned slice is integrated and verified — not when every agent returns. Leftover slices that turned out unnecessary are a sign the plan was optimistic, and that is worth saying in the report rather than quietly shipping them.
