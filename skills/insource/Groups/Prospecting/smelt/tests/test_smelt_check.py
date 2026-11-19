#!/usr/bin/env python3
"""Mutation tests for smelt_check.py — does each check actually fire?

A checker that reports nothing on a real package is not evidence the package is
clean; it may be evidence the check cannot run at all. So each case builds a small
package that is correct, injects exactly one defect, and requires the named check to
report it. The inverse half matters just as much: the unmutated package must report
nothing, because a check that fires on ordinary writing gets skimmed and then ignored
— which is worse than no check, since it lends its authority to whichever findings
are left.

Run:  python tests/test_smelt_check.py     (from the smelt skill folder)
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CHECK = os.path.join(SKILL, "scripts", "smelt_check.py")

# Long enough to be a real block, and carrying four identifiers a "rewritten" twin
# can share: a date, two code names, and a source path.
LONG = ("The pool sits between the application and the database, and its size is a "
        "statement about what you are willing to queue for. Sizing it at the connection "
        "ceiling rather than the execution ceiling turns the pool into a queue with "
        "extra steps, which is measured in `pg_stat_activity` against `default_pool_size` "
        "and not in opinion. Twelve workers against four execution slots buys latency "
        "for nobody and a convoy for everyone, as `experience/20-pool-sizing.md` records "
        "at length, with the numbers from the 2026-04-11 run and `MaxBackends` as the "
        "hard bound the whole argument rests on. ")

OTHER = ("Replication lag is the quantity that decides what a read may promise. A stale "
         "read is not a bug when the freshness contract names it and is a data-loss "
         "ticket when nobody wrote the contract down, which `experience/28-lag.md` shows "
         "across three incidents dated 2026-05-02 with the failover logs behind it. ")

REWRITTEN = ("Restated for the reader who skips the arithmetic: set `default_pool_size` "
             "from the execution ceiling, read `pg_stat_activity` before believing a "
             "tuning story, and remember `MaxBackends` is the wall. The 2026-04-11 "
             "numbers are the same ones `experience/20-pool-sizing.md` carries. ")


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(text)


def rewrite(path: str, edit) -> None:
    """Read the whole file *before* opening it for write.

    `open(p,"w").write(open(p).read()+x)` truncates first and then edits an empty
    string — which the checker then correctly reports as a missing INDEX, sending you
    to debug a tool that was telling the truth about your test.
    """
    text = io.open(path, encoding="utf-8").read()
    write(path, edit(text))


def base_package(root: str) -> None:
    """A small, clean knowledge base: every check should pass on this."""
    write(os.path.join(root, "INDEX.md"),
          "# INDEX\n\n"
          "## Layout\n\n"
          "```\nkb/\n  knowledge/   the knowledge\n"
          "  provenance/  the audit trail\n  .work/       working material; do not read\n```\n\n"
          "| File | Owns |\n|---|---|\n"
          "| [pool.md](knowledge/pool.md) | Pool sizing |\n"
          "| [lag.md](knowledge/lag.md) | Replication lag |\n"
          "| [sources.md](provenance/sources.md) | coverage |\n"
          "| [fold history](provenance/fold/experience.md) | the running state |\n")
    write(os.path.join(root, "README.md"),
          "# README\n\nSmelted 2026-11-18 from the run at ../mine/demo. Every claim "
          "carries its source and its evidence.\n")
    write(os.path.join(root, "knowledge", "pool.md"),
          "# Pool\n\n**What this file owns.** Pool sizing.\n\n"
          "**What this file does not own.** Lag is [lag.md](lag.md).\n\n" + LONG +
          '\n\nQuoted: "the pool is a queue with extra steps, not a capacity plan."\n')
    write(os.path.join(root, "knowledge", "lag.md"),
          "# Lag\n\n**What this file owns.** Replication lag.\n\n"
          "**What this file does not own.** Sizing is [pool.md](pool.md).\n\n" + OTHER)
    write(os.path.join(root, "provenance", "sources.md"),
          "# Sources\n\n| Path | Disposition | Contributed |\n|---|---|---|\n"
          "| `experience/20-pool-sizing.md` | read in full | the ceiling rule |\n")
    write(os.path.join(root, "provenance", "fold", "experience.md"), "# Fold\n\n" + LONG)
    write(os.path.join(root, ".work", "notes.md"),
          "# Working notes\n\nNothing here is delivered.\n")


def source_run(root: str) -> None:
    """The corpus the quotes came from: cards, plus cached primary bytes."""
    write(os.path.join(root, "experience", "20-pool-sizing.md"),
          "# Pool sizing\n\nNotes taken while reading, not the source itself.\n")
    # what a quotation is actually verbatim against
    write(os.path.join(root, "cache", "pg-docs-pooling.txt"),
          "Connection Pooling\n\nThe pool is a queue with extra steps, not a capacity "
          "plan.\n")


def run(kb: str, *args: str) -> tuple[str, dict]:
    out = os.path.join(os.path.dirname(kb), "out")
    p = subprocess.run([sys.executable, CHECK, *args, kb, "--out", out],
                       capture_output=True, text=True, timeout=600)
    fp = os.path.join(out, "findings.json")
    data = {"findings": [], "not_applicable": []}
    if os.path.exists(fp):
        data = json.load(io.open(fp, encoding="utf-8"))
    return p.stdout + p.stderr, data


def checks(data: dict) -> set[str]:
    return {f["check"] for f in data.get("findings", [])}


# --- one mutation per check ------------------------------------------------

def m_undeclared(root):
    write(os.path.join(root, "scratchpad", "a.txt"), "x" * 2000)
    return "undeclared-directory"


def m_debris(root):
    write(os.path.join(root, ".work", "_sweep2.py"), "pass\n")
    return "iteration-debris"


def m_empty(root):
    os.makedirs(os.path.join(root, "provenance", "hollow"), exist_ok=True)
    return "empty-directory"


def m_scaffolding(root):
    write(os.path.join(root, ".work", "bulk.bin"), "x" * 4_000_000)
    return "scaffolding-outweighs-product"


def m_counts(root):
    rewrite(os.path.join(root, "README.md"), lambda s: s +
            "\n\nThe base holds 7 files in `knowledge/`, each owning one region.\n")
    return "count-disagrees-with-tree"


def m_conflicting(root):
    """Same URLs, two artifacts, different partitions.

    A class column with one value is not a partition, so each artifact here really
    sorts the set — and the field names differ on purpose, because that is the case
    that matters. A checker that only notices disagreement under an identical column
    name catches almost nothing in the wild.
    """
    urls = [f"https://ex{i:02d}.test/a" for i in range(10)]
    write(os.path.join(root, ".work", "a.json"), json.dumps(
        [{"url": u, "klass": "read-evidence" if i < 7 else "working-notes"}
         for i, u in enumerate(urls)]))
    write(os.path.join(root, ".work", "b.json"), json.dumps(
        [{"url": u, "cat": ("read-evidence" if i < 3 else
                            "working-notes" if i < 8 else "uncached")}
         for i, u in enumerate(urls)]))
    return "conflicting-artifacts"


def m_fetch_claim(root):
    rewrite(os.path.join(root, "README.md"), lambda s: s +
            "\n\nThe header path was wrong; content confirmed by fetching on "
            "2026-11-16 (`DEFAULT_EQ_SEL` and `MaxBackends` present at the corrected "
            "path), so the claim keeps its grade.\n")
    return "fetch-claim-without-receipt"


def m_dup_verbatim(root):
    """The easiest duplication: the same paragraph pasted again below."""
    rewrite(os.path.join(root, "knowledge", "pool.md"), lambda s: s + "\n\n" + LONG)
    return "duplicated-finding"


def m_dup_rewritten(root):
    """The same names carrying two passages — a reading cue, not a duplicate verdict.

    Hand-adjudication on a real package showed this signal cannot tell one claim
    restated from one piece of evidence cited for two claims (4 of 10 pairs were
    real), so the tool reports a list with that base rate rather than a defect.
    """
    rewrite(os.path.join(root, "knowledge", "pool.md"), lambda s: s + "\n\n" + REWRITTEN)
    return "shared-evidence-review"


def m_broken_link(root):
    rewrite(os.path.join(root, "knowledge", "pool.md"), lambda s: s +
            "\n\nSee [the ladder](sharding-and-ladders.md) for the partition schemes.\n")
    return "broken-internal-links"


def m_unlinked_named(root):
    write(os.path.join(root, "provenance", "links.md"),
          "# Links\n\n" + " ".join(f"https://ex{i}.test/p" for i in range(20)) + "\n")
    rewrite(os.path.join(root, "INDEX.md"), lambda s: s.replace(
        "| [lag.md](knowledge/lag.md) | Replication lag |",
        "| [lag.md](knowledge/lag.md) | Replication lag |\n"
        "| links.md holds every URL checked | url ledger |"))
    return "unlinked-but-named"


def m_orphan(root):
    write(os.path.join(root, "knowledge", "stray.md"), "# Stray\n\n" + OTHER)
    return "orphan-file"


def m_no_index(root):
    os.remove(os.path.join(root, "INDEX.md"))
    return "no-index"


def m_non_address(root):
    write(os.path.join(root, "provenance", "links.md"),
          "# Links\n\nhttps://real.test/page is fine, and so is "
          "https://documentation.test/flyway/… which is not, nor https://mr_url "
          "copied out of a shell snippet.\n")
    return "non-addresses-in-the-inventory"


def m_bad_quote(root):
    rewrite(os.path.join(root, "knowledge", "pool.md"), lambda s: s +
            '\n\nAs the manual puts it: "every connection is a thread with a bill "\n'
            "attached, which nobody in this corpus ever wrote.\n")
    return "quotes-unlocated"



def m_package_empty(root):
    for f in os.listdir(root):
        fp = os.path.join(root, f)
        import shutil as _s
        _s.rmtree(fp) if os.path.isdir(fp) else os.remove(fp)
    return "package-empty"


def m_source_missing(root):
    return "source-missing"


def m_no_primary(root):
    """A source run that cached no primary bytes: only the run's own notes."""
    return "no-primary-cache"


