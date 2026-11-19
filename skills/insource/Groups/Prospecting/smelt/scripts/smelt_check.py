#!/usr/bin/env python3
"""smelt_check.py — the mechanical half of smelt's verify pass.

Stdlib only; no dependencies, no network unless `links --sweep` is asked for.

The division of labour is deliberate: this script measures, the agent judges.
It never decides whether a claim is right, whether a yield is honest, or whether
a contradiction should be smoothed. It reports the facts a human or an agent
cannot reliably eyeball at package scale — files nobody declared, counts that
disagree with the tree, two artifacts answering one question twice, quotes that
appear nowhere in the corpus, links recorded as live when the tool that checked
them never looked — and exits with each finding numbered so the run can resolve
it or waive it in writing.

  package <kb>                     structure, declarations, receipts, duplicates
  quotes  <kb> --source <run>      verbatim audit of every quoted span
  links   <kb> [--sweep]           URL inventory, validation, status, archive
  all     <kb> [--source <run>]    package + quotes (+ links only with --sweep)

Common: --json  --waivers <file>  --out <dir>  --verbose
Nothing here blocks delivery. Unwaived findings are a report the agent must
answer, not a gate that answers for it.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
MD_EXT = (".md", ".markdown", ".txt")
# Deliverable = what a consumer reads. Cache = how it was made.
DELIVERABLE_ROOTS = {"INDEX.md", "README.md", "knowledge"}
# A cache zone is anything whose name begins with "." or sits in a declared
# cache folder; provenance/ is a third thing — a *published* audit trail.
CACHE_NAMES = {"cache", ".cache", "work", ".work", "build", ".build", "scratch", "tmp"}
# Bytes that came from somewhere else. A JSON the run wrote about its own work is a
# ledger, not a receipt, and cannot vouch for a fetch the way fetched bytes can.
PAYLOAD_EXT = (".html", ".htm", ".xml", ".eml", ".pdf", ".body", ".bin", ".png",
               ".jpg", ".jpeg", ".gif", ".csv", ".tsv", ".json.gz", ".txt.gz")


def is_cache(rel_dir: str) -> bool:
    """Working material: named as a cache, or hidden."""
    leaf = rel_dir.rsplit("/", 1)[-1].lower()
    return leaf in CACHE_NAMES or leaf.startswith(".")


# --------------------------------------------------------------------------
# findings
# --------------------------------------------------------------------------

class Findings:
    """Collected advisories with stable ids, so a waiver file can name them."""

    def __init__(self) -> None:
        self.items: list[dict] = []
        self.na: list[str] = []

    def add(self, check: str, subject: str, detail: str, suggest: str = "") -> None:
        key = f"{check}:{subject}"
        fid = "SM-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:8].upper()
        if any(f["id"] == fid for f in self.items):
            return                      # two patterns, one finding
        self.items.append(
            {"id": fid, "check": check, "subject": subject, "detail": detail,
             "suggest": suggest}
        )

    def not_applicable(self, check: str, why: str) -> None:
        """A check that cannot run says so out loud. A silent pass is a lie."""
        self.na.append(f"{check}: {why}")

    def merge_waivers(self, path: str | None) -> None:
        if not path or not os.path.exists(path):
            return
        try:
            data = json.load(io.open(path, encoding="utf-8"))
        except Exception as e:  # a broken waiver file must not hide findings
            self.add("waivers-unreadable", path, f"{type(e).__name__}: {e}",
                     "fix or remove the waiver file; do not let it fail closed")
            return
        waived = {w.get("id"): w for w in data if isinstance(w, dict)}
        for f in self.items:
            w = waived.get(f["id"])
            if w and str(w.get("reason", "")).strip():
                f["waived"] = str(w["reason"]).strip()

    @property
    def open_items(self) -> list[dict]:
        return [f for f in self.items if not f.get("waived")]

    def report(self, title: str, verbose: bool) -> None:
        print(f"\n=== {title} ===")
        by: dict[str, list[dict]] = {}
        for f in self.items:
            by.setdefault(f["check"], []).append(f)
        if not by:
            print("  no findings")
        for check in sorted(by):
            rows = by[check]
            print(f"\n  {check}  ({len(rows)})")
            for f in rows:
                mark = "WAIVED " if f.get("waived") else "OPEN   "
                print(f"    [{mark}{f['id']}] {f['subject']}")
                for line in wrap(f["detail"], 74):
                    print(f"        {line}")
                if f.get("waived"):
                    print(f"        waived: {f['waived']}")
                elif verbose and f["suggest"]:
                    print(f"        -> {f['suggest']}")
        if self.na:
            print("\n  checks that did not apply:")
            for n in self.na:
                print(f"    - {n}")
        if self.open_items:
            print(f"\n  {len(self.open_items)} finding(s) need an answer: fix them, or "
                  f"record a reason in the waivers file.")
        print(f"  totals: {len(self.items)} findings, "
              f"{len(self.open_items)} unwaived, {len(self.na)} not-applicable")


def wrap(text: str, width: int) -> list[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    out, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > width:
            out.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        out.append(cur)
    return out or [""]


def read(path: str) -> str:
    try:
        return io.open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def walk_files(root: str, skip_dirs: tuple = ()) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "__pycache__", "node_modules"}
                       and not any(d.startswith(s) for s in skip_dirs)]
        for fn in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, fn), root).replace("\\", "/"))
    return sorted(out)


def md_docs(files: list[str]) -> list[str]:
    return [f for f in files if f.lower().endswith(MD_EXT)]


# --------------------------------------------------------------------------
# text normalisation shared by the duplicate and quote checks
# --------------------------------------------------------------------------

TRANS = {
    "‘": "'", "’": "'", "“": '"', "”": '"', "—": "-", "–": "-",
    "…": "...", " ": " ", " ": " ", " ": " ",
}


def normalize(s: str) -> str:
    for k, v in TRANS.items():
        s = s.replace(k, v)
    s = unicodedata.normalize("NFKC", s)
    # rejoin a word hyphenated across a line break, the way a scan does it
    s = re.sub(r"([A-Za-z])-\s*\n\s*([a-z])", r"\1\2", s)
    s = re.sub(r"[^a-z0-9' ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def shingles(norm: str, n: int = 8) -> set[str]:
    w = norm.split()
    if len(w) < n:
        return {" ".join(w)} if w else set()
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


# --------------------------------------------------------------------------
# 1. package
# --------------------------------------------------------------------------

def check_package(kb: str, F: Findings, verbose: bool, out: str = ".") -> None:
    files = walk_files(kb)
    if not files:
        F.add("package-empty", kb, "no files to check")
        return
    index_p = os.path.join(kb, "INDEX.md")
    index = read(index_p)
    if not index:
        F.add("no-index", "INDEX.md", "the entry point is missing or unreadable",
              "write it: layout, file map, routes, grading")

    dirs = sorted({f.split("/")[0] for f in files if "/" in f})

    # -- 1a. everything present must be declared --------------------------
    # "declared in the Layout tree" means the diagram itself. section() runs to the
    # next heading, so testing membership in the whole section would pass on a
    # sentence that merely mentions the folder further down the page.
    _lay = section(index, "Layout") or ""
    _fences = re.findall(r"```[^\r\n]*\r?\n(.*?)```", _lay, re.S)
    lay = "\n".join(_fences) or _lay
    for d in dirs:
        if d.lower() not in index.lower():
            F.add("undeclared-directory", d,
                  f"'{d}/' exists in the package ({count_in_tree(files, d)} files, "
                  f"{human_bytes(size_in_tree(kb, d))}) but the INDEX never names it. "
                  "A consumer cannot tell product from scaffolding, and may read the "
                  "wrong one.",
                  "add it to the INDEX layout block with one line on what it is for "
                  "and whether a reader should open it")
        elif lay and d.lower() not in lay.lower():
            F.add("directory-outside-layout-block", d,
                  f"'{d}/' is named somewhere in INDEX.md but not inside the Layout "
                  "tree, which is the block a reader uses to learn the shape",
                  "list it under Layout with its purpose")

    # -- 1b. the product must not be smaller than the scaffolding ---------
    prod = sum(size_in_tree(kb, d) for d in dirs if d in DELIVERABLE_ROOTS)
    if os.path.exists(os.path.join(kb, "INDEX.md")):
        prod += os.path.getsize(os.path.join(kb, "INDEX.md"))
    scaffold = sum(size_in_tree(kb, d) for d in dirs if is_cache(d))
    if scaffold and prod and scaffold > prod:
        F.add("scaffolding-outweighs-product", "package",
              f"the deliverable is {human_bytes(prod)} while internal working material is "
              f"{human_bytes(scaffold)}: the package's centre of gravity has moved out of "
              "the thing it exists to ship.",
              "keep only what the audit needs: fold superseded drafts in, delete "
              "abandoned runs or mark them superseded in the index line")

    # -- 1c. iteration debris and empty dirs ------------------------------
    for rel in files:
        b = os.path.basename(rel)
        if re.search(r"\w\d\.(py|sh|ps1|js|txt|json|md)$", b, re.I) or re.match(
                r"(?i)^[_\-]*(fix|patch|redo|retry|try|new|old|bak|copy|final2?|v2)[_.\-]",
                b):
            F.add("iteration-debris", rel,
                  "the name records an iteration rather than a role, and its "
                  "predecessor is usually still beside it — so the package holds two "
                  "answers to one question and says nothing about which won",
                  "fold the improvement into the first file, or mark the older "
                  "superseded in the same place the newer one is cited")
    for dirpath, dirnames, filenames in os.walk(kb):
        if not filenames and not any(
                os.listdir(os.path.join(dirpath, d)) for d in dirnames):
            rel = os.path.relpath(dirpath, kb).replace("\\", "/")
            if rel != ".":
                F.add("empty-directory", rel,
                      "created and never filled: an abandoned approach still taking "
                      "space in the tree a reader has to interpret",
                      "fill it, delete it, or record what it was going to hold")

    # -- 1d. one measurement, one artifact --------------------------------
    audit_artifacts(kb, files, F)

    # -- 1e. fetch-based claims need a receipt ----------------------------
    fetch_claims(kb, files, F)

    # -- 1f. counts that disagree with the tree ---------------------------
    count_claims(kb, files, F)

    # -- 1g. the same finding written twice -------------------------------
    duplicate_findings(kb, files, F, out)

    # -- 1h. file graph ---------------------------------------------------
    file_graph(kb, files, F)


def audit_artifacts(kb: str, files: list[str], F: Findings) -> None:
    """Two artifacts measuring the same set, then disagreeing about it.

    A checker cannot know that `klass` and `cat` ask one question. It can know
    that two row-lists hold the *same URLs* — that is the overlap that proves they
    measured one set — and that they then partition it differently.
    """
    lists: list[tuple[str, list, dict, set]] = []
    for rel in files:
        if not rel.endswith(".json") or not is_cache(os.path.dirname(rel)):
            continue
        try:
            data = json.load(io.open(os.path.join(kb, rel), encoding="utf-8"))
        except Exception:
            continue
        if not (isinstance(data, list) and data and isinstance(data[0], dict)):
            continue
        urls = {str(r.get("url")) for r in data if isinstance(r, dict) and r.get("url")}
        dist = {}
        for key in data[0]:
            c: dict[str, int] = {}
            for row in data:
                v = row.get(key)
                k = (f"<set:{bool(v)}>" if isinstance(v, (list, dict))
                     else str(v)[:48])
                c[k] = c.get(k, 0) + 1
            if 1 < len(c) <= 12:
                dist[key] = c
        lists.append((rel, data, dist, urls, set(data[0])))
    if len(lists) < 2:
        F.not_applicable("duplicate-measurements",
                         "fewer than two list-shaped artifacts in the working material")
        return
    compared = 0
    OBSERVE = {"url", "status", "checked", "method", "err", "tool_error", "bytes",
               "final_url", "chain", "title", "date", "path", "file"}
    for i in range(len(lists)):
        for j in range(i + 1, len(lists)):
            a, ra, da, ua, ka_ = lists[i]
            b, rb, db, ub, kb_ = lists[j]
            if len(ra) != len(rb) or not ua or not ub:
                continue
            overlap = len(ua & ub) / max(1, len(ua | ub))
            if overlap < 0.8:
                continue                      # different sets: no contradiction possible
            if ka_ <= kb_ or kb_ <= ka_:
                continue                      # one extends the other: pipeline stages,
            #                                       not two rival measurements
            ja = {k: v for k, v in da.items() if k not in OBSERVE}
            jb = {k: v for k, v in db.items() if k not in OBSERVE}
            if not ja or not jb:
                continue
            compared += 1
            agree = any(sorted(x.values(), reverse=True) == sorted(y.values(), reverse=True)
                        for x in ja.values() for y in jb.values())
            if agree:
                continue
            (ak, av), (bk, bv) = next(iter(ja.items())), next(iter(jb.items()))
            F.add("conflicting-artifacts", f"{a} vs {b}",
                  f"both classify the same {len(ra)} URLs ({overlap:.0%} identical), under "
                  f"'{ak}' = {short_dist(av)} against '{bk}' = {short_dist(bv)}. No "
                  "partition either artifact produces matches the other, and nothing in "
                  "the package says which one the delivered ledger was built from — so the "
                  "reader has to infer it from the prose, which is the opposite of a ledger.",
                  "name the authoritative artifact beside the ledger it feeds, then fold or "
                  "mark superseded the other. If they answer different questions, say what "
                  "each one answers.")


    if compared == 0:
        F.not_applicable(
            "duplicate-measurements",
            f"{len(lists)} list artifacts in the working material, but no two of them "
            "measure the same set of URLs under different field sets — every candidate "
            "pair was either a pipeline stage of the other (one extends the other's "
            "fields) or a different set. Nothing was compared, so this is not a pass.")


def fetch_claims(kb: str, files: list[str], F: Findings) -> None:
    """'Verified by fetching' needs the fetched bytes, not a note saying so.

    A JSON the run wrote about its own checking is a ledger. It records the
    conclusion; only the payload records the evidence.
    """
    payloads = [f for f in files if f.lower().endswith(PAYLOAD_EXT)
                and not f.endswith(".json")]
    claims = []
    pat = re.compile(r"(?i)\b(verified|confirmed|re-?established|checked)\b[^.\n]{0,70}"
                     r"\bby (fetching|a fetch|requesting)|fetched on \d{4}-\d\d-\d\d")
    for rel in md_docs(files):
        text = read(os.path.join(kb, rel))
        m = pat.search(text)
        if m:
            claims.append((rel, re.sub(r"\s+", " ",
                                       text[max(0, m.start() - 60):m.end() + 200])[:190]))
    if not claims:
        F.not_applicable("fetch-receipts", "no prose claims of a confirming fetch")
        return
    if not payloads:
        F.add("fetch-claim-without-receipt", ", ".join(sorted({r for r, _ in claims})),
              f"{len(claims)} file(s) assert content was fetched and confirmed, and the "
              "package retains no fetched bytes anywhere — only the run's own "
              "summaries of what it saw. The claim is then checkable solely by "
              "re-fetching, which is the thing a delivered base exists to avoid. "
              f"Example: {claims[0][1]}",
              "cache the bytes beside the claim, one file per fetch, and name them in "
              "the ledger row: a fetched claim should be as re-checkable as a quoted one")


def count_claims(kb: str, files: list[str], F: Findings) -> None:
    """Count claims whose directory is stated outright, checked against the tree.

    Deliberately narrow. "The four folder knowledge files" is a real bug when the
    directory holds three, but the phrase names no directory, so a checker that
    guessed which one it meant would report a true defect with false supporting
    numbers — worse than staying quiet. Only a count attached to a path is resolved.
    """
    counts: dict[str, int] = {}
    for rel in files:
        for part in filter(None, os.path.dirname(rel).split("/")):
            counts[part] = counts.get(part, 0) + 1
    checked = 0
    pats = [
        re.compile(r"(?i)(\d+)\s+(?:[\w-]+\s+){0,2}files?\s+in\s+[`']?([\w.\-/]+)"),
        re.compile(r"(?i)[`']([\w.\-/]+)/?[`']\s*[—:(-]{0,3}\s*(?:the\s+)?(\d+)\s+"
                   r"(?:[\w-]+\s+){0,2}files?"),
        re.compile(r"(?i)\b(\d+)\s+(?:[\w-]+\s+){0,2}files?\s*[—(-]?\s*in\s+"
                   r"[`']?([\w.\-/]+)"),
    ]
    for rel in [f for f in ("INDEX.md", "README.md") if f in files]:
        text = read(os.path.join(kb, rel))
        for pat in pats:
            for m in pat.finditer(text):
                g1, g2 = m.group(1), m.group(2)
                want, hint = (int(g1), g2) if g1.isdigit() else (int(g2), g1)
                if not str(want).isdigit():
                    continue
                leaf = hint.rstrip("/").replace("`", "").rsplit("/", 1)[-1]
                if leaf not in counts:
                    continue
                checked += 1
                if counts[leaf] != want:
                    F.add("count-disagrees-with-tree", f"{rel}: \"{m.group(0)[:64]}\"",
                          f"the text says {want}; '{leaf}/' holds {counts[leaf]} counted "
                          "from the tree just now. A count in prose is a claim the "
                          "directory can falsify, and it is the entry point that carries it.",
                          "emit the number from the artifact that holds the rows, or drop "
                          "it and let the layout say it once")
    if not checked:
        F.not_applicable("count-claims",
                         "no count claim named a directory this checker could resolve "
                         "without guessing")


DOC_EXT = (".md", ".markdown", ".txt", ".html", ".json", ".csv", ".tsv", ".yaml")


def signature(text: str) -> tuple[set, set, set]:
    """(identifiers, fact-shaped identifiers, 4-grams).

    Two passages naming the same source file are not one finding twice: route tables
    and card sections name the same files constantly. Two passages naming the same
    date, status code and symbols are. So document addresses drop out of the
    signature, and what remains is split by whether it carries a fact — a number, a
    date, or a code identifier. Case is folded on both sources, or `EXPLAIN` and
    `explain` count as two tokens and every file's own subject vocabulary starts
    looking like a rare shared signal.
    """
    ids = {i.lower() for i in re.findall(r"`([^`]{4,60})`", text)}
    ids |= {i.lower() for i in re.findall(
        r"\b\d{4}-\d{2}-\d{2}\b|\b\d{3,}\b|\b[A-Z][A-Z0-9_]{4,}\b", text)}
    ids = {i.strip(" .;:`") for i in ids if not i.lower().endswith(DOC_EXT)}
    facts = {i for i in ids if re.search(r"\d|_|\.|::", i)}
    return ids, facts, shingles(normalize(text), 4)


# Sections every card carries as a matter of form — provenance, reach, ownership
# declarations, evidence-quality caveats. They must share dates, paths and byte
# counts with each other, so comparing them for repetition reports the base's own
# scaffolding back as a defect. Hand-adjudicating ten candidate pairs on a real
# package found exactly that: four real duplicates, six artefacts of these sections.
STRUCTURAL = re.compile(
    r"(?i)(source lineage|lineage|reach\b|census|denominator|evidence[- ]quality|"
    r"what this file (does not )?own|contradictions this file|"
    r"files? (read|opened|fetched)|provenance|the tools that produced|yield)")
# An identifier that names a thing: a symbol, path, column, class. A bare number is
# not that. Two reach tables agreeing on "614" is arithmetic coincidence, and counting
# any digit-bearing token as a fact turned six such pairs into findings.
NAMES = ("_", ".", "::", "/", "->")


def name_shaped(tok: str) -> bool:
    return len(tok) >= 5 and not tok.isdigit() and any(s in tok for s in NAMES)


def structural(label: str, body: str) -> bool:
    """Is this block the base's own scaffolding rather than an assertion?

    The role markers live in two places: a heading names the section, but in a
    card-per-section file the lineage and reach notes are bold lead-ins inside one
    heading, so the label says "Card 21" while the paragraph says "Source lineage".
    Checking only the label let exactly that class of noise through.
    """
    if STRUCTURAL.search(label or ""):
        return True
    head = normalize(body)[:48]
    return bool(re.match(
        r"^(source lineage|lineage|reach|census|evidence quality|what this file|"
        r"denominators|the tools that produced)", head))


def duplicate_findings(kb: str, files: list[str], F: Findings,
                    out: str = ".") -> None:
    """One finding written twice — in the base whose rule says it is not.

    Word overlap is the weak signal: an author restating a finding changes every
    sentence while naming the same paths, pages and dates. But raw shared
    identifiers over-report, because `schema-design.md` legitimately appears in a
    file map, a route table and a dozen cross-links. What identifies a *finding* is
    a token the rest of the package does not use — so each token is weighted by how
    many blocks carry it, and only the rare ones count.
    """
    # The delivered base is where one-owner-per-fact governs. `provenance/fold/` is
    # history kept exactly as the fold left it, and `merges.md` is an operation ledger
    # whose rows repeat their own labels by design — flagging those teaches the reader
    # to ignore the report.
    skip_prefix = ("provenance/fold/", "provenance/merges.md")
    targets = [f for f in md_docs(files)
               if not is_cache(os.path.dirname(f)) and not f.startswith(skip_prefix)]
    cues: list[tuple[str, str, str, list[str], float, float]] = []
    for rel in targets:
        rows = []
        df: dict[str, int] = {}
        for label, body in blocks(os.path.join(kb, rel)):
            if len(normalize(body)) <= 160:
                continue
            ids, facts, sh = signature(body)
            rows.append((label, facts, ids, sh, structural(label, body)))
            for tok in ids:
                df[tok] = df.get(tok, 0) + 1
        # Rarity is judged inside the file: a path one document mentions twice is a
        # repeated finding, while a file name its index and its route table both list
        # is one fact routed two ways. Package-wide rarity hides the first case.
        rare = {tok for tok, n in df.items() if n <= 3}
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                la, fa, ia, sa, sca = rows[i]
                lb, fb, ib, sb, scb = rows[j]
                # A heading and the paragraph introducing its own section say one
                # thing at two zooms, which is the structure this skill asks writers
                # to produce — recognised by the labels nesting, never by position.
                # (Skipping "the first block" outright was wrong once blocks split at
                # paragraphs: it silenced every duplicate of a file's opening section.)
                na, nb = normalize(la), normalize(lb)
                if na != nb and na and (na in nb or nb in na):
                    continue
                sc = len(sa & sb) / max(1, min(len(sa), len(sb)))
                shared = (ia & ib) & rare
                shared_facts = (fa & fb) & rare
                ic = len(shared) / max(1, min(len(ia & rare), len(ib & rare)))
                # Two different questions, two different answers. Near-verbatim text is
                # duplication and is called that. Whether two passages make ONE claim
                # twice or cite ONE piece of evidence for two different claims is not
                # decidable from text — the tokens are identical either way, and this
                # base re-cites the same source lines across cards on purpose — so that
                # case is reported as a pair to read, never as a verdict.
                if sc >= 0.90:
                    F.add("duplicated-finding", f"{rel}: '{la[:44]}' ~ '{lb[:44]}'",
                          f"two passages are near-verbatim (phrase overlap {sc:.2f}, "
                          f"shared names: {', '.join(sorted(shared)[:4])[:120]}). Smelt's "
                          "rule is that two statements of one thing become one statement "
                          "with two pieces of evidence.",
                          "merge them, keeping both provenances as evidence on one row")
                    continue
                if sca or scb:
                    continue      # scaffolding against scaffolding is not a finding
                named = sorted(t for t in shared if name_shaped(t))
                # two sibling paragraphs under one heading need denser agreement than
                # two sections do: a heading and the text beneath it restate by design
                if (len(shared) < 3 or len(named) < 2 or ic < (0.60 if la == lb else 0.35)
                        or not any(re.search(
                            r"\d{4}-\d{2}-\d{2}|[a-z0-9_/]{2}[._][a-z]{1,4}\b|_", f)
                            for f in shared_facts)):
                    continue
                cues.append((rel, la, lb, named, ic, sc))
    if cues:
        # The whole list goes to a file: naming four of ten pairs would leave the
        # reader with a cue they cannot work through, which is the same defect as an
        # unexamined quote residual — the number looks accounted for, the items are not.
        try:
            os.makedirs(out, exist_ok=True)
            json.dump([{"file": r, "a": l, "b": o, "shared_names": n,
                        "identifier_overlap": round(i, 3),
                        "phrase_overlap": round(s, 3)}
                       for r, l, o, n, i, s in cues],
                      io.open(os.path.join(out, "shared_evidence.json"), "w",
                              encoding="utf-8"), indent=1, ensure_ascii=False)
            where = " full list in shared_evidence.json"
        except Exception:
            where = " (could not write the list; see the examples below)"
        # One aggregate, because the base rate is what makes this honest. Hand-
        # adjudicating ten candidate pairs on a real package: four restated one claim
        # and should merge, six were one piece of evidence legitimately cited for two
        # different claims. A per-pair "finding" at that precision is a report the
        # reader learns to skim, which is worse than the list it replaces.
        ex = "; ".join(f"{r}: '{l[:26]}' ~ '{o[:26]}' ({', '.join(n[:2])[:60]})"
                       for r, l, o, n, _, _ in cues[:4])
        F.add("shared-evidence-review", f"{len(cues)} pair(s)",
              f"{len(cues)} passage pairs rest on the same specific names — e.g. {ex}"
              + (" …" if len(cues) > 4 else "") + where
              + ". NOT a duplicate verdict, and it is not one at any threshold: one "
              "assertion stated twice and one piece of evidence supporting two claims "
              "look identical from the outside, and this skill's own bases re-cite the "
              "same source lines across cards deliberately. Measured on a real "
              "package: 4 of 10 candidate pairs were true duplicates; the scaffolding "
              "and bare-number filters removed four of the six that were not, and the "
              "list that survives is roughly four in ten real. Read them; spend the "
              "effort on the ones that repeat a claim.",
              "for each pair that states one claim: merge with both provenances kept as "
              "evidence; for each that shares evidence only: confirm the owner is named "
              "and leave it")


def file_graph(kb: str, files: list[str], F: Findings) -> None:
    docs = md_docs(files)
    if not docs:
        F.not_applicable("file-graph", "no markdown documents")
        return
    index = read(os.path.join(kb, "INDEX.md"))
    from_index = set()
    for m in re.finditer(r"\]\(([^)#\s]+)", index):
        from_index.add(os.path.normpath(os.path.join(kb, m.group(1))).replace("\\", "/"))
    inbound: dict[str, int] = {f: 0 for f in docs}
    broken = []
    for rel in docs:
        base = os.path.dirname(rel)
        for m in re.finditer(r"\]\(([^)#\s]+)(?:#[^)]*)?\)",
                             read(os.path.join(kb, rel))):
            tgt = m.group(1)
            if re.match(r"(?i)^https?://|^mailto:", tgt):
                continue
            resolved = os.path.normpath(os.path.join(kb, base, tgt)).replace("\\", "/")
            if not os.path.exists(resolved):
                broken.append(f"{rel} -> {tgt}")
            else:
                r = os.path.relpath(resolved, kb).replace("\\", "/")
                if r == rel:
                    continue
                if r in inbound:
                    inbound[r] += 1
                elif os.path.isdir(resolved):
                    # Routing to `provenance/fold/` reaches whatever is inside it.
                    # Counting only file-to-file links calls a routed folder an orphan.
                    for k in inbound:
                        if k.startswith(r + "/"):
                            inbound[k] += 1
    if broken:
        F.add("broken-internal-links", f"{len(broken)} link(s)",
              "; ".join(broken[:6]) + (" …" if len(broken) > 6 else ""),
              "fix the path, or the file it should point at")
    # working material is not meant to be linked; published audit files are
    for f, n in sorted(inbound.items()):
        if n or f in ("INDEX.md", "README.md"):
            continue
        if is_cache(os.path.dirname(f)):
            continue
        leaf = os.path.basename(f)
        if f in from_index:
            continue          # linked from the entry point: reachable
        if leaf.lower() in index.lower():
            F.add("unlinked-but-named", f,
                  "the INDEX names this file in its Layout text yet links nothing to it, so "
                  "a consumer that navigates by following links — which is how an agent "
                  "moves through a package — never arrives. Describing a file is not "
                  "routing to it.",
                  "link it from the INDEX route table or from the knowledge file that "
                  "depends on it")
        else:
            F.add("orphan-file", f,
                  "nothing links here and the INDEX never names it",
                  "link it from its nearest sibling, or state why it stands alone")


def blocks(path: str) -> list[tuple[str, str]]:
    """Paragraph-level blocks, each labelled with the nearest heading above it.

    Splitting only on headings made a duplicated paragraph invisible: paste a
    paragraph back in without a heading and it merges with its neighbour, so there
    is no pair left to compare — which is the exact defect this function exists to
    find. Blank lines end a block; contiguous table rows stay one block.
    """
    text = read(path)
    out: list[tuple[str, str]] = []
    cur: list[str] = []
    label = "head"
    kind: str | None = None

    def flush() -> None:
        nonlocal cur, kind
        body = "".join(cur).strip()
        if len(body) > 40:
            out.append((label, body))
        cur, kind = [], kind

    for raw in text.split("\n"):
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush()
            continue
        if line.startswith("#"):
            flush()
            label = s.lstrip("# ").strip()[:58]
            cur, kind = [line + "\n"], "head"
            continue
        if s.startswith("|"):
            if kind != "table":
                flush()
                kind = "table"
            cur.append(line + "\n")
            continue
        if re.match(r"^([-*]\s+\*\*|\d+\.\s+\*\*)", s):
            flush()
            label = re.sub(r"[#*|`]", "", s).strip()[:58]
            cur, kind = [line + "\n"], "item"
            continue
        if kind not in ("para", None):
            flush()
        kind = "para"
        cur.append(line + "\n")
    flush()
    return [(l, b) for l, b in out if len(normalize(b)) > 160]


# --------------------------------------------------------------------------
# 2. quotes
# --------------------------------------------------------------------------

def check_quotes(kb: str, source: str | None, F: Findings, out: str, verbose: bool) -> None:
    if not source:
        F.not_applicable("quote-audit",
                         "no --source run given: quotes can only be audited against "
                         "the corpus they came from, never against memory")
        return
    if not os.path.isdir(source):
        F.add("source-missing", source, "the --source path is not a directory",
              "point it at the mining run the base was smelted from")
        return
    cards, prim = {}, {}
    for dirpath, dirnames, filenames in os.walk(source):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        rel_dir = os.path.relpath(dirpath, source).replace("\\", "/")
        for fn in filenames:
            if not fn.lower().endswith((".md", ".txt", ".json", ".csv", ".tsv", ".html",
                                        ".yaml", ".yml")):
                continue
            p = os.path.join(dirpath, fn)
            if os.path.getsize(p) > 12_000_000:
                continue
            rel = f"{rel_dir}/{fn}" if rel_dir != "." else fn
            t = normalize(read(p))
            if rel.startswith(("experience/", "distillation/", "plan/")):
                cards[rel] = t
            else:
                prim[rel] = t
    if not prim:
        F.add("no-primary-cache", source,
              f"the source run holds no non-card artifacts ({len(cards)} card files): "
              "every quote would match only the run's own prose, which proves the run "
              "wrote it consistently, not that a source said it",
              "smelt a run that cached its fetched bytes, or state the limit in the ledger")
    allprim = " ".join(prim.values())
    allcards = " ".join(cards.values())
    span = re.compile(r'"([^"]{40,320})"')
    tot = hp = hc = miss = 0
    unmatched: list[dict] = []
    for rel in md_docs(walk_files(kb)):
        text = read(os.path.join(kb, rel))
        for q in span.findall(text):
            if any(x in q for x in ("[?", "|", "**", "\n", "`")):
                continue
            nq = normalize(q)
            if len(nq) < 30:
                continue
            tot += 1
            if nq in allprim:
                hp += 1
            elif nq in allcards:
                hc += 1
            else:
                miss += 1
                unmatched.append({"file": rel, "quote": q[:300]})
    if not tot:
        F.not_applicable("quote-audit", "no quoted spans of 40+ characters found")
        return
    pct = 100.0 * (hp + hc) / tot
    print(f"\n  quotations: {tot} spans | {hp} in cached primary bytes | "
          f"{hc} in the run's own prose | {miss} found nowhere | {pct:.1f}% located")
    os.makedirs(out, exist_ok=True)
    jp = os.path.join(out, "quote_audit.json")
    json.dump({"total": tot, "in_primary": hp, "in_run_prose": hc, "unmatched": miss,
               "located_pct": round(pct, 2), "spans_unmatched": unmatched},
              io.open(jp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"  unmatched spans written for examination (not counting): {jp}")
    if miss:
        F.add("quotes-unlocated", f"{miss} of {tot} spans",
              "these quoted spans appear in neither the cached primary bytes nor the "
              "run's own prose. Most are usually the writer's scare quotes or a span "
              "taken between two quotation marks — but 'most' is a hypothesis, and a "
              "fabricated quotation is the one defect that poisons an otherwise sound "
              "base, so each needs an answer, not a percentage.",
              "examine every unlocated span and record which kind it is; a real "
              "quotation must be repaired or downgraded to paraphrase")
    if hp == 0 and hc:
        F.add("quotes-checked-against-prose-only", "quote audit",
              f"all {hc} located spans matched the run's own writing rather than cached "
              "primary bytes — which is consistency, not corroboration",
              "state the denominator honestly in the ledger")


# --------------------------------------------------------------------------
# 3. links
# --------------------------------------------------------------------------

URL_PAT = re.compile(r"https?://[^\s<>{}\[\]\"'`|)+]+", re.I)
BAD_URL = re.compile(r"[\u2026\u2013\u2014\u00a0]|\s")
# Whole-label placeholder hosts. Matched against the host, never as a substring:
# a first pass rejected `use-the-index-luke.com` — a load-bearing source in the very
# corpus this tool audits — for containing the word "the" inside its hostname.
PLACEHOLDER_HOST = re.compile(
    r"^(?:my|mr|the|a|an|some|this|that)?[-_]?(?:url|uri|host|domain|path|file|example|"
    r"placeholder|invalid|test\d*)$", re.I)


def reject_reason(u: str) -> str | None:
    """Why this string cannot be an address, or None to go and ask it."""
    if BAD_URL.search(u):
        return "contains characters no address carries (an ellipsis, a dash, whitespace)"
    try:
        p = urllib.parse.urlsplit(u)
    except ValueError as e:
        return f"unparseable: {e}"
    host = (p.netloc or "").rsplit("@", 1)[-1].split(":")[0]
    if p.scheme.lower() not in ("http", "https"):
        return f"scheme {p.scheme!r} is not something to fetch"
    if not host or "." not in host:
        return f"host has no dot ({host!r})"
    # No label-length rule. `127.0.0.1` and `1.1.1.1` are addresses, and a shape test
    # that calls them suspicious drops exactly the citations nobody notices are gone.
    if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", host):
        return None
    return None


def looks_placeholder(u: str) -> bool:
    host = (urllib.parse.urlsplit(u).netloc or "").rsplit("@", 1)[-1].split(":")[0]
    return any(PLACEHOLDER_HOST.match(l) for l in host.split("."))


def human_bytes(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.0f}{u}" if u == "B" else f"{n:.1f}{u}"
        n /= 1024.0
    return f"{n:.1f}TB"


def count_in_tree(files: list[str], d: str) -> int:
    return len([f for f in files if f.startswith(d + "/")])


def size_in_tree(kb: str, d: str) -> int:
    t = 0
    for dirpath, _, fns in os.walk(os.path.join(kb, d)):
        for fn in fns:
            try:
                t += os.path.getsize(os.path.join(dirpath, fn))
            except OSError:
                pass
    return t


def section(text: str, name: str) -> str | None:
    m = re.search(rf"^#+\s*{re.escape(name)}\s*$(.*?)(?=^#+\s|\Z)", text, re.M | re.S | re.I)
    return m.group(1) if m else None


def short_dist(d: dict, n: int = 4) -> str:
    items = sorted(d.items(), key=lambda x: -x[1])[:n]
    return "{" + ", ".join(f"{k!r}:{v}" for k, v in items) + "}"


def collect_urls(kb: str, files: list[str]) -> dict[str, set]:
    where: dict[str, set] = {}
    for rel in md_docs(files):
        for u in URL_PAT.findall(read(os.path.join(kb, rel))):
            u = u.rstrip(".,;:!?'")
            where.setdefault(u, set()).add(rel)
    return where


def check_links(kb: str, F: Findings, out: str, sweep: bool, workers: int,
                timeout: int, limit: int, keep_bytes: bool) -> None:
    urls = collect_urls(kb, walk_files(kb))
    if not urls:
        F.not_applicable("link-sweep", "no http(s) URLs anywhere in the package")
        return
    os.makedirs(out, exist_ok=True)
    rejected: dict[str, str] = {}
    clean: dict[str, set] = {}
    for u, w in urls.items():
        why = reject_reason(u)
        if why:
            rejected[u] = why
        else:
            clean[u] = w
    placeholders = sorted(u for u in clean if looks_placeholder(u))
    if rejected:
        F.add("non-addresses-in-the-inventory", f"{len(rejected)} of {len(urls)} candidates",
              "a URL regex also catches prose that names an address in passing, and each "
              "of these was then counted as a citation and swept as if it could answer: "
              + "; ".join(f"{u!r} — {w}" for u, w in list(rejected.items())[:5])
              + (" …" if len(rejected) > 5 else "")
              + ". The denominator a ledger reports is then not the number of citations "
              "the corpus makes.",
              "validate before counting; report the swept total as candidates minus "
              "rejected, and keep the rejections visible rather than deleting them")
    if placeholders:
        F.add("placeholder-looking-hosts-swept-anyway", f"{len(placeholders)} URL(s)",
              "these hosts look like a template or a stub (" + ", ".join(
                  p[:52] for p in placeholders[:3]) + "), but a hostname that merely "
              "reads oddly is not evidence of a bad citation, so they were kept in the "
              "sweep rather than dropped: the answer comes from the request, not from a "
              "guess about the name.",
              "confirm by hand whether the corpus cited a real page or an unfilled example")
    print(f"\n  URL candidates: {len(urls)} | rejected as non-addresses: {len(rejected)} "
          f"| to check: {min(len(clean), limit or len(clean))}")
    if not sweep:
        F.not_applicable("link-status",
                         "inventory only: pass --sweep to make live requests. "
                         "A status is never inferred from a previous run's file")
        json.dump({"candidates": len(urls), "rejected": rejected,
                   "placeholder_hosts": placeholders, "clean": sorted(clean)},
                  io.open(os.path.join(out, "url_inventory.json"), "w",
                          encoding="utf-8"), indent=1)
        return
    targets = sorted(clean)[:limit] if limit else sorted(clean)
    t0 = time.time()
    rows = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(probe, u, timeout, keep_bytes, out): u for u in targets}
        for i, fu in enumerate(cf.as_completed(futs), 1):
            rows.append(fu.result())
    rows.sort(key=lambda r: r["url"])
    jp = os.path.join(out, "links_checked.json")
    json.dump(rows, io.open(jp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    elapsed = time.time() - t0
    stat: dict[str, int] = {}
    for r in rows:
        k = r["tool_error"] or (str(r["status"]) if r["status"] else "ERR")
        stat[k] = stat.get(k, 0) + 1
    print(f"  checked {len(rows)} in {elapsed:.0f}s ({len(targets) / max(elapsed, .001):.1f}"
          f"/s, {workers} workers) -> {jp}")
    print("  outcomes:", ", ".join(f"{k}={v}" for k, v in sorted(
        stat.items(), key=lambda x: -x[1])))
    live200 = [r for r in rows if r["status"] == 200]
    moved = [r for r in live200 if r["final_url"] and same_host(r["url"], r["final_url"])
             and r["url"].rstrip("/") != r["final_url"].rstrip("/")]
    offsite = [r for r in live200 if r["final_url"] and not same_host(r["url"], r["final_url"])]
    if offsite:
        F.add("redirect-offsite-unrecorded", f"{len(offsite)} URL(s)",
              "these answered 200 at a *different host* than cited. A 200 is not the "
              "citation holding: it can mean the site moved, or that the path now lands "
              "on a homepage, a search page, or a marketing page that merely mentions the "
              "topic. The chain is recorded per row in the JSON.",
              "for each, say in the ledger whether the destination still documents the "
              "claim it supports")
    if moved:
        F.add("redirect-same-host", f"{len(moved)} URL(s)",
              f"{len(moved)} citations resolved to a different path on the same host "
              "(recorded with the full chain). Usually benign, occasionally a "
              "deprecated-version redirect.",
              "spot-check the ones carrying load-bearing claims")
    dead = [r for r in rows if r["status"] in (404, 410) and not r.get("wayback_url")]
    if dead:
        F.add("dead-without-archive-attempt", f"{len(dead)} URL(s)",
              "404/410 with no archive lookup recorded. Recovery is cheap to try and "
              "changing: a recovered citation keeps a claim's grade, an unrecovered one "
              "must lower it and write a gap.",
              "run with --archive, or record 'no snapshot exists' as the attempt")
    toolerr = [r for r in rows if r["tool_error"]]
    if toolerr:
        F.add("tool-errors-recorded", f"{len(toolerr)} URL(s)",
              "reported as their own class, never folded into 'dead' or 'unreachable': "
              + "; ".join(f"{r['url'][:60]} ({r['tool_error'][:40]})" for r in toolerr[:4]) +
              ". A checker that cannot encode an address, or that died on its own "
              "exception, has told you something about itself — not about the source.",
              "fix the extractor for these and re-check; do not classify them as source "
              "conditions")
    if not keep_bytes:
        F.add("status-only-verification", "sweep depth",
              "this sweep recorded transport status only — it never compared the page's "
              "content to the claim the citation supports, so a soft-404, a cookie wall, "
              "or a page that merely mentions the topic all read as alive. "
              "Re-run with --content and --save-bytes if any claim here is load-bearing.",
              "state the depth in the ledger: 'checked: HTTP status, N URLs, content not "
              "compared' is a reach line, and a reach line is expected, not an apology")


def same_host(a: str, b: str) -> bool:
    return (urllib.parse.urlsplit(a).netloc or "").lower().removeprefix(
        "www.") == (urllib.parse.urlsplit(b).netloc or "").lower().removeprefix("www.")


MAX_HOPS = 6


def _no_redirect_opener():
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    return urllib.request.build_opener(NoRedirect)


def probe(url: str, timeout: int, keep_bytes: bool, out: str) -> dict:
    """Ask one address, following redirects by hand so every hop is recorded.

    urlopen swallows 301/302 silently, which leaves `chain` empty and the moved
    destination as the only trace that a citation resolves elsewhere now. The hop
    list is what a reader needs in order to judge whether the far end still supports
    the claim, so the chain is walked explicitly and written down.
    """
    row = {"url": url, "status": None, "final_url": url, "chain": [], "method": None,
           "tool_error": None, "err": None, "bytes": 0, "title": None,
           "wayback_url": None, "wayback_ts": None, "checked": time.strftime("%Y-%m-%d")}
    opener = _no_redirect_opener()
    # HEAD is skipped when bytes were asked for: it answers 200 with no body, so the
    # walk would stop there and --save-bytes would silently retain nothing.
    for method in (("GET",) if keep_bytes else ("HEAD", "GET")):
        cur, hops = url, 0
        row["chain"] = []          # one clean walk per method, never HEAD's hops plus GET's
        while hops < MAX_HOPS:
            try:
                req = urllib.request.Request(cur, headers=UA, method=method)
                with opener.open(req, timeout=timeout) as r:
                    body = r.read(400_000) if method == "GET" else b""
                    row.update(status=r.status, final_url=cur, method=method,
                               bytes=len(body),
                               title=first_title(body) if body else None)
                    if keep_bytes and body:
                        save_receipt(out, url, body, r.headers)
                    return row
            except urllib.error.HTTPError as e:
                if e.code in (301, 302, 303, 307, 308):
                    loc = e.headers.get("Location", "")
                    nxt = urllib.parse.urljoin(cur, loc) if loc else None
                    row["chain"].append({"from": cur, "to": nxt, "code": e.code})
                    row.update(status=f"{e.code} redirect", final_url=cur, method=method)
                    if not nxt:
                        return row
                    cur, hops = nxt, hops + 1
                    continue
                if method == "HEAD" and e.code in (404, 410, 403, 405, 429, 500, 501):
                    break              # a HEAD answer is not evidence about the page
                row.update(status=e.code, final_url=cur, method=method)
                return row
            except UnicodeError as e:
                row["tool_error"] = f"checker cannot encode this address: {e}"
                return row
            except Exception as e:
                # classify on the whole message; the display string is shortened after,
                # or "[WinError 10061] No connection could be made ... actively refused"
                # is cut before the word that says whose fault it is
                full = f"{type(e).__name__}: {e}"
                row["err"] = full[:90]
                row["_full"] = full
                row["method"] = method
                break
    if row["chain"] and isinstance(row["status"], str):
        return row        # still redirecting after MAX_HOPS: the chain is itself the answer
    if not row["status"]:
        low = (row.get("_full") or row["err"] or "").lower()
        row["tool_error"] = (None if any(x in low for x in
                                         ("getaddrinfo", "name or service", "11001",
                                          "no such host")) else
                             (row["err"] if any(x in low for x in
                                                ("ssl", "certificate", "timeout",
                                                 "timed out", "unreachable", "refused"))
                              else f"unclassified tool failure: {row['err']}"))
    return row


def first_title(body: bytes) -> str | None:
    try:
        t = body.decode("utf-8", "replace")
    except Exception:
        return None
    m = re.search(r"(?is)<title[^>]*>(.{0,180}?)</title>", t)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def save_receipt(out: str, url: str, body: bytes, headers) -> None:
    d = os.path.join(out, "receipts")
    os.makedirs(d, exist_ok=True)
    key = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    with io.open(os.path.join(d, key + ".http"), "w", encoding="utf-8") as fh:
        fh.write(f"url: {url}\nchecked: {time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        fh.write(f"status/headers:\n{headers}\n")
    with open(os.path.join(d, key + ".body"), "wb") as fh:
        fh.write(body)


def check_archive(kb: str, out: str, F: Findings, workers: int, timeout: int) -> None:
    lp = os.path.join(out, "links_checked.json")
    if not os.path.exists(lp):
        F.add("archive-lookup-blocked", lp,
              "no sweep output to attach snapshots to — run 'links --sweep' first")
        return
    rows = json.load(io.open(lp, encoding="utf-8"))
    todo = [r for r in rows if isinstance(r.get("status"), int) and r["status"] >= 400
            and not r.get("wayback_url")]
    print(f"\n  archive lookups: {len(todo)} dead/blocked URL(s)")
    if not todo:
        return

    def avail(u):
        try:
            q = "https://archive.org/wayback/available?url=" + urllib.parse.quote(u, safe="")
            with urllib.request.urlopen(urllib.request.Request(q, headers=UA),
                                        timeout=timeout) as r:
                j = json.loads(r.read().decode("utf-8", "replace"))
            s = (j.get("archived_snapshots") or {}).get("closest") or {}
            return s.get("timestamp"), s.get("url")
        except Exception:
            return None, None

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        res = dict(zip([r["url"] for r in todo],
                       ex.map(lambda r: avail(r["url"]), todo)))
    hit = 0
    for r in rows:
        ts, u = res.get(r["url"], (None, None))
        if u:
            r["wayback_ts"], r["wayback_url"] = ts, u
            hit += 1
    json.dump(rows, io.open(lp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"  snapshots found: {hit}/{len(todo)}")
    if hit < len(todo):
        F.add("dead-unrecoverable", f"{len(todo) - hit} URL(s)",
              "no archive snapshot either. Per the skill these stay in the ledger as "
              "dead — the unreachable citation is knowledge about the corpus — and each "
              "claim they supported gets its provenance downgraded at the citation point.")


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="smelt package checker (measures; the "
                                             "agent judges)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("package", "quotes", "links", "all"):
        p = sub.add_parser(name)
        p.add_argument("kb", help="the smelted knowledge base directory")
        p.add_argument("--source", help="the mining run it was smelted from")
        p.add_argument("--out", help="where artifacts land (default <kb>/.smelt-check)")
        p.add_argument("--waivers", help="JSON [{id, reason}] for findings kept open")
        p.add_argument("--json", action="store_true", help="machine-readable output")
        p.add_argument("--verbose", "-v", action="store_true")
        if name in ("links", "all"):
            p.add_argument("--sweep", action="store_true",
                           help="make live requests (off by default: never hit N hosts "
                                "without being asked)")
            p.add_argument("--archive", action="store_true",
                           help="look up an Internet Archive snapshot for every dead row")
            p.add_argument("--content", action="store_true",
                           help="fetch and keep the body so identity can be compared")
            p.add_argument("--save-bytes", action="store_true",
                           help="retain the raw bytes as receipts next to the ledger")
            p.add_argument("--workers", type=int, default=12)
            p.add_argument("--timeout", type=int, default=20)
            p.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(argv)
    kb = os.path.abspath(a.kb)
    if not os.path.isdir(kb):
        print(f"not a directory: {kb}", file=sys.stderr)
        return 2
    out = a.out or os.path.join(kb, ".smelt-check")
    F = Findings()
    if a.cmd in ("package", "all"):
        check_package(kb, F, a.verbose, out)
        F.report("package " + os.path.basename(kb), a.verbose)
    if a.cmd in ("quotes", "all"):
        q = Findings()
        check_quotes(kb, a.source, q, out, a.verbose)
        q.report("quote audit", a.verbose)
        F.items += q.items
        F.na += q.na
    if a.cmd == "links" or (a.cmd == "all" and getattr(a, "sweep", False)):
        L = Findings()
        check_links(kb, L, out, a.sweep, a.workers, a.timeout, a.limit,
                    a.save_bytes or a.content)
        if getattr(a, "archive", False):
            check_archive(kb, out, L, a.workers, a.timeout)
        L.report("links", a.verbose)
        F.items += L.items
        F.na += L.na
    F.merge_waivers(a.waivers)
    if a.json:
        print(json.dumps({"findings": F.items, "not_applicable": F.na},
                         indent=1, ensure_ascii=False))
    os.makedirs(out, exist_ok=True)
    json.dump({"findings": F.items, "not_applicable": F.na},
              io.open(os.path.join(out, "findings.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
