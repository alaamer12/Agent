# Candidates and the bequeath report

The job of step 1–2 is **not** to admire the session. It is to find the small number of things that would be
rebuilt from scratch by the next agent, and to price the work of making them survivable.

## The three-question test

A candidate qualifies only if all three answers are yes:

1. **Would a future agent redo this?** If the work was one-off reading, an opinion, or a decision already
   recorded, no.
2. **Did it cost something to obtain?** Time, failed attempts, an undocumented behaviour, a version-specific
   workaround. A five-minute snippet can still qualify if it encodes a fact (the exact header, the ordering
   constraint).
3. **Can it survive without this conversation?** It must be describable and runnable by someone who never
   saw the context. If it only makes sense "as we discussed", it is not an asset yet.

## What qualifies, by type

| Type | Qualifies when | Typically becomes |
|---|---|---|
| Script | it ran more than once, or encodes a non-obvious step | a CLI with arguments, `--help`, exit codes |
| Command sequence | the order matters, or one step was discovered the hard way | a documented procedure, or a script if it is deterministic |
| Debugging procedure | it isolated a cause (not just "we fixed it") | a troubleshooting guide with the failing signal and the check order |
| Configuration | a known-good combination (versions, flags, env vars) | a template with comments naming what must be changed |
| Query / data logic | it answered a question and would answer it again | a parameterized query with a documented schema assumption |
| Pattern | it recurs across files/services in this project | a short guide with one canonical example |
| Constraint / dead end | "X fails because Y" was established | a check script or a documented limitation — genuinely valuable |
| Document fragment | a reusable explanation (an architecture note, a runbook) | a doc asset, only if nothing equivalent exists |

## Direct, generalize, or don't

- **Direct** — already parameterized and portable: copy it in, write the card, test it where it stands. Rare.
- **Generalize** — the behaviour is right but it is welded to this task: strip the coupling, add inputs, test.
- **Don't** — the asset is a fragment of a workflow, or its value is entirely context (a one-off investigation
  summary), or extracting it would require inventing behaviour that was never observed.

## The report format

```markdown
| # | Name | Type | Original purpose | Bequeath proposal | Future use | Form |
|---|---|---|---|---|---|---|
| 1 | `flaky-test-hunter` | script | found the 3 tests that failed only under load | add `--repeat`, `--timeout`, machine-readable output; remove hardcoded test paths | when a suite is flaky under CI load | generalize |
| 2 | `pg-lock-check.sql` | query | proved the migration waited on a lock held by a reader | parameterize the table name; document the privilege needed | diagnosing blocked migrations | direct |
| 3 | `nextjs-15-params` | constraint | established that `params` is async in 15.2 and the sync form silently returns undefined | write a check + 6-line note | any Next 15 route refactor | generalize |
```

Then, one line per row, the **strip list**: what has to change before it is reusable —
`/tmp/repro.py`, project name `acme-billing`, version `4.2.1`, token in the header, hardcoded port 5433.

## Bad candidates (these look valuable and are not)

- **The final solution itself.** A feature is not an asset unless it fits the catalog's skills; what is
  bequeathable is the *method* that produced it.
- **Session-specific data.** Logs, dumps and outputs with customer data — evidence, not an asset; and they
  belong in the incident record, not in `bequest/`.
- **Half-finished ideas.** An approach that was never shown to work becomes a confusion for the next agent.
- **Anything containing a secret or a personal path.** The cost of leaking exceeds everything the asset saves.
- **A duplicate of what already exists** in `bequest/` or in the project's tools — improve in place instead.

## Saying "nothing qualifies"

Two honest sentences, not a padded table:

> "Nothing from this session qualifies: the work was reading three files and answering a question, and the one
> script that ran was a two-line `jq` filter. Nothing stored."

That answer costs the user nothing and protects the directory from noise. A `bequest/` full of trivia is worse
than an empty one, because future agents stop reading it.
