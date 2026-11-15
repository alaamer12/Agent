# Database Constraints: The Same Rules Where Data Is Stored

Applies to **both modes**. Type rules about visible states (uppercase, non-empty, integer, positive, a closed set, a format, a range) are row-local predicates, so a database can enforce them with `CHECK` or a domain. The rule is then enforced in every place a value lives: the compiler, the boundary check, and the database.

*Standing note: identifiers in examples (`user_iso`, `port`, constraint names) are illustrative roles; follow the project's and database's own naming conventions ([naming](./tier-principles.md#naming-describe-the-role-follow-the-ecosystem)). `[bracketed]` options are examples, not a closed set. Verified by running: PostgreSQL 16.2 and SQLite 3.45.1. Not run here: MySQL, MariaDB, SQL Server, Oracle. Check the project's database version.*

## 1. Why the database too

The compiler and the boundary check protect values that pass through your code. They cannot protect writes that bypass it: other services, scripts, migrations, manual SQL. A constraint is the last line of defense, and because the rules are simple predicates it costs one line each. Prefer the compiler first ([compiler first](./wrong-type-errors.md)); the database constraint is the last rung for persisted data.

## 2. Concept to database feature

| Concept | PostgreSQL | SQLite and engines without domains |
|---------|-----------|------------------------------------|
| Visible state (tier 1) | `CREATE DOMAIN … AS base CHECK (VALUE …)` | `CHECK` on the column, repeated per column (generate it) |
| A state built on a state (chain) | a domain built on a domain (verified) | the conjunction of the checks |
| Domain meaning (tier 2 brand) | a domain on top of the tier 1 domain | one `CHECK` with the combined rule |
| Closed set | enum type, or `CHECK (col IN (…))` | `CHECK (col IN (…))` |
| Required | `NOT NULL` | `NOT NULL` |
| Optional | nullable column | nullable column |
| Stored kind | column type | a `STRICT` table, or `CHECK (typeof(col) = 'integer')` |
| Record (tier 3) | table or composite type | table |
| Tagged union | a `kind` column plus a `CHECK` tying data columns to the kind (verified), or one table per case | same |
| Relation between columns | a `CHECK` over several columns | a `CHECK` over several columns |

## 3. What translates, what does not

- **Translates:** visible states and domain rules that look only at the row: case, emptiness, integer-ness, sign, finiteness, closed sets, formats, ranges.
- **Does not translate:** operations (trim, truncate, decode). They stay in the creation point. If the domain needs the outcome as a guarantee, state the outcome as part of the brand's rule ([distinguishability test](../tiers/tier-1-primitives.md#what-qualifies-as-a-refinement-the-distinguishability-test)).
- **Not a `CHECK`:** uniqueness and references (`UNIQUE`, `FOREIGN KEY`), and anything non-deterministic or depending on other rows.

## 4. Pitfalls (verified unless marked)

| Pitfall | What happens | Do |
|---------|--------------|----|
| **NULL passes a `CHECK`** | `CHECK (x = upper(x))` accepts `NULL` (PostgreSQL, SQLite) | add `NOT NULL` to required fields |
| **`x = upper(x)` is weaker than "uppercase letters"** | it also accepts digits and uncased letters: `'U1'`, `'ΩΩ'` pass | the tier 1 state means "has no lowercase letters"; the brand narrows it (`[A-Z]{2}`) |
| **Case functions differ** | SQLite `upper`/`lower` are ASCII-only (`'é'` stays); PostgreSQL `upper('straße')` is `'STRAßE'` while JavaScript gives `'STRASSE'` | write brand rules as explicit character classes; compare with shared vectors |
| **Floats accept NaN and Infinity** | PostgreSQL `double precision` stores them; SQLite stores NaN as NULL | `CHECK (v NOT IN ('NaN','Infinity','-Infinity'))` in PostgreSQL |
| **Loose column typing** | a non-`STRICT` SQLite `INTEGER` column accepts `1.5` | use `STRICT` (SQLite 3.37+) |
| **Old engines** | MySQL enforces `CHECK` only from 8.0.16 and MariaDB from 10.2.1 (not run here) | confirm the version enforces it |

## 5. Keeping the places consistent

One rule, defined once, with the others derived or tested. Options:

- `[derive the DDL from the shape and brand definitions]`
- `[derive types from the database with the project's introspection tool]`
- `[write both and test them against shared vectors]`

Shared vectors are the dependable fallback: one list of accepted and rejected values, run through the creation point and through the database. The [walkthrough](../examples/database-walkthrough.md) runs this and shows the disagreements it catches.

## 6. Adding a rule to existing data

PostgreSQL (verified): `ALTER TABLE … ADD CONSTRAINT … CHECK (…) NOT VALID` rejects new bad rows at once without scanning old ones; `ALTER TABLE … VALIDATE CONSTRAINT …` then fails and names the rule if old rows violate it. `ALTER DOMAIN … ADD CONSTRAINT … NOT VALID` is accepted the same way. In engines without `NOT VALID`, query for violating rows first.

## 7. Errors

Name constraints so they identify the rule, in the project's naming convention (domain-based constraints in PostgreSQL already name the failing domain: a lowercase `iso` fails the tier 1 domain, `USA` fails the tier 2 one). Map a constraint violation to the project's failure carrier at the data-access boundary; the database message is a last resort, not user-facing text.

## 8. In the two modes

- **Mode A:** add `CHECK`s for the rules the code already enforces, starting with the ones that have caused bad data.
- **Mode B:** domains mirror the tiers: tier 1 domains, tier 2 domains built on them, tier 3 tables. Migrations hold one definition per tier, in the same order as the type files.

## 9. Done when

- [ ] Each persisted rule exists as a constraint (or domain) as well as in the types
- [ ] Required fields have `NOT NULL`; floats exclude NaN and Infinity where they should
- [ ] Brand rules use explicit character classes where the domain means ASCII
- [ ] Shared vectors run against the creation point and the database, with no disagreement
- [ ] New constraints on live tables are added without blocking, then validated
