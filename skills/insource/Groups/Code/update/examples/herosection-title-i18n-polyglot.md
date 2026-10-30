# Updating a Hero Title Across Locales - Polyglot Walkthrough

**Principle (Update skill):** the claim lives in many copies; the visible string is only one of them. The mechanics differ per stack, the method does not: find the source of truth, enumerate every locale, change all of them together, verify nothing stale remains.

**Scenario.** The hero headline changes from "A fast code editor" to "The AI-first IDE" (a *meaning* change: the product description changed, so metadata and docs repeating "code editor" are now wrong too). The project ships English, Arabic, and French.

## 0. Claim

> Old: "A fast code editor" -> New: "The AI-first IDE". Meaning change. Search vocabulary: `A fast code editor`, `code editor`, `hero.title`, plus the Arabic and French wordings found in the locale files.

## 1. React + react-i18next (JSON)

Trace: `HeroSection.tsx` renders `t("hero.title", "A fast code editor")`; the source of truth is the key in `locales/<lng>/home.json`, and the inline default is a second copy.

```bash
rg -n "hero\.title|A fast code editor|code editor" src docs README.md index.html
python scripts/locale_parity.py --root src/locales --key hero.title
```

```tsx
// Before
<h1>{t("hero.title", "A fast code editor")}</h1>
// After - inline default updated too, or it masks a missing locale entry
<h1>{t("hero.title", "The AI-first IDE")}</h1>
```

```jsonc
// locales/en/home.json
{ "hero": { "title": "The AI-first IDE" }, "meta": { "description": "Symphony is the AI-first IDE for teams." } }
// locales/ar/home.json  - re-expressed, not word-for-word; Latin brand names left as in neighboring strings
{ "hero": { "title": "بيئة التطوير الأولى بالذكاء الاصطناعي" }, "meta": { "description": "سيمفوني بيئة تطوير مبنية على الذكاء الاصطناعي للفرق." } }
// locales/fr/home.json
{ "hero": { "title": "L'IDE pensé pour l'IA" }, "meta": { "description": "Symphony est l'IDE pensé pour l'IA, destiné aux équipes." } }
```

Notice `meta.description` also said "code editor": found by the *concept* search, not by the headline string.

## 2. Flutter (ARB)

```bash
rg -n "heroTitle|A fast code editor" lib
```

```json
// lib/l10n/app_en.arb
{ "heroTitle": "The AI-first IDE", "@heroTitle": { "description": "Landing hero headline" } }
// lib/l10n/app_ar.arb
{ "heroTitle": "بيئة التطوير الأولى بالذكاء الاصطناعي" }
```

Then run `flutter gen-l10n` - the generated `app_localizations_*.dart` files are outputs; never edit them by hand.

## 3. Android (strings.xml)

```bash
rg -n "hero_title|A fast code editor" app/src
```

```xml
<!-- res/values/strings.xml -->
<string name="hero_title">The AI-first IDE</string>
<!-- res/values-ar/strings.xml -->
<string name="hero_title">بيئة التطوير الأولى بالذكاء الاصطناعي</string>
<!-- res/values-fr/strings.xml (apostrophe must be escaped) -->
<string name="hero_title">L\'IDE pensé pour l\'IA</string>
```

Check every `values-*` folder, including region variants (`values-ar-rEG`) and any `tools:ignore="MissingTranslation"` that hides gaps.

## 4. Django / gettext (.po) - the natural-language-key trap

Here the key is the English text, so changing the wording changes the **msgid** in every catalog.

```python
# Before
title = _("A fast code editor")
# After
title = _("The AI-first IDE")
```

```po
# locale/ar/LC_MESSAGES/django.po
# Before
msgid "A fast code editor"
msgstr "محرر شيفرة سريع"
# After - msgid changed in EVERY language file, otherwise the translation silently stops matching
msgid "The AI-first IDE"
msgstr "بيئة التطوير الأولى بالذكاء الاصطناعي"
```

```bash
rg -n 'msgid "A fast code editor"' locale
python manage.py makemessages -a      # re-extracts, marks stale entries as obsolete (#~)
python manage.py compilemessages      # rebuilds .mo; never hand-edit .mo
```

Do not leave obsolete `#~` entries that still contain the old claim without mentioning them.

## 5. Rails (YAML)

```yaml
# config/locales/en.yml
en:
  home:
    hero:
      title: "The AI-first IDE"
# config/locales/ar.yml
ar:
  home:
    hero:
      title: "بيئة التطوير الأولى بالذكاء الاصطناعي"
```

Lazy lookups (`t(".hero.title")`) resolve per view path; search for the relative form too: `rg -n 't\("\.hero\.title"\)' app/views`.

## 6. Anywhere: non-locale copies of the same claim

These never contain the key, only the idea.

```bash
rg -n -i "code editor" --glob '!node_modules' --glob '!dist' --glob '!CHANGELOG.md'
```

| Hit | Decision |
|-----|----------|
| `index.html` `<meta property="og:title" ...>` | Update |
| `README.md` tagline and the screenshot caption | Update the text; flag the screenshot |
| `tests/hero.test.tsx` `getByText("A fast code editor")` | Update expected string |
| `__snapshots__/hero.snap` | Regenerate with the test runner |
| `package.json` `"description"` | Update |
| `CHANGELOG.md` "1.0: landing page for the fast code editor" | **Leave** (history) |
| App-store listing, social bio, OG image with the old words baked in | **Needs a human** |

## 7. Verify

```bash
python scripts/sweep.py --term "A fast code editor" --term "محرر شيفرة سريع" --term "éditeur de code rapide"
python scripts/locale_parity.py --root src/locales --grep "code editor"
python scripts/locale_parity.py --root src/locales     # no missing keys, no values identical to English
```

Remaining hits must be only `CHANGELOG.md` (history) and anything reported as needing a human.

## Key points

- The inline default, the locale files, the metadata, and the tests are all copies of one claim.
- Natural-language keys turn a wording change into a key rename across every catalog.
- Generated files (`.mo`, generated Dart, snapshots, build output) are regenerated, never patched.
- Search the other languages' old wording too: it finds hard-coded translations in docs and tests.