def m_prose_only(root):
    """A quotation whose only home is the run's own prose, not any fetched bytes.

    The cached primary text has to go, or the pre-existing quotation still matches
    it and the check is right to stay quiet.
    """
    os.remove(os.path.join(os.path.dirname(root), "run", "cache", "pg-docs-pooling.txt"))
    rewrite(os.path.join(root, "knowledge", "pool.md"), lambda s: s + (
        '\n\nAs the card has it: "notes taken while reading, not the source itself", '
        "which is wording this run wrote for itself.\n"))
    return "quotes-checked-against-prose-only"


def m_outside_layout(root):
    """A folder named in the INDEX prose but missing from the Layout tree block."""
    write(os.path.join(root, "appendix", "notes.md"), "# Notes\n\n" + OTHER)
    rewrite(os.path.join(root, "INDEX.md"), lambda s: s.replace(
        "\n| File | Owns |",
        "\nThe `appendix/` folder holds reader notes.\n\n| File | Owns |"))
    return "directory-outside-layout-block"


MUTATIONS = [
    ("undeclared-directory", m_undeclared, "package"),
    ("scaffolding-outweighs-product", m_scaffolding, "package"),
    ("iteration-debris", m_debris, "package"),
    ("empty-directory", m_empty, "package"),
    ("count-disagrees-with-tree", m_counts, "package"),
    ("conflicting-artifacts", m_conflicting, "package"),
    ("fetch-claim-without-receipt", m_fetch_claim, "package"),
    ("duplicated-finding (verbatim)", m_dup_verbatim, "package"),
    ("shared-evidence-review", m_dup_rewritten, "package"),
    ("broken-internal-links", m_broken_link, "package"),
    ("unlinked-but-named", m_unlinked_named, "package"),
    ("orphan-file", m_orphan, "package"),
    ("no-index", m_no_index, "package"),
    ("non-addresses-in-the-inventory", m_non_address, "links"),
    ("quotes-unlocated", m_bad_quote, "quotes"),
    ("package-empty", m_package_empty, "package"),
    ("source-missing", m_source_missing, "quotes"),
    ("no-primary-cache", m_no_primary, "quotes"),
    ("quotes-checked-against-prose-only", m_prose_only, "quotes"),
    ("directory-outside-layout-block", m_outside_layout, "package"),
]


