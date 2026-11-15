#!/usr/bin/env python3
"""build_timeline.py - merge logs from several sources and answer: WHEN did it die, and when was the
process's own LAST SIGN OF LIFE? The gap between them is the most important number in a silent-death case.

  build_timeline.py app.log:app heartbeat.log:hb watchdog.log:watchdog events.txt:os --death "2026-03-12 13:49:40"
  build_timeline.py *.log --keywords --window 15
  build_timeline.py *.log --gaps 300           # silent gaps > 300 s inside each source

Source spec is PATH[:label]. Timestamps: ISO (2026-03-12 13:21:15[.mmm]), US (3/12/2026 1:49:41 PM), syslog (Oct 19 13:21:15,
needs --year). Lines without a timestamp are ignored. All times are assumed to be in the SAME timezone - convert first if not.
OBSERVER sources (OS event log, watchdog, journald...) witness the process but are not the process: they are excluded from
'last sign of life'. Labels os/event/wer/watchdog/journal/syslog/dmesg are detected automatically; add more with --observer.

Why: in the DemoApp case the interaction log's last line was 13:21 but the process died at 13:49. Nobody stated that 28 silent
minutes meant 'no instrumentation covers the moment of death' - the evidence that justified adding a heartbeat.
"""
import argparse
import collections
import datetime as dt
import re
import signal
import sys

ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})(?:[.,](\d{1,6}))?")
US = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4}),? +(\d{1,2}):(\d{2}):(\d{2})(?: ?([AaPp][Mm]))?")
SYS = re.compile(r"\b([A-Z][a-z]{2}) +(\d{1,2}) (\d{2}):(\d{2}):(\d{2})\b")
MONTHS = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
KEYWORDS = re.compile(r"(fatal|crash|abort|unhandled|exception|0x[cC]000[0-9a-fA-F]{4}|sig(segv|abrt|kill|bus)|oom|out of memory|killed|"
                      r"watchdog|relaunch|exit|stopp|shutdown|start(ed|ing)?\b|failfast|fail-fast|panic|ANR)", re.I)
OBSERVER_RX = re.compile(r"(^|[^a-z])(os|event|events|eventlog|wer|watchdog|supervisor|journal|journald|syslog|dmesg)([^a-z]|$)", re.I)


def parse_ts(line, year):
    m = ISO.search(line)
    if m:
        y, mo, d, h, mi, s, f = m.groups()
        return dt.datetime(int(y), int(mo), int(d), int(h), int(mi), int(s), int((f or "0").ljust(6, "0")[:6]))
    m = US.search(line)
    if m:
        mo, d, y, h, mi, s, ap = m.groups()
        h = int(h)
        if ap:
            h = h % 12 + (12 if ap.lower() == "pm" else 0)
        return dt.datetime(int(y), int(mo), int(d), h, int(mi), int(s))
    m = SYS.search(line)
    if m and m.group(1) in MONTHS and year:
        return dt.datetime(year, MONTHS[m.group(1)], int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))
    return None


def split_spec(spec):
    """'C:\\logs\\a.log:app' -> ('C:\\logs\\a.log','app'); 'C:\\logs\\a.log' -> (same, '')"""
    if ":" in spec:
        p, _, lab = spec.rpartition(":")
        if lab and not lab.startswith(("\\", "/")) and len(p) > 1:
            return p, lab
    return spec, ""


def load(spec, year):
    path, label = split_spec(spec)
    label = label or path.replace("\\", "/").split("/")[-1]
    with open(path, "rb") as fb:
        enc = "utf-16" if fb.read(2) in (b"\xff\xfe", b"\xfe\xff") else "utf-8"
    rows = []
    with open(path, encoding=enc, errors="replace") as f:
        for n, line in enumerate(f, 1):
            ts = parse_ts(line, year)
            if ts:
                rows.append((ts, label, n, line.rstrip("\n")))
    return label, rows


def norm(msg):
    return re.sub(r"\s+", " ", re.sub(r"0x[0-9a-fA-F]+|\d+", "#", ISO.sub("", msg))).strip()[:120]


