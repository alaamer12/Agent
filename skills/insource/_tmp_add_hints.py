"""Throwaway: declare argument-hint + patch-bump for the 14 flagged skills. Delete after."""
import re, sys
from pathlib import Path
import yaml

HINTS = {
 "compare": "<two or more things> [dimensions to compare on]",
 "Groups/Agent/mistakes": "[<id|keyword|path> | add <description>]",
 "Groups/Agent/Session/context": "[light|utter] [what to reconstruct]",
 "Groups/Agent/subagent": "[forked] <what to delegate>",
 "Groups/Audit/exmaine": "[full | <area>]",
 "Groups/Audit/treat": "[<tool or library>] [in <path>]",
 "Groups/Crawl/Scraping/scrape": "<framework> [--auto|--url <site>] [flags]",
 "Groups/Design/denoise": "[lite|medium|ultra] <target>",
 "Groups/Files/pdf": "[read|write] <file or task> [options]",
 "Groups/Prospecting/mine": "[read|run|case] <topic or source> [budget]",
 "Groups/Prospecting/smelt": "<source folder> into <destination>",
 "Groups/Talk/inquire": "[verbose|concise] [what needs deciding]",
 "techstack": "[normal|ultra] <what to choose or evaluate>",
}

for rel, hint in HINTS.items():
    f = Path(rel) / "SKILL.md"
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, rel
    fm = m.group(1)
    assert "argument-hint" not in fm, rel
    ver = re.search(r"^version:\s*(\d+)\.(\d+)\.(\d+)\s*$", fm, re.M)
    assert ver, rel
    fm_new = fm[:ver.start()] + f"version: {ver.group(1)}.{ver.group(2)}.{int(ver.group(3))+1}" + fm[ver.end():]
    fm_new += f'\nargument-hint: "{hint}"'
    data = yaml.safe_load(fm_new + "\n")
    assert data["argument-hint"] == hint and re.match(r"^\d+\.\d+\.\d+$", data["version"]), rel
    f.write_text("---\n" + fm_new + "\n---\n" + text[m.end():], encoding="utf-8")
    print(f"{rel:40s} {data['version']}  {hint}")