# --------------------------------------------------------------------------
# the network half: seven checks that only a live request can settle
#
# Local servers, not public sites. A test that depends on someone else's redirect
# still being configured the same way next month is not a test, and sweeping real
# hosts from a suite is rude. Everything here is deterministic and offline.
# --------------------------------------------------------------------------

def network_suite():
    import socket
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    fails = []
    servers = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, loc=None, body=b"<html><title>t</title>ok</html>"):
            self.send_response(code)
            self.send_header("Content-Type", "text/html")
            if loc:
                self.send_header("Location", loc)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_HEAD(self):
            self.do_GET()

        def do_GET(self):
            port = self.server.server_address[1]
            if self.path == "/straight":
                self._send(200)
            elif self.path == "/moved":
                self._send(301, "http://127.0.0.1:%d/arrived" % port)
            elif self.path == "/arrived":
                self._send(200)
            elif self.path == "/leaves":
                other = servers["offsite"].server_address[1]
                self._send(301, "http://127.0.0.1:%d/elsewhere" % other)
            elif self.path == "/elsewhere":
                # the far end of the off-host hop: without a live destination the
                # citation lands on a 404 and the offsite check never gets to run
                self._send(200)
            elif self.path == "/gone":
                self._send(404, body=b"<html>not here</html>")
            else:
                self._send(404, body=b"<html>no route</html>")

    def serve(name):
        s = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        servers[name] = s
        threading.Thread(target=s.serve_forever, daemon=True).start()
        return s.server_address[1]

    try:
        p_main = serve("main")
        p_off = serve("offsite")
    except OSError as e:
        return ["network suite could not bind a local port: %s" % e]

    # a socket that accepts and hangs up with no response at all: the checker's own
    # failure, which must never be booked as a property of the source
    abrupt = socket.socket()
    try:
        abrupt.bind(("127.0.0.1", 0))
        abrupt.listen(8)
        p_abrupt = abrupt.getsockname()[1]
    except OSError as e:
        abrupt.close()
        return ["network suite could not bind the abrupt-close socket: %s" % e]

    def hangup():
        while True:
            try:
                c, _ = abrupt.accept()
                c.close()
            except OSError:
                return

    threading.Thread(target=hangup, daemon=True).start()

    urls = ["http://127.0.0.1:%d/straight" % p_main,
            "http://127.0.0.1:%d/moved" % p_main,
            "http://127.0.0.1:%d/leaves" % p_main,
            "http://127.0.0.1:%d/gone" % p_main,
            "http://127.0.0.1:%d/abrupt" % p_abrupt]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            kb = os.path.join(tmp, "kb")
            os.makedirs(kb)
            base_package(kb)
            write(os.path.join(kb, "provenance", "links.md"),
                  "# Links\n\n" + "\n".join("- %s" % u for u in urls) + "\n")
            # run() already passes --out <dir-of-kb>/out; a second --out would
            # be silently overridden by the later flag, so read where it lands.
            out = os.path.join(tmp, "out")
            _, data = run(kb, "links", "--sweep", "--save-bytes")
            got = checks(data)
            rows = json.load(io.open(os.path.join(out, "links_checked.json"),
                                     encoding="utf-8"))
            by = {r["url"]: r for r in rows}
            moved = by["http://127.0.0.1:%d/moved" % p_main]
            leaves = by["http://127.0.0.1:%d/leaves" % p_main]
            dropped = by["http://127.0.0.1:%d/abrupt" % p_abrupt]

            for cid, why in [("redirect-same-host", "a citation that landed on another path"),
                             ("redirect-offsite-unrecorded", "a citation that left the host"),
                             ("dead-without-archive-attempt", "a 404 nobody tried to rescue"),
                             ("tool-errors-recorded", "the checker's own failure, kept apart")]:
                ok = cid in got
                print("  %-9s %s%s" % ("fires" if ok else "DEAD", cid,
                                       "" if ok else "  (saw %s)" % sorted(got)))
                if not ok:
                    fails.append("%s: never fires against %s" % (cid, why))

            # the hop list is the entire reason redirects are walked by hand
            for label, row in (("same-host", moved), ("offsite", leaves)):
                ok = bool(row.get("chain")) and bool(row["chain"][0].get("to"))
                print("  %-9s hop written down (%s)" % ("recorded" if ok else "MISSING", label))
                if not ok:
                    fails.append("%s: chain empty, though the finding promises it" % label)
            ok = leaves["final_url"].startswith("http://127.0.0.1:%d" % p_off)
            print("  %-9s chain followed to its destination" % ("followed" if ok else "WRONG"))
            if not ok:
                fails.append("offsite: never reached the second server")
            ok = bool(dropped.get("tool_error"))
            print("  %-9s checker failure kept out of the dead/unreachable class"
                  % ("separated" if ok else "MERGED"))
            if not ok:
                fails.append("abrupt close was not classed as a tool error: %s" % dropped)
            rec = os.path.join(out, "receipts")
            ok = os.path.isdir(rec) and any(f.endswith(".body") for f in os.listdir(rec))
            print("  %-9s --save-bytes retained the fetched bytes" % ("kept" if ok else "MISSING"))
            if not ok:
                fails.append("--save-bytes wrote no receipts")

            # dead URLs with no snapshot must come back as unrecoverable, not quiet.
            # This run keeps no bytes, so it is also where the depth label belongs:
            # a sweep that retained everything has nothing to confess.
            _, d2 = run(kb, "links", "--sweep", "--archive")
            got2 = checks(d2)
            for cid, why in [("dead-unrecoverable", "no snapshot exists for these"),
                             ("status-only-verification", "an unlabelled sweep depth")]:
                ok = cid in got2
                print("  %-9s %s" % ("fires" if ok else "DEAD", cid))
                if not ok:
                    fails.append("%s: never fires against %s" % (cid, why))

        # and the guard that refuses to run a lookup against an empty ledger
        with tempfile.TemporaryDirectory() as tmp2:
            kb2 = os.path.join(tmp2, "kb")
            os.makedirs(kb2)
            base_package(kb2)
            write(os.path.join(kb2, "provenance", "links.md"),
                  "# Links\n\n" + "\n".join("- %s" % u for u in urls) + "\n")
            _, d3 = run(kb2, "links", "--archive", "--out", os.path.join(tmp2, "fresh"))
            ok = "archive-lookup-blocked" in checks(d3)
            print("  %-9s archive-lookup-blocked" % ("fires" if ok else "DEAD"))
            if not ok:
                fails.append("archive-lookup-blocked: ran a lookup with nothing to attach it to")
    finally:
        for s in servers.values():
            s.shutdown()
        abrupt.close()
    return fails


