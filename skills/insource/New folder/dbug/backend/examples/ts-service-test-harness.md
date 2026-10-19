# Example: TypeScript Isolated Service Test Harness

This example illustrates testing an application service or ORM query in isolation.

```typescript
import { resolve } from "node:path";
import dotenv from "dotenv";

dotenv.config({ path: resolve(process.cwd(), ".env") });

async function runTestHarness() {
  console.log("Testing service operation...");

  // Example:
  // const db = createDatabaseConnection();
  // const service = new UserService(db);
  // const user = await service.getUserById("user-123");
  // console.assert(user !== null, "User must exist");

  console.log("Test completed successfully.");
}

runTestHarness().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});
```
