# Data Gates — Never Let a Template Assume an Unverified Value

## Step 0 — Discover the Weakness Before Writing the Gate

A gate without discovery is guessing. **Before applying any ladder, the agent must surface the assumption itself, find what (if anything) guarantees it, and tell the user.**

Average is not the contract: 100 rows averaging 30 chars tells you nothing about whether a 3,000-char name can arrive tomorrow via import, API, or admin form.

**The Assumption Ledger** — build one row per windowed value before touching code:

| Column | Content |
|---|---|
| Value + window | e.g. `name` → title 30-60, h1 ≤40 |
| Template's implicit assumption | "names fit in ~50 chars" |
| Measured reality | `MAX/AVG/PERCENTILE` over ALL rows + NULL count |
| **Assurance chain** | what actually guarantees the bound (or `NOTHING`) |
| Decision | enforce / add constraint / accept — surfaced to user |

**Trace the assurance chain — the answer determines WHERE the gate belongs:**

1. **Database constraint** — `VARCHAR(100)` column or `CHECK (length(name) <= 100)`: a 3,000-char value *cannot exist*. Template may rely on it; add a cheap assert as regression tripwire, no full ladder needed. (Watch: TEXT columns and `VARCHAR(4000)` are not guarantees at the sizes your windows need — and a DB bound is NOT the score window: a `VARCHAR(60)` name column still overflows a 30-60 *title* once the 9-char ` \| Site` suffix is appended. Recompute the window including every template suffix before declaring a constraint sufficient.)
2. **Application-level validation** — schema checks (`z.string().max(100)`, FluentValidation, `validates_length_of`, form maxlength): guaranteed at write time, but imports/seed scripts/DB-direct writes may bypass it — keep the template gate as belt-and-suspenders.
3. **Pipeline/convention only** — data quality via admin discipline, CSV imports, external sync: no hard bound → **gate at the template boundary** (full ladder + assertion) AND flag the risk.
4. **NOTHING** — free-text with no bound anywhere: the most common state and the one agents must never silently accept. Report explicitly: *"nothing prevents a 3,000-char name; your template assumes ≤50."*

**Introspection recipes (generic, per layer):**
```sql
-- measured reality (Postgres/MySQL/SQLite equivalents)
SELECT COUNT(*) total, AVG(LENGTH(name)) avg, MAX(LENGTH(name)) max,
       SUM(CASE WHEN name IS NULL THEN 1 ELSE 0 END) nulls FROM funds;
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns WHERE table_name = 'funds';   -- VARCHAR bound? TEXT = unbounded
```
```
grep the write paths instead of assuming they exist:
  validation schemas:  z\.string\(\)\.max | Length\( | validates_length_of | maxlength= | AssertMaxLength
  import/seed paths:   INSERT/COPY/import commands/seeders/backfills (these bypass UI validation)
```

**Then present the options and act on the answer** (UP mode: choose, state why, and note it in the report; ANALYZE mode: recommend with the tradeoff table):

| Option | When it's the right call | Cost |
|---|---|---|
| **A — enforce upstream** (add/verify DB `VARCHAR`/`CHECK` or schema validation) | data should be sane for humans too; the outlier is a defect | migration + write-path change; touches data owners |
| **B — gate at the template boundary** (ladder + assert + log) | display window must hold regardless of source; always valid as the last line | template complexity; invisible rewrites unless paired with a loud signal |
| **C — accept as-is** | measured MAX has real headroom AND an assurance exists (chain level 1 or 2) | zero now, a broken title on the day someone imports a 3,000-char name |

**Never silently skip Step 0.** A full ladder on a value already bound (constraint + suffix arithmetic) *inside* the window is noise; a trusted template on an unbounded TEXT column is the bug. Say which it is, to the user, in the report.

## The Trap

Every scored window is an assumption about **data you don't control**:

- Title template `{name} | {Site}` assumes names ~20-50 chars. A 78-char entity name ships a 91-char title → length check 0/6, and Google truncates it anyway (~580-600 px ≈ 60 chars desktop — pixels, not characters; mobile cuts earlier).
- h1 window ≤ 40 chars, slug regex `[a-z0-9-]{3,100}`, description ≤ 160 — all break silently on outliers.
- **The worst one: dumb trimming cuts the atomic unit.** `text.slice(0, 160)` on a strategy paragraph that first names the fund at char 200 produces a "perfect" description with **no keyword** → Meta silently 0/5. `name.slice(0, 45)` can amputate half a multi-word keyword phrase, which normalized matching then can't find anywhere.

Score is computed on data shapes the code assumed. **Gate the value at the template boundary; never trust the database, the average, or "names are usually short."**

## The Windows Table

