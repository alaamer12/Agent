# The delegation contract - section 10

The user's original ask had three parts: what the **main agent** does, how it **submits subagents**, and how
**subagents do their tasks**. This section is where all three live, and it is the part of the rulebook that
scales the project's throughput - so it gets its own reference.

## The premise to state first

Write it as the section's opening line, because every rule below follows from it and an agent that does not
know it will negotiate the rules away:

> A subagent cannot see the parent's conversation and cannot ask follow-up questions. Anything absent from its
> prompt is unavailable to it, and the gap will be filled by a guess.

Related asymmetries worth stating: a subagent sees only what it opens, so the *paths* it must open are named
for it; it cannot tell the parent what it noticed mid-task except through its report; and it cannot see other
subagents, so overlapping scopes produce duplicated or contradictory work.

## Main agent duties

1. **Name by responsibility.** The name is the handle, the report filename, and the label in status reporting -
   one identity, three uses. `pipeline-diff-reviewer`, not `agent-2`. Ask the user for the project's naming
   shape (role-based, role+sequence) and record it.
2. **Full context up front.** Goal; the files and paths already located; decisions already made (approach
   chosen, options rejected, naming settled); the exact expected output. A brief that says "refactor the auth
   module the usual way" has delegated the framing to someone who cannot ask what "usual" means.
3. **Per-task document list.** On top of the baseline block, name the *specific* documents this task needs -
   if it touches the pipeline, list `worker-pool-and-rate-limiter.md`; if it touches UI, list the UI conventions
   doc and the relevant mockup path. This is the single highest-value line in a subagent prompt, because the
   general context list in `AGENTS.md` cannot know what the task will touch.
4. **Propagate the obligations.** Units check, shell and package-manager rules, environment rules, debug
   permissions, cleanup, reporting. These travel in the block, and the block travels in the prompt.
5. **Bound the scope.** Explicitly say which paths the subagent may modify and which it must not. When several
   subagents run in parallel, scopes must be disjoint or sequenced - see write conflicts below.
6. **Set the autonomy level** (see the table).
7. **Merge, don't re-do.** In fan-out, the orchestrator splits, launches, and integrates. If it is doing every
   leaf's work itself, the fan-out was decorative.
8. **Collect and reconcile reports.** Confirm each landed; resolve contradictions between subagents before
   acting on either. A contradiction between two reports is a finding, not noise.
9. **Ask authority on the subagent's behalf.** A subagent cannot ask the user mid-task. Enumerate the
   ask-per-session actions the task needs under section 13 - external installs, external processes,
   existing-DB writes, credentials, machine config - and ask the user in one batch before dispatch; record
   the grant or denial in the brief (Autonomy Bounds). A denial re-scopes the task; it is never bypassed
   by the subagent improvising.
10. **The subagent must respect this file.** The block and the per-task doc list are the rulebook slice;
    the brief states that the subagent follows AGENTS.md as if it had read it, and the report names the
    rules that shaped decisions and every granted action it took.

## Subagent duties

- Read the listed documents **in full** and follow them exactly; the prompt's doc list beats memory.
- Do the scoped task; return anything outside it as a *finding*, not as a change.
- Reuse before creating (units duty); say why when not.
- Obey execution, environment, and debug permissions; do not edit `.env`; do not rewrite pushed history; do
  not touch files outside scope.
- Write the report and return its summary with the deliverable.
- If the task cannot be done as briefed, say so with the evidence rather than substituting a goal it *can*
  complete. Silent substitution is the failure that costs the most: the parent receives a confident success
  about a different question.

## Autonomy levels - record the project's default and the exceptions

| The subagent faces… | Decide alone | Return undecided |
|---|---|---|
| Naming inside its own scope, with the project's convention | yes | |
| A reversible local edit that completes the task | yes | |
| Anything touching files outside its stated scope | | yes |
| A design decision with two defensible shapes | | yes, with a recommendation and the trade-off |
| Destructive or hard-to-reverse actions (delete, reset, force-push, migration, dropping data) | | always |
| Cost, contract, security, or personal-data implications | | always |
| The brief appears to be based on a wrong premise | | yes - name the premise and the evidence |

