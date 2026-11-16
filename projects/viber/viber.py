#!/usr/bin/env python3
"""Viber census CLI — the agent's read/write interface to .viber/.data/viber.json + telemetry.db.

Usage: python viber.py <command> [args] [--flags]
Resolution: CWD-relative .viber/.data/ unless --census overrides.
Stdlib only. Exit codes: 0 ok, 1 not found/invalid, 2 usage.
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
        print(f"error: census not found: {path}", file=sys.stderr)
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


def output(data, args):
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif isinstance(data, str):
        print(data)
    elif isinstance(data, list):
        for item in data:
            print(item if isinstance(item, str) else json.dumps(item, ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


# --- Read commands ---

def cmd_skill(census, args):
    name = args.name
    if name not in census["skills"]:
        print(f"error: skill '{name}' not in census", file=sys.stderr)
        return 1
    entry = census["skills"][name]
    if args.path:
        print(entry.get("path") or "null")
        return 0
    if args.content:
        c = entry["content"]
        paths = [c["entry"]] + c["references"] + c["assets"] + c["examples"]
        output(paths, args)
        return 0
    if args.brief:
        print(f"{name} v{entry.get('version') or '?'} — {(entry.get('description') or '')[:80]}")
        return 0
    output(entry, args)
    return 0


def cmd_step(census, args):
    if args.name:
        for step in census["lifecycle"]:
            if step["step"].lower() == args.name.lower():
                output(step, args)
                return 0
        print(f"error: step '{args.name}' not found", file=sys.stderr)
        return 1
    step = current_step(census)
    if not step:
        print("error: no current step determinable", file=sys.stderr)
        return 1
    output(step, args)
    return 0


def cmd_next(census, args):
    step = current_step(census)
    if not step:
        print("error: no current step", file=sys.stderr)
        return 1
    skills = census["skills"]
    blocked = []
    for name in step.get("skills", []):
        entry = skills.get(name)
        if not entry:
            continue
        blockers = entry.get("fit", {}).get("blockers", [])
        if blockers:
            blocked.append({"skill": name, "blockers": blockers})
            continue
        result = {"skill": name, "when": entry["fit"].get("when", ""), "consumes": entry["fit"].get("consumes", []), "produces": entry["fit"].get("produces", [])}
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
                result["suggestion"] = f"historically followed by {top} ({successors[top]}x)"
        output(result, args)
        return 0
    output({"status": "all blocked", "step": step["step"], "blocked": blocked}, args)
    return 0


def cmd_deck(census, args):
    decks = census.get("decks", {})
    if args.name:
        if args.name not in decks:
            print(f"error: deck '{args.name}' not found", file=sys.stderr)
            return 1
        output(decks[args.name], args)
        return 0
    if args.brief:
        for k, v in decks.items():
            print(f"{k} ({v['nature']}): {len(v.get('skills', []))} skills")
        return 0
    output(decks, args)
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
    output(result, args)
    return 0


def cmd_list(census, args):
    names = sorted(census["skills"].keys())
    if args.brief:
        for n in names:
            e = census["skills"][n]
            print(f"{n} v{e.get('version') or '?'}")
    else:
        output(names, args)
    return 0


def cmd_stats(census, args):
    db_path = resolve_db(resolve_census(args))
    if not db_path.is_file():
        output({"note": "no telemetry data yet"}, args)
        return 0
    conn = get_db(db_path)
    if args.name:
        rows = conn.execute("SELECT COUNT(*), MAX(ts), SUM(CASE WHEN outcome='ok' THEN 1 ELSE 0 END), SUM(CASE WHEN outcome='fail' THEN 1 ELSE 0 END) FROM invocations WHERE skill=?", (args.name,)).fetchone()
        conn.close()
        total, last, ok, fail = rows
        result = {"skill": args.name, "count": total or 0, "lastUsed": last, "ok": ok or 0, "fail": fail or 0}
    else:
        rows = conn.execute("SELECT skill, COUNT(*) as c, MAX(ts) FROM invocations GROUP BY skill ORDER BY c DESC").fetchall()
        conn.close()
        result = [{"skill": r[0], "count": r[1], "lastUsed": r[2]} for r in rows]
    output(result, args)
    return 0


def cmd_patterns(census, args):
    db_path = resolve_db(resolve_census(args))
    if not db_path.is_file():
        output({"note": "no telemetry data yet"}, args)
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
    output([{"sequence": k, "count": v} for k, v in top], args)
    return 0


# --- Write commands ---

def cmd_set(census, args, census_path):
    target = args.skill
    field = args.field
    value = args.value
    if target == ".":
        if field != "phase":
            print("error: project-level set only supports 'phase'", file=sys.stderr)
            return 1
        if value not in VALID_PHASES:
            print(f"error: phase must be one of {VALID_PHASES}", file=sys.stderr)
            return 1
        old = census.get("projectPhase")
        census["projectPhase"] = value
        census.setdefault("history", []).append({"date": today(), "event": f"phase transition {old}->{value}"})
        save_census(census_path, census)
        print(f"projectPhase: {old} -> {value}")
        return 0
    if target not in census["skills"]:
        print(f"error: skill '{target}' not in census", file=sys.stderr)
        return 1
    if field not in ALLOWED_SET_FIELDS:
        print(f"error: allowed fields: {ALLOWED_SET_FIELDS}", file=sys.stderr)
        return 1
    entry = census["skills"][target]
    if field == "blockers":
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            print("error: blockers must be a JSON array", file=sys.stderr)
            return 1
        entry["fit"]["blockers"] = parsed
    elif field == "phase":
        if value not in VALID_PHASES and value != "null":
            print(f"error: phase must be one of {VALID_PHASES} or null", file=sys.stderr)
            return 1
        entry["fit"]["phase"] = None if value == "null" else value
    save_census(census_path, census)
    print(f"{target}.{field} updated")
    return 0


def cmd_log(census, args, census_path):
    target = args.skill
    event = args.event
    record = {"date": today(), "event": event}
    if target == ".":
        census.setdefault("history", []).append(record)
    else:
        if target not in census["skills"]:
            print(f"error: skill '{target}' not in census", file=sys.stderr)
            return 1
        census["skills"][target].setdefault("history", []).append(record)
    save_census(census_path, census)
    print(f"logged: {event}")
    return 0


def cmd_add_skill(census, args, census_path):
    name = args.name
    if name in census["skills"]:
        print(f"error: skill '{name}' already exists", file=sys.stderr)
        return 1
    if not args.deck or not args.path:
        print("error: --deck and --path required", file=sys.stderr)
        return 1
    skill_dir = Path(args.path)
    if not (skill_dir / "SKILL.md").is_file():
        print(f"error: no SKILL.md at {args.path}", file=sys.stderr)
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
    print(f"added: {name}")
    return 0


def cmd_remove_skill(census, args, census_path):
    name = args.name
    if name not in census["skills"]:
        print(f"error: skill '{name}' not in census", file=sys.stderr)
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
    print(f"removed: {name}")
    return 0


def cmd_refresh(census, args, census_path):
    name = args.name
    if name not in census["skills"]:
        print(f"error: skill '{name}' not in census", file=sys.stderr)
        return 1
    entry = census["skills"][name]
    path_str = entry.get("path")
    if not path_str:
        print(f"error: skill '{name}' has no path", file=sys.stderr)
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
        print(f"error: SKILL.md not found at {skill_dir}", file=sys.stderr)
        return 1
    fm = parse_frontmatter(skill_md)
    entry["version"] = fm.get("version")
    entry["description"] = fm.get("description", "")
    entry["content"] = list_content(skill_dir)
    entry.setdefault("history", []).append({"date": today(), "event": "refreshed from disk"})
    save_census(census_path, census)
    print(f"refreshed: {name} v{entry['version']}")
    return 0


def cmd_use(census, args):
    name = args.skill
    if name not in census["skills"]:
        print(f"error: skill '{name}' not in census", file=sys.stderr)
        return 1
    db_path = resolve_db(resolve_census(args))
    conn = get_db(db_path)
    step = current_step(census)
    conn.execute("INSERT INTO invocations (skill, ts, step, phase) VALUES (?, ?, ?, ?)",
                 (name, now_iso(), step["step"] if step else None, census.get("projectPhase")))
    conn.commit()
    conn.close()
    print(f"recorded: use {name}")
    return 0


def cmd_outcome(census, args):
    name = args.skill
    result = args.result
    if result not in ("ok", "fail", "skip"):
        print("error: result must be ok|fail|skip", file=sys.stderr)
        return 1
    db_path = resolve_db(resolve_census(args))
    if not db_path.is_file():
        print("error: no telemetry db", file=sys.stderr)
        return 1
    conn = get_db(db_path)
    row = conn.execute("SELECT id FROM invocations WHERE skill=? AND outcome IS NULL ORDER BY id DESC LIMIT 1", (name,)).fetchone()
    if not row:
        conn.close()
        print(f"error: no open invocation for '{name}'", file=sys.stderr)
        return 1
    conn.execute("UPDATE invocations SET outcome=?, note=? WHERE id=?", (result, args.note, row[0]))
    conn.commit()
    conn.close()
    print(f"closed: {name} -> {result}")
    return 0


# --- Main ---

def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--census", help="override census path")
    common.add_argument("--json", action="store_true", help="raw JSON output")
    common.add_argument("--brief", action="store_true", help="one-line output")

    parser = argparse.ArgumentParser(prog="viber.py", description="Viber census CLI", parents=[common])
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("skill", parents=[common]); p.add_argument("name"); p.add_argument("--content", action="store_true", help="print content file paths only"); p.add_argument("--path", action="store_true", help="print disk path only")
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