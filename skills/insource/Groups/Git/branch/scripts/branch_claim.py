#!/usr/bin/env python3
"""branch_claim.py - session-scoped branch claims for agents sharing one repository.

Deterministic mechanics only: it records who acquired which branch, refuses to clobber another
holder's claim, and answers "what should the next acquirer do". It decides nothing about strategy.

Two things are written, on purpose:

  <common git dir>/agent-branch   human-readable ledger: the collision policy + one block per claim
  refs/agent/<slug>               an atomic claim, created with `git update-ref <ref> <oid> <zeros>`
                                  which git rejects if the ref already exists

The ref is the truth (atomic, shared by every worktree, visible to `git for-each-ref`); the file is the
explanation. A session that edits the file without the ref, or vice versa, is reported as inconsistent
rather than trusted.

Usage:
  python branch_claim.py acquire --branch feature/x [--role NAME] [--worktree PATH] [--ttl 4h] [--note TEXT]
  python branch_claim.py status [--json]
  python branch_claim.py check --branch feature/x          # exit 0 free, 3 held, 4 mine, 5 stale
  python branch_claim.py renew --branch feature/x [--ttl 4h]
  python branch_claim.py release --branch feature/x [--role NAME]
  python branch_claim.py policy [--collision no-steal|take-next] [--scope TEXT] [--ttl 4h]
  python branch_claim.py takeover --branch feature/x --role NAME --reason TEXT   # explicit, records the act
  python branch_claim.py                                            # self-test (temp git repos)

Exit codes: 0 ok · 1 error · 2 usage · 3 held-by-another · 4 stale claim exists · 5 already mine
stdout is ASCII.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime
import io
import json
import os
import re
import subprocess
import sys
import tempfile

LEDGER = "agent-branch"
REF_PREFIX = "refs/agent/"
ZERO = "0" * 40
DEFAULT_TTL_H = 4
VALID_COLLISION = ("no-steal", "take-next", "ask")


def emit(text=""):
    enc = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        text.encode(enc)
        print(text)
    except UnicodeEncodeError:
        print(text.encode(enc, "backslashreplace").decode(enc, "strict"))


def git(*args, **kw):
    """Run git in the target repo; returns CompletedProcess (never raises on non-zero)."""
    return subprocess.run(("git",) + tuple(args), capture_output=True, text=True,
                          errors="replace", **kw)


def _abs(base, value):
    """git may print a relative path (`.git`); resolve it against the repo, not the process cwd."""
    value = value.strip()
    if not value:
        return None
    return value if os.path.isabs(value) else os.path.abspath(os.path.join(base or os.getcwd(), value))


def dirs(cwd=None):
    """(common_dir, top_level) resolved through git, so linked worktrees share the ledger."""
    common = git("rev-parse", "--git-common-dir", cwd=cwd)
    top = git("rev-parse", "--show-toplevel", cwd=cwd)
    if common.returncode != 0 or top.returncode != 0:
        return None, None
    base = cwd or os.getcwd()
    return _abs(base, common.stdout), _abs(base, top.stdout)


def slug(branch):
    return re.sub(r"[^a-z0-9]+", "-", branch.lower()).strip("-")


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def parse_ttl(text):
    m = re.fullmatch(r"(\d+)\s*([hmd]?)", (text or "").strip().lower())
    if not m:
        raise ValueError("ttl must look like 90m, 4h, or 2d")
    n, unit = int(m.group(1)), (m.group(2) or "h")
    return datetime.timedelta(**{"hours": n} if unit == "h" else
                              {"minutes": n} if unit == "m" else {"days": n})


def stamp(dt=None):
    return (dt or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


# ----------------------------------------------------------------- ledger io

def read_ledger(path):
    """Return {'policy': {...}, 'claims': [ {...}, ... ]}; a missing file is an empty ledger."""
    out = {"policy": {}, "claims": []}
    if not os.path.exists(path):
        return out
    section = None
    cur = None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if line.strip() == "policy:":
                section, cur = "policy", None
                continue
            if line.strip() == "claims:":
                section = "claims"
                continue
            if section == "policy":
                k, _, v = line.strip().partition(":")
                if _:
                    out["policy"][k.strip()] = v.strip()
                continue
            if section == "claims":
                if line.startswith("  - branch:") or line.startswith("- branch:"):
                    cur = {"branch": line.split(":", 1)[1].strip()}
                    out["claims"].append(cur)
                elif line.startswith("    ") and cur is not None:
                    k, _, v = line.strip().partition(":")
                    if _:
                        cur[k.strip()] = v.strip()
    return out


def write_ledger(path, data):
    lines = ["# agent-branch: session-scoped branch claims (NOT project policy)",
             "# policy: what this session acquired and what another acquirer must do",
             "# project-lifecycle strategy belongs in AGENTS.md, not here", "policy:"]
    for key in ("collision", "ttl", "scope", "updated"):
        if data["policy"].get(key):
            lines.append("  %s: %s" % (key, data["policy"][key]))
    lines.append("claims:")
    if not data["claims"]:
        lines.append("  (none)")
    for claim in data["claims"]:
        first = True
        for key in ("branch", "owner", "worktree", "pid", "acquired", "ttl", "expires", "ref", "note"):
            value = claim.get(key)
            if value in (None, ""):
                continue
            lines.append(("  - " if first else "    ") + "%s: %s" % (key, value))
            first = False
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    os.replace(tmp, path)


def find_claim(data, branch):
    for claim in data["claims"]:
        if claim.get("branch") == branch:
            return claim
    return None


def refs_state(cwd):
    """Map slug -> (ref, oid) for every refs/agent/* claim."""
    state = {}
    r = git("for-each-ref", "--format=%(refname) %(objectname)", REF_PREFIX, cwd=cwd)
    for line in r.stdout.splitlines():
        ref, _, oid = line.partition(" ")
        if ref:
            state[ref[len(REF_PREFIX):]] = (ref, oid.strip())
    return state


def age_minutes(claim):
    try:
        acquired = datetime.datetime.strptime(claim["acquired"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
    except (KeyError, ValueError):
        return None
    ttl = claim.get("ttl") or "%dh" % DEFAULT_TTL_H
    try:
        window = parse_ttl(ttl)
    except ValueError:
        return None
    return (now() - (acquired + window)).total_seconds() / 60.0


def is_stale(claim):
    minutes = age_minutes(claim)
    return minutes is not None and minutes > 0


def this_session(role):
    return (role or os.environ.get("AGENT_ROLE") or os.environ.get("SESSION_NAME")
            or "pid-%d" % os.getpid())


# ----------------------------------------------------------------- commands

def cmd_acquire(args):
    common, _ = dirs(args.cwd)
    if not common:
        emit("ERROR: not a git repository (or git unavailable)")
        return 1
    path = os.path.join(common, LEDGER)
    data = read_ledger(path)
    refs = refs_state(args.cwd)
    mine = this_session(args.role)

    existing = find_claim(data, args.branch)
    ref = REF_PREFIX + slug(args.branch)
    ref_taken = slug(args.branch) in refs

    if existing or ref_taken:
        holder = (existing or {}).get("owner") or "ref:%s" % refs.get(slug(args.branch), ("", "?"))[1][:8]
        if existing and existing.get("owner") == mine and not ref_taken:
            emit("NOTE: ledger says %s is mine but the claim ref is missing; recreating it" % args.branch)
        elif existing and existing.get("owner") == mine:
            emit("ALREADY MINE: %s (owner %s)" % (args.branch, mine))
            return 5
        elif existing and is_stale(existing):
            emit("STALE: %s held by %s, expired %s ago" % (args.branch, existing.get("owner"),
                                                            existing.get("ttl")))
            emit("       refusing to take it. Either: renew it with its owner, choose another branch name,")
            emit("       or run takeover with a reason if you are that owner's session and finished.")
            return 4
        else:
            policy = data["policy"].get("collision") or "no-steal"
            emit("HELD: %s by %s%s" % (args.branch, holder,
                                        " (policy: %s)" % policy if policy else ""))
            emit("      options: take a different branch name, split the scope, serialize with the holder,")
            emit("      or agree explicitly: branch_claim.py takeover --branch %s --role %s --reason '...'"
                 % (args.branch, mine))
            return 3

    head = git("rev-parse", "HEAD", cwd=args.cwd)
    if head.returncode != 0:
        emit("ERROR: cannot resolve HEAD (empty repository?)")
        return 1
    cas = git("update-ref", ref, head.stdout.strip(), ZERO, cwd=args.cwd)
    if cas.returncode != 0:
        # the ref appeared between the check and the create: another session won the race
        emit("HELD: claim ref %s already exists (%s)" % (ref, cas.stderr.strip().splitlines()[:1] or ["?"]))
        return 3
    try:
        ttl = parse_ttl(args.ttl or data["policy"].get("ttl") or "%dh" % DEFAULT_TTL_H)
    except ValueError as e:
        git("update-ref", "-d", ref, head.stdout.strip(), cwd=args.cwd)
        emit("ERROR: %s" % e)
        return 2
    claim = {"branch": args.branch, "owner": mine, "acquired": stamp(),
             "ttl": str(args.ttl or data["policy"].get("ttl") or "%dh" % DEFAULT_TTL_H),
             "expires": stamp(now() + ttl), "ref": ref, "pid": str(os.getpid())}
    if args.worktree:
        claim["worktree"] = _abs(args.cwd, args.worktree)
    if args.note:
        claim["note"] = args.note
    data["claims"].append(claim)
    data["policy"]["updated"] = stamp()
    write_ledger(path, data)
    emit("ACQUIRED %s by %s until %s" % (args.branch, mine, claim["expires"]))
    emit("  ref: %s @ %s" % (ref, head.stdout.strip()[:8]))
    if args.worktree:
        emit("  worktree: %s" % claim["worktree"])
    return 0


def cmd_status(args):
    common, _ = dirs(args.cwd)
    if not common:
        emit("ERROR: not a git repository")
        return 1
    data = read_ledger(os.path.join(common, LEDGER))
    refs = refs_state(args.cwd)
    rows = []
    for claim in data["claims"]:
        s = slug(claim["branch"])
        rows.append({
            "branch": claim["branch"], "owner": claim.get("owner", "?"),
            "acquired": claim.get("acquired", ""), "expires": claim.get("expires", "?"),
            "worktree": claim.get("worktree", ""), "state": "STALE" if is_stale(claim) else "ACTIVE",
            "ref": "present" if s in refs else "MISSING",
        })
    orphans = [ref for s, (ref, oid) in refs.items()
               if not any(slug(c["branch"]) == s for c in data["claims"])]
    if args.json:
        emit(json.dumps({"policy": data["policy"], "claims": rows, "orphan_refs": orphans}, indent=2))
        return 0
    if not rows and not orphans:
        emit("no claims recorded; no agent refs held")
        return 0
    emit("policy: %s" % (", ".join("%s=%s" % kv for kv in sorted(data["policy"].items())) or "unset"))
    emit("%-34s %-14s %-8s %-20s %-7s %s" % ("BRANCH", "OWNER", "STATE", "EXPIRES", "REF", "WORKTREE"))
    for r in rows:
        emit("%-34s %-14s %-8s %-20s %-7s %s"
             % (r["branch"][:34], str(r["owner"])[:14], r["state"], r["expires"], r["ref"], r["worktree"]))
    if orphans:
        emit("")
        emit("ORPHAN CLAIM REFS (ref exists, no ledger entry - a session died or edited the file):")
        for ref in orphans:
            emit("  %s" % ref)
    return 0


def cmd_check(args):
    common, _ = dirs(args.cwd)
    if not common:
        emit("ERROR: not a git repository")
        return 1
    data = read_ledger(os.path.join(common, LEDGER))
    claim = find_claim(data, args.branch)
    ref_taken = slug(args.branch) in refs_state(args.cwd)
    mine = this_session(args.role)
    if not claim and not ref_taken:
        emit("FREE %s" % args.branch)
        return 0
    if claim and claim.get("owner") == mine:
        emit("MINE %s (owner %s%s)" % (args.branch, mine, ", stale" if is_stale(claim) else ""))
        return 5
    if claim and is_stale(claim):
        emit("STALE %s held by %s" % (args.branch, claim.get("owner")))
        return 4
    emit("HELD %s by %s" % (args.branch, (claim or {}).get("owner") or "a claim ref"))
    return 3


def cmd_release(args):
    common, _ = dirs(args.cwd)
    if not common:
        emit("ERROR: not a git repository")
        return 1
    path = os.path.join(common, LEDGER)
    data = read_ledger(path)
    claim = find_claim(data, args.branch)
    if not claim:
        emit("nothing recorded for %s" % args.branch)
        return 1
    mine = args.role or claim.get("owner")
    if claim.get("owner") != mine and not args.force:
        emit("REFUSED: %s is held by %s, not %s (a session releases its own claims)"
             % (args.branch, claim.get("owner"), mine))
        return 3
    ref = claim.get("ref") or (REF_PREFIX + slug(args.branch))
    r = git("update-ref", "-d", ref, cwd=args.cwd)
    if r.returncode != 0:
        emit("WARNING: ledger entry removed but %s not deleted (%s)" % (ref, r.stderr.strip()[:120]))
    data["claims"] = [c for c in data["claims"] if c.get("branch") != args.branch]
    write_ledger(path, data)
    emit("RELEASED %s (was %s)" % (args.branch, claim.get("owner")))
    return 0


def cmd_renew(args):
    common, _ = dirs(args.cwd)
    if not common:
        return 1
    path = os.path.join(common, LEDGER)
    data = read_ledger(path)
    claim = find_claim(data, args.branch)
    if not claim:
        emit("nothing recorded for %s" % args.branch)
        return 1
    try:
        ttl = parse_ttl(args.ttl or claim.get("ttl") or "%dh" % DEFAULT_TTL_H)
    except ValueError as e:
        emit("ERROR: %s" % e)
        return 2
    claim["acquired"] = stamp()
    claim["ttl"] = args.ttl or claim.get("ttl") or "%dh" % DEFAULT_TTL_H
    claim["expires"] = stamp(now() + ttl)
    write_ledger(path, data)
    emit("RENEWED %s until %s" % (args.branch, claim["expires"]))
    return 0


def cmd_policy(args):
    common, _ = dirs(args.cwd)
    if not common:
        emit("ERROR: not a git repository")
        return 1
    path = os.path.join(common, LEDGER)
    data = read_ledger(path)
    if args.collision:
        if args.collision not in VALID_COLLISION:
            emit("ERROR: --collision must be one of %s" % ", ".join(VALID_COLLISION))
            return 2
        data["policy"]["collision"] = args.collision
    if args.ttl:
        try:
            parse_ttl(args.ttl)
        except ValueError as e:
            emit("ERROR: %s" % e)
            return 2
        data["policy"]["ttl"] = args.ttl
    if args.scope is not None:
        data["policy"]["scope"] = args.scope or "-"
    data["policy"]["updated"] = stamp()
    write_ledger(path, data)
    emit("POLICY: %s" % ", ".join("%s=%s" % kv for kv in sorted(data["policy"].items())))
    return 0


def cmd_takeover(args):
    """Explicit, recorded, and still refused without a reason: a takeover is a decision, not a cleanup."""
    if not args.reason:
        emit("ERROR: --reason is required (what you are taking over and why the holder is finished)")
        return 2
    common, _ = dirs(args.cwd)
    if not common:
        emit("ERROR: not a git repository")
        return 1
    path = os.path.join(common, LEDGER)
    data = read_ledger(path)
    claim = find_claim(data, args.branch)
    if claim and not is_stale(claim) and claim.get("owner") != this_session(args.role):
        emit("REFUSED: %s is an ACTIVE claim by %s (expires %s)." % (args.branch, claim.get("owner"),
                                                                     claim.get("expires")))
        emit("         Takeover of a live claim is not mechanical - agree with the holder or its operator,")
        emit("         then re-run. Meanwhile: different branch name, split scope, or serialize.")
        return 3
    if claim:
        data["claims"] = [c for c in data["claims"] if c.get("branch") != args.branch]
        old_ref = claim.get("ref") or (REF_PREFIX + slug(args.branch))
        r = git("rev-parse", "--verify", old_ref, cwd=args.cwd)
        if r.returncode == 0:
            git("update-ref", "-m", "takeover by %s: %s" % (this_session(args.role), args.reason),
                "-d", old_ref, r.stdout.strip(), cwd=args.cwd)
        write_ledger(path, data)
    emit("TAKEOVER accepted for %s; acquiring" % args.branch)
    args.role = this_session(args.role)
    args.note = "took over from prior holder: %s" % args.reason
    rc = cmd_acquire(args)
    if rc == 0:
        data = read_ledger(path)
        new = find_claim(data, args.branch)
        if new:
            new["note"] = "%s (taken over %s)" % (new.get("note", ""), stamp())
            write_ledger(path, data)
            emit("  takeover recorded in the ledger note")
    return rc


# ------------------------------------------------------------------ self-test

def _git_at(cwd, *args):
    r = git(*args, cwd=cwd)
    if r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr.strip()[:200]))
    return r.stdout


def sandbox():
    root = tempfile.mkdtemp(prefix="branch-claim-")
    repo = os.path.join(root, "repo")
    os.makedirs(repo)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    _git_at(repo, "init", "-q", ".")
    with open(os.path.join(repo, "f.txt"), "w") as fh:
        fh.write("x\n")
    _git_at(repo, "add", "f.txt")
    _git_at(repo, "commit", "-qm", "init")
    return repo, env


def selftest():
    checks = failed = 0

    def check(name, cond, detail=""):
        nonlocal checks, failed
        checks += 1
        emit("%-46s %s %s" % (name, "PASS" if cond else "FAIL", "" if cond else str(detail)[:150]))
        failed += 0 if cond else 1

    if git("--version").returncode != 0:
        emit("SKIP: git not available")
        return 0
    repo, env = sandbox()
    os.environ.update(env)
    a, b, c, d = "alpha", "beta", "gamma", "delta"
    try:
        rc = cmd_acquire(argparse.Namespace(branch=a, role="s1", worktree=None, ttl="4h", note="mine",
                                           cwd=repo, force=False))
        check("acquire succeeds and records", rc == 0)
        led = read_ledger(os.path.join(repo, ".git", LEDGER))
        check("ledger holds the claim with an owner",
              any(x["branch"] == a and x["owner"] == "s1" for x in led["claims"]))
        check("claim ref exists in git", slug(a) in refs_state(repo))
        rc2 = cmd_acquire(argparse.Namespace(branch=a, role="s2", worktree=None, ttl="4h", note=None,
                                             cwd=repo, force=False))
        check("second session cannot take a live claim", rc2 == 3)
        rc3 = cmd_acquire(argparse.Namespace(branch=a, role="s1", worktree=None, ttl="4h", note=None,
                                             cwd=repo, force=False))
        check("re-acquiring own claim is not an error path", rc3 == 5)
        rc4 = cmd_check(argparse.Namespace(branch=b, role=None, cwd=repo))
        check("unheld branch reports FREE", rc4 == 0)
        rc5 = cmd_check(argparse.Namespace(branch=a, role="s2", cwd=repo))
        check("held branch reports HELD", rc5 == 3)
        rc6 = cmd_takeover(argparse.Namespace(branch=a, role="s2", reason="", cwd=repo, worktree=None,
                                             ttl="4h", note=None, force=False))
        check("takeover without a reason is refused", rc6 == 2)
        rc7 = cmd_takeover(argparse.Namespace(branch=a, role="s2", reason="holder crashed mid-task",
                                              cwd=repo, worktree=None, ttl="4h", note=None, force=False))
        check("takeover of a live claim still refuses", rc7 == 3)
        led = read_ledger(os.path.join(repo, ".git", LEDGER))
        check("refused takeover left the claim intact",
              any(x["branch"] == a and x["owner"] == "s1" for x in led["claims"]))
        # a stale claim is reported as stale, not silently taken
        led["claims"][0]["acquired"] = stamp(now() - datetime.timedelta(hours=9))
        write_ledger(os.path.join(repo, ".git", LEDGER), led)
        rc8 = cmd_acquire(argparse.Namespace(branch=a, role="s3", worktree=None, ttl="4h", note=None,
                                             cwd=repo, force=False))
        check("expired claim reports STALE, never steals", rc8 == 4)
        rc9 = cmd_release(argparse.Namespace(branch=a, role="s2", cwd=repo, force=False))
        check("a session cannot release another's claim", rc9 == 3)
        rc10 = cmd_release(argparse.Namespace(branch=a, role="s1", cwd=repo, force=False))
        check("owner release clears ledger and ref",
              rc10 == 0 and slug(a) not in refs_state(repo)
              and not find_claim(read_ledger(os.path.join(repo, ".git", LEDGER)), a))
        rc11 = cmd_policy(argparse.Namespace(collision="take-next", ttl="2h", scope="no shared files",
                                             cwd=repo))
        pol = read_ledger(os.path.join(repo, ".git", LEDGER))["policy"]
        check("policy persists collision/ttl/scope",
              rc11 == 0 and pol.get("collision") == "take-next" and pol.get("ttl") == "2h")
        rc12 = cmd_policy(argparse.Namespace(collision="bogus", ttl=None, scope=None, cwd=repo))
        check("invalid collision value refused", rc12 == 2)
        cmd_acquire(argparse.Namespace(branch=c, role="s9", worktree=None, ttl="1h", note=None,
                                       cwd=repo, force=False))
        st = cmd_status(argparse.Namespace(cwd=repo, json=False))
        check("status lists active claims", st == 0)
        # orphan detection: ref exists with no ledger row (a session died or edited the file away)
        os.remove(os.path.join(repo, ".git", LEDGER))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            st2 = cmd_status(argparse.Namespace(cwd=repo, json=True))
        payload = json.loads(buf.getvalue()) if st2 == 0 else {}
        check("ledger loss is reported as orphan refs",
              any(slug(c) in ref for ref in payload.get("orphan_refs", []))
              and payload.get("claims") == [], buf.getvalue()[:120])
        check("acquire after ledger loss still creates the branch record",
              cmd_acquire(argparse.Namespace(branch=d, role="s1", worktree=None, ttl="4h", note=None,
                                            cwd=repo, force=False)) == 0)
        # linked worktree shares the common dir, hence the ledger
        wt = os.path.join(repo, "..", "wt1")
        _git_at(repo, "worktree", "add", "-q", "-B", "wt-branch", wt, "HEAD")
        common, top = dirs(wt)
        check("worktree resolves the same common git dir",
              os.path.samefile(common, os.path.join(repo, ".git")))
        cmd_release(argparse.Namespace(branch=d, role="s1", cwd=repo, force=False))
        rc_bad = cmd_acquire(argparse.Namespace(branch="x", role="r", worktree=None, ttl="4h", note=None,
                                                cwd=tempfile.mkdtemp(), force=False))
        check("non-repo directory is refused cleanly", rc_bad == 1)
        check("ttl parser rejects garbage", _ttl_rejects())
    finally:
        import shutil
        shutil.rmtree(repo, ignore_errors=True)

    emit("self-test: %d/%d checks passed" % (checks - failed, checks))
    return 0 if failed == 0 else 1


def _ttl_rejects():
    try:
        parse_ttl("soon")
        return False
    except ValueError:
        return True


# ------------------------------------------------------------------ entry

def main(argv=None):
    ap = argparse.ArgumentParser(prog="branch_claim")
    ap.add_argument("--cwd", default=None, help="run against this repository (default: current dir)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("acquire")
    a.add_argument("--branch", required=True)
    a.add_argument("--role")
    a.add_argument("--worktree")
    a.add_argument("--ttl")
    a.add_argument("--note")
    a.add_argument("--force", action="store_true")

    s = sub.add_parser("status")
    s.add_argument("--json", action="store_true")

    ch = sub.add_parser("check")
    ch.add_argument("--branch", required=True)
    ch.add_argument("--role")

    rn = sub.add_parser("renew")
    rn.add_argument("--branch", required=True)
    rn.add_argument("--ttl")

    rl = sub.add_parser("release")
    rl.add_argument("--branch", required=True)
    rl.add_argument("--role")
    rl.add_argument("--force", action="store_true")

    po = sub.add_parser("policy")
    po.add_argument("--collision")
    po.add_argument("--ttl")
    po.add_argument("--scope", default=None)

    tk = sub.add_parser("takeover")
    tk.add_argument("--branch", required=True)
    tk.add_argument("--role")
    tk.add_argument("--reason")
    tk.add_argument("--worktree")
    tk.add_argument("--ttl")
    tk.add_argument("--note")
    tk.add_argument("--force", action="store_true")

    args = ap.parse_args(argv)
    return {"acquire": cmd_acquire, "status": cmd_status, "check": cmd_check, "renew": cmd_renew,
            "release": cmd_release, "policy": cmd_policy, "takeover": cmd_takeover}[args.cmd](args)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(selftest())
    sys.exit(main())
