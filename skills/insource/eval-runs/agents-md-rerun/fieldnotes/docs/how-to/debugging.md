# How to debug in this project

- Reproduce first, against the local SQLite copy - never diagnose from code-reading alone.
- Escalation order: query the DB directly -> call the service layer -> then the UI; stop at the
  layer that reveals the fault.
- Data access: inspect local data freely; modify only `data/dev.sqlite`; staging DB writes are an
  ask-first item (sections 11, 16).
- Verification: a fix counts when the original reproduction stops reproducing, then section 19's
  gates run.
- Cleanup: delete reproduction scratch and any seeded bad rows when the task ends.
