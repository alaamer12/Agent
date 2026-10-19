# Selective Execution of Tests

## Goal

Any developer (or CI job) must be able to run a meaningful subset of the suite with a short, memorable command. The default command runs the fast, high-value suite (normally pure unit tests).

## Preferred mechanisms (in order)

1. Native tags / markers / attributes when the runner supports them cleanly.
2. Lightest accepted ecosystem convention (Cargo features, pytest markers, Jest projects, Go build tags, directory layout, etc.).
3. Thin wrapper script that normalizes the interface.

## Wrapper script guidelines

When a wrapper is needed:

- Provide a single entry point (`./test`, `test.sh`, `test.ps1`, `npm test`, etc.).
- Accept simple category names: `unit`, `integration`, `e2e`, `slow`, `property`, `auth`, …
- Default (no arguments) runs the fast suite.
- Document the commands in the project README or CONTRIBUTING.
- Keep the script under ~50–80 lines; it is glue, not a framework.

Example shape (Bash):

```bash
#!/usr/bin/env bash
set -euo pipefail

case "${1:-unit}" in
  unit)        cargo nextest run --features unit ;;
  integration) cargo nextest run --features integration ;;
  e2e)         cargo nextest run --features e2e ;;
  all)         cargo nextest run --all-features ;;
  *)           echo "Unknown category: $1"; exit 1 ;;
esac
```

Similar thin wrappers can be written in Python, Node, or PowerShell when those are the project’s common tools.

## Design rules

- Categories should reflect risk and cost, not arbitrary labels.
- Slow or environment-heavy suites must never be part of the default command.
- The selection mechanism itself must not become tribal knowledge.