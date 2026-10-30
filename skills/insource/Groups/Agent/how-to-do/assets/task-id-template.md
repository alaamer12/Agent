### [DOMAIN-SHORTID] Short human-readable task title
<!-- id: DOMAIN-SHORTID | domain: <domain-file-name-without-extension> | status: draft -->

**Matches queries like:** "<generalized phrasing 1>", "<generalized phrasing 2>", "<generalized phrasing 3>"

**Origin query (raw):** "<the exact request that caused this task-ID to be written>"
**Origin query (interpolated):** <what the agent understood this to concretely mean in this repo's terms>

**Preconditions:**
- <anything that must be true about the repo/environment before these steps apply>
- <e.g. a specific tool, config, or convention this task-ID assumes exists>

**Steps:**

##### Step 1 — <short imperative title>
- Files:
  - `<full absolute or repo-root-relative path>` — <exact edit to make in this file, described generally enough to apply to any instance of this task, not just the origin instance>
  - `<full path>` — <exact edit>
- Why: <reason this step exists — what breaks or silently degrades if it's skipped>

##### Step 2 — <short imperative title> *(optional)*
- Condition: <the exact signal in a query that means this step should be included — e.g. "only if the query mentions X"; required whenever a step is marked optional>
- Files:
  - `<full path>` — <exact edit>
- Why: <reason>

<!--
  Steps are not forced into a fixed shape beyond the Files list.
  Add sub-bullets, nested lists, or full paragraphs directly under a step
  whenever there's a gotcha, a non-obvious interaction, or a reason a future
  agent would otherwise have to rediscover the hard way. The Files list is
  the only mandatory part of a step — everything else exists to transfer
  understanding, not to satisfy a template shape.
-->

**Verification:**
- <how to confirm the task was done correctly — a command to run, a state to check, a query to test>

---
#### Patches
<!-- newest first. See task-patch-template.md for the format of each entry. -->
