# Documentation index schema

The format `scripts/build_index.py` produces, and how to read/extend it.

## Top-level shape

```json
{
  "library": "some-library",
  "version": "4.1.0",
  "generated_at": "2026-09-27T18:00:00.000000",
  "source_dir": "docs/pruned/some-library",
  "sections": [ /* flat list, one entry per heading-delimited section */ ],
  "topics": { /* the same sections, grouped by topic for fast lookup */ }
}
```

## `sections` entries

```json
{
  "file": "Installation.md",
  "heading": "Install via Bun",
  "level": 2,
  "topic": "installation",
  "line_start": 12,
  "line_end": 18
}
```

- `file` is relative to `source_dir`.
- `line_start`/`line_end` are 1-indexed, inclusive, and delimit exactly the lines to read for this section — jump straight there instead of reading the whole file.
- A file with no Markdown headings at all still gets a single section with `"heading": null` covering the whole file, so nothing is silently excluded from the index.

## `topics` map

Same section objects (minus `topic`, since it's the key), grouped for O(1) "give me everything about configuration" lookups:

```json
{
  "installation": [ {"file": "...", "heading": "...", "line_start": 1, "line_end": 8}, ... ],
  "configuration": [ ... ],
  "api": [ ... ],
  "features": [ ... ],
  "usage": [ ... ],
  "notes": [ ... ],
  "other": [ ... ]
}
```

## Topic categorization rules

Each heading is checked against keyword lists **in this order** (first match wins), defined in `build_index.py`'s `TOPIC_KEYWORDS`:

1. **notes** — note, warning, caution, important, gotcha, breaking change, deprecat(ed/ion), migration
2. **installation** — install, setup, getting started, quick start
3. **configuration** — config, option, setting, environment variable
4. **api** — api, reference, method, endpoint, function, class, interface
5. **features** — feature, capabilit(y/ies)
6. **usage** — usage, how to, example, guide, tutorial
7. **other** — fallback when nothing above matches

`notes` is checked first deliberately: a heading like "Important: usage restrictions" should land in `notes`, not `usage`, since the caveat is the point of that section.

This is heading-text keyword matching, not content analysis — a section titled "Overview" that's actually about configuration will land in `other`. Always skim the generated index and re-file anything that's obviously wrong before treating it as reliable; the SKILL.md's workflow already says this, it's repeated here because it's the single most common way this index degrades in usefulness over time if left unchecked.

## Extending categorization

To add or adjust a topic, edit `TOPIC_KEYWORDS` in `build_index.py` — it's a simple ordered list of `(topic_name, [keywords])` tuples, matched as case-insensitive substrings against the heading text. Keep new keywords specific enough not to false-positive on unrelated headings (e.g. adding a bare `"api"` keyword is fine; adding a bare `"set"` for "settings" would also match "Reset" or "Offset").