| Scored value | Window | Atomic unit that MUST survive the gate | Gate action when violated (ordered) |
|---|---|---|---|
| Title | 30-60 chars (pixel ≈600; query within first ~50 chars) | full keyword phrase, once | 1) drop secondary suffix 2) shorter brand form 3) word-boundary cut **preserving whole keyword** 4) pad short ones with category/type qualifier — never filler |
| h1 | ≤ 40 chars | keyword phrase (position 1) | strip trailing corporate boilerplate ("LLC", "لإدارة صناديق الاستثمار"), keep leading keyword core; full name moves to a visible sub-line |
| Meta description | ≤ 160 (mobile ≈ 120) | keyword — placed within first ~50-60 chars | rebuild from template with keyword first; then word-boundary truncate; **assert keyword present post-cut, else fallback template** |
| Slug | `[a-z0-9-]{3,100}` | ≥1 keyword word | re-transliterate from translated name / add category stem; bare numeric ID is the last resort (loses partial credit) |
| Alt text | none | localized name | already name-derived — gate only the manager-phrase append for length |

## Gate Rules

1. **Define the contract** per value: allowed range + the atomic unit (keyword) that must survive every degradation step.
2. **Sample worst case, not average** — before shipping a template, query the actual extremes: `MAX(LENGTH(name))`, longest strategy copy, entities with NULL optionals. A template validated on typical rows is unvalidated.
3. **Keyword-atomic degradation** — truncation operates on semantic units (whole keyword phrase, then word boundary), never raw characters. The keyword is indivisible; everything after it is expendable.
4. **Assert after building** — the template function's last step verifies its own output (`contains keyword` + `length window`) and falls through to the next rung, ending in the P2 keyword-bearing fallback template. No silent violations, ever.
5. **Fail loud outside the render path** — gates rewriting values invisibly = silent content mutation. Each gate trip should record *which entity* and *which rung* it took (admin health signal, log, completeness report per P16) so data owners fix the source; the gate only protects the floor meanwhile.
6. **Gate tests live in the repo** — a fixture per extreme shape (78-char name, 3-char name, keyword-at-char-200 description, non-transliterable name) run in CI; any PR touching title/heading/description templates must pass them.

## Recipes

**Anti-pattern → gate (TypeScript, metadata builder):**
```ts
// ANTI: assumes names fit, and slice can bisect the keyword
const title = `${fund.name} | SNDUK`;
const desc  = strategy.slice(0, 160);

// AFTER: rung ladder + post-build assertion, keyword indivisible
const hasKw = (t: string, kw: string) => normalize(t).includes(normalize(kw));
const inWindow = (t: string) => t.length >= 30 && t.length <= 60;

function buildTitle(name: string, typeLabel?: string): string {
  const cut = trimWordBoundaryKeeping(name, 45);        // keyword phrase whole
  const rungs = [
    `${name} - ${typeLabel ?? ""} | SNDUK`.replace(/\s-\s\|/, " |"),
    `${name} | SNDUK`,
    `${cut} | SNDUK`,
    `${cut} — SNDUK`.padEnd(0),                          // last resort keeps kw + site
  ];
  return rungs.find(t => hasKw(t, name) && inWindow(t))
      ?? `${trimWordBoundaryKeeping(name, 30)} | SNDUK`;
}
```

**Keyword-aware truncate (Ruby, description):**
```ruby
# The keyword is atomic: cut AFTER it survives, else rebuild from fallback.
def seo_description(entity, keyword, site_name)
  real = entity.meta_description || entity.copy.to_s
  cand = real.strip.gsub(/\s+/, " ")
  return cut_at_word(cand, 160) if cand[0, 60].downcase.include?(keyword.downcase) # kw front-loaded
  "#{keyword} على #{site_name}: #{real}".tap { |t| break cut_at_word(t, 160) }      # rebuild, kw at 0
end
```

**C# (Blazor/Laravel-style validation at the view-model edge):**
```csharp
// Gate in the page-model: measured against the table, not the average.
static string TitleGate(string name, string? type) {
    string[] rungs = { $"{name} — {type} | {Site}", $"{name} | {Site}", TruncateKeepPhrase(name, 45) + $" | {Site}" };
    return rungs.FirstOrDefault(t => t.Contains(name, StringComparison.OrdinalIgnoreCase)
                                  && t.Length is >= 30 and <= 60)
        ?? throw new SeoGateBreach(name);   // logged, never rendered broken
}
```

## Related Rubric Truths (verified externally)

- Google truncates titles by **pixel width (~580-600 px desktop ≈ under 60 chars)**; it also still *reads* full titles for ranking — the window is a **display** constraint, so front-load the query + the click reason inside the first ~50 chars (rankosaur; zyppy; screamingfrog).
- Google may ignore/rewrite titles that are stuffed, boilerplate-duplicated, or misaligned with the H1 — gates protect the score, uniqueness protects the click (title-tags.md patterns).
- Meta descriptions: keyword within the first ~50-60 chars (mobile renders ~120); Google rewrites descriptions that don't match the query/passage — so keyword presence ≠ snippet control; match intent (Google Search Central snippet docs; lowfruits).
- Pixel awareness over character counts: when a name is near the limit, **estimate render width, not length** — a 55-char Arabic name and a 55-char Latin name display differently; for bilingual sites, gate each locale's template separately.
