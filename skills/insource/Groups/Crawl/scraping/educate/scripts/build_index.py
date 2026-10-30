#!/usr/bin/env python3
"""
Build an API-like index over a directory of pruned Markdown documentation,
so the agent can jump straight to the right file/section instead of reading
or searching every file every time it needs something.

USAGE
    python build_index.py <pruned-docs-dir> --library NAME --version VERSION -o index.json

Walks every .md file under the given directory, extracts headings, and
buckets each section into one of: installation, configuration, api,
features, usage, notes, other -- see references/index-schema.md for the
exact schema and topic-matching rules.

This is a heuristic (keyword matching on heading text), not a guarantee.
Skim the output afterward and re-file anything that landed in the wrong
bucket -- see the "Build the documentation index" step in SKILL.md.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

# Order matters: the first topic whose keywords match wins. Keep "notes"
# checked early since warnings/caveats often get miscategorized as "usage"
# if checked later (e.g. a heading like "Important: usage restrictions").
TOPIC_KEYWORDS = [
    ("notes", ["note", "warning", "caution", "important", "gotcha", "breaking change", "deprecat", "migration"]),
    ("installation", ["install", "setup", "getting started", "quick start", "quickstart"]),
    ("configuration", ["config", "option", "setting", "environment variable", "env var"]),
    ("api", ["api", "reference", "method", "endpoint", "function", "class", "interface"]),
    ("features", ["feature", "capabilit"]),
    ("usage", ["usage", "how to", "example", "guide", "tutorial", "walkthrough"]),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def categorize(heading_text: str) -> str:
    lowered = heading_text.lower()
    for topic, keywords in TOPIC_KEYWORDS:
        if any(kw in lowered for kw in keywords):
            return topic
    return "other"


def extract_sections(md_path: Path, docs_root: Path):
    with open(md_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    headings = []
    for i, line in enumerate(lines, start=1):
        m = HEADING_RE.match(line.rstrip("\n"))
        if m:
            headings.append({"line": i, "level": len(m.group(1)), "text": m.group(2).strip()})

    sections = []
    rel_path = str(md_path.relative_to(docs_root))
    for idx, h in enumerate(headings):
        line_end = headings[idx + 1]["line"] - 1 if idx + 1 < len(headings) else len(lines)
        sections.append({
            "file": rel_path,
            "heading": h["text"],
            "level": h["level"],
            "topic": categorize(h["text"]),
            "line_start": h["line"],
            "line_end": line_end,
        })

    # A file with no headings at all still gets one "other" section covering
    # the whole file, so nothing is silently left out of the index.
    if not sections and lines:
        sections.append({
            "file": rel_path,
            "heading": None,
            "level": 0,
            "topic": "other",
            "line_start": 1,
            "line_end": len(lines),
        })

    return sections


def build_index(docs_dir: str, library: str, version: str):
    docs_root = Path(docs_dir)
    all_sections = []
    for md_path in sorted(docs_root.rglob("*.md")):
        all_sections.extend(extract_sections(md_path, docs_root))

    topics = {}
    for section in all_sections:
        topics.setdefault(section["topic"], []).append(
            {"file": section["file"], "heading": section["heading"],
             "line_start": section["line_start"], "line_end": section["line_end"]}
        )

    return {
        "library": library,
        "version": version,
        "generated_at": datetime.now().isoformat(),
        "source_dir": str(docs_root),
        "sections": all_sections,
        "topics": topics,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("docs_dir", help="Directory of pruned Markdown docs to index.")
    parser.add_argument("--library", required=True, help="Library/framework name this index is for.")
    parser.add_argument("--version", required=True, help="Version these docs correspond to.")
    parser.add_argument("-o", "--output", default="index.json", help="Output path for the index (default: index.json).")
    args = parser.parse_args()

    index = build_index(args.docs_dir, args.library, args.version)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    topic_counts = {topic: len(sections) for topic, sections in index["topics"].items()}
    print(f"Indexed {len(index['sections'])} section(s) across "
          f"{len(set(s['file'] for s in index['sections']))} file(s).")
    print(f"By topic: {topic_counts}")
    print(f"Written to: {args.output}")


if __name__ == "__main__":
    main()
