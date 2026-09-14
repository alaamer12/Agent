---
name: backend-db-debugging
description: Universal workflows, patterns, and templates for debugging backend services, databases, schema drift, migrations, environment loading, and module/package path resolution in ephemeral scratch environments.
---

# Universal Backend & Database Debugging

A project-agnostic, production-grade guide for inspecting database schemas, validating backend service layers, resolving workspace/monorepo module paths, dynamically discovering environment variables, and verifying database migrations safely in ephemeral scratch environments.

---

## When to Use

- **Database schema inspection**: Diagnosing schema drift, missing columns, type mismatches, nullability violations, broken foreign keys, missing indexes, or misconfigured Row Level Security (RLS) policies and permissions.
- **Service layer verification**: Testing backend services, business logic, handlers, data access layers, or ORM models in isolation without spinning up the entire frontend or full web server.
- **Environment & config discovery**: Resolving `.env` files across monorepos, multi-tier architectures, or nested package hierarchies with deterministic precedence.
- **Path & workspace resolution**: Executing isolated scripts in monorepos or nested packages while cleanly resolving workspace aliases, tsconfig paths, and package exports.
- **Migration validation**: Authoring, testing, and verifying SQL migrations for idempotency, transactional rollback safety, and schema parity.

---

## Core Principles & Scratch Environment Guardrails

1. **Ephemeral Scratch Isolation**:
   - Write all ad-hoc debug and verification scripts inside a designated scratch directory (e.g., `scratch/`, `temp/`, `.tmp/`).
   - Clean up non-template scratch files after completing the investigation to keep the repository clean.
2. **Deterministic Environment Discovery**:
   - Read configuration and credentials dynamically from `process.env` (never hardcode passwords, API keys, or connection strings in scripts).
   - Search multiple candidate paths hierarchically with precedence (`.env.local` > `.env` > parent/subpackage `.env`).
3. **Non-Destructive Testing**:
   - Use database transactions with rollback (`ROLLBACK`) whenever validating mutations or destructive operations.
   - For tests requiring committed rows, explicitly clean up test entities in a `finally` block or use unique test identifiers.
4. **Direct Service Execution**:
   - Test backend service classes and query functions directly in a script harness to isolate root causes (differentiating database errors, service logic bugs, and UI/transport issues).
5. **Idempotent Migrations**:
   - Ensure DDL/DCL scripts can be rerun safely (`IF EXISTS`, `IF NOT EXISTS`, `CREATE OR REPLACE`, safe policy drops).

---

## Systematic Debugging Workflow

```
1. Setup Scratch Script (e.g. scratch/debug-task.ts)
       │
       ▼
2. Load Environment Hierarchy (discover .env files & normalize DB URLs)
       │
       ▼
3. Resolve Module & Workspace Paths (tsconfig paths, workspace packages)
       │
       ▼
4. Execute Targeted Diagnostics:
   ├── A. Inspect DB Schema & Catalogs (columns, constraints, RLS, indexes)
   ├── B. Test Service & Business Logic (isolated function calls, assert results)
   └── C. Validate Migration DDL (dry-run transactions, schema assertions)
       │
       ▼
5. Analyze Evidence & Apply Source Fixes
       │
       ▼
6. Clean Up Temporary Scratch Files
```

---

## 1. Environment Discovery & Precedence (Pseudocode / Logic)

Regardless of the programming language or runtime, use a hierarchical discovery algorithm to resolve configuration across parent/child directories:

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

    // Canonicalize common database aliases
    if not environmentMap.hasKey("DATABASE_URL"):
        environmentMap["DATABASE_URL"] = environmentMap["POSTGRES_URL"] 
                                       or environmentMap["MYSQL_URL"] 
                                       or environmentMap["DB_CONNECTION_STRING"]

    return environmentMap
