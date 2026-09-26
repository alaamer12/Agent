# Example: TypeScript & Bun Schema Inspector

This example shows a concrete TypeScript implementation for inspecting live PostgreSQL / Supabase schemas using `postgres.js` and `dotenv`.

```typescript
import { resolve } from "node:path";
import { existsSync } from "node:fs";
import dotenv from "dotenv";
import postgres from "postgres";

function loadEnv() {
  const root = process.cwd();
  const searchPaths = [
    resolve(root, ".env"),
    resolve(root, ".env.local"),
    resolve(root, "apps/web/.env"),
    resolve(root, "packages/db/.env"),
  ];

  for (const p of searchPaths) {
    if (existsSync(p)) {
      dotenv.config({ path: p, override: false });
    }
  }

  return process.env.DATABASE_URL || process.env.POSTGRES_URL;
}

const connectionString = loadEnv();
if (!connectionString) {
  console.error("DATABASE_URL is not set.");
  process.exit(1);
}

const sql = postgres(connectionString, { max: 1 });

async function inspectTable(schema: string, tableName: string) {
  const columns = await sql`
    SELECT column_name, data_type, udt_name, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_schema = ${schema} AND table_name = ${tableName}
    ORDER BY ordinal_position;
  `;
  console.table(columns);
}

async function main() {
  try {
    await inspectTable("public", "users");
  } finally {
    await sql.end();
  }
}

main().catch(console.error);
```
