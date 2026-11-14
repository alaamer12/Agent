# Instrument header template

Every file promoted into `.debugging/instruments/` opens with this block,
adapted to the file's comment syntax (`#`, `//`, `--`). It is what makes a
promoted tool self-explanatory to a future agent that wasn't there.

```
INSTRUMENT: <verb-object name matching the file, e.g. verify-schema>
PURPOSE:    <what question this answers, in one line>
USAGE:      <run command with every parameter shown>
            e.g. bun run .debugging/instruments/verify-schema.ts --table users
INPUTS:     <--table: any table name; reads DATABASE_URL via env resolution chain>
EXIT CODES: 0 = condition holds · 1 = violated (usable in CI / bisect drivers)
ORIGIN:     <.debugging/bugs/<record>.md or commit — the bug that made this>
RELATED:    <other instruments/tests it pairs with | none>
```

Rules embedded here are deliberate:
- `USAGE`/`INPUTS` must show *generalized* parameters — a header that
  admits hardcoded incident values is evidence the promotion was wrong
  (it should have stayed `tmp/` and been deleted).
- `ORIGIN` keeps the trail from permanent tool back to real bug — future
  maintainers learn *why* it exists, not just what it does.
- `EXIT CODES` restated on every instrument keeps the "any script is a
  CI-able assertion" convention alive across the folder.