```

---

## 2. Monorepo & Module Path Resolution (Language-Agnostic)

When writing ad-hoc scripts in a temporary workspace directory (e.g. `scratch/`, `temp/`):

1. **Workspace Package Aliases**:
   - Ensure the interpreter/runtime can locate internal workspace packages (e.g. via workspace definitions, `PYTHONPATH`, `go.work`, `tsconfig.json`, or module alias loaders).
2. **Deterministic Root Invocation**:
   - Always invoke debug scripts relative to the repository root to maintain consistent relative path resolution across nested packages.
3. **Dependency Isolation**:
   - Keep debug helpers self-contained; if runtime-specific packages (e.g., `dotenv`) are required, ensure they are present in workspace development dependencies.

---

## 3. Database Schema & Policy Inspection (Workflow & Pseudocode)

Inspect database metadata directly via native system catalogs or information schema rather than relying solely on static code definitions:

```pseudocode
function inspectDatabaseSchema(dbConnection, targetTableName, targetSchema = "public"):
    // 1. Query column definitions, data types, nullability, defaults
    columns = queryInformationSchemaColumns(dbConnection, targetSchema, targetTableName)
    displayTable("Columns & Types", columns)

    // 2. Query primary keys, foreign keys, and unique constraints
    constraints = queryInformationSchemaConstraints(dbConnection, targetSchema, targetTableName)
    displayTable("Constraints & Foreign Keys", constraints)

    // 3. Query engine-specific security policies (e.g. RLS in PostgreSQL)
    if engineSupportsSecurityPolicies(dbConnection):
        policies = queryEngineSecurityPolicies(dbConnection, targetSchema, targetTableName)
        displayTable("Active Access Policies", policies)
```

---

## 4. Backend Service Layer Verification (Pseudocode)

Isolate defects by executing backend service functions directly in a lightweight harness before testing through HTTP or UI layers:

```pseudocode
function runIsolatedServiceTest():
    env = loadProjectEnvironment()
    dbClient = initializeDatabaseClient(env["DATABASE_URL"])
    service = instantiateTargetService(dbClient)

    try:
        // Step 1: Validate read / query operations
        queryResult = service.fetchRecordById("test_id")
        assert(queryResult != null, "Expected valid record from query")

        // Step 2: Validate mutation operations safely
        transaction = dbClient.beginTransaction()
        try:
            createdRecord = service.createRecord({ ...payload })
            assert(createdRecord.id != null, "Expected created record ID")
        finally:
            transaction.rollback() // Maintain non-destructive state

        print("All service verification checks passed.")
    except Exception as error:
        print("Service verification failure:", error)
        exitWithCode(1)
    finally:
        dbClient.close()
```

---

## 5. Migration Authoring & Verification Workflow

Follow this universal workflow when validating database schema migrations:

1. **Idempotent DDL Design**:
   - Guard additions (`ADD COLUMN IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`).
   - Use safe replacement or conditional drops for access policies, views, and functions (`DROP POLICY IF EXISTS`, `CREATE OR REPLACE`).
   - For database engines with mutable search paths (e.g., PostgreSQL `SECURITY DEFINER` functions), explicitly set fixed search paths (`SET search_path = public, pg_temp`).
2. **Dry-Run in Transaction**:
   - Execute migration DDL inside a dry-run transaction block (`BEGIN ... ROLLBACK`) to verify syntax, constraints, and data compatibility without mutating live databases prematurely.
3. **Synchronize Schema Definitions**:
   - Keep ORM/query builder schemas, migrations, and canonical master DDL files aligned whenever schema changes occur.

---

## Reference Guides & Examples

- [`references/env-and-resolution.md`](references/env-and-resolution.md) — Universal environment discovery and workspace module resolution strategies across runtimes.
- [`references/database-verification.md`](references/database-verification.md) — System catalog queries for PostgreSQL, MySQL, and SQLite.
- [`examples/ts-bun-schema-inspector.md`](examples/ts-bun-schema-inspector.md) — Example concrete TypeScript / Bun implementation for schema inspection.
- [`examples/ts-service-test-harness.md`](examples/ts-service-test-harness.md) — Example concrete TypeScript implementation for isolated service testing.
- [`templates/test-migration.sql`](templates/test-migration.sql) — Universal SQL migration verification template with transactional rollback safety.
