#!/usr/bin/env python3
"""Query and maintain the fahlwy source catalog (data.csv + log.csv).

The catalog is CSV, not prose: one row per source with filterable columns
(id, category, provider, family, host, url_form, kind, status, last_proven,
first_seen, access, rights, coverage, notes), and one row per hunt in log.csv
(date, action, category, subject, detail).

Usage:
    catalog.py stats
    catalog.py list --category icon --status verified --older-than 30
    catalog.py urls --category image --kind image      # one URL form per line
    catalog.py urls --status verified | xargs python scripts/verify_sources.py any
    catalog.py get simple-icons
    catalog.py search "viewBox"
    catalog.py stale --days 30
    catalog.py stamp picsum dicebear                     # re-confirmed today
    catalog.py add --id x --category image --provider X --url-form https://... --notes "..."
    catalog.py set loremflickr --status degraded --note "upstream 500s"
    catalog.py log ADD image provider-x "why/how"
    catalog.py export --format md

Writes are atomic (temp file + os.replace). Every status-changing write appends a
ledger line, so log.csv cannot drift from data.csv.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data.csv")
LOG = os.path.join(ROOT, "log.csv")
COLS = ["id", "category", "provider", "family", "host", "url_form", "kind",
        "status", "last_proven", "first_seen", "access", "rights", "coverage", "notes"]
LOGCOLS = ["date", "action", "category", "subject", "detail"]
STATUSES = ("verified", "degraded", "site-only", "dead", "refuse")
KINDS = ("image", "video", "audio", "pdf", "any")
ACTIONS = ("ADD", "UPGRADE", "DOWNGRADE", "CONFIRM", "CORRECTION", "NOTE", "MIGRATE")
FILTER_COLS = ("category", "status", "kind", "family", "host", "access", "rights")


def read(path, fields):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return [{k: (r.get(k) or "") for k in fields} for r in csv.DictReader(fh)]


def write(path, fields, rows):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def ledger(action, category, subject, detail, date=None):
    if action not in ACTIONS:
        sys.exit(f"action must be one of {ACTIONS}")
    rows = read(LOG, LOGCOLS)
    rows.insert(0, {"date": date or dt.date.today().isoformat(), "action": action,
                    "category": category, "subject": subject, "detail": detail})
    write(LOG, LOGCOLS, rows)


def matches(row, args):
    for col in FILTER_COLS:
        want = getattr(args, col, None)
        if want and row[col].lower() not in {w.strip().lower() for w in want.split(",")}:
            return False
    if args.older_than:
        if age(row) < int(args.older_than):
            return False
    if args.newer_than:
        if age(row) > int(args.newer_than):
            return False
    return True


def age(row):
    return (dt.date.today() - dt.date.fromisoformat(row["last_proven"])).days


def emit(rows, cols):
    if not rows:
        print("(no rows)")
        return
    w = csv.writer(sys.stdout)
    w.writerow(cols)
    for r in rows:
        w.writerow([r[c] for c in cols])


def load_rows():
    rows = read(DATA, COLS)
    if not rows:
        sys.exit(f"empty catalog: {DATA}")
    return rows


def cmd_list(args):
    rows = [r for r in load_rows() if matches(r, args)]
    if args.limit:
        rows = rows[: int(args.limit)]
    emit(rows, args.cols.split(",") if args.cols else
         ["id", "category", "provider", "status", "last_proven", "coverage"])
    print(f"{len(rows)} row(s)", file=sys.stderr)
    return 0 if rows else 1


def cmd_urls(args):
    rows = [r for r in load_rows() if matches(r, args)]
    if not rows:
        print("(no rows)", file=sys.stderr)
        return 1
    sys.stdout.write("".join(f"{r['url_form']}\n" for r in rows))
    return 0


def cmd_get(args):
    by_id = {r["id"]: r for r in load_rows()}
    missing = [i for i in args.ids if i not in by_id]
    for i in args.ids:
        if i in by_id:
            print(json.dumps(by_id[i], indent=2, ensure_ascii=False))
    if missing:
        print("missing: " + ", ".join(missing), file=sys.stderr)
    return 1 if missing else 0


def cmd_search(args):
    needle = " ".join(args.text).lower()
    rows = [r for r in load_rows() if needle in " ".join(r[c] for c in COLS).lower()]
    emit(rows, ["id", "category", "provider", "status", "notes"])
    return 0 if rows else 1


def cmd_stats(args):
    rows = load_rows()
    print(f"sources   {len(rows)} rows, {len({r['family'] for r in rows})} provider families")
    for label, key in (("category", "category"), ("status", "status"), ("kind", "kind"),
                       ("access", "access"), ("rights", "rights")):
        tally = {}
        for r in rows:
            tally[r[key]] = tally.get(r[key], 0) + 1
        line = "  ".join(f"{v}={n}" for v, n in sorted(tally.items(), key=lambda kv: -kv[1]))
        print(f"\n{label}:\n  {line}")
    ages = sorted(age(r) for r in rows if r["status"] in ("verified", "degraded"))
    if ages:
        print(f"\nfreshness  median {ages[len(ages) // 2]} d, "
              f"{sum(1 for a in ages if a > 30)} row(s) unproven >30 d")
    return 0


def cmd_stale(args):
    rows = sorted((r for r in load_rows()
                   if r["status"] in ("verified", "degraded") and age(r) > args.days),
                  key=lambda r: r["last_proven"])
    emit(rows, ["id", "category", "provider", "status", "last_proven"])
    print(f"{len(rows)} row(s) unproven for >{args.days} days", file=sys.stderr)
    return 0


def update_rows(ids, fields, action, default_category):
    rows = load_rows()
    targets = set(ids)
    found = []
    for r in rows:
        if r["id"] in targets:
            r.update(fields)
            found.append(r)
    missing = targets - {r["id"] for r in found}
    if missing:
        sys.exit(f"no such id(s): {', '.join(sorted(missing))} (try: catalog.py search <term>)")
    write(DATA, COLS, rows)
    return found


def cmd_stamp(args):
    date = args.date or dt.date.today().isoformat()
    found = update_rows(args.ids, {"last_proven": date}, "CONFIRM", "")
    for r in found:
        ledger("CONFIRM", r["category"], r["id"],
               args.note or f"re-verified {r['kind']} bytes at {r['url_form']} on {date}")
    print(f"stamped {len(found)} row(s) -> {date}")
    return 0


def cmd_set(args):
    fields = {c: getattr(args, c) for c in COLS if getattr(args, c, None) is not None}
    if not fields:
        sys.exit("nothing to set (--status/--url-form/--notes/...)")
    if "status" in fields and fields["status"] not in STATUSES:
        sys.exit(f"status must be one of {STATUSES}")
    found = update_rows(args.ids, fields, "CORRECTION", "")
    detail = args.note or "field edit: " + json.dumps(fields, ensure_ascii=False)
    for r in found:
        ledger(args.action, r["category"], r["id"], detail)
    print(f"updated {len(found)} row(s): {', '.join(r['id'] for r in found)}")
    return 0


def cmd_add(args):
    rows = load_rows()
    if any(r["id"] == args.id for r in rows):
        sys.exit(f"id already exists: {args.id}")
    if args.status not in STATUSES:
        sys.exit(f"status must be one of {STATUSES}")
    if args.kind not in KINDS:
        sys.exit(f"kind must be one of {KINDS}")
    today = args.date or dt.date.today().isoformat()
    row = {"id": args.id, "category": args.category, "provider": args.provider,
           "family": args.family or args.id, "host": args.host or "",
           "url_form": args.url_form, "kind": args.kind, "status": args.status,
           "last_proven": today, "first_seen": args.first_seen or today,
           "access": args.access or "keyless", "rights": args.rights or "unknown",
           "coverage": args.coverage or "-", "notes": args.notes or ""}
    rows.append(row)
    write(DATA, COLS, rows)
    ledger(args.action, args.category, args.id,
           args.note or f"added {args.status} {args.kind} source: {args.url_form}")
    print(f"added {args.id}")
    return 0


def cmd_log(args):
    ledger(args.action.upper(), args.category, args.subject, " ".join(args.detail), args.date)
    print("logged")
    return 0


def cmd_export(args):
    rows = [r for r in load_rows() if matches(r, args)]
    if args.format == "json":
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    out = ["# fahlwy source catalog", ""]
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    for cat in sorted(by_cat):
        out.append(f"## {cat} ({len(by_cat[cat])})")
        for r in by_cat[cat]:
            mark = {"verified": "OK", "degraded": "WARN", "site-only": "SITE",
                    "dead": "DEAD", "refuse": "REFUSE"}[r["status"]]
            flags = " ".join(f"[{r[k]}]" for k in ("access", "rights") if r[k] not in ("", "unknown"))
            out.append(f"- {mark} **{r['provider']}** ({r['family']}) {flags} `{r['url_form']}` "
                       f"- {r['coverage']}; proven {r['last_proven']}")
            if r["notes"]:
                out.append(f"  - {r['notes']}")
        out.append("")
    print("\n".join(out))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="catalog.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)

    def filters(sp, cols=True):
        for c in FILTER_COLS:
            sp.add_argument(f"--{c.replace('_', '-')}", dest=c)
        sp.add_argument("--older-than", dest="older_than", help="last_proven at least N days ago")
        sp.add_argument("--newer-than", dest="newer_than", help="last_proven within N days")
        if cols:
            sp.add_argument("--cols", help="comma-separated columns to print")
        sp.set_defaults(**{c: None for c in FILTER_COLS}, older_than=None, newer_than=None)

    sub.add_parser("stats", help="row counts by column + freshness summary").set_defaults(func=cmd_stats)

    sp = sub.add_parser("list", help="filterable row listing")
    filters(sp); sp.add_argument("--limit", type=int); sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("urls", help="URL forms only (pipe to verify_sources.py)")
    filters(sp, cols=False); sp.set_defaults(func=cmd_urls)

    sp = sub.add_parser("get", help="full JSON for one or more ids")
    sp.add_argument("ids", nargs="+"); sp.set_defaults(func=cmd_get)

    sp = sub.add_parser("search", help="substring match across every column")
    sp.add_argument("text", nargs="+"); sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("stale", help="rows needing re-verification")
    sp.add_argument("--days", type=int, default=30); sp.set_defaults(func=cmd_stale)

    sp = sub.add_parser("stamp", help="set last_proven (byte-confirmed)")
    sp.add_argument("ids", nargs="+"); sp.add_argument("--date"); sp.add_argument("--note")
    sp.set_defaults(func=cmd_stamp)

    sp = sub.add_parser("set", help="edit fields of existing rows")
    sp.add_argument("ids", nargs="+")
    for c in COLS:
        if c != "id":
            sp.add_argument(f"--{c.replace('_', '-')}", dest=c)
    sp.add_argument("--note"); sp.add_argument("--action", default="CORRECTION",
                                                choices=ACTIONS)
    sp.set_defaults(**{c: None for c in COLS}, func=cmd_set)

    sp = sub.add_parser("add", help="append a new row")
    sp.add_argument("--id", required=True); sp.add_argument("--category", required=True)
    sp.add_argument("--provider", required=True); sp.add_argument("--url-form", dest="url_form",
                                                                 required=True)
    for c in ("kind", "status", "family", "host", "first_seen", "date", "access", "rights",
              "coverage", "notes", "note"):
        sp.add_argument(f"--{c.replace('_', '-')}", dest=c)
    sp.add_argument("--action", default="ADD", choices=ACTIONS)
    sp.set_defaults(kind="any", status="verified", func=cmd_add)

    sp = sub.add_parser("log", help="append a growth-ledger line")
    sp.add_argument("action", choices=ACTIONS); sp.add_argument("category")
    sp.add_argument("subject"); sp.add_argument("detail", nargs="+")
    sp.add_argument("--date"); sp.set_defaults(func=cmd_log)

    sp = sub.add_parser("export", help="render the catalog as markdown or json")
    filters(sp, cols=False); sp.add_argument("--format", default="md", choices=("md", "json"))
    sp.set_defaults(func=cmd_export)
    return p


def main(argv):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
