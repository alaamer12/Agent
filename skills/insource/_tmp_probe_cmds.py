"""Throwaway: inventory command/mode signals vs argument-hint presence across registry SKILL.md."""
import re, sys
from pathlib import Path
sys.path.insert(0, ".")
import manager
from manager import walk_skills, read_frontmatter

HEAD = re.compile(r"^#{1,6}\s+.*\b(commands?|modes?|subcommands?)\b.*$", re.I | re.M)
SLASH = re.compile(r"`/[a-z0-9][a-z0-9-]*(?:\s+[^\s`][^`]*){0,3}`")
WORD = re.compile(r"\b(commands?|modes?|subcommands?)\b", re.I)

rows = []
for d in walk_skills(Path("."), prune=False):
    p = d / "SKILL.md"
    text = p.read_text(encoding="utf-8", errors="replace")
    body = text.split("---", 2)[2] if text.count("---") >= 2 else text
    fm, _ = read_frontmatter(p)
    hint = (fm or {}).get("argument-hint")
    heads = [m.group(0).strip() for m in re.finditer(HEAD, body)]
    slashes = SLASH.findall(body)[:6]
    words = len(WORD.findall(body))
    if heads or slashes or words:
        rows.append((d.relative_to(".").as_posix(), bool(hint), heads, slashes, words))

for name, hint, heads, slashes, words in sorted(rows):
    print(f"{name:60s} hint={'Y' if hint else 'N'} heads={heads} slashes={slashes[:3]} words={words}")
