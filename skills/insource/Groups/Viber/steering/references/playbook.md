# playbook

> This document defines the `playbook` steering folder: step-by-step operational recipes for executing a specific task. It lives exclusively in the **tech tier** (`tech/playbook/`); see [`index.md`](index.md) for the taxonomy overview.

**Scope rule.** Default to `tech/<area>/playbook/`; use `tech/shared/playbook/` only after the [Universal Scope Test](layout.md#universal-scope-test) passes. Area files link to shared facts and contain only their delta.

**Holds.** Step-by-step recipes to **run, operate, or configure** a specific technical task (e.g., how to seed a local database, how to rotate API tokens, how to run a containerized environment, or how to execute a production release).

**Does not hold.**
- Business policies or rules ([`policy.md`](policy.md)).
- Business operational workflows (e.g. how customer support onboard clients; which belong in business documentation).
- How to write or implement software well ([`doctrine.md`](doctrine.md)).
- Platform runtime behavior (the steering function folder, [`function.md`](function.md)).
- General, rarely updated project guidance that applies to every task (e.g., general git conventions or setup scripts, which belong in `AGENTS.md` or developer onboarding guides).

**The test.** The completion test: Does the reader finish the document having **run** a specific procedure? If they finish knowing a rule, it is `doctrine` or `policy`. If they finish understanding a concept, it is `domain`. If it is a generic workflow that applies identically across all tasks, it is outside the taxonomy.

**Interview before authoring.** Complete the [Tech Directory Interview and Authoring Gate](documentation-conventions.md#mandatory-tech-directory-interview-and-authoring-gate) for this directory. Ask or explicitly confirm:
- What exact task does this runbook enable, who performs it, when is it used, and does every area need this same procedure or only one area?
- What prerequisites, permissions, tools, versions, environments, and inputs are required?
- Which steps and commands are authoritative, and have they been demonstrated or are they only proposed?
- How are secrets and other sensitive values supplied without placing them in the document?
- What observable result proves success, how is failure diagnosed, and what rollback or recovery is safe?
- Who owns and maintains the procedure, and which parts must never run against production?

Record the confirmed task, operator, prerequisites, ordered procedure, verification, recovery, ownership, and safety limits in the directory's ledger row. Do not invent commands or present an untested recipe as operational truth.

**Example (`tech/<area>/playbook/seed-demo-data`).**
"1. Connect to the local database instance using the developer connection string.
2. Execute the seeding script: `bun run seed:fixtures`.
3. Verify that 10 mock assets and 5 demo portfolios are populated in the database table."
