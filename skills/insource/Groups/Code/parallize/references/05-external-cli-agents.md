# Harnesses without subagents: external CLI agents

Some environments cannot spawn in-process subagents but can run a separate agent process from the terminal (for
example a headless CLI agent such as `junie`, `claude -p`, or `codex exec`). The plan is identical; only the
mechanics change.

## Rules

1. **One process per slice, one directory per run.** Put every log under one task directory, e.g.
   `.agents/<task>/`, with a distinct log and metadata file per slice. Logs must be visible to the user, not
   buried in a temp path.
2. **Record the session id.** Store the id (and process id) next to its log so a follow-up can resume the same
   agent instead of restarting it cold.
3. **Background, then monitor.** Start the process in the background, then poll the log at a steady cadence and
   report progress. The main agent stays alive while any process runs — it does not return to the user with the
   work unfinished.
4. **Follow-up carries context.** A resumed agent does not remember the conversation. Re-state the goal, the
   established conventions, and the expected artifact — never just "continue".
5. **Anomaly rule.** A process that has run far longer than its slice warrants, with no new output, is anomalous:
   inspect, report, and ask the user before killing it.
6. **Cleanup after verification.** Remove the task directory only once the slice's output is integrated and
   verified — the logs are the evidence trail until then.

## Wave mechanics

- The cap is the number of processes the machine can run without starving — verify it; do not assume the
  subagent cap applies.
- Launch a wave's processes together, from the same snapshot, then monitor them as a group.
- A failed process is restarted alone with its log attached to the new brief; never restart the wave.
- Shared files are still edited by one owner only: give the CLI agents disjoint paths exactly as you would
  subagents.

## What stays with the main agent

Everything in `03-main-agent-work.md` — interfaces, sensitive code, destructive operations, shared files,
integration. A CLI agent is easier to lose track of than a subagent, so the ownership table matters more, not
less.
