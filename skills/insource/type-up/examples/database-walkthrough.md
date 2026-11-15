# Database Walkthrough: one rule, every place

Applies to both modes. The reference is [database constraints](../references/database-constraints.md). Identifiers are illustrative roles (see [naming](../references/principles.md#3-naming--describe-the-role-follow-the-ecosystem)). Every SQL and harness result below was run on PostgreSQL 16.2 and SQLite 3.45.1.

## Example 1: `UserIso` in every place it lives

The rule: a user's ISO code is exactly two uppercase ASCII letters.

| Place | Form | Rejects |
|-------|------|---------|
| Compiler | the built-in `Uppercase<string>` plus a brand for the meaning (TypeScript); `NewType` (Python); opaque type (Scala) | a plain `string`, a lowercase literal |
| Boundary check | the project's check (library schema, `TryFrom`, type guard) using `[A-Z]{2}` | `"us"`, `"USA"` at runtime |
| PostgreSQL | domains, the second built on the first | `'us'`, `'USA'`, `'U1'`, `'ÉÉ'` |
| SQLite | an explicit `CHECK` on a `STRICT` table | the same |

PostgreSQL, chain of domains (tier 1 state, then tier 2 meaning, then a record):

```sql
CREATE DOMAIN uppercase_text AS text CHECK (VALUE = upper(VALUE));            -- tier 1 state
CREATE DOMAIN positive_int   AS integer CHECK (VALUE > 0);                    -- tier 1 state
CREATE DOMAIN user_iso       AS uppercase_text CHECK (VALUE ~ '^[A-Z]{2}$');  -- tier 2 meaning
CREATE DOMAIN port           AS positive_int   CHECK (VALUE <= 65535);        -- tier 2 meaning
CREATE TABLE app_user (iso user_iso NOT NULL, port port);                     -- tier 3 record
```

Results: `'US'` accepted. `'us'` rejected by `uppercase_text_check` (the tier 1 domain). `'USA'` rejected by `user_iso_check` (the tier 2 domain). Port `0` rejected by `positive_int_check`; `99999` by `port_check`. A `NULL` port is accepted (nullable); a `NULL` iso is rejected by `NOT NULL`. The error names the exact tier whose rule broke.

SQLite, no domains, one explicit rule on a strict table:

```sql
CREATE TABLE app_user (
  iso  TEXT    NOT NULL CHECK (length(iso) = 2 AND iso NOT GLOB '*[^A-Z]*'),
  port INTEGER          CHECK (port > 0 AND port <= 65535)
) STRICT;
```

`STRICT` matters: a port of `1.5` or `'abc'` is rejected as a wrong stored kind ("cannot store REAL value in INTEGER column"), whereas a non-strict `INTEGER` column accepted `1.5`.

## Example 2: shared vectors catch the places that disagree

One list of accepted and rejected values, run through the boundary check, two SQLite rules, and the PostgreSQL domain chain:

```python
ACCEPT = ["US", "DE", "JP"]
REJECT = ["us", "Us", "USA", "U", "", "U1", "éé", "ÉÉ", "ΩΩ"]       # last four: digit and non-ASCII

def code_accepts(s): return re.fullmatch(r"[A-Z]{2}", s) is not None     # boundary check
# SQLite naive : CHECK (iso = upper(iso) AND length(iso) = 2)
# SQLite ascii : CHECK (length(iso) = 2 AND iso NOT GLOB '*[^A-Z]*')
# PostgreSQL   : user_iso domain chain from Example 1
for v in ACCEPT + REJECT:
    results = {place: accepts(v) for place, accepts in places.items()}   # then compare with the expectation
```

Result:

| Value | code | SQLite naive | SQLite ascii | PostgreSQL | Expected |
|-------|------|--------------|--------------|-----------|----------|
| `US`, `DE`, `JP` | accept | accept | accept | accept | accept |
| `us`, `Us`, `USA`, `U`, `""` | reject | reject | reject | reject | reject |
| `U1` | reject | **accept** | reject | reject | reject |
| `éé` | reject | **accept** | reject | reject | reject |
| `ÉÉ` | reject | **accept** | reject | reject | reject |
| `ΩΩ` | reject | **accept** | reject | reject | reject |

The naive rule `iso = upper(iso)` is true for any value with no lowercase ASCII letter: digits and non-ASCII letters pass (SQLite's `upper` is ASCII-only). The explicit character class agrees with the code everywhere. Without the vectors, the database would have silently accepted values the type forbids. A related divergence to include in vectors when a rule uses case conversion: PostgreSQL `upper('straße')` is `'STRAßE'`, JavaScript gives `'STRASSE'`.

## Example 3: a tagged union as a table

The tier 3 union `idle | loading | success(results) | error(message)` becomes a `kind` column whose data columns are tied to their case:

```sql
CREATE TABLE search_state (
  kind    text NOT NULL CHECK (kind IN ('idle','loading','success','error')),
  results jsonb,
  message text,
  CONSTRAINT data_only_in_its_case CHECK (
    (kind = 'success') = (results IS NOT NULL) AND (kind = 'error') = (message IS NOT NULL))
);
```

A `success` row with results is accepted. An `idle` row carrying results is rejected, and so is an `error` row without a message: the database enforces the same "data exists only in the case that has it" rule as the type.

## Example 4: tightening a live table

```sql
ALTER TABLE h ADD CONSTRAINT c_upper CHECK (c = upper(c)) NOT VALID;  -- accepted; old bad row remains
INSERT INTO h VALUES ('worse');                                        -- rejected immediately
ALTER TABLE h VALIDATE CONSTRAINT c_upper;                             -- fails: names c_upper, an old row violates it
```

Fix or migrate the old rows, then validate again. The same applies to `ALTER DOMAIN … ADD CONSTRAINT … NOT VALID`.

## Example 5: other databases

Engines without domains repeat the explicit `CHECK` per column, generated from the single rule definition. Confirm the engine enforces `CHECK` (MySQL before 8.0.16 parses and ignores it; not run here), then run the same vectors.
