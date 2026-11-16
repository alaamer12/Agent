# Worked example — the flagship row

The pattern behind `mixed-type-field`: **if a value encodes more than one primitive, split it.**

Money is the common case:

```text
Bad:  price = "$12.50"        price = "12 USD"       price = 12
Good: price_amount = 1250     price_currency = USD
```

The same test applies to anything with a value and a unit or a second dimension:

| Composite value | Split into |
|---|---|
| Money | `amount` (integer minor units or decimal) + `currency` (ISO 4217) |
| Duration | `value` + `unit` (`ms`, `s`, `min`, `h`) |
| Distance / weight | `value` + `unit`, canonical at storage |
| Temperature | `value` + `unit` (`C`, `F`, `K`) |
| Range | `min` + `max` (and inclusivity if it matters) |
| Phone | `e164` + optional `extension` |
| Address | `line1`, `line2`, `locality`, `region`, `postcode`, `country` |
| Person name | `display_name` + optional `given_name` / `family_name` |
| Geo point | `latitude` + `longitude` (and precision if needed) |
| Percentage | `ratio` (0–1) or `basis_points`, never an ambiguous `5` |

Formatting belongs at the presentation layer. Parsing belongs at the boundary. Storage stays
atomic.
