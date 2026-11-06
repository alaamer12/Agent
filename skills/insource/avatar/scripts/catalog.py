#!/usr/bin/env python3
"""catalog.py - read/write interface for the avatar skill's approach catalog.

data.csv is the global, approach-unbiased registry of ways to create avatars;
log.csv is the append-only growth ledger; each verified approach may encapsulate
its own resource registry (e.g. approaches/modular-svg-rig/wagba-avatars.csv).
Query and extend through this script so the skill compounds instead of being
re-learned. It never deletes: rows change status (verified/degraded/dead).

Usage:
  catalog.py list [--family F] [--status S] [--cols a,b,c]
  catalog.py get ID [ID...]
  catalog.py search TEXT
  catalog.py stats
  catalog.py stale [--days 30]
  catalog.py stamp ID [ID...]
  catalog.py set ID --status S [--note N] [--family F ...]
  catalog.py add --id ID --family F --mechanism M --status S [...]
  catalog.py resources ID          (path + row summary of its resource CSV)
  catalog.py log ACTION SUBJECT NOTE
  catalog.py export [--format md|json] [--family F] [--status S]
  (no arguments)                  run the self-test

Exit codes: 0 ok, 1 findings/stale rows, 2 usage or data error. ASCII output.
On Windows use `python`, not `python3`.
"""
import csv
import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data.csv")
LOG = os.path.join(ROOT, "log.csv")
COLUMNS = ["id", "family", "mechanism", "inputs", "outputs", "parts_model",
           "tooling", "status", "last_proven", "first_seen", "resources",
           "artifacts", "notes"]
STATUSES = ("verified", "unverified", "degraded", "dead")
ACTIONS = ("ADD", "CONFIRM", "UPDATE", "DOWNGRADE", "NOTE", "REFACTOR")
DEFAULT_COLS = ["id", "family", "status", "last_proven", "resources"]


def today():
    return datetime.date.today().isoformat()


def load():
    with open(DATA, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    # a misquoted field silently shifts every later column - fail loudly instead
    for r in rows:
        if None in r or any(v is None for v in r.values()):
            raise SystemExit("error: data.csv row %r has the wrong field count - quote fields "
                             "containing commas" % (r.get("id") or list(r.values())[:1]))
    return rows


def save(rows):
    tmp = DATA + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLUMNS)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, DATA)


def append_log(action, subject, note):
    tmp = LOG + ".tmp"
    exists = os.path.exists(LOG)
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["timestamp", "action", "subject", "note"])
        if exists:
            with open(LOG, newline="", encoding="utf-8") as src:
                rd = csv.reader(src)
                next(rd, None)
                for row in rd:
                    w.writerow(row)
        w.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    action, subject, note.replace('"', "'")])
    os.replace(tmp, LOG)


def find(rows, id_):
    hits = [r for r in rows if r["id"] == id_]
    if not hits:
        print("error: no row %r (catalog.py list shows what exists)" % id_)
        raise SystemExit(2)
    return hits[0]


def fmt(row, cols):
    return " | ".join("%s=%s" % (c, (row.get(c, "") or "-")[:60]) for c in cols)


def filtered(rows, args):
    out = rows
    for field in ("family", "status"):
        v = getattr(args, field, None)
        if v:
            out = [r for r in out if r[field].lower() == v.lower()]
    return out


def cmd_list(args):
    rows = filtered(load(), args)
    cols = args.cols.split(",") if args.cols else DEFAULT_COLS
    for r in rows:
        print(fmt(r, cols))
    print("-- %d row(s)" % len(rows))
    return 0


def cmd_get(args):
    rows = load()
    print(json.dumps([find(rows, i) for i in args.ids], indent=1))
    return 0


def cmd_search(args):
    needle = args.text.lower()
    hits = [r for r in load() if any(needle in (v or "").lower() for v in r.values())]
    for r in hits:
        print(fmt(r, DEFAULT_COLS))
    print("-- %d match(es)" % len(hits))
    return 1 if not hits else 0