def negative_checks():
    """Things the checker must NOT reject. A filter that silently drops real
    citations is worse than no filter, because nothing downstream can see the loss."""
    fails = []
    cases = {
        "IPv4 host": "http://127.0.0.1:8080/a",
        "short-label host": "https://a.test/b",
        "query and fragment": "https://ex.test/p?q=1&r=2#frag",
        "trailing punctuation": "https://ex.test/page.",
    }
    with tempfile.TemporaryDirectory() as tmp:
        kb = os.path.join(tmp, "kb")
        os.makedirs(kb)
        base_package(kb)
        write(os.path.join(kb, "provenance", "links.md"),
              "# Links\n\n" + "\n".join("- %s" % u for u in cases.values()) + "\n")
        _, data = run(kb, "links")
        got = checks(data)
        out = os.path.join(tmp, "out", "url_inventory.json")
        inv = json.load(io.open(out, encoding="utf-8")) if os.path.exists(out) else {}
        clean = set(inv.get("clean", []))
        rejected = set(inv.get("rejected", {}))
        # An empty inventory would make every case below "not in clean", which reads
        # as a rejection but only means the fixture wrote nothing — say so here.
        if inv.get("candidates") != len(cases):
            return ["negative-checks fixture produced %r candidates, expected %d"
                    % (inv.get("candidates"), len(cases))]
        for label, url in cases.items():
            kept = url.rstrip(".") in clean or url in clean
            print("  %-9s %s" % ("swept" if kept else "REJECTED", label))
            if not kept:
                fails.append("validator rejects a real address: %s (%s) — rejected: %s"
                             % (label, url, sorted(rejected)[:2]))
        if "non-addresses-in-the-inventory" in got:
            fails.append("clean inventory trips non-addresses-in-the-inventory")
        # The contract for a host that merely *looks* like a stub: say so, and ask it
        # anyway. Dropping it quietly is how a real citation disappears from a ledger.
        if "placeholder-looking-hosts-swept-anyway" not in got:
            fails.append("placeholder-looking-hosts-swept-anyway: did not flag the "
                         "stub-shaped hosts, so the flag-and-still-sweep contract is unproven")
        for u in inv.get("placeholder_hosts", []):
            if u not in clean:
                fails.append("placeholder host dropped instead of swept: %s" % u)
    return fails


