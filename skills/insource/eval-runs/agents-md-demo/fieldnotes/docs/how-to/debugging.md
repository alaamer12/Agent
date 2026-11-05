# How to debug in this project

- **Reproduce first:** run the MAUI app offline against a seeded local SQLite store to confirm the
  failure without the server.
- **Escalation order:** query the SQLite store directly -> call the service/sync layer -> reproduce
  in the ViewModel/UI.
- **Data access:** inspect and mutate the local device DB freely; writing to a live PocketBase
  instance is an authority ask (section 11).
- **Visual verification:** build + run on the Android emulator or Windows target; capture device logs
  on sync failures.
- **Cleanup:** delete `scratch/` artifacts when done.
- **Persistence:** if a sync bug looks correct in code, do not stop at one failed attempt - reproduce
  across a real offline->online transition.