def cmd_stats(args):
    rows = load()
    fam, st = {}, {}
    ages = []
    for r in rows:
        fam[r["family"]] = fam.get(r["family"], 0) + 1
        st[r["status"]] = st.get(r["status"], 0) + 1
        if r["last_proven"] not in ("-", ""):
            d = datetime.date.fromisoformat(r["last_proven"])
            ages.append((datetime.date.today() - d).days)
    print("rows: %d | families: %s | status: %s" % (len(rows), fam, st))
    if ages:
        ages.sort()
        print("last_proven age (days): median %d, max %d" % (ages[len(ages) // 2], ages[-1]))
    return 0


def cmd_stale(args):
    rows = [r for r in load()
            if r["last_proven"] in ("-", "") or
            (datetime.date.today() - datetime.date.fromisoformat(r["last_proven"])).days > args.days]
    for r in rows:
        print(fmt(r, ["id", "status", "last_proven"]))
    print("-- %d row(s) older than %d days or never proven" % (len(rows), args.days))
    return 1 if rows else 0


def cmd_stamp(args):
    rows = load()
    for id_ in args.ids:
        r = find(rows, id_)
        r["last_proven"] = today()
        append_log("CONFIRM", id_, "last_proven stamped by catalog.py stamp")
    save(rows)
    print("stamped: %s" % ", ".join(args.ids))
    return 0


def cmd_set(args):
    rows = load()
    r = find(rows, args.id)
    changes = []
    for field in COLUMNS:
        v = getattr(args, field.replace("-", "_"), None) if False else None
    for kv in args.fields:
        if "=" not in kv:
            raise SystemExit("error: set fields are key=value, got %r" % kv)
        k, v = kv.split("=", 1)
        if k not in COLUMNS:
            raise SystemExit("error: unknown column %r" % k)
        if k == "status" and v not in STATUSES:
            raise SystemExit("error: status must be one of %s" % (STATUSES,))
        changes.append("%s: %s -> %s" % (k, r[k][:30], v[:30]))
        r[k] = v
    if args.note:
        r["notes"] = (r["notes"] + " | " if r["notes"] not in ("", "-") else "") + args.note
        changes.append("note appended")
    if any(c.startswith("status") for c in changes):
        append_log("DOWNGRADE" if "status" in " ".join(changes) else "UPDATE", args.id,
                   "; ".join(changes))
    else:
        append_log("UPDATE", args.id, "; ".join(changes))
    save(rows)
    print("; ".join(changes) or "nothing changed")
    return 0


def cmd_add(args):
    rows = load()
    if any(r["id"] == args.id for r in rows):
        raise SystemExit("error: id %r already exists - use set/stamp, never duplicate" % args.id)
    if args.status not in STATUSES:
        raise SystemExit("error: status must be one of %s" % (STATUSES,))
    row = {c: getattr(args, c, None) or "-" for c in COLUMNS}
    row["id"], row["status"] = args.id, args.status
    row["first_seen"] = today()
    if row["status"] == "verified" and row["last_proven"] == "-":
        row["last_proven"] = today()
    rows.append(row)
    save(rows)
    append_log("ADD", args.id, (args.notes if args.notes else row["mechanism"])[:120])
    print("added %s (%s)" % (args.id, args.status))
    return 0


def cmd_resources(args):
    r = find(load(), args.id)
    path = os.path.join(ROOT, r["resources"])
    print("resource registry for %s: %s" % (args.id, r["resources"]))
    if r["resources"] in ("-", "") or not os.path.exists(path):
        print("  (none registered yet - this approach has no built resources)")
        return 0
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    kinds = {}
    for x in rows:
        kinds[x.get("kind", "?")] = kinds.get(x.get("kind", "?"), 0) + 1
    print("  %d row(s): %s" % (len(rows), ", ".join("%s=%d" % kv for kv in sorted(kinds.items()))))
    for x in rows:
        if x.get("status") not in ("verified",):
            print("  non-verified: %s [%s]" % (x.get("id"), x.get("status")))
    return 0


def cmd_log(args):
    if args.action not in ACTIONS:
        raise SystemExit("error: action must be one of %s" % (ACTIONS,))
    append_log(args.action, args.subject, args.note)
    print("logged")
    return 0


def cmd_export(args):
    rows = filtered(load(), args)
    if args.format == "json":
        print(json.dumps(rows, indent=1))
        return 0
    print("| id | family | status | last_proven | mechanism |")
    print("|---|---|---|---|---|")
    for r in rows:
        print("| %s | %s | %s | %s | %s |" % (r["id"], r["family"], r["status"],
                                              r["last_proven"], r["mechanism"][:90]))
    return 0


def selftest():
    import subprocess
    import tempfile
    shutil_dir = os.path.dirname(os.path.abspath(__file__))
    bad = 0
    checks = [
        (["list"], 0), (["stats"], 0), (["get", "modular-svg-rig"], 0),
        (["search", "envelope"], 0), (["resources", "modular-svg-rig"], 0),
        (["get", "no-such-row"], 2), (["search", "zzz-nothing"], 1),
    ]
    for argv, expect in checks:
        p = subprocess.run([sys.executable, os.path.join(shutil_dir, "catalog.py")] + argv,
                           capture_output=True, text=True)
        ok = p.returncode == expect
        print("%-38s %s" % ("cmd " + " ".join(argv), "PASS" if ok else
                             "FAIL (exit %d, want %d)" % (p.returncode, expect)))
        bad += 0 if ok else 1
    # round-trip add/stamp/set on a temp copy of the whole skill root
    import shutil
    tmp = tempfile.mkdtemp(prefix="avatar-catalog-")
    try:
        for f in ("data.csv", "log.csv"):
            shutil.copy(os.path.join(ROOT, f), tmp)
        os.makedirs(os.path.join(tmp, "scripts"))
        shutil.copy(os.path.abspath(__file__), os.path.join(tmp, "scripts"))
        script = os.path.join(tmp, "scripts", "catalog.py")
        p = subprocess.run([sys.executable, script, "add", "--id", "t-row", "--family",
                            "test", "--mechanism", "m", "--status", "unverified"],
                           capture_output=True, text=True)
        ok = p.returncode == 0
        p2 = subprocess.run([sys.executable, script, "stamp", "t-row"],
                            capture_output=True, text=True)
        p3 = subprocess.run([sys.executable, script, "set", "t-row", "status=dead",
                             "--note", "selftest"], capture_output=True, text=True)
        with open(os.path.join(tmp, "data.csv"), encoding="utf-8") as fh:
            row = [r for r in csv.DictReader(fh) if r["id"] == "t-row"][0]
        with open(os.path.join(tmp, "log.csv"), encoding="utf-8") as fh:
            logs = list(csv.DictReader(fh))
        ok2 = ok and p2.returncode == 0 and p3.returncode == 0 \
            and row["status"] == "dead" and row["last_proven"] == today() \
            and logs[-1]["action"] == "DOWNGRADE" and logs[1]["action"] == "CONFIRM"
        print("%-38s %s" % ("add/stamp/set round-trip + ledger", "PASS" if ok2 else "FAIL"))
        bad += 0 if ok2 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("self-test: %d problems" % bad)
    return 0 if bad == 0 else 1


def main(argv):
    import argparse
    if not argv:
        return selftest()
    ap = argparse.ArgumentParser(prog="catalog.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def filters(sp, cols=True):
        sp.add_argument("--family"); sp.add_argument("--status")
        if cols:
            sp.add_argument("--cols")
        return sp

    filters(sub.add_parser("list")).set_defaults(func=cmd_list)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    sp = sub.add_parser("get"); sp.add_argument("ids", nargs="+"); sp.set_defaults(func=cmd_get)
    sp = sub.add_parser("search"); sp.add_argument("text"); sp.set_defaults(func=cmd_search)
    sp = sub.add_parser("stale"); sp.add_argument("--days", type=int, default=30)
    sp.set_defaults(func=cmd_stale)
    sp = sub.add_parser("stamp"); sp.add_argument("ids", nargs="+"); sp.set_defaults(func=cmd_stamp)
    sp = sub.add_parser("set"); sp.add_argument("id"); sp.add_argument("fields", nargs="*")
    sp.add_argument("--note"); sp.set_defaults(func=cmd_set)
    sp = sub.add_parser("add")
    for c in COLUMNS:
        if c not in ("id", "status", "last_proven", "first_seen"):
            sp.add_argument("--" + c.replace("_", "-"), dest=c)
    sp.add_argument("--status", required=True); sp.add_argument("--id", required=True)
    sp.set_defaults(func=cmd_add)
    sp = sub.add_parser("resources"); sp.add_argument("id"); sp.set_defaults(func=cmd_resources)
    sp = sub.add_parser("log"); sp.add_argument("action"); sp.add_argument("subject")
    sp.add_argument("note"); sp.set_defaults(func=cmd_log)
    filters(sub.add_parser("export")).add_argument("--format", default="md",
                                                   choices=("md", "json"))
    sub.choices["export"].set_defaults(func=cmd_export)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