def adjudication_negatives():
    """The six noise pairs I found by hand must not come back as findings.

    Controlled pair: the same shared-name paragraphs written twice, once as ordinary
    prose (a legitimate reading cue) and once prefixed with a scaffolding lead-in
    (which must be suppressed). Only the difference between those two runs shows that
    the suppression is the filter's doing rather than the evidence being thin.
    """
    SHARED_NAMES = ("Read `src/backend/tcop/postinit.c` at lines 935-960 for the "
                    "reserved-slot tiers, and `src/postmaster/postmaster.c` at 2373-2385 "
                    "for the admission switch; both were re-opened on 2026-11-13 from the "
                    "cached bytes, and the error text `sorry, too many clients already` is "
                    "quoted from the second of those two files, not paraphrased. ")
    LINEAGE = "**Source lineage.** " + SHARED_NAMES
    PLAIN = "**Admission detail.** " + SHARED_NAMES
    NUMBERS = ("Fully read: eleven pages at 614 words, 562 lines and 574 tokens per "
               "section, one at 908 words; the profile carries 663 lines against 661 "
               "splits, and the second book 1,203 words across five sampled pages, all "
               "of which came out of the same census command run twice. ")

    def build(first, second):
        root = tempfile.mkdtemp()
        kb = os.path.join(root, "kb")
        os.makedirs(kb)
        base_package(kb)
        rewrite(os.path.join(kb, "knowledge", "pool.md"), lambda s: s + "\n\n" + first)
        rewrite(os.path.join(kb, "knowledge", "lag.md"), lambda s: s + "\n\n" + second)
        return root, kb

    fails = []
    checks_expect = [
        ("plain shared names are a reading cue", PLAIN, PLAIN,
         "shared-evidence-review", True),
        ("scaffolding sections are not", LINEAGE, LINEAGE,
         "shared-evidence-review", False),
        ("bare numbers are not evidence of a repeat", NUMBERS, NUMBERS,
         "shared-evidence-review", False),
    ]
    for label, a, b, cid, want in checks_expect:
        root, kb = build(a, b)
        try:
            _, data = run(kb, "package")
            got = cid in checks(data)
            ok = got == want
            print("  %-9s %s" % ("ok" if ok else "WRONG", label))
            if not ok:
                fails.append("%s: expected %s=%s, got findings %s"
                             % (label, cid, want, sorted(checks(data))))
        finally:
            shutil.rmtree(root, ignore_errors=True)
    return fails


