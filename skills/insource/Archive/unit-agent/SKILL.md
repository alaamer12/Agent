---
name: unit-agent
description: Command-line Junie interface for running code tasks. Use this skill to orchestrate Junie subtasks via CLI, especially when you need specific configurations like --plan, --brave, or custom project locations.
---

# Unit Agent (Junie CLI)

Command-line Junie interface for running code tasks autonomously or interactively. Use this skill when you need to delegate a scoped task to Junie itself as a tool, or when the user describes a task that fits the "Junie as a CLI" pattern.

## Core Usage

### Interactive mode
Start an interactive session with Junie.
```bash
junie
```

### Non-interactive mode
Run a specific task and exit.
```bash
junie "Fix the bug in the login function"
# or
junie --task "Fix the bug"
```

---

## Core Options

| Flag | Description |
|------|-------------|
| `--task=<text>` | Task description (alternative to positional argument). |
| `--prompt=<text>` | Start interactive mode with an initial prompt already submitted. |
| `--plan` | **Plan Mode**: Start interactive mode in Plan Mode (requires approval before execution). |
| `--session-id=<id>` | Follow up on a previously executed session. |
| `--resume` | Resume the last session (or the one specified by `--session-id`). |
| `--brave` | **Brave Mode**: Turns on Brave Mode (skips some safety prompts, interactive only). |
| `--goal` | **Goal Mode**: Run in orchestrated step-by-step mode. |
| `-p, --project=<dir>` | Target project directory (default: current directory). |
| `--review` | Run an automated code review on the project. |

---

## Mandatory Orchestration Rules

When the main agent orchestrates `unit-agent` instances, the following rules are **mandatory**:

1. **CLI Only**: You MUST always use the `junie` CLI via terminal commands (e.g., `powershell` or `cmd`). Do NOT use the internal `spawn_subagent` tool for these tasks.
2. **Log Visibility & Structure**: All sessions MUST be visible.
   - Create a directory for the task: `.junie/sessions/<task-title>/`.
   - Redirect stdout and stderr to a background log file named `.junie/sessions/<task-title>/output_<pid>.txt` (where `<pid>` is a unique identifier or the process ID).
   - Store the session ID and PID in `.junie/sessions/<task-title>/meta.json` for persistent tracking and follow-up.
3. **Persistent Execution**: Do NOT terminate or kill any `unit-agent` process until the user explicitly mentions it.
4. **Active Monitoring**: The main agent's mission is to continuously review the progress of the unit-agents by inspecting their logs in the task-specific session folder and reporting status to the user.
5. **Follow-up Context**: When assigning a follow-up task (via `--session-id`), the main agent MUST provide more context than the user explained. Do not just pass a minimal command; include a detailed prompt that explains the goal, expected artifacts, and stylistic consistency (e.g., "Add two more screens matching the established Tailwind theme" instead of just "add two more screens").
6. **Persistence & Lifecycle**: 
   - The main agent must remain active as long as any unit-agent is running. Use "no-op" commands, sleep, or handle side-tasks to keep the session alive.
   - To avoid the "interrupted task" problem in follow-ups, ensure the main agent explicitly waits for completion and continues monitoring until the unit-agent exits naturally or is stopped by the user.
7. **Anomaly Detection**: Record and report any anomalies, such as an agent running for too long without progress. In such cases, ask the user for instructions.
8. **Hygiene**: The main agent must clean up the session directory (`.junie/sessions/<task-title>/`) only after the unit-agent has finished its work and the results have been verified/reported.

---

## Configuration & Environment

### Project Guidelines
Specify custom guidelines to steer the agent's behavior.
- `--guidelines-filename=<name>`: Change the default guidelines filename.
- `--ide-guidelines=<path>`: Prepend content from a file to existing guidelines.

### BYOK (Bring Your Own Key)
Configure specific providers and models.
- `--model=<name>`: Model to use for the primary agent (default: `gemini-3-flash-preview`).
- `--provider=<name>`: Provider (`openai`, `anthropic`, `google`, `xai`, `openrouter`, `copilot`, `litellm`).
- `--effort=<level>`: Effort level (`low`, `medium`, `high`).

---

## System & Automation (Non-interactive)

Use these when running Junie as part of a script or CI pipeline.

| Flag | Description |
|------|-------------|
| `--input-format=<fmt>` | `text` or `json`. |
| `--output-format=<fmt>` | `text`, `json`, or `json-stream`. |
| `--json-output-file=<path>` | File to write JSON output to (defaults to stdout). |
| `--skip-update-check` | **Mandatory**: Skip startup update checks (always use this flag). |

---

## Advanced Management

### Gateway Mode
Run Junie as a headless background worker.
- `--gateway`: Run as a headless gateway.
- `--gateway-status`: Print PID, host, port, and directory of the running gateway.
- `--gateway-stop`: Stop the running gateway.

### Extension & Skill Locations
- `--skill-location=<path>`: Additional folders to search for skills.
- `--mcp-location=<path>`: Additional folders for MCP servers.
- `--agent-location=<path>`: Additional folders for custom agents.

---

### Workflow: Delegating with Unit Agent

When you need to run a sub-task using `unit-agent`:

1. **Assign a Name**: If the user did not choose a name, assign a descriptive name (e.g., `agent-plan`, `agent-goal`).
2. **Identify Scope**: Determine the exact directory (`-p`) and the task description.
3. **Choose Mode**: Select `--plan`, `--brave`, or `--goal` as appropriate.
4. **Set Constraints**: Use `--ide-guidelines` if specific standards are required.
5. **Execute with Logging & Structure**:
   - Create the task directory: `mkdir -p .junie/sessions/<task-title>`.
   - Construct the command: `junie <task> --skip-update-check [options] > .junie/sessions/<task-title>/output_<name>.txt 2>&1`.
   - Run via the terminal with `background: true`.
   - Capture the session ID and store it in `.junie/sessions/<task-title>/meta.json`.
6. **Monitor & Report**:
   - Periodically read `.junie/sessions/<task-title>/output_<name>.txt`.
   - Provide progress updates and report any anomalies to the user.
   - **Persistence**: Stay alive (no-op/side-tasks) and maintain an active watch until the agent completes its mission or you are told to stop.
7. **Follow-up (Resuming Sessions)**:
   - Identify the previous session ID from `.junie/sessions/<task-title>/meta.json`.
   - Provide a **Detailed Prompt**: Expand the user's request with context from the original session (e.g., "Using the same Tailwind UI and mobile-first design from Screen 1, add Screen 8: Settings").
   - Command: `junie "<detailed_prompt>" --session-id <id> --skip-update-check [options] > .junie/sessions/<task-title>/output_followup_<timestamp>.txt 2>&1`.
8. **Finalize & Cleanup**:
   - Once an agent finishes, report the final outcome.
   - Wait for user confirmation or explicit instruction before stopping/killing processes.
   - Clean up the session folder `.junie/sessions/<task-title>/` after completion.
