"""Validate registry completeness and every captured evidence reference."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "anti-slop"
REGISTRY_FILE = SKILL_ROOT / "registry" / "registry.json"
LOCAL_CATALOG = ROOT / "antipatterns.json"


def validate() -> list[str]:
    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    patterns = registry["patterns"]
    examples = registry["examples"]
    errors = []
    ids = [pattern["id"] for pattern in patterns]
    registry_ids = set(ids)
    example_ids = {example["id"] for example in examples}
    local_records = json.loads(LOCAL_CATALOG.read_text(encoding="utf-8"))
    local_by_id = {record["id"]: record for record in local_records}

    if len(patterns) != 67:
        errors.append(f"expected 67 patterns, found {len(patterns)}")
    if len(ids) != len(set(ids)):
        errors.append("pattern IDs are not unique")
    if len(examples) != 11:
        errors.append(f"expected 11 examples, found {len(examples)}")
    if Counter(pattern["catalogSection"] for pattern in patterns) != {
        "Your design system": 4,
        "Visual Details": 8,
        "Typography": 11,
        "Color & Contrast": 7,
        "Layout & Space": 12,
        "Motion": 6,
        "Copy": 5,
        "Imagery": 4,
        "General quality": 10,
    }:
        errors.append("catalog section totals do not match the official counts")
    if Counter(pattern["category"] for pattern in patterns) != {
        "design-system": 4,
        "slop": 38,
        "quality": 25,
    }:
        errors.append("routing category totals do not match the catalog badges")
    if Counter(pattern["detection"]["officialModality"] for pattern in patterns) != {
        "source": 49,
        "browser": 12,
        "design-review": 6,
    }:
        errors.append("official modality totals do not match the catalog")

    registry_root = REGISTRY_FILE.parent
    expected_local_ids = set()
    for pattern in patterns:
        for required in ("id", "name", "category", "catalogSection", "scope", "detection", "provenance", "knowledge", "detectionGuide", "tests"):
            if required not in pattern:
                errors.append(f"{pattern.get('id', '<unknown>')} lacks `{required}`")
        if not pattern.get("catalogDescription"):
            errors.append(f"{pattern['id']} has no captured catalog description")
        if pattern["detection"].get("status") != "knowledge-and-detection-guidance-complete":
            errors.append(f"{pattern['id']} knowledge/detection documents are not complete")
        local_source = pattern.get("localSource")
        if local_source:
            expected_local_ids.add(local_source["id"])
            local = local_by_id.get(local_source["id"])
            if local is None:
                errors.append(f"{pattern['id']} refers to unknown local ID {local_source['id']}")
            elif any(local_source.get(key) != local.get(key) for key in ("id", "category", "name", "description")):
                errors.append(f"{pattern['id']} local-source metadata differs from antipatterns.json")
            for relative in local_source["files"]:
                if not (registry_root / relative).is_file():
                    errors.append(f"{pattern['id']} has missing local source {relative}")
        knowledge_path = registry_root / pattern["knowledge"]
        detection_path = registry_root / pattern["detectionGuide"]
        if not knowledge_path.is_file():
            errors.append(f"{pattern['id']} has missing knowledge file {pattern['knowledge']}")
        else:
            knowledge = knowledge_path.read_text(encoding="utf-8")
            checks = {
                "definition": r"^## .*definition|^## .*empirical",
                "harm/problem": r"^## .*harm|^## .*problem|^## .*principle",
                "recognition/evidence": r"^## .*recognition|^## .*signal|^## .*visual|^## .*browser",
                "causes": r"^## .*causes",
                "exceptions": r"^## .*exceptions",
                "correction": r"^## .*correction",
                "research references": r"^## .*references",
            }
            for field, expression in checks.items():
                if not re.search(expression, knowledge, re.IGNORECASE | re.MULTILINE):
                    errors.append(f"{pattern['id']} knowledge is missing `{field}`")
        if not detection_path.is_file():
            errors.append(f"{pattern['id']} has missing detection guide {pattern['detectionGuide']}")
        else:
            detection = detection_path.read_text(encoding="utf-8")
            if not re.search(r"^## .*false-positive", detection, re.IGNORECASE | re.MULTILINE):
                errors.append(f"{pattern['id']} detection guide lacks false-positive controls")
            if not re.search(r"^## .*test disposition|^## .*test coverage", detection, re.IGNORECASE | re.MULTILINE):
                errors.append(f"{pattern['id']} detection guide lacks test disposition")
        for example_id in pattern["provenance"]["exampleIds"]:
            if example_id not in example_ids:
                errors.append(f"{pattern['id']} points to unknown example {example_id}")
        if pattern["detection"]["regexCanConfirm"] is not False:
            errors.append(f"{pattern['id']} incorrectly allows regex confirmation")

    for example in examples:
        for relative in [example["textCapture"], *example["screenshotCaptures"]]:
            if not (registry_root / relative).is_file():
                errors.append(f"{example['id']} has missing evidence file {relative}")
        for pattern_id in example["relatedPatternIds"]:
            if pattern_id not in registry_ids:
                errors.append(f"{example['id']} points to unknown pattern {pattern_id}")

    for required in [
        registry["sourceMap"],
        "../assets/source/slop.html",
        "../assets/source/slop.txt",
    ]:
        if not (registry_root / required).is_file():
            errors.append(f"registry evidence file is missing: {required}")

    if len(expected_local_ids) != 60:
        errors.append(f"expected 60 mapped local IDs, found {len(expected_local_ids)}")
    if expected_local_ids != set(local_by_id):
        errors.append("registry local IDs do not match the complete antipatterns.json set")
    catalog_screenshots = list((SKILL_ROOT / "assets" / "screenshots" / "slop" / "impeccable.style_slop").glob("*.png"))
    if len(catalog_screenshots) != 23:
        errors.append(f"expected 23 sequential Slop captures, found {len(catalog_screenshots)}")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("Registry validation failed:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)
    print("Registry validation passed: 67 unique patterns, complete knowledge/detection fields, 11 linked examples, 60 local IDs, and existing evidence files.")