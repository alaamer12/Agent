# Data files

Vocabularies that describe the outside world live in `scripts/data/`, not in code, because they go stale: new frameworks, new trackers, other languages. They can be extended without touching a script. Standards vocabularies (HTML elements, CSS units and properties) stay in code because a spec defines them.

## Fast path
1. Find the vocabulary in "The files" below.
2. Edit the JSON/TXT file directly; no code change is needed.
3. Use the format section for that file (signatures are the only structured one).
4. A missing entry degrades gracefully; add only what you can verify.

## Contents
- The files
- Technology signatures
- Trackers, phrases, colours
- Design rules for heuristics

## The files
| File | Used by | What it holds |
|---|---|---|
| `tech_signatures.json` | `design patterns` | Technology fingerprints, CDN URL grammars, and the response-header policy (which headers count as informative vs noise) |
| `trackers.txt` | `website`, `design patterns` | Analytics/ads/telemetry domains (one per line, `#` comments, subdomains match) |
| `more_phrases.json` | `dom` | "Show more" button texts, grouped by language |
| `css_named_colors.json` | `design tokens` | The full CSS named-colour table (name -> hex) |
| `css_features.json` | `design tokens` | Notable modern CSS properties and selector constructs to call out in the summary (reporting only) |

All are starter sets, not closed worlds. A missing entry degrades gracefully (raw evidence is still reported, a button can be named with `--more-phrase`, a host blocked with `--block`).

## Technology signatures
Format (`tech_signatures.json`, or your own file passed with `design --signatures FILE`; same-name entries replace built-ins, new entries are added):

```json
{
  "cdn_patterns": [ { "name": "my CDN", "re": "cdn\\.example\\.com/(?P<pkg>[\\w.-]+)@(?P<ver>[\\w.-]+)/" } ],
  "signatures": [
    { "name": "Zorblax", "category": "meta-framework",
      "signals": [
        { "in": "meta_generator", "re": "^zorblax", "weight": "strong" },
        { "in": "attr_prefix",    "re": "^data-zorb", "weight": "medium" }
      ] }
  ]
}
```

- `in` (the evidence pool): `meta_generator`, `meta_name`, `header` (`"name: value"`), `cookie_name`, `script_src`, `stylesheet_href`, `any_url` (host+path, query ignored), `comment`, `attr_name`, `attr_prefix`, `class_name`, `class_prefix`, `tag`, `inline_script`, `json_script_id`, `script_type`, `global`, `css_banner`, `css_text`, `root_marker`, `input_name`, `package`.
- `re`: case-insensitive regex searched in each pool entry.
- `weight`: `strong` (unambiguous), `medium` (suggestive), `weak` (common word). Confidence: **high** = any strong; **medium** = two or more medium (or medium + weak); **low** otherwise.
- A version is read from the matched generator/header/banner text or from an inferred package version.
- Keep signals specific (a unique attribute, path, header or global). Avoid generic words that appear in page text; weak signals alone never exceed `low`.

## Trackers, phrases, colours
- `trackers.txt`: add domains, one per line. Per run: `website --block HOST`, `--no-default-blocklist`.
- `more_phrases.json`: add a language object (`"xx": ["phrase", ...]`) or phrases to an existing one. Phrases are lowercase literals, matched as the whole button text or as a short prefix (so `Show more (24)` matches `show more`). Per run: `dom --more-lang xx`, `--more-phrase TEXT`.
- `css_named_colors.json`: generated from the CSS Color 4 table (name -> `#rrggbb`); regenerate only if the spec adds colours.

## Design rules for heuristics
These keep the scripts honest; follow them when adding detection:
1. Report **evidence first**, names second; never print "none" when you only mean "none known".
2. Prefer **structural** measures over name lists (variable families by shared prefix, theme scopes by variable overlap, atomic CSS by rule size, generated classes by hash shape).
3. Put vocabularies in **data files**, with a per-run override.
4. Match URLs on host and path only; never store cookie values or other secrets.
5. Keep thresholds and limits as **named constants** at the top of the module (with a comment), not as literals inside expressions.
6. Add a regression test in `scripts/test_tech.py` (offline) or `scripts/test_dom.py` (browser) for every new rule, including an unlisted/negative case.
