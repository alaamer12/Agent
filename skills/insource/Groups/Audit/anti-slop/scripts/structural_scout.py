"""Read-only source-signature scout; all output is candidate evidence."""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "anti-slop" / "registry" / "registry.json"
SUPPORTED_SUFFIXES = {
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".html",
    ".htm",
    ".jsx",
    ".tsx",
    ".vue",
    ".svelte",
    ".md",
    ".txt",
}
HTML_SUFFIXES = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte"}
TEXT_SUFFIXES = {".html", ".htm", ".md", ".txt"}
IGNORED_DIRS = {
    ".git",
    ".next",
    ".nuxt",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}
MAX_FILE_BYTES = 1_000_000

REGEX_RULES = {
    "gradient-text": re.compile(
        r"(?:-webkit-)?background-clip\s*:\s*text\b|"
        r"-webkit-text-fill-color\s*:\s*transparent\b",
        re.IGNORECASE,
    ),
    "repeating-stripes-gradient": re.compile(
        r"repeating-(?:linear|radial|conic)-gradient\s*\(", re.IGNORECASE
    ),
    "layout-transition": re.compile(
        r"\btransition(?:-property)?\s*:\s*[^;{}]*"
        r"\b(?:width|height|margin(?:-[\w-]+)?|padding(?:-[\w-]+)?|"
        r"top|right|bottom|left|grid-template-rows|grid-template-columns)\b",
        re.IGNORECASE,
    ),
    "marquee": re.compile(
        r"@keyframes\s+[\w-]*marquee\b|\banimation(?:-name)?\s*:\s*[^;{}]*\bmarquee\b",
        re.IGNORECASE,
    ),
    "justified-text": re.compile(r"\btext-align\s*:\s*justify(?:-all)?\b", re.IGNORECASE),
}
CSS_BLOCK = re.compile(r"([^{}]+)\{([^{}]*)\}", re.DOTALL)
LETTER_SPACING = re.compile(
    r"\bletter-spacing\s*:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*em\b",
    re.IGNORECASE,
)
EM_DASH = re.compile(r"—|--")
PLACEHOLDER_SRC = re.compile(r"(?:placeholder|dummy|example|missing|broken)(?:[./_-]|$)", re.IGNORECASE)
CSS_STYLE_SUFFIXES = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".vue", ".svelte"}


class Element:
    def __init__(self, tag: str, attrs: dict[str, str | None], line: int) -> None:
        self.tag = tag
        self.attrs = attrs
        self.line = line
        self.children: list[Element | str] = []


class ElementTreeParser(HTMLParser):
    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Element("__root__", {}, 1)
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        element = Element(tag.lower(), dict(attrs), self.getpos()[0])
        self.stack[-1].children.append(element)
        if element.tag not in self.VOID_TAGS:
            self.stack.append(element)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack[-1].children.append(Element(tag.lower(), dict(attrs), self.getpos()[0]))

    def handle_endtag(self, tag: str) -> None:
        target = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == target:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def _text(node: Element) -> str:
    return " ".join(child if isinstance(child, str) else _text(child) for child in node.children)


def _snippet(source: str, start: int) -> tuple[int, int, str]:
    line = source.count("\n", 0, start) + 1
    line_start = source.rfind("\n", 0, start) + 1
    line_end = source.find("\n", start)
    if line_end < 0:
        line_end = len(source)
    text = source[line_start:line_end].strip()
    if len(text) > 240:
        text = text[:237] + "..."
    return line, start - line_start + 1, text


def _candidate(
    pattern_id: str,
    path: str,
    source: str,
    start: int,
    explanation: str,
) -> dict[str, object]:
    line, column, snippet = _snippet(source, start)
    return {
        "patternId": pattern_id,
        "path": path.replace("\\", "/"),
        "line": line,
        "column": column,
        "snippet": snippet,
        "evidenceModality": "structural",
        "status": "candidate",
        "confidence": "candidate",
        "explanation": explanation,
    }


