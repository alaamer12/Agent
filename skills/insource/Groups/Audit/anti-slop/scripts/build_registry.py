"""Build the canonical registry from the reviewed catalog source map."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "anti-slop"
SOURCE_MAP = SKILL_ROOT / "source-map.md"
LOCAL_CATALOG = ROOT / "antipatterns.json"
RUST_REGISTRY = ROOT / "registry.rs"
OUTPUT = SKILL_ROOT / "registry" / "registry.json"
CATALOG_URL = "https://impeccable.style/slop/"
STRUCTURAL_CANDIDATE_RULES = {
    "side-tab",
    "gpt-thin-border-wide-shadow",
    "gradient-text",
    "repeating-stripes-gradient",
    "layout-transition",
    "marquee",
    "em-dash-overuse",
    "broken-image",
    "all-caps-body",
    "justified-text",
    "wide-tracking",
    "nested-cards",
    "repeated-container-text",
    "skipped-heading",
    "images-move-on-hover",
}
EXPECTED_SECTIONS = {
    "Your design system": 4,
    "Visual Details": 8,
    "Typography": 11,
    "Color & Contrast": 7,
    "Layout & Space": 12,
    "Motion": 6,
    "Copy": 5,
    "Imagery": 4,
    "General quality": 10,
}


def clean_cell(value: str) -> str:
    return value.strip()


def read_table(source: str, start_heading: str, end_heading: str) -> list[list[str]]:
    inside = False
    rows = []
    for line in source.splitlines():
        if line == start_heading:
            inside = True
            continue
        if inside and line.startswith("## "):
            if line == end_heading:
                break
            continue
        if inside and line.startswith("|") and not line.startswith("|---"):
            cells = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
            if cells and cells[0].isdigit():
                rows.append(cells)
            elif cells and cells[0].startswith("<https://"):
                rows.append(cells)
            elif len(cells) >= 2 and cells[0] not in {"#", "Example"}:
                rows.append(cells)
    return rows


def rust_string(block: str, field: str) -> str | None:
    match = re.search(rf"\b{field}:\s*\"((?:\\.|[^\"\\])*)\"", block)
    return json.loads(f'"{match.group(1)}"') if match else None


def read_rust_registry(source: str) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    builtins_match = re.search(
        r"pub static ANTIPATTERNS:\s*&\[Antipattern\]\s*=\s*&\[(.*?)\n\];",
        source,
        re.DOTALL,
    )
    if not builtins_match:
        raise ValueError("Could not locate the built-in Antipattern array in registry.rs")

    builtins: dict[str, dict[str, object]] = {}
    blocks = re.findall(r"Antipattern\s*\{(.*?)\n\s*\},", builtins_match.group(1), re.DOTALL)
    for block in blocks:
        pattern_id = rust_string(block, "id")
        category = rust_string(block, "category")
        name = rust_string(block, "name")
        description = rust_string(block, "description")
        if not all((pattern_id, category, name, description)):
            raise ValueError(f"Incomplete Antipattern record in registry.rs: {block[:100]!r}")
        scopes_match = re.search(r"\bscopes:\s*Some\(&\[(.*?)\]\)", block, re.DOTALL)
        severity_match = re.search(r"\bseverity:\s*Some\(\"([^\"]+)\"\)", block)
        builtins[pattern_id] = {
            "id": pattern_id,
            "category": category,
            "name": name,
            "description": description,
            "scopes": re.findall(r'\"([^\"]+)\"', scopes_match.group(1)) if scopes_match else [],
            "severity": severity_match.group(1) if severity_match else None,
            "skillSection": rust_string(block, "skill_section"),
            "skillGuideline": rust_string(block, "skill_guideline"),
        }

    engines_match = re.search(r"pub const RULE_ENGINE_SUPPORT:.*?=\s*&\[(.*?)\n\];", source, re.DOTALL)
    engine_support = {}
    if engines_match:
        for engine, supported in re.findall(r'\("([^\"]+)"\s*,\s*&\[(.*?)\]\)', engines_match.group(1), re.DOTALL):
            engine_support[engine] = re.findall(r'\"([^\"]+)\"', supported)

    immediate_match = re.search(r"pub const IMMEDIATE_TIER_RULES:.*?=\s*&\[(.*?)\n\];", source, re.DOTALL)
    immediate_rules = re.findall(r'\"([^\"]+)\"', immediate_match.group(1)) if immediate_match else []
    seen_scopes = []
    for record in builtins.values():
        for scope in record["scopes"]:
            if scope not in seen_scopes:
                seen_scopes.append(scope)

    metadata = {
        "builtInCount": len(builtins),
        "sourceFile": "../../registry.rs",
        "scopes": seen_scopes,
        "ruleEngineSupport": engine_support,
        "immediateTierRuleIds": immediate_rules,
        "supportsRuntimeExtension": "pub fn extend(" in source,
    }
    return builtins, metadata


def build() -> dict[str, object]:
    source = SOURCE_MAP.read_text(encoding="utf-8")
    catalog_text = (SKILL_ROOT / "assets" / "source" / "slop.txt").read_text(encoding="utf-8")
    catalog_lines = catalog_text.splitlines()
    try:
        catalog_cursor = next(i for i, line in enumerate(catalog_lines) if line.strip() == "The catalog") + 1
    except StopIteration as error:
        raise ValueError("Captured Slop text has no catalog section") from error
    local_records = json.loads(LOCAL_CATALOG.read_text(encoding="utf-8"))
    local_by_id = {record["id"]: record for record in local_records}
    rust_source = RUST_REGISTRY.read_text(encoding="utf-8")
    rust_by_id, local_registry_metadata = read_rust_registry(rust_source)
    if set(local_by_id) != set(rust_by_id):
        raise ValueError("antipatterns.json and registry.rs built-in IDs do not match")
    for pattern_id, local in local_by_id.items():
        rust = rust_by_id[pattern_id]
        for key in ("id", "category", "name", "description"):
            if local[key] != rust[key]:
                raise ValueError(f"antipatterns.json and registry.rs disagree on {pattern_id}.{key}")
    pattern_rows = read_table(source, "## Catalog entries", "## Example pages")
    example_rows = read_table(source, "## Example pages", "## Capture notes")

    if len(pattern_rows) != 67:
        raise ValueError(f"Expected 67 catalog rows; found {len(pattern_rows)}")
    if len(example_rows) != 11:
        raise ValueError(f"Expected 11 example rows; found {len(example_rows)}")

    examples: dict[str, dict[str, object]] = {}
    pattern_examples: dict[str, list[str]] = {}
    for row in example_rows:
        if len(row) != 5:
            raise ValueError(f"Malformed example row: {row}")
        name, url_cell, related_cell, text_path, screenshot_cell = row
        example_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        url = url_cell.strip("<>")
        related_ids = re.findall(r"`([^`]+)`", related_cell)
        screenshot_paths = [
            f"../{path}"
            for path in re.findall(r"`([^`]+)`", screenshot_cell)
        ]
        examples[example_id] = {
            "id": example_id,
            "name": name,
            "url": url,
            "textCapture": f"../{text_path.strip('`')}",
            "screenshotCaptures": screenshot_paths,
            "relatedPatternIds": related_ids,
        }
        for pattern_id in related_ids:
            pattern_examples.setdefault(pattern_id, []).append(example_id)

    patterns = []
    section_counts: dict[str, int] = {}
    modality_counts: dict[str, int] = {}
    for row in pattern_rows:
        if len(row) != 6:
            raise ValueError(f"Malformed catalog row: {row}")
        number, pattern_id, name, section, modality, local_id = row
        pattern_id = pattern_id.strip("`")
        local_id = local_id.strip("`")
        title_index = next(
            (i for i in range(catalog_cursor, len(catalog_lines)) if catalog_lines[i].strip() == name),
            None,
        )
        if title_index is None:
            raise ValueError(f"Catalog name {name!r} for {pattern_id} was not found in captured Slop text")
        description_index = next(
            (i for i in range(title_index + 1, len(catalog_lines)) if catalog_lines[i].strip()),
            None,
        )
        if description_index is None:
            raise ValueError(f"Catalog description for {pattern_id} is missing")
        catalog_description = catalog_lines[description_index].strip()
        catalog_cursor = description_index + 1
        section_counts[section] = section_counts.get(section, 0) + 1
        modality_key = modality.lower().replace(" ", "-")
        modality_counts[modality_key] = modality_counts.get(modality_key, 0) + 1
        local = None if local_id == "—" else local_by_id.get(local_id)
        if local_id != "—" and local is None:
            raise ValueError(f"Unknown local ID {local_id!r} for {pattern_id}")
        category = (
            "design-system"
            if section == "Your design system"
            else local["category"]
            if local
            else "slop"
        )
        catalog_badge = (
            "Your design system"
            if category == "design-system"
            else "Quality"
            if category == "quality"
            else "AI slop"
        )
        source_engine_scopes = rust_by_id[pattern_id]["scopes"] if local else []
        source_severity = rust_by_id[pattern_id]["severity"] if local else None
        source_skill_section = rust_by_id[pattern_id]["skillSection"] if local else None
        source_skill_guideline = rust_by_id[pattern_id]["skillGuideline"] if local else None
        implementation = {
            "source": "source-text-or-structure-candidate",
            "browser": "rendered-browser-inspection",
            "design-review": "visual-contextual-review",
        }[modality_key]
        knowledge_path = SKILL_ROOT / "patterns" / pattern_id / "knowledge.md"
        detection_path = SKILL_ROOT / "patterns" / pattern_id / "detection.md"
        pattern_docs_complete = knowledge_path.is_file() and detection_path.is_file()
        test_disposition = {
            "source": "source-candidate-accuracy-tests-pending",
            "browser": "browser-runtime-calibration-pending",
            "design-review": "visual-context-calibration-pending",
        }[modality_key]
        patterns.append(
            {
                "id": pattern_id,
                "name": name,
                "category": category,
                "catalogBadge": catalog_badge,
                "catalogSection": section,
                "catalogDescription": catalog_description,
                "sourceEngineScopes": source_engine_scopes,
                "severity": source_severity,
                "confidenceGuidance": "All automated/source matches are candidates; use visual/contextual evidence before confirmation.",
                "detectorApplicability": (
                    "structural-candidate-detector"
                    if pattern_id in STRUCTURAL_CANDIDATE_RULES
                    else "visual-contextual-review"
                    if modality_key == "design-review"
                    else "browser-runtime-review"
                    if modality_key == "browser"
                    else "source-inspection-without-deterministic-detector"
                ),
                "scope": ["page", "multi-page", "application", "project"],
                "detection": {
                    "officialModality": modality_key,
                    "currentDisposition": implementation,
                    "status": "knowledge-and-detection-guidance-complete" if pattern_docs_complete else "pattern-documents-pending",
                    "regexCanConfirm": False,
                },
                "localSource": (
                    {
                        "id": local["id"],
                        "category": local["category"],
                        "name": local["name"],
                        "description": local["description"],
                        "scopes": source_engine_scopes,
                        "severity": source_severity,
                        "skillSection": source_skill_section,
                        "skillGuideline": source_skill_guideline,
                        "files": ["../../antipatterns.json", "../../registry.rs"],
                    }
                    if local
                    else None
                ),
                "provenance": {
                    "catalogUrl": CATALOG_URL,
                    "catalogText": "../assets/source/slop.txt",
                    "catalogDom": "../assets/source/slop.html",
                    "catalogScreenshots": "../assets/screenshots/slop/impeccable.style_slop/*.png",
                    "exampleIds": pattern_examples.get(pattern_id, []),
                },
                "knowledge": f"../patterns/{pattern_id}/knowledge.md",
                "detectionGuide": f"../patterns/{pattern_id}/detection.md",
                "tests": {
                    "status": "pending",
                    "fixtureDirectory": f"../tests/fixtures/{pattern_id}/",
                    "disposition": test_disposition,
                },
            }
        )

    if section_counts != EXPECTED_SECTIONS:
        raise ValueError(f"Unexpected section counts: {section_counts}")
    if modality_counts != {"source": 49, "browser": 12, "design-review": 6}:
        raise ValueError(f"Unexpected official modality counts: {modality_counts}")
    catalog_badge_counts = {
        badge: sum(pattern["catalogBadge"] == badge for pattern in patterns)
        for badge in ("AI slop", "Quality", "Your design system")
    }
    if catalog_badge_counts != {"AI slop": 38, "Quality": 25, "Your design system": 4}:
        raise ValueError(f"Unexpected catalog badge counts: {catalog_badge_counts}")
    mapped_local_ids = {
        pattern["localSource"]["id"]
        for pattern in patterns
        if pattern["localSource"] is not None
    }
    if mapped_local_ids != set(local_by_id):
        missing = sorted(set(local_by_id) - mapped_local_ids)
        unknown = sorted(mapped_local_ids - set(local_by_id))
        raise ValueError(f"Local source mapping mismatch; missing={missing}, unknown={unknown}")
    if len({pattern["id"] for pattern in patterns}) != 67:
        raise ValueError("Catalog IDs must be unique")
    for pattern_id, example_ids in pattern_examples.items():
        if pattern_id not in {pattern["id"] for pattern in patterns}:
            raise ValueError(f"Example points to unknown pattern {pattern_id}")

    return {
        "schemaVersion": 1,
        "catalog": {
            "name": "Impeccable Slop catalog",
            "url": CATALOG_URL,
            "snapshotDate": "2026-10-06",
            "patternCount": 67,
            "detectorRuleCount": 61,
            "designReviewCount": 6,
            "localSourceCount": len(local_by_id),
        },
        "sourceMap": "../source-map.md",
        "localRegistry": local_registry_metadata,
        "patterns": patterns,
        "examples": list(examples.values()),
    }


if __name__ == "__main__":
    registry = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(registry['patterns'])} patterns and {len(registry['examples'])} examples to {OUTPUT}")