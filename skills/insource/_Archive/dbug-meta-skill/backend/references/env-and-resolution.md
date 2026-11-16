# Environment Discovery & Workspace Path Resolution

This reference covers universal patterns for dynamically locating and loading environment files and resolving monorepo / multi-package modules in backend debugging scripts across modern runtimes.

---

## 1. Environment Loading Hierarchy & Precedence

When executing scripts in complex repositories or monorepos, environment variables should be resolved in deterministic order:

1. **Active Process Environment** (`process.env`) — already supplied by the shell, CI, or container.
2. **Local Overrides** (`.env.local`, `apps/<app>/.env.local`, `packages/<pkg>/.env.local`).
3. **Application / Package Environments** (`apps/<app>/.env`, `packages/<pkg>/.env`, `services/<srv>/.env`).
4. **Repository Root Environment** (`.env`).

### Multi-Path Environment Discovery Logic (Pseudocode)

```pseudocode
function loadProjectEnvironment(candidateDirectories, precedenceOrder):
    environmentMap = {}

    for each directory in candidateDirectories (from lowest to highest priority):
        for each filename in [".env", ".env.local", ".env.test"]:
            filePath = joinPath(directory, filename)
            if fileExists(filePath):
                fileVariables = parseEnvFile(filePath)
                environmentMap.merge(fileVariables, override=true)

    // Apply active process/system environment overrides
    environmentMap.merge(getSystemEnvironment(), override=true)

    // Normalize common database connection aliases
    if not environmentMap.hasKey("DATABASE_URL"):
        environmentMap["DATABASE_URL"] = environmentMap["POSTGRES_URL"] 
                                       or environmentMap["MYSQL_URL"] 
                                       or environmentMap["DB_CONNECTION_STRING"]
                                       or environmentMap["DIRECT_URL"]

    return environmentMap
```

---

## 2. Universal Workspace & Module Path Resolution

When executing scripts in a monorepo or nested package structure, scripts run from a temporary directory (e.g., `scratch/` or `temp/`) need to import internal workspace packages.

### Strategy A: Runtime-Level Resolution (Bun / tsx / Deno)

Modern runtimes automatically resolve workspace packages defined in root `package.json` `workspaces` (npm, pnpm, yarn, bun):

```bash
# Bun (native workspace and tsconfig path support)
bun run scratch/debug-script.ts

# Node with tsx (native TypeScript and ESM support)
npx tsx scratch/debug-script.ts

# Node with ts-node
npx ts-node -r tsconfig-paths/register scratch/debug-script.ts
```

### Strategy B: Path Mapping via `scratch/tsconfig.json`

If the runtime does not resolve internal aliases out of the box, place a `tsconfig.json` in the scratch directory pointing to workspace source trees:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "esnext",
    "moduleResolution": "bundler",
    "paths": {
      "@app/*": ["../packages/*/src", "../apps/*/src"]
    }
  }
}
```

### Strategy C: Programmatic Module Alias Registration

For vanilla Node.js / CommonJS execution, register aliases at runtime before importing application code:

```typescript
import moduleAlias from "module-alias";
import { resolve } from "node:path";

moduleAlias.addAliases({
  "@core": resolve(__dirname, "../packages/core/src"),
  "@db": resolve(__dirname, "../packages/db/src"),
});
```

---

## 3. Best Practices for Scratch Scripts

1. **Self-Contained Execution**: Scratch scripts should handle their own `.env` loading and client instantiation so they can be run in isolation.
2. **Deterministic Exit Codes**: Always exit with code `0` on success and `1` on failure (`process.exit(1)`) so scripts can be used in CI/verification pipelines.
3. **Redact Sensitive Output**: Log confirmation of connection (e.g. database host, active user) without printing raw passwords or credentials.
4. **Cleanup Guarantee**: Ensure database connections, HTTP clients, and workers are cleanly closed (`await client.end()`, `await pool.close()`, `await prisma.$disconnect()`) in a `finally` block to prevent hanging process exits.
