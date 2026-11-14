# Example: isolated service harness, three runtimes

Concrete instances of the harness pattern in
[`../references/backend.md`](../references/backend.md): call the suspect
service *by itself*, controlled inputs, write path inside a rolled-back
transaction, deterministic exit code. Lives in `.debugging/tmp/`;
becomes a bisect driver, and the seed of a committed test.

## TypeScript (Bun or Node + tsx)

```typescript
import { resolve } from "node:path";
import dotenv from "dotenv";

dotenv.config({ path: resolve(process.cwd(), ".env") }); // or the chain in env-and-resolution.md

async function main(): Promise<number> {
  const db = createDatabaseClient(process.env.DATABASE_URL!); // project's factory
  const svc = new UserService(db); // replicate real DI wiring deliberately

  try {
    const user = await svc.getUserById("known-user-id");
    console.assert(user !== null, "expected record");

    // write path — never leave a trace
    await db.begin(async (tx) => {
      const created = await svc.create({ name: "harness-probe" }, tx);
      console.assert(created.id != null, "create must return id");
      throw new Error("rollback-sentinel"); // abort after assertion, per backend.md guardrail 3
    }).catch((e) => { if (e.message !== "rollback-sentinel") throw e; });

    return 0;
  } catch (err) {
    console.error("harness failure:", err);
    return 1;
  } finally {
    await db.close();
  }
}

process.exitCode = await main();
```

## Python

```python
import os, sys, logging
from contextlib import closing

logging.basicConfig(level="INFO", format="[harness] %(message)s")

def main() -> int:
    db = open_db(os.environ["DATABASE_URL"])          # project's factory
    svc = UserService(db)                             # same wiring as the app
    try:
        user = svc.get_user_by_id("known-user-id")    # read path
        assert user is not None, "expected record"

        with db.transaction() as tx:                  # write path, rolled back
            created = svc.create(name="harness-probe", tx=tx)
            assert created.id is not None
            tx.rollback()                             # explicit: leave no trace
        return 0
    except Exception:
        logging.exception("harness failure")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
```

## Go

```go
package main

import (
    "context"
    "log"
    "os"
)

func main() {
    os.Exit(run())
}

func run() int {
    db, err := openDB(os.Getenv("DATABASE_URL")) // project's factory
    if err != nil {
        log.Printf("harness failure: %v", err)
        return 1
    }
    defer db.Close() // cleanup guarantee, any language idiom

    ctx := context.Background()
    svc := NewUserService(db) // replicate real wiring

    user, err := svc.GetUserByID(ctx, "known-user-id")
    if err != nil || user == nil {
        log.Printf("read path wrong: %v", err)
        return 1
    }

    tx, err := db.BeginTx(ctx, nil) // write path in a transaction...
    if err != nil {
        log.Printf("begin: %v", err)
        return 1
    }
    defer tx.Rollback() // the guard: never commits, always unwinds
    if _, err := svc.Create(ctx, tx, "harness-probe"); err != nil {
        log.Printf("write path wrong: %v", err)
        return 1
    }
    return 0
}
```

**What the three have in common — and why:** env via the resolution
chain (never hardcoded), direct service call (no HTTP/UI), read assertion
+ rolled-back write, deterministic exit code (`0`/`1`) so the identical
file works as manual check, `git bisect run` driver, and regression-test
seed. The three classic distinctions it makes (function vs caller, logic
vs state, app vs transport) are in `../references/backend.md`.
