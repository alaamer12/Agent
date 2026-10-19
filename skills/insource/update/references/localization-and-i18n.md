# Localization and i18n: Updating Text That Exists in Many Languages

A project with N locales has N+ copies of every user-facing sentence. Updating only the source language leaves N-1 stale claims. This file covers how to find, change, and verify them across ecosystems.

## Contents
1. Procedure
2. Where translations live, by ecosystem
3. Traps that break a locale update
4. Writing the new translations
5. Arabic and other RTL / complex-plural languages
6. Verification

## 1. Procedure

1. **Enumerate the locale set.** List every language the project ships (folders under `locales/`, `lang/`, `res/values-*`, `*.lproj`, `.arb` files, `.po` files, the i18n config's `supportedLngs`). Do not assume the languages you can see in the component.
2. **Locate the entry in each locale** by key (or by msgid for natural-language keys). Use `scripts/locale_parity.py --key <key>` for JSON layouts: it prints the key's value in every language and marks locales where it is missing.
3. **Detect pipeline ownership.** If the project uses Crowdin, Lokalise, Phrase, Weblate, Transifex, or exports locale files from a platform (look for `crowdin.yml`, `.lokalise`, `l10n.toml`, CI jobs that pull translations, a "do not edit" header), the source locale is edited in the repo and other locales are filled by the platform. Update the source locale, tell the user the rest will propagate, and do not hand-edit pulled files.
4. **Choose the translation policy** (SKILL.md "Copies in other languages"): translate, translate+flag, defer to pipeline, or remove-to-fallback. State it.
5. **Apply to every locale file in one change**, so no commit leaves the set inconsistent.
6. **Verify** (section 6).

## 2. Where translations live

| Ecosystem | Typical files | Lookup in code |
|-----------|---------------|----------------|
| react-i18next / i18next | `locales/<lng>/<ns>.json` or `<lng>.json` | `t("ns:key")`, `<Trans i18nKey>` |
| next-intl / vue-i18n / svelte-i18n | `messages/<lng>.json` | `t("key")`, `$t("key")` |
| FormatJS / react-intl | `lang/<lng>.json` or extracted `defaultMessage` | `formatMessage({ id, defaultMessage })`, `defineMessages` |
| gettext (Python/Django, PHP, C) | `locale/<lng>/LC_MESSAGES/*.po` + compiled `.mo` | `_("msgid")`, `gettext(...)` |
| Rails | `config/locales/<lng>.yml` | `t(".title")`, `I18n.t("...")` |
| Laravel | `lang/<lng>/*.php` or `lang/<lng>.json` | `__("key")`, `trans(...)` |
| Android | `res/values[-xx]/strings.xml` | `@string/name`, `getString(R.string.name)` |
| iOS / macOS | `<lng>.lproj/Localizable.strings` or `.xcstrings` | `NSLocalizedString("key", ...)`, `String(localized:)` |
| Flutter | `lib/l10n/app_<lng>.arb` | `AppLocalizations.of(context)!.key` |
| Angular | `messages.<lng>.xlf` | `i18n` attribute, `$localize` |
| .NET | `Resources.<culture>.resx` | `Resources.Key`, `IStringLocalizer` |

Compiled artifacts (`.mo`, bundled JSON, `.arb`-generated Dart) are rebuilt by the project's command (`msgfmt`, `flutter gen-l10n`, the build) - run it rather than editing output.

## 3. Traps that break a locale update

- **Natural-language keys.** With gettext `msgid`, or i18next configured with natural-language keys (`t("Build faster")`, often `keySeparator: false`), the *key is the old English text*. Changing the English wording means changing the key in **every** locale file, or all translations silently stop matching and fall back. Check how the project keys its strings before editing.
- **Inline defaults mask gaps.** `t("hero.title", "Build faster")` renders fine in a locale that lacks the key, hiding the omission. Update the default too, and do not rely on the UI to reveal missing entries.
- **Fallback chains.** `fallbackLng: "en"` means a deleted or missing key shows English. That is only acceptable if the user agrees (policy 4, remove-to-fallback).
- **Placeholders and interpolation.** `{{name}}`, `{name}`, `%s`, `%1$d`, `${var}`, `{count, plural, ...}`. Keep the same placeholders in every language; reordering is fine, dropping or renaming is a bug.
- **Rich-text slots.** `<Trans>` uses indexed tags (`<1>bold</1>`); FormatJS uses named tags (`<b>..</b>`). The tags must stay balanced and keep the same indices/names across languages.
- **ICU plural/select blocks.** Copy the structure; adapt only the text and the plural categories the language needs.
- **HTML or Markdown inside strings.** Keep the markup valid and escaped consistently with the rest of the file.
- **Dynamic keys.** `` t(`hero.${variant}.title`) `` - update all variants under the prefix.
- **Duplicated keys.** The same sentence under `hero.title`, `meta.title`, and `og.title`: confirm each is meant to change, then change each.
- **Length and layout.** German and Finnish run long; CJK has no spaces; Arabic and Hebrew mirror the layout. A new headline that fits in English can overflow elsewhere - flag if the component has fixed widths.
- **Pluralized or gendered phrasing** changing meaning when the number or noun changes (a trial of "7 days" vs "1 day").

## 4. Writing the new translations

- Match the file's existing voice (formal/informal address, terminology, brand terms left in Latin script or transliterated). Read neighboring strings in the same file first.
- Re-express the *new claim*; do not machine-translate word for word from the old translation.
- Keep brand and product names exactly as other strings in that locale write them.
- When confidence is lower (rare languages, specialized terminology, marketing slogans that rely on wordplay), translate plainly and put the locale in the "needs native review" list rather than inventing clever copy.
- Never copy the English text into another locale as a placeholder without saying so; an untranslated string is a visible defect and `locale_parity.py` will flag it as identical to the reference.

## 5. Arabic and other RTL / complex-plural languages

- **Direction.** Arabic text is right-to-left. Latin brand names or numbers inside an Arabic sentence can render in surprising order, especially next to punctuation. If a string mixes scripts, test the rendered result or wrap the Latin run appropriately (`&lrm;` / `&rlm;` marks, `<bdi>`, or `dir="auto"`) following what the project already does.
- **Plurals.** Arabic has six plural categories (`zero`, `one`, `two`, `few`, `many`, `other`). i18next JSON v4 uses suffixed keys (`key_zero`, `key_one`, `key_two`, `key_few`, `key_many`, `key_other`); ICU uses the same categories in the `plural` block. If the claim contains a count ("7 days"), update every needed form, not just `_one`/`_other`. Russian, Polish, Czech, and others need `few`/`many` as well.
- **Numerals.** Some Arabic locales use Arabic-Indic digits (`٧`), others Western (`7`). Follow what the existing strings in that file do; formatting via `Intl.NumberFormat` or the framework's formatter is preferable to hand-typed digits.
- **Punctuation.** Arabic comma `،`, semicolon `؛`, question mark `؟`. Match the file.
- **Diacritics (tashkeel).** Follow the file: some projects vocalize headlines, most do not. Do not introduce them inconsistently.
- **Register.** Modern Standard Arabic is the usual default for UI copy unless the project has dialect-specific locales (e.g. `ar-EG`, `ar-SA`); keep each locale's convention.
- **Grammatical gender and number agreement** change with the noun and count; re-check the sentence, don't swap one word.

## 6. Verification

- `scripts/locale_parity.py --root <locales dir>`: no missing keys; no values identical to the reference language unless deliberate (brand names, loanwords).
- `scripts/locale_parity.py --root <locales dir> --grep "<old wording>"`: no remaining matches, or each is explained.
- `scripts/sweep.py "<old text>" "<old translation(s)>"` (add `--allow` for approved leftovers): leftovers in tests, docs, metadata.
- Project checks: i18n linters (`i18next-parser`, `eslint-plugin-i18next`, `formatjs extract`/`verify`, `msgfmt --check`, `flutter gen-l10n`), unit tests, type-check, build.
- If the project uses a custom locale checker (e.g. a ts-morph based key-validation CLI), run it: it catches dangling and unused keys that grep cannot.
- Spot-check the rendered page in at least the source language and one RTL language if the layout can break.
