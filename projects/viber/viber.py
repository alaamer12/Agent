#!/usr/bin/env python3
"""Viber census CLI — the agent's read/write interface to .viber/.data/viber.json + telemetry.db.

Usage: python viber.py <command> [args] [--flags]
Resolution: CWD-relative .viber/.data/ unless --census overrides.
Exit codes: 0 ok, 1 not found/invalid, 2 usage.
Display: rich when installed, plain fallback otherwise. --no-rich forces plain.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DATA_DIR = Path(".viber/.data")
CENSUS_NAME = "viber.json"
DB_NAME = "telemetry.db"
ALLOWED_SET_FIELDS = {"blockers", "phase"}
VALID_PHASES = {"DR", "IP", "PP"}

# --- Display layer ---

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.text import Text
    from rich import box
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False

_use_rich = False
_console = None


def init_display(no_rich=False):
    global _use_rich, _console
    _use_rich = _RICH_AVAILABLE and not no_rich
    if _use_rich:
        _console = Console(stderr=False)


def display_table(title, columns, rows):
    if _use_rich:
        t = Table(title=title, box=box.ROUNDED, show_lines=False, title_style="bold cyan")
        for col in columns:
            t.add_column(col, style="white", no_wrap=False)
        for row in rows:
            t.add_row(*[str(c) for c in row])
        _console.print(t)
    else:
        widths = [len(c) for c in columns]
        str_rows = [[str(c) for c in row] for row in rows]
        for row in str_rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))
        header = "  ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
        sep = "  ".join("-" * w for w in widths)
        print(f"\n  {title}")
        print(f"  {header}")
        print(f"  {sep}")
        for row in str_rows:
            print("  " + "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
        print()


def display_panel(title, body, subtitle=None):
    if _use_rich:
        _console.print(Panel(body, title=title, subtitle=subtitle, border_style="cyan", box=box.ROUNDED))
    else:
        width = max(len(title), max((len(line) for line in body.split("\n")), default=0)) + 4
        print(f"\n  +{'-' * width}+")
        print(f"  | {title.center(width - 2)} |")
        print(f"  +{'-' * width}+")
        for line in body.split("\n"):
            print(f"  | {line.ljust(width - 2)} |")
        print(f"  +{'-' * width}+")
        if subtitle:
            print(f"  {subtitle}")
        print()


def display_tree(label, items):
    if _use_rich:
        tree = Tree(f"[bold]{label}[/bold]")
        for item in items:
            tree.add(item)
        _console.print(tree)
    else:
        print(f"  {label}")
        for item in items:
            print(f"    {item}")


def display_success(msg):
    if _use_rich:
        _console.print(f"[green]ok[/green] {msg}")
    else:
        print(f"ok: {msg}")


def display_error(msg):
    if _use_rich:
        _console.print(f"[red]error[/red] {msg}", style="red")
    else:
        print(f"error: {msg}", file=sys.stderr)


def display_info(msg):
    if _use_rich:
        _console.print(f"[dim]{msg}[/dim]")
    else:
        print(msg)


def display_kv(title, pairs):
    if _use_rich:
        t = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        t.add_column("key", style="bold cyan", no_wrap=True)
        t.add_column("value", style="white")
        for k, v in pairs:
            t.add_row(k, str(v))
        _console.print(Panel(t, title=title, border_style="cyan", box=box.ROUNDED))
    else:
        display_panel(title, "\n".join(f"{k}: {v}" for k, v in pairs))


def display_json(data):
    if _use_rich:
        _console.print_json(json.dumps(data, ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


# --- Core helpers ---

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def resolve_census(args):
    if args.census:
        return Path(args.census)
    return Path.cwd() / DEFAULT_DATA_DIR / CENSUS_NAME


def resolve_db(census_path):
    return census_path.parent / DB_NAME


def load_census(path):
    if not path.is_file():
        display_error(f"census not found: {path}")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def save_census(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def get_db(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("""CREATE TABLE IF NOT EXISTS invocations (
        id INTEGER PRIMARY KEY,
        skill TEXT NOT NULL,
        ts TEXT NOT NULL,
        step TEXT,
        phase TEXT,
        outcome TEXT,
        note TEXT
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_skill_ts ON invocations(skill, ts)")
    conn.commit()
    return conn


def parse_frontmatter(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    result = {}
    current_key = None
    current_val = []
    for line in block.split("\n"):
        m = re.match(r"^([a-z_-]+):\s*(.*)", line)
        if m:
            if current_key:
                result[current_key] = " ".join(current_val).strip()
            current_key = m.group(1)
            val = m.group(2).strip()
            if val in (">-", ">", "|", "|-"):
                current_val = []
            else:
                current_val = [val.strip("'\"")]
        elif current_key and line.startswith("  "):
            current_val.append(line.strip().strip("'\""))
    if current_key:
        result[current_key] = " ".join(current_val).strip()
    return result


def list_content(skill_dir):
    refs, assets, examples = [], [], []
    for sub, target in [("references", refs), ("assets", assets), ("examples", examples)]:
        d = skill_dir / sub
        if d.is_dir():
            for f in sorted(d.rglob("*")):
                if f.is_file():
                    target.append(str(f.relative_to(skill_dir)).replace("\\", "/"))
    for sub_dir in sorted(skill_dir.iterdir()):
        if sub_dir.is_dir() and sub_dir.name not in ("references", "assets", "examples", ".git", "__pycache__", "scripts"):
            for sub, target in [("references", refs), ("assets", assets), ("examples", examples)]:
                d = sub_dir / sub
                if d.is_dir():
                    for f in sorted(d.rglob("*")):
                        if f.is_file():
                            target.append(str(f.relative_to(skill_dir)).replace("\\", "/"))
    return {"entry": "SKILL.md", "references": refs, "assets": assets, "examples": examples}


def current_step(census):
    phase = census.get("projectPhase", "DR")
    for step in census.get("lifecycle", []):
        if step.get("phase") == phase:
            return step
    for step in census.get("lifecycle", []):
        if step.get("phase") is None:
            return step
    return None


def skill_step(census, name):
    for step in census.get("lifecycle", []):
        if name in step.get("skills", []) or name in step.get("commands", []):
            return step["step"]
    return "-"


# --- Read commands ---

def cmd_skill(census, args):
    name = args.name
    if name not in census["skills"]:
        display_error(f"skill '{name}' not in census")
        return 1
    entry = census["skills"][name]
    if args.path:
        print(entry.get("path") or "null")
        return 0
    if args.content:
        c = entry["content"]
        display_tree(f"{name} content", [c["entry"]] + c["references"] + c["assets"] + c["examples"])
        return 0
    if args.brief:
        desc = (entry.get("description") or "")[:100]
        if _use_rich:
            _console.print(f"[bold cyan]{name}[/bold cyan] [dim]v{entry.get('version') or '?'}[/dim] — {desc}")
        else:
            print(f"{name} v{entry.get('version') or '?'} — {desc}")
        return 0
    if args.json:
        display_json(entry)
        return 0
    fit = entry.get("fit", {})
    pairs = [
        ("version", entry.get("version") or "?"),
        ("deck", entry.get("deck", "?")),
        ("owned", "yes" if entry.get("owned") else "no"),
        ("path", entry.get("path") or "null"),
        ("step", skill_step(census, name)),
        ("role", fit.get("role", "")),
        ("when", fit.get("when", "")),
        ("produces", ", ".join(fit.get("produces", [])) or "-"),
        ("consumes", ", ".join(fit.get("consumes", [])) or "-"),
        ("blockers", ", ".join(fit.get("blockers", [])) or "none"),
    ]
    display_kv(name, pairs)
    desc = entry.get("description") or ""
    if desc:
        display_panel("description", desc)
    c = entry.get("content", {})
    all_files = c.get("references", []) + c.get("assets", []) + c.get("examples", [])
    if all_files:
        display_tree("content", [c.get("entry", "SKILL.md")] + all_files)
    return 0


def cmd_step(census, args):
    if args.name:
        for step in census["lifecycle"]:
            if step["step"].lower() == args.name.lower():
                target = step
                break
        else:
            display_error(f"step '{args.name}' not found")
            return 1
    else:
        target = current_step(census)
        if not target:
            display_error("no current step determinable")
            return 1
    if args.json:
        display_json(target)
        return 0
    skills = target.get("skills", [])
    commands = target.get("commands", [])
    rows = []
    for s in skills:
        entry = census["skills"].get(s, {})
        blocked = entry.get("fit", {}).get("blockers", [])
        status = "[red]blocked[/red]" if blocked and _use_rich else ("blocked" if blocked else "ready")
        rows.append((s, entry.get("version") or "?", status))
    for c in commands:
        rows.append((c, "-", "command"))
    display_table(f"{target['step']} [{target.get('phase') or 'any'}]", ["Skill", "Version", "Status"], rows)
    display_info(f"goal: {target.get('goal', '')}")
    return 0


def cmd_next(census, args):
    step = current_step(census)
    if not step:
        display_error("no current step")
        return 1
    skills = census["skills"]
    blocked = []
    for name in step.get("skills", []):
        entry = skills.get(name)
        if not entry:
            continue
        blockers = entry.get("fit", {}).get("blockers", [])
        if blockers:
            blocked.append((name, ", ".join(blockers)))
            continue
        fit = entry.get("fit", {})
        suggestion = ""
        db_path = resolve_db(resolve_census(args))
        if db_path.is_file():
            conn = get_db(db_path)
            rows = conn.execute("SELECT skill FROM invocations ORDER BY id DESC LIMIT 50").fetchall()
            conn.close()
            seq = [r[0] for r in reversed(rows)]
            successors = {}
            for i, s in enumerate(seq[:-1]):
                if s == name:
                    nxt = seq[i + 1]
                    successors[nxt] = successors.get(nxt, 0) + 1
            if successors:
                top = max(successors, key=successors.get)
                suggestion = f"historically followed by {top} ({successors[top]}x)"
        if args.json:
            display_json({"skill": name, "when": fit.get("when", ""), "consumes": fit.get("consumes", []), "produces": fit.get("produces", []), "suggestion": suggestion})
            return 0
        pairs = [
            ("when", fit.get("when", "")),
            ("consumes", ", ".join(fit.get("consumes", [])) or "-"),
            ("produces", ", ".join(fit.get("produces", [])) or "-"),
        ]
        if suggestion:
            pairs.append(("suggestion", suggestion))
        display_kv(f"next: {name}", pairs)
        return 0
    if args.json:
        display_json({"status": "all blocked", "step": step["step"], "blocked": [{"skill": n, "blockers": b} for n, b in blocked]})
        return 0
    display_table(f"all blocked — {step['step']}", ["Skill", "Blockers"], blocked)
    return 0


def cmd_deck(census, args):
    decks = census.get("decks", {})
    if args.name:
        if args.name not in decks:
            display_error(f"deck '{args.name}' not found")
            return 1
        d = decks[args.name]
        if args.json:
            display_json(d)
            return 0
        pairs = [("name", d.get("name", "")), ("nature", d.get("nature", "")), ("registry", d.get("registry", "")), ("skills", str(len(d.get("skills", []))))]
        if d.get("remote"):
            pairs.append(("remote", d["remote"]))
        display_kv(f"deck: {args.name}", pairs)
        display_tree("skills", d.get("skills", []))
        return 0
    rows = [(k, v.get("nature", "?"), str(len(v.get("skills", []))), v.get("registry", "")) for k, v in decks.items()]
    if args.json:
        display_json(decks)
        return 0
    display_table("decks", ["Deck", "Nature", "Skills", "Registry"], rows)
    return 0


def cmd_status(census, args):
    step = current_step(census)
    blocker_count = sum(1 for e in census["skills"].values() if e.get("fit", {}).get("blockers"))
    result = {
        "projectPhase": census.get("projectPhase"),
        "currentStep": step["step"] if step else None,
        "totalSkills": len(census["skills"]),
        "blockedSkills": blocker_count,
        "unclassified": len(census.get("unclassified", [])),
    }
    if args.json:
        display_json(result)
        return 0
    phase = result["projectPhase"] or "?"
    phase_style = {"DR": "yellow", "IP": "green", "PP": "blue"}.get(phase, "white")
    pairs = [
        ("phase", f"[{phase_style}]{phase}[/{phase_style}]" if _use_rich else phase),
        ("step", result["currentStep"] or "-"),
        ("skills", str(result["totalSkills"])),
        ("blocked", str(result["blockedSkills"])),
        ("unclassified", str(result["unclassified"])),
    ]
    display_kv("viber status", pairs)
    return 0


def cmd_list(census, args):
    names = sorted(census["skills"].keys())
    if args.json:
        display_json(names)
        return 0
    if args.brief:
        rows = [(n, census["skills"][n].get("version") or "?") for n in names]
        display_table("skills", ["Name", "Version"], rows)
        return 0
    rows = []
    for n in names:
        e = census["skills"][n]
        rows.append((n, e.get("version") or "?", e.get("deck", "?"), skill_step(census, n), "owned" if e.get("owned") else ""))
    display_table("skills", ["Name", "Version", "Deck", "Step", "Owned"], rows)
    return 0


def cmd_stats(census, args):
    db_path = resolve_db(resolve_census(args))
    if not db_path.is_file():
        display_info("no telemetry data yet")
        return 0
    conn = get_db(db_path)
    if args.name:
        row = conn.execute("SELECT COUNT(*), MAX(ts), SUM(CASE WHEN outcome='ok' THEN 1 ELSE 0 END), SUM(CASE WHEN outcome='fail' THEN 1 ELSE 0 END), SUM(CASE WHEN outcome='skip' THEN 1 ELSE 0 END) FROM invocations WHERE skill=?", (args.name,)).fetchone()
        conn.close()
        total, last, ok, fail, skip = row
        result = {"skill": args.name, "count": total or 0, "lastUsed": last, "ok": ok or 0, "fail": fail or 0, "skip": skip or 0}
        if args.json:
            display_json(result)
            return 0
        display_kv(f"stats: {args.name}", [(k, str(v)) for k, v in result.items()])
        return 0
    rows = conn.execute("SELECT skill, COUNT(*) as c, MAX(ts), SUM(CASE WHEN outcome='ok' THEN 1 ELSE 0 END), SUM(CASE WHEN outcome='fail' THEN 1 ELSE 0 END) FROM invocations GROUP BY skill ORDER BY c DESC").fetchall()
    conn.close()
    if args.json:
        display_json([{"skill": r[0], "count": r[1], "lastUsed": r[2], "ok": r[3] or 0, "fail": r[4] or 0} for r in rows])
        return 0
    display_table("telemetry", ["Skill", "Uses", "Last Used", "OK", "Fail"], [(r[0], r[1], r[2] or "-", r[3] or 0, r[4] or 0) for r in rows])
    return 0


def cmd_patterns(census, args):
    db_path = resolve_db(resolve_census(args))
    if not db_path.is_file():
        display_info("no telemetry data yet")
        return 0
    conn = get_db(db_path)
    rows = conn.execute("SELECT skill FROM invocations ORDER BY id").fetchall()
    conn.close()
    seq = [r[0] for r in rows]
    pairs = {}
    for i in range(len(seq) - 1):
        pair = f"{seq[i]} -> {seq[i+1]}"
        pairs[pair] = pairs.get(pair, 0) + 1
    top = sorted(pairs.items(), key=lambda x: -x[1])[:15]
    if args.json:
        display_json([{"sequence": k, "count": v} for k, v in top])
        return 0
    display_table("patterns", ["Sequence", "Count"], [(k, v) for k, v in top])
    return 0


# --- Write commands ---

def cmd_set(census, args, census_path):
    target = args.skill
    field = args.field
    value = args.value
    if target == ".":
        if field != "phase":
            display_error("project-level set only supports 'phase'")
            return 1
        if value not in VALID_PHASES:
            display_error(f"phase must be one of {sorted(VALID_PHASES)}")
            return 1
        old = census.get("projectPhase")
        census["projectPhase"] = value
        census.setdefault("history", []).append({"date": today(), "event": f"phase transition {old}->{value}"})
        save_census(census_path, census)
        display_success(f"projectPhase: {old} -> {value}")
        return 0
    if target not in census["skills"]:
        display_error(f"skill '{target}' not in census")
        return 1
    if field not in ALLOWED_SET_FIELDS:
        display_error(f"allowed fields: {sorted(ALLOWED_SET_FIELDS)}")
        return 1
    entry = census["skills"][target]
    if field == "blockers":
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            display_error("blockers must be a JSON array")
            return 1
        entry["fit"]["blockers"] = parsed
    elif field == "phase":
        if value not in VALID_PHASES and value != "null":
            display_error(f"phase must be one of {sorted(VALID_PHASES)} or null")
            return 1
        entry["fit"]["phase"] = None if value == "null" else value
    save_census(census_path, census)
    display_success(f"{target}.{field} updated")
    return 0


def cmd_log(census, args, census_path):
    target = args.skill
    event = args.event
    record = {"date": today(), "event": event}
    if target == ".":
        census.setdefault("history", []).append(record)
    else:
        if target not in census["skills"]:
            display_error(f"skill '{target}' not in census")
            return 1
        census["skills"][target].setdefault("history", []).append(record)
    save_census(census_path, census)
    display_success(f"logged: {event}")
    return 0


def cmd_add_skill(census, args, census_path):
    name = args.name
    if name in census["skills"]:
        display_error(f"skill '{name}' already exists")
        return 1
    if not args.deck or not args.path:
        display_error("--deck and --path required")
        return 1
    skill_dir = Path(args.path)
    if not (skill_dir / "SKILL.md").is_file():
        display_error(f"no SKILL.md at {args.path}")
        return 1
    fm = parse_frontmatter(skill_dir / "SKILL.md")
    content = list_content(skill_dir)
    census["skills"][name] = {
        "version": fm.get("version"),
        "description": fm.get("description", ""),
        "deck": args.deck,
        "path": args.path,
        "owned": False,
        "content": content,
        "fit": {"role": "", "when": "", "after": [], "before": [], "produces": [], "consumes": [], "blockers": []},
        "history": [{"date": today(), "event": "registered via add-skill"}]
    }
    deck = census.get("decks", {}).get(args.deck)
    if deck and name not in deck.get("skills", []):
        deck.setdefault("skills", []).append(name)
        deck["skills"].sort()
    save_census(census_path, census)
    display_success(f"added: {name} v{fm.get('version') or '?'}")
    return 0


def cmd_remove_skill(census, args, census_path):
    name = args.name
    if name not in census["skills"]:
        display_error(f"skill '{name}' not in census")
        return 1
    del census["skills"][name]
    for deck in census.get("decks", {}).values():
        if name in deck.get("skills", []):
            deck["skills"].remove(name)
    for step in census.get("lifecycle", []):
        if name in step.get("skills", []):
            step["skills"].remove(name)
        if name in step.get("commands", []):
            step["commands"].remove(name)
    save_census(census_path, census)
    display_success(f"removed: {name}")
    return 0


def cmd_refresh(census, args, census_path):
    name = args.name
    if name not in census["skills"]:
        display_error(f"skill '{name}' not in census")
        return 1
    entry = census["skills"][name]
    path_str = entry.get("path")
    if not path_str:
        display_error(f"skill '{name}' has no path")
        return 1
    skill_dir = Path(path_str)
    if not skill_dir.is_absolute():
        if entry.get("owned"):
            skill_dir = census_path.parent / path_str
        else:
            registry = census.get("decks", {}).get(entry.get("deck", "author"), {}).get("registry", "")
            skill_dir = Path(registry) / path_str if registry else census_path.parent / path_str
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        display_error(f"SKILL.md not found at {skill_dir}")
        return 1
    fm = parse_frontmatter(skill_md)
    entry["version"] = fm.get("version")
    entry["description"] = fm.get("description", "")
    entry["content"] = list_content(skill_dir)
    entry.setdefault("history", []).append({"date": today(), "event": "refreshed from disk"})
    save_census(census_path, census)
    display_success(f"refreshed: {name} v{entry['version']}")
    return 0


def cmd_use(census, args):
    name = args.skill
    if name not in census["skills"]:
        display_error(f"skill '{name}' not in census")
        return 1
    db_path = resolve_db(resolve_census(args))
    conn = get_db(db_path)
    step = current_step(census)
    conn.execute("INSERT INTO invocations (skill, ts, step, phase) VALUES (?, ?, ?, ?)",
                 (name, now_iso(), step["step"] if step else None, census.get("projectPhase")))
    conn.commit()
    conn.close()
    display_success(f"use {name}")
    return 0


def cmd_outcome(census, args):
    name = args.skill
    result = args.result
    if result not in ("ok", "fail", "skip"):
        display_error("result must be ok|fail|skip")
        return 1
    db_path = resolve_db(resolve_census(args))
    if not db_path.is_file():
        display_error("no telemetry db")
        return 1
    conn = get_db(db_path)
    row = conn.execute("SELECT id FROM invocations WHERE skill=? AND outcome IS NULL ORDER BY id DESC LIMIT 1", (name,)).fetchone()
    if not row:
        conn.close()
        display_error(f"no open invocation for '{name}'")
        return 1
    conn.execute("UPDATE invocations SET outcome=?, note=? WHERE id=?", (result, args.note, row[0]))
    conn.commit()
    conn.close()
    display_success(f"{name} -> {result}")
    return 0


# --- Main ---

def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--census", help="override census path")
    common.add_argument("--json", action="store_true", help="raw JSON output")
    common.add_argument("--brief", action="store_true", help="compact output")
    common.add_argument("--no-rich", action="store_true", help="force plain text even if rich is installed")

    parser = argparse.ArgumentParser(prog="viber.py", description="Viber census CLI", parents=[common])
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("skill", parents=[common]); p.add_argument("name"); p.add_argument("--content", action="store_true", help="content file paths only"); p.add_argument("--path", action="store_true", help="disk path only")
    p = sub.add_parser("step", parents=[common]); p.add_argument("name", nargs="?")
    sub.add_parser("next", parents=[common])
    p = sub.add_parser("deck", parents=[common]); p.add_argument("name", nargs="?")
    sub.add_parser("status", parents=[common])
    sub.add_parser("list", parents=[common])
    p = sub.add_parser("stats", parents=[common]); p.add_argument("name", nargs="?")
    sub.add_parser("patterns", parents=[common])
    p = sub.add_parser("set", parents=[common]); p.add_argument("skill"); p.add_argument("field"); p.add_argument("value")
    p = sub.add_parser("log", parents=[common]); p.add_argument("skill"); p.add_argument("event")
    p = sub.add_parser("add-skill", parents=[common]); p.add_argument("name"); p.add_argument("--deck"); p.add_argument("--path")
    p = sub.add_parser("remove-skill", parents=[common]); p.add_argument("name")
    p = sub.add_parser("refresh", parents=[common]); p.add_argument("name")
    p = sub.add_parser("use", parents=[common]); p.add_argument("skill")
    p = sub.add_parser("outcome", parents=[common]); p.add_argument("skill"); p.add_argument("result"); p.add_argument("note", nargs="?")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(2)

    init_display(no_rich=args.no_rich)
    census_path = resolve_census(args)
    census = load_census(census_path)

    read_cmds = {"skill": cmd_skill, "step": cmd_step, "next": cmd_next, "deck": cmd_deck, "status": cmd_status, "list": cmd_list, "stats": cmd_stats, "patterns": cmd_patterns}
    write_cmds = {"set": cmd_set, "log": cmd_log, "add-skill": cmd_add_skill, "remove-skill": cmd_remove_skill, "refresh": cmd_refresh}
    telemetry_cmds = {"use": cmd_use, "outcome": cmd_outcome}

    if args.command in read_cmds:
        sys.exit(read_cmds[args.command](census, args))
    elif args.command in write_cmds:
        sys.exit(write_cmds[args.command](census, args, census_path))
    elif args.command in telemetry_cmds:
        sys.exit(telemetry_cmds[args.command](census, args))
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()