# Search Vocabulary: Explicit Search Done Properly

An exact-string search finds the copies that were easiest to find. Build a vocabulary first, then search with all of it. `scripts/sweep.py` automates most of the forms below (pass several terms at once, including old wording read from each locale file); the rest needs judgment.

## 1. Build the vocabulary

| Source of terms | Examples |
|-----------------|----------|
| The old text, whole | `Build faster, ship sooner` |
| Distinctive fragments | `ship sooner`, `Build faster` (partial reuse in meta, docs, emails) |
| The key / identifier | `hero.title`, `heroTitle`, `HERO_TITLE`, `hero-title`, `hero_title` |
| The value, if numeric | `14`, `14 days`, `14-day`, `fourteen`, `two weeks` |
| The old name, if renamed | `OldBrand`, `old-brand`, `oldbrand`, `@oldbrand`, `oldbrand.com` |
| The text in **other languages** | read it out of each locale file; these are search terms too |
| Names for the same concept | `MAX_UPLOAD_MB`, `maxFileSize`, `upload_limit`, `sizeCap` |

Rule of thumb: if you found the old text in a locale file, add that locale's wording to the vocabulary and search for it. This is how hard-coded copies of translations (in tests, emails, docs) get found.

## 2. Forms the same text takes in real repos

| Form | Why it hides | Example |
|------|--------------|---------|
| Case variants | Headings, CSS `text-transform`, constants | `BUILD FASTER`, `build-faster` |
| Whitespace and wraps | Hard-wrapped Markdown, JSX line breaks, template literals | `Build faster,\n  ship sooner` |
| HTML entities | `&amp;`, `&rsquo;`, `&#1575;` | `Don&rsquo;t wait` |
| Unicode / JSON escapes | `\u0627`, `\"`, `\'` | `"\u0627\u0628\u0646\u0650"` |
| URL-encoded | links, `mailto:` subjects, share URLs | `Build%20faster` |
| Curly vs straight quotes | Typographic cleanup in CMS or docs | `Don't` / `Don't` |
| Numerals and separators | Arabic-Indic digits, `1,000` vs `1 000` vs `1.000` | `١٤ يومًا` |
| Unit/currency words | Translated per locale | `14 days`, `14 jours`, `14 يومًا`, `14 Tage` |
| Markup split | Text broken by tags or `<Trans>` components | `Build <b>faster</b>, ship sooner` |
| String concatenation | Pieces joined in code | `"Build faster" + ", ship sooner"` |
| Dynamic keys | Template literals building keys | `` t(`hero.${v}.title`) `` |

Search for the shorter distinctive fragments to catch concatenation and markup splits; search the key prefix to catch dynamic keys.

## 3. Search from both directions

- **Text -> key -> usages.** Find the old text in locale files, take its key, then search for the key in code (`t("hero.title")`, `i18n.t('hero.title')`, `Trans i18nKey=`, `formatMessage({ id: "hero.title" })`).
- **Key -> text.** Searching only for text misses locale files whose translation differs; searching only for the key misses hard-coded copies. Do both.
- **Usages of the constant** in addition to the constant's value; and the raw value as a bare literal elsewhere.

## 4. Commands

`rg` (ripgrep) is fastest and respects `.gitignore`; `git grep` is a fine fallback and also works on a specific commit.

```bash
# literal, case-insensitive, with context
rg -i -F "ship sooner" -C1

# tolerate wraps/extra whitespace: build a regex, enable multiline
rg -i -U "Build\s+faster,\s+ship\s+sooner"

# key and its identifier forms
rg -n "hero[._-]?title|heroTitle|HERO_TITLE"

# dynamic keys: search the prefix
rg -n "hero\.\$\{|\"hero\.\" ?\+|'hero\.' ?\+"

# include things .gitignore hides that you still care about (generated docs, dist for comparison)
rg -uu -l "ship sooner"

# which files only? (to plan the edit)
rg -l -i -F "ship sooner"

# in a non-checked-out branch or tag
git grep -n -i -F "ship sooner" origin/main
```

Windows PowerShell without `rg`:

```powershell
Get-ChildItem -Recurse -File -Exclude *.lock |
  Select-String -Pattern "ship\s+sooner" -CaseSensitive:$false |
  Select-Object Path, LineNumber, Line
```

## 5. Noise control

- Very short terms (`Pro`, `10`) produce junk: anchor them with context (`"10 MB"`, `\b10\b.*upload`) and review hits by hand.
- Skip `node_modules`, build output, and lockfiles in the first pass; then check whether a *committed* generated file contains the old text (that means regenerate, not hand-edit).
- Large repos: group hits by directory before reading; decide per group.

## 6. What text search cannot find

Images and baked-in text (OG cards, hero art, screenshots), PDFs, videos, CMS/database content, remote dashboards (analytics funnels, email provider templates, app-store listings), and **paraphrases that share no words** with the old text. Those are found by reasoning about the claim - see `reference-surfaces.md` - and anything unreachable goes in the report as "needs a human".
