---
name: debug-eas
description: >-
  A professional workflow for diagnosing, cleaning, and fixing Expo Application Services (EAS) build failures.
  Integrates Expo MCP tools with custom log processing scripts to turn noisy logs into actionable debug data.
---
# Debug EAS

A professional workflow for diagnosing, cleaning, and fixing Expo Application Services (EAS) build failures. This skill integrates Expo MCP tools with custom log processing scripts to turn massive, noisy build logs into actionable debug data.

## Skill Stack

- `terminal-ops`: For repository state verification and executing local scripts.
- `api-and-interface-design`: For checking Expo Router and API route configurations.
- `react-native-best-practices`: For debugging native module issues and dependency conflicts.

## When to Use

- An EAS build fails (Android/iOS).
- EAS logs are too large or noisy to read directly (JSON-heavy).
- You need to identify the root cause of a Gradle failure, dependency resolution error, or App Config issue.
- You want to verify a fix by triggering a new EAS build.

## Tools & Helpers

### Expo MCP Tools
- `mcp_expo_build_list`: Find the relevant build ID.
- `mcp_expo_build_logs`: Retrieve the raw logs.
- `mcp_expo_build_run`: Trigger a new build after a fix.
- `mcp_expo_read_documentation`: Check Expo docs for specific error codes.

### Log Cleaning Utility
The skill relies on `scripts/clean_eas_logs.py` to filter noise.
Usage: `python scripts/clean_eas_logs.py <log_file> [flags]`
- `--errors-only`: The recommended first pass. Highlights failures and warnings.
- `--skip <PHASE>`: Skip verbose phases like `RUN_GRADLEW` if the error is known to be elsewhere.
- `--skip-source stdout`: Useful when only `stderr` contains relevant error details.

## Workflow

### 1. Identify and Fetch
- Use `mcp_expo_build_list` to find the failing build.
- Use `mcp_expo_build_logs` to fetch the raw log data.
- Save the logs to a local file: `eas-build-<id>.log`.

### 2. Process and Filter
- Run the cleaner: `python scripts/clean_eas_logs.py eas-build-<id>.log --errors-only --no-delay`.
- Inspect the generated `-clean.log`.
- If the error is not clear, run without `--errors-only` but skip successful noisy phases (e.g., `INSTALL_CUSTOM_TOOLS`, `PREPARE_PROJECT`).

### 3. Root Cause Analysis
Categorize the failure:
- **Phase: RUN_GRADLEW**: Likely a Java/Kotlin error, native module incompatibility, or Gradle configuration issue.
- **Phase: INSTALL_DEPENDENCIES**: Bun/npm/yarn resolution error. Check `package.json`.
- **Phase: READ_APP_CONFIG**: Syntax error in `app.json` or `app.config.js`.
- **Phase: CONFIGURE_PROJECT**: EAS project configuration or environment variable issue.

### 4. Implementation & Verification
- Apply the fix in the codebase.
- Verify locally if possible (e.g., `bun run lint`, `bunx expo doctor`).
- Trigger a verification build using `mcp_expo_build_run --platform <android|ios> --profile <profile>`.

## Output Format

When reporting build issues, use this structure:

```text
BUILD ID: <id>
PLATFORM: <android/ios>
FAILING PHASE: <phase_name>
ROOT CAUSE: <brief description of the error>
ACTION: <what was changed to fix it>
VERIFICATION: <new build id or local test result>
```

## Pitfalls

- **Stale Logs**: Always fetch the latest logs if you've made changes and re-run the build.
- **Gradle Noise**: The `RUN_GRADLEW` phase can produce thousands of lines of progress; always use the cleaner to isolate `stderr` and `ERROR` markers.
- **Environment**: EAS builds run in a managed CI; local success doesn't always guarantee EAS success (check `eas.json`).
