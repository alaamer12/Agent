# Catalog discipline - how this skill compounds

Two layers of memory, one rule: **every run writes back**.

| Layer | File | Holds | Granularity |
|---|---|---|---|
| Global catalog | `data.csv` | every *way to create avatars* the skill knows, with proof status | one row per approach |
| Approach registry | `approaches/<id>/<name>-avatars.csv` | the concrete *resources that approach has actually produced* (slots, parts, combos, fixtures, endpoints, palettes) | one row per built resource |

The global catalog is deliberately unbiased: it never privileges one family (vector-rig is one row among
many, just the one currently `verified`). Approach registries are the opposite: maximally concrete - file
paths, envelopes, params, dates. A new approach graduates from `data.csv` row to having its own folder +
registry the first time it produces real artifacts.

## The rules (same ones that make fahlwy's catalog work)

- **Never delete a row - flip its `status`.** `verified → degraded → dead` keeps the graveyard, and the
  graveyard is what stops a re-hunt of a method that already failed here.
- **`last_proven` is evidence, not decoration.** A row is only trustworthy as fresh as its stamp;
  `catalog.py stale --days 30` lists what to re-prove. Seeded-but-never-run rows stay `unverified` with
  `last_proven=-` - the catalog distinguishes "known idea" from "proven here" and so should you.
- **The ledger explains, the CSV records.** `log.csv` is append-only and carries the *why* ("grapheme rule
  for CJK names was the trap", "param docs had changed since seeding"); `catalog.py add/stamp/set`
  auto-log, and `catalog.py log NOTE <family> "<lesson>"` captures method lessons that are no row's.
- **Every build registers its resources.** Shipped parts/combos/endpoints/palettes get rows in the approach
  registry with file paths and verification dates; an unregistered artifact might as well not exist - the
  next run will rebuild it from scratch or, worse, trust a stale copy.
- **Discovery of a new way is the headline event.** When a run invents or finds an approach not in
  `data.csv` (someone's CSS-only dicebear clone, a font-glyph scheme, a face-mesh tool), it gets an `add`
  row the same session, `unverified` if merely found, `verified` only after this environment actually
  produced an avatar with it. The catalog is how "infinite possibilities" becomes cumulative knowledge
  instead of a blank page every time.

## Querying instead of skimming

```bash
python scripts/catalog.py list --status verified
python scripts/catalog.py search "palette"
python scripts/catalog.py resources modular-svg-rig   # what the built approach already contains
python scripts/catalog.py stats
python scripts/catalog.py export --format md          # prose view for a report
```

`python scripts/catalog.py` with no arguments runs the self-test (round-trips add/stamp/set on a temp
copy) - run it once after any edit to `catalog.py` itself.