def _css_block_candidates(source: str, path: str) -> list[dict[str, object]]:
    findings = []
    for match in CSS_BLOCK.finditer(source):
        selector, declarations = match.group(1), match.group(2)
        lower = declarations.lower()
        if re.search(r"\bborder-left(?:-width)?\s*:", lower) and re.search(
            r"\bborder-radius\s*:", lower
        ):
            findings.append(
                _candidate(
                    "side-tab",
                    path,
                    source,
                    match.start(2),
                    "A CSS rule combines a left-side border with rounded corners; verify its role and rendered use.",
                )
            )
        if re.search(r"\bborder(?:-(?:width|style|color))?\s*:", lower) and re.search(
            r"\bbox-shadow\s*:", lower
        ):
            findings.append(
                _candidate(
                    "gpt-thin-border-wide-shadow",
                    path,
                    source,
                    match.start(2),
                    "A CSS rule combines border and shadow; visual review must determine whether they redundantly define the surface.",
                )
            )
        selector_lower = selector.lower()
        if ":hover" in selector_lower and re.search(r"\bimg\b", selector_lower) and re.search(
            r"\btransform\s*:\s*[^;]*(?:scale|translate|rotate)", lower
        ):
            findings.append(
                _candidate(
                    "images-move-on-hover",
                    path,
                    source,
                    match.start(2),
                    "A hovered image is transformed; verify touch/keyboard alternatives and whether motion serves a purpose.",
                )
            )
    return findings


def _html_candidates(source: str, path: str) -> list[dict[str, object]]:
    parser = ElementTreeParser()
    parser.feed(source)
    findings = []
    heading_rank = None

    def walk(node: Element) -> None:
        nonlocal heading_rank
        if node.tag == "img":
            src = node.attrs.get("src")
            srcset = node.attrs.get("srcset")
            src_value = (src or "").strip()
            if (src is None and not srcset) or (not src_value and not srcset) or PLACEHOLDER_SRC.search(src_value):
                findings.append(
                    _candidate(
                        "broken-image",
                        path,
                        source,
                        max(0, _line_offset(source, node.line)),
                        "The image source is empty, absent, or placeholder-like; confirm its runtime loading state.",
                    )
                )

        if re.fullmatch(r"h[1-6]", node.tag):
            current = int(node.tag[1])
            if heading_rank is not None and current > heading_rank + 1:
                findings.append(
                    _candidate(
                        "skipped-heading",
                        path,
                        source,
                        max(0, _line_offset(source, node.line)),
                        f"Heading rank jumps from h{heading_rank} to {node.tag}; inspect the full content outline.",
                    )
                )
            heading_rank = current

        text = _text(node)
        if node.tag == "p":
            letters = [char for char in text if char.isalpha()]
            if len(text.strip()) >= 80 and len(letters) >= 50 and all(char.isupper() for char in letters):
                findings.append(
                    _candidate(
                        "all-caps-body",
                        path,
                        source,
                        max(0, _line_offset(source, node.line)),
                        "A long paragraph is authored in uppercase; review its role, language, and reading context.",
                    )
                )

        classes = set((node.attrs.get("class") or "").split())
        is_card = "card" in classes or "panel" in classes or "data-card" in node.attrs
        if is_card:
            descendants = list(_descendants(node))
            if any(
                child is not node
                and ("card" in set((child.attrs.get("class") or "").split()) or "panel" in set((child.attrs.get("class") or "").split()))
                for child in descendants
            ):
                findings.append(
                    _candidate(
                        "nested-cards",
                        path,
                        source,
                        max(0, _line_offset(source, node.line)),
                        "A card/panel contains another card-like element; verify whether each boundary has a distinct role.",
                    )
                )
            segments = [segment.strip().casefold() for segment in _text_segments(node) if len(segment.strip()) >= 3]
            repeated = [phrase for phrase, count in Counter(segments).items() if count >= 3]
            if repeated:
                findings.append(
                    _candidate(
                        "repeated-container-text",
                        path,
                        source,
                        max(0, _line_offset(source, node.line)),
                        f"The container repeats a literal text segment at least three times: {repeated[0]!r}.",
                    )
                )

        for child in node.children:
            if isinstance(child, Element):
                walk(child)

    walk(parser.root)
    return findings


def _line_offset(source: str, line: int) -> int:
    if line <= 1:
        return 0
    position = 0
    for _ in range(line - 1):
        next_line = source.find("\n", position)
        if next_line < 0:
            return len(source)
        position = next_line + 1
    return position