def main() -> int:
    """Two halves: does each check fire when its defect exists, and does the report
    stay silent when nothing is wrong. Both directions are needed — a check tuned to
    catch one real defect may fire on ordinary writing everywhere else, and a report
    full of noise is read as 'nothing to see here'."""
    fails: list[str] = []

    # ---- the clean package: no finding should fire at all ----------------
    with tempfile.TemporaryDirectory() as tmp:
        kb = os.path.join(tmp, "kb")
        os.makedirs(kb)
        base_package(kb)
        src = os.path.join(tmp, "run")
        os.makedirs(src)
        source_run(src)
        for cmd, extra in (("package", ()), ("quotes", ("--source", src)), ("links", ())):
            out, data = run(kb, cmd, *extra)
            got = checks(data)
            print(f"clean {cmd:8s} -> findings: {sorted(got) or 'none'}")
            if "Traceback" in out:
                fails.append(f"clean {cmd}: crashed\n{out.strip()[:300]}")
            for g in got:
                fails.append(f"clean {cmd} trips {g} — a check that fires on ordinary "
                             f"writing will be skimmed and then ignored")

    # ---- each defect must be named by its check --------------------------
    print()
    for label, mutate, cmd in MUTATIONS:
        want = label.split(" ")[0]
        with tempfile.TemporaryDirectory() as tmp:
            kb = os.path.join(tmp, "kb")
            os.makedirs(kb)
            base_package(kb)
            src = os.path.join(tmp, "run")
            os.makedirs(src)
            source_run(src)
            if want == "source-missing":
                extra = ("--source", os.path.join(tmp, "nowhere"))
                out, data = run(kb, cmd, *extra)
                got = checks(data)
                print(("  fires     " if want in got else "  DEAD      ")
                      + f"{label} (saw {sorted(got)})")
                if want not in got:
                    fails.append(f"{label}: never fires")
                continue
            if want == "no-primary-cache":
                os.remove(os.path.join(src, "cache", "pg-docs-pooling.txt"))
            mutate(kb)
            extra = ("--source", src) if cmd == "quotes" else ()
            out, data = run(kb, cmd, *extra)
            got = checks(data)
            if want in got:
                print(f"  fires     {label}")
            elif "Traceback" in out:
                first = [l for l in out.splitlines() if l.strip().startswith(("File", "TypeError",
                                                                             "ValueError", "NameError"))]
                print(f"  CRASH     {label}: {(first[:1] or ['see output'])[0][:110]}")
                fails.append(f"{label}: checker crashed")
            else:
                print(f"  DEAD      {label}: '{want}' did not fire (saw {sorted(got)})")
                fails.append(f"{label}: check {want} never fires")

    print()
    print("--- the validator must not reject real addresses ---")
    fails += negative_checks()

    if "--no-network" not in sys.argv:
        print()
        print("--- network checks (local servers) ---")
        fails += network_suite()
    else:
        print("\nskipped: the network suite (--no-network)")

    print("\n" + ("PASS — every check demonstrably fires, and the clean package is quiet"
                  if not fails else f"FAIL ({len(fails)})\n  " + "\n  ".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