def fmt(td):
    s = int(td.total_seconds())
    sign, s = ("-" if s < 0 else ""), abs(s)
    return "%s%dh%02dm%02ds" % (sign, s // 3600, s % 3600 // 60, s % 60)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--death", help="time of death, e.g. '2026-03-12 13:49:40' (from dump / WER / event log)")
    ap.add_argument("--window", type=float, default=10, help="minutes before/after death to print")
    ap.add_argument("--year", type=int, default=dt.date.today().year)
    ap.add_argument("--keywords", action="store_true")
    ap.add_argument("--grep")
    ap.add_argument("--gaps", type=float, default=300)
    ap.add_argument("--no-collapse", action="store_true")
    ap.add_argument("--observer", action="append", default=[])
    a = ap.parse_args()
    data = {}
    for spec in a.sources:
        try:
            label, rows = load(spec, a.year)
            data[label] = rows
        except OSError as ex:
            print("!! cannot read %s: %s" % (spec, ex), file=sys.stderr)
    if not data:
        sys.exit(2)
    death = dt.datetime.fromisoformat(a.death) if a.death else None
    observers = {l for l in data if OBSERVER_RX.search(l)} | set(a.observer)

    print("## Sources\n| source | entries | first | last |\n|---|---|---|---|")
    for label, rows in data.items():
        print("| %s | %d | %s | %s |" % ((label, len(rows), rows[0][0], max(r[0] for r in rows)) if rows else (label, 0, "-", "- (no timestamps parsed)")))

    if death:
        print("\n## Last sign of life before death (%s)" % death)
        overall = None
        for label, rows in data.items():
            before = [r for r in rows if r[0] <= death]
            if not before:
                print("- %s: nothing before death" % label)
                continue
            last = max(before, key=lambda r: r[0])
            if label in observers:
                print("- %s [observer - witnesses, not life]: last entry %s, %s before death" % (label, last[0].strftime("%H:%M:%S"), fmt(death - last[0])))
                continue
            print("- %s: last entry %s (line %d), **%s before death**: %s" % (label, last[0].strftime("%H:%M:%S"), last[2], fmt(death - last[0]), last[3][:90].strip()))
            if overall is None or last[0] > overall[0]:
                overall = last
        if overall:
            gap = death - overall[0]
            print("\n**Overall: the process's own last sign of life is %s before death (%s).**" % (fmt(gap), overall[1]))
            print("=> The moment of death is NOT covered by instrumentation. Treat any 'cause' as inferred; add a periodic heartbeat "
                  "(references/fix-verify-observe.md) so the next death is bracketed to one interval." if gap > dt.timedelta(minutes=2)
                  else "=> Death is bracketed tightly; read the entries just before it as the likely lead-up.")
        else:
            print("\n**No non-observer source has any entry before death: the process left no trace of its own.**")
        after = [r for rows in data.values() for r in rows if r[0] > death]
        if after:
            f = min(after, key=lambda r: r[0])
            print("- first entry AFTER death: %s [%s] %s" % (f[0].strftime("%H:%M:%S"), f[1], f[3][:80].strip()))
        print("- hint: if a heartbeat stops AND the watchdog logs nothing, both processes vanished together -> suspect an external kill (class E): "
              "a rebuild/release script, installer, logoff, or user.")

    print("\n## Silent gaps > %.0f s inside each source" % a.gaps)
    for label, rows in data.items():
        ts = sorted(r[0] for r in rows)
        for g, start in sorted(((b - x, x) for x, b in zip(ts, ts[1:]) if (b - x).total_seconds() > a.gaps), reverse=True)[:3]:
            print("- %s: %s silent starting %s" % (label, fmt(g), start.strftime("%Y-%m-%d %H:%M:%S")))
    allrows = sorted((x for rows in data.values() for x in rows), key=lambda r: (r[0], r[1], r[2]))
    rx = re.compile(a.grep, re.I) if a.grep else None
    if death:
        lo, hi = death - dt.timedelta(minutes=a.window), death + dt.timedelta(minutes=a.window)
        allrows = [r for r in allrows if lo <= r[0] <= hi]
        print("\n## Merged timeline, death -%.0f/+%.0f min" % (a.window, a.window))
    else:
        print("\n## Merged timeline")
    seen, printed = collections.Counter(), 0
    for ts, label, n, line in allrows:
        if (a.keywords and not KEYWORDS.search(line)) or (rx and not rx.search(line)):
            continue
        seen[(label, norm(line))] += 1
        if not a.no_collapse and seen[(label, norm(line))] > 2:
            continue
        print("%s %s [%s:%d]%s %s" % ("!!" if KEYWORDS.search(line) else "  ", ts.strftime("%m-%d %H:%M:%S"), label, n,
                                       (" (%s)" % fmt(ts - death)) if death else "", line.strip()[:140]))
        printed += 1
        if printed > 400:
            print("... truncated at 400 lines; narrow with --window/--grep/--keywords")
            break
    reps = [(k, c) for k, c in seen.items() if c > 2]
    if reps and not a.no_collapse:
        print("\n(collapsed repeats)")
        for (label, msg), c in sorted(reps, key=lambda x: -x[1])[:8]:
            print("  x%d [%s] %s" % (c, label, msg))


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    main()
