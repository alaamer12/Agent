# Environment discovery & workspace path resolution for debug scripts

Universal patterns for loading environment files and resolving project
modules from ad-hoc scratch scripts (`.debugging/tmp/`), across runtimes.
Read this the first time a scratch script can't find a package or a
config value. Tool names below are examples from real ecosystems, not a
closed set — map them onto your stack.

## 1. Environment loading hierarchy & precedence

Resolve environment variables in deterministic order, lowest to highest:

1. **Repository root environment** (`.env`)
2. **Application / package environments** (`apps/<app>/.env`, `packages/<pkg>/.env`, `services/<srv>/.env`)
3. **Local overrides** (`.env.local`, `.env.test`)
4. **Active process environment** — already supplied by the shell, CI, or container; always wins.

### Multi-path discovery (pseudocode)

```pseudocode
function loadProjectEnvironment(candidateDirectories, precedenceOrder):
    environmentMap = {}
    for each directory in candidateDirectories (from lowest to highest priority):
        for each filename in [".env", ".env.local", ".env.test"]:
            if fileExists(joinPath(directory, filename)):
                environmentMap.merge(parseEnvFile(...), override=true)
    environmentMap.merge(getSystemEnvironment(), override=true)   # process env wins

    # Normalize connection-string aliases — which aliases exist is
    # engine/hosting-specific (e.g. POSTGRES_URL, MYSQL_URL,
    # DB_CONNECTION_STRING, DIRECT_URL): treat canonical name as the
    # first defined among its known aliases.
    if not environmentMap.hasKey("DATABASE_URL"):
        environmentMap["DATABASE_URL"] = firstDefined(environmentMap, CANONICAL_ALIASES)
    return environmentMap
```

Classic symptom this decodes: "works when run from the app folder,
breaks from root" → invocation-root + env-precedence, not a logic bug.

## 2. Workspace & module resolution from a scratch directory

A script in a temp/scratch dir must import the project's own packages.
Three universal strategies, cheapest first:

**Strategy A — use a runtime that resolves workspaces natively, from the
repo root.** Examples: Bun (`bun run .debugging/tmp/script.ts`, native
workspace + tsconfig-path support); Node via tsx (`npx tsx ...`); Python
(`python -m` from the repo root, or packages installed editable so
`pip`/`poetry` metadata resolves them, or `PYTHONPATH` pointed at source
roots); Go (`go run ./path/to/cmd` from the module root — same module
resolves everything; local deps via `replace` directives in `go.mod`).

**Strategy B — a path-mapping shim in the scratch directory** when the
runtime doesn't resolve aliases out of the box. Example (TypeScript): a
`tsconfig.json` in the scratch dir mapping `@app/*` to the workspace
source trees. Python equivalent: a `.pth` file or explicit `sys.path`
insertion; the principle is "declare the alias map next to the script".

**Strategy C — programmatic alias registration before importing app
code.** Examples: Node with `module-alias` (`addAliases({"@core": resolve(...)})`);
Python `sys.path.insert(0, str(ROOT / "packages/core/src"))`; Go has no
runtime hook — the idiomatic equivalent is a thin wrapper package in the
module tree (strategy A with an extra main).

```typescript
// TypeScript example — Strategy C
import moduleAlias from "module-alias";
import { resolve } from "node:path";
moduleAlias.addAliases({
  "@core": resolve(__dirname, "../packages/core/src"),
  "@db": resolve(__dirname, "../packages/db/src"),
});
```

```python
# Python example — Strategy B/C combined
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]          # repo root from .debugging/tmp/
sys.path.insert(0, str(ROOT / "packages" / "core" / "src"))
from core.services import get_user_by_id            # noqa: E402
```

## 3. Best practices for scratch scripts

1. **Self-contained execution** — handle your own `.env` loading and
   client instantiation so the script runs in isolation.
2. **Deterministic exit codes** — `0` on success, `1` on failure in every
   language's idiom (`process.exit(1)`, `sys.exit(1)`, `os.Exit(1)`) so
   the same file serves as manual check, bisect driver, and CI-able probe.
3. **Redact sensitive output** — print confirmation (host, active user)
   without raw passwords or credentials.
4. **Cleanup guarantee** — close database connections, HTTP clients, and
   workers in `finally` / context manager / `defer` to prevent hanging
   processes and leaked handles.