def _descendants(node: Element) -> Iterable[Element]:
    yield node
    for child in node.children:
        if isinstance(child, Element):
            yield from _descendants(child)


def _text_segments(node: Element) -> Iterable[str]:
    for child in node.children:
        if isinstance(child, str):
            if child.strip():
                yield html.unescape(child)
        else:
            yield from _text_segments(child)


def scan_text(source: str, path: str = "<memory>") -> list[dict[str, object]]:
    """Return source-backed candidate findings without confirming violations."""
    findings: list[dict[str, object]] = []
    suffix = Path(path).suffix.lower()
    style_source = suffix in CSS_STYLE_SUFFIXES or path == "<memory>"

    if style_source:
        for pattern_id, expression in REGEX_RULES.items():
            for match in expression.finditer(source):
                findings.append(
                    _candidate(
                        pattern_id,
                        path,
                        source,
                        match.start(),
                        "A source signature was found; consult the pattern guide and confirm context before reporting.",
                    )
                )

        findings.extend(_css_block_candidates(source, path))
        for match in LETTER_SPACING.finditer(source):
            if float(match.group(1)) > 0.05:
                findings.append(
                    _candidate(
                        "wide-tracking",
                        path,
                        source,
                        match.start(),
                        "Positive letter spacing exceeds the local candidate heuristic; inspect the text role and rendered result.",
                    )
                )

    if suffix in HTML_SUFFIXES:
        findings.extend(_html_candidates(source, path))

    if suffix in TEXT_SUFFIXES:
        dash_matches = list(EM_DASH.finditer(source))
        if len(dash_matches) >= 8 and len(dash_matches) * 500 >= max(1, len(source)):
            findings.append(
                _candidate(
                    "em-dash-overuse",
                    path,
                    source,
                    dash_matches[0].start(),
                    "The local saturation heuristic is met; punctuation frequency is not evidence of AI authorship or a confirmed copy problem.",
                )
            )

    return findings


def candidate_detector_ids(registry: dict[str, object]) -> set[str]:
    return {
        pattern["id"]
        for pattern in registry["patterns"]
        if pattern["detectorApplicability"] == "structural-candidate-detector"
    }


def iter_source_files(targets: list[Path]) -> Iterable[Path]:
    seen: set[Path] = set()
    for target in targets:
        if target.is_file():
            candidates = [target]
        elif target.is_dir():
            candidates = (
                path
                for path in target.rglob("*")
                if path.is_file() and not any(part in IGNORED_DIRS for part in path.parts)
            )
        else:
            continue
        for path in candidates:
            resolved = path.resolve()
            if resolved in seen or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            seen.add(resolved)
            yield path


def scan_paths(
    targets: list[Path],
    selected_patterns: set[str] | None = None,
) -> tuple[list[dict[str, object]], list[str]]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    known_ids = {pattern["id"] for pattern in registry["patterns"]}
    implemented = candidate_detector_ids(registry)
    if selected_patterns is not None:
        unknown = selected_patterns - known_ids
        if unknown:
            raise ValueError(f"Unknown pattern IDs: {', '.join(sorted(unknown))}")
        selected_patterns &= implemented

    findings = []
    scanned = []
    for path in iter_source_files(targets):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        display_path = path.as_posix()
        scanned.append(display_path)
        for finding in scan_text(content, display_path):
            if finding["patternId"] in implemented and (
                selected_patterns is None or finding["patternId"] in selected_patterns
            ):
                findings.append(finding)
    return findings, scanned


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="+", type=Path)
    parser.add_argument("--pattern", action="append", dest="patterns", help="Registry pattern ID; repeat to select several")
    parser.add_argument("--json", action="store_true", help="Emit the machine-readable candidate contract")
    args = parser.parse_args()

    try:
        selected = set(args.patterns) if args.patterns else None
        findings, scanned = scan_paths(args.targets, selected)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    if args.json:
        print(
            json.dumps(
                {
                    "evidenceModality": "structural",
                    "findingStatus": "candidate-only",
                    "scannedFileCount": len(scanned),
                    "findings": findings,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        for finding in findings:
            print(
                f"{finding['patternId']} candidate {finding['path']}:{finding['line']}:{finding['column']} "
                f"{finding['snippet']}"
            )
        print(f"Scanned {len(scanned)} source files; found {len(findings)} structural candidates (none confirmed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())