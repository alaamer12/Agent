# Example: schema inspector & state dump, three runtimes

Two shapes of the same move — **ask the system directly and read its
answer as data**: a script that diffs live catalog vs expected, and a
dev-gated endpoint that serves live state as JSON (the
"make a server-side page and read its values" technique,
[`../SKILL.md`](../SKILL.md) §Ways to see).

## 1. TypeScript — PostgreSQL/Supabase-family schema inspector (postgres.js)

```typescript
import { resolve } from "node:path";
import { existsSync } from "node:fs";
import dotenv from "dotenv";
import postgres from "postgres";

function loadEnv() {
  // generic precedence chain — adapt the candidate list to the repo's layout
  for (const p of [resolve(process.cwd(), ".env"), resolve(process.cwd(), ".env.local")]) {
    if (existsSync(p)) dotenv.config({ path: p, override: false });
  }
  return process.env.DATABASE_URL || process.env["POSTGRES_URL"]; // alias set per env-and-resolution.md
}

const conn = loadEnv();
if (!conn) { console.error("no connection string resolved"); process.exit(1); }

const sql = postgres(conn, { max: 1 });

async function inspectTable(schema: string, tableName: string) {
  const columns = await sql`
    SELECT column_name, data_type, udt_name, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_schema = ${schema} AND table_name = ${tableName}
    ORDER BY ordinal_position`;
  console.table(columns);
  return columns;
}

try { await inspectTable("public", "users"); }
finally { await sql.end(); }
```

## 2. Python — stdlib SQLite inspector (zero new dependencies)

```python
import json, sqlite3, sys

def inspect(db_path: str, table: str) -> dict:
    con = sqlite3.connect(db_path)
    try:
        cols = con.execute(f"PRAGMA table_info({table})").fetchall()
        fks = con.execute(f"PRAGMA foreign_key_list({table})").fetchall()
        return {"columns": cols, "foreign_keys": fks}
    finally:
        con.close()

if __name__ == "__main__":
    print(json.dumps(inspect(sys.argv[1], sys.argv[2]), indent=2))
    sys.exit(0)
```

Exit 0/1 makes both scripts bisect drivers and CI-able probes; the
`--table`-style parameters are what earns promotion to
`.debugging/instruments/`.

## 3. Dev-gated JSON state endpoint — same idea, served over HTTP

The app itself answering "what do you believe right now?" for config,
cache keys, pool stats, flags. **Gate = non-production only, no secrets
in the payload, deliberate keep-or-delete** (rule 5 of
[`../references/instrumentation.md`](../references/instrumentation.md)).

Go (stdlib `net/http`, the `pprof`-pattern — example of the genre):

```go
if os.Getenv("APP_ENV") != "production" {
    mux.HandleFunc("/debug/statez", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]any{
            "flags":      cfg.FlagsSnapshot(),
            "cache_keys": cache.Keys(),
            "pool":       map[string]int{"open": db.Stats().OpenConnections,
                                          "waiters": db.Stats().WaitCount},
        })
    })
}
```

Python (FastAPI-shaped; any router works):

```python
@app.get("/debug/statez", include_in_schema=False)
async def statez():
    if settings.env == "production":
        raise HTTPException(404)
    return {"flags": settings.flags_snapshot(),
            "cache_keys": list(cache.keys()),
            "pool": pool.stats()}
```

Query it (`curl localhost:PORT/debug/statez`) like any data source: the
JSON *is* the evidence, diffable between the passing and failing
environment — the environment differential made one request cheaper.