The line that projects most often leave unwritten is the last: a subagent that discovers the task's premise is
wrong needs permission to *stop*, or it will complete a wrong task beautifully.

## Authority for subagents - and the autonomous exception

- **Default: ask per session, on the subagent's behalf.** Batch the questions before dispatch ("the
  subagent will need to <action> - do you grant authority?"), record each answer in the brief, and re-scope
  on a denial.
- **Autonomous sessions override the asking.** When the user has already placed the agent in an
  anonymous, autonomous state (e.g. `iwts` - "I want to sleep", "take over"), the agent and its subagents
  hold full authority for the delegated work unless the user carved something out. The brief says so; hard
  constraints (privacy paths, never-sacrifice commitments) still apply, and destructive or out-of-project
  actions are still reported.

## The baseline block

The block exists because instruction files do not reliably reach a delegated context, so **the rules travel
inside the prompt**. Two disciplines make it safe:

1. **It is a projection, not a second source.** Every clause maps to a section (context→2, skills→1, shell/
   tooling→6, env→7, debug→8, units→4, report→10). The body wins on any disagreement.
2. **Regenerate on change.** State that in the file: *"editing sections 1-9 requires regenerating this block."*
   `scripts/agents_lint.py` compares clause topics against the sections and flags a block clause with no
   corresponding section (and vice versa), which is how drift gets caught before it mis-informs every
   subagent.

Three slots the parent fills per delegation, and they belong in the block so they are never forgotten:
`TASK-SPECIFIC DOCS`, `SCOPE`, `OUTPUT CONTRACT`. A prompt without `OUTPUT CONTRACT` is how a subagent returns
an essay when a patch was needed.

Keep the block under ~20 lines. It is compressed on purpose; anything longer stops being pasted, and an unused
block is worse than none.

## Reports

The report is the durable record; the returned text is transient. Specify in the rulebook:

- **Location and pattern** - e.g. `.repertoire/agents/<name>.md`.
- **Collision policy** - the same role running twice overwrites its report unless the pattern carries a
  sequence or timestamp (`<name>-<yyyymmdd-HHmm>.md`). Decide this with the user; leaving it implicit means the
  second run silently erases the first one's evidence.
- **Contents** - goal as briefed, actions taken, files touched, decisions made and why, verification performed
  *with results*, anything left undecided, and (when the task went off-script) where it diverged.
- **Who writes it** - the subagent, or the parent on its behalf if the subagent cannot write files. Say which,
  because "the subagent should" fails quietly.

## Fan-out

If the project uses a shorthand (`x->2x->4x`), record the grammar, the execution steps, and the three things an
unstated limit always produces:

- **Depth cap** and **total-worker cap** (both). A depth cap without a worker cap still allows 2→4→8→16 = 30
  workers, and the cost is invisible until it is spent.
- **Failure handling** - if a leaf fails, report it in the merged result; do not have the orchestrator quietly
  redo its scope (that defeats the split and hides the failure).
- **Merge responsibility** - each intermediate agent merges its children before returning; the root merges
  everything into one response.

## Write conflicts - the gap a fan-out rulebook usually has

Parallel subagents editing the same file corrupt each other's work, and shared worktrees make this a live risk
even without fan-out. Record the rule:

- Assign **disjoint paths** per subagent, stated in `SCOPE`.
- Sequence anything that must touch a shared file (lockfiles, generated types, a barrel export, migration
  index) rather than letting two agents append to it.
- A subagent that finds a file changed underneath it re-reads, adapts additively, and reports - it does not
  "restore" or overwrite work it did not create.
- The parent reconciles: concurrent edits are a merge problem for the parent, not for the leaf that noticed
  last.
