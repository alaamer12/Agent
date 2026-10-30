#!/usr/bin/env python3
"""bench_stats.py - iteration math, per-candidate statistics, and a paired-bootstrap verdict.

  python scripts/bench_stats.py --budget 300 --per-iteration 2.4      # how many iterations fit the budget
  python scripts/bench_stats.py --samples runs.csv --baseline fts5    # stats + verdict (markdown by default)
  python scripts/bench_stats.py --samples runs.csv --null like,like2  # noise floor from a same-impl pair
  python scripts/bench_stats.py --environment                        # snapshot block to paste into REPORT.md
  python scripts/bench_stats.py                                      # self-test

CSV needs a header with candidate,iteration,value (extra columns are ignored). Values are in whatever unit the
harness measured; this script never converts them. It computes facts - medians, spread, confidence intervals -
and states plainly when a run cannot rank two candidates. Exit 0 always except usage errors (2).
"""

import argparse
import csv
import datetime
import json
import os
import platform
import random
import statistics
import subprocess
import sys


# ------------------------------------------------------------------ budget math

def iteration_math(budget, per_iteration, warmup_frac, reserve_frac):
    """Split the wall-clock budget: reporting is not optional, so reserve it first."""
    if per_iteration <= 0:
        return "error: --per-iteration must be > 0", 2
    measure = budget * (1 - reserve_frac)
    n_total = int(measure // per_iteration)
    warm = int(n_total * warmup_frac)
    n = n_total - warm
    lines = [
        "budget %.0fs - per-iteration %.3fs - warmup %d%% - analysis/report reserve %d%%"
        % (budget, per_iteration, warmup_frac * 100, reserve_frac * 100),
        "time left for measuring: %.0fs" % measure,
        "iterations: %d total = %d warmup + %d measured" % (n_total, warm, n) if n_total else "iterations: 0",
    ]
    if n < 5:
        lines.append("verdict: too few iterations to rank candidates - raise the budget, shorten the workload,")
        lines.append("         or accept an inconclusive run and say so in the report")
    elif n < 20:
        lines.append("verdict: %d iterations supports roughly a %.0f%% gap claim; smaller differences are noise"
                     % (n, 100 * (2.5 / (n ** 0.5)) if n else 0))
    else:
        lines.append("verdict: %d iterations is enough for a few-percent claim, subject to the noise floor" % n)
    lines.append("reserve the last %.0fs for analysis and the write-up (do not spend it on iterations)"
                 % (budget * reserve_frac))
    return "\n".join(lines), 0


# ------------------------------------------------------------------ samples

def load_samples(path):
    rows = []
    if path.endswith(".json"):
        data = json.load(open(path, encoding="utf-8"))
        for r in data:
            rows.append((str(r["candidate"]), int(r.get("iteration", len(rows))), float(r["value"])))
        return rows
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        need = {"candidate", "iteration", "value"}
        if not rd.fieldnames or not need.issubset(set(rd.fieldnames)):
            raise ValueError("CSV header must contain candidate,iteration,value (got %r)" % rd.fieldnames)
        for r in rd:
            rows.append((r["candidate"].strip(), int(float(r["iteration"])), float(r["value"])))
    return rows


def stats_of(values):
    s = sorted(values)
    n = len(s)
    med = statistics.median(s)
    p95 = s[min(n - 1, int(round(0.95 * (n - 1))))]
    mad = statistics.median([abs(v - med) for v in s])
    mean = statistics.fmean(s)
    cv = (statistics.pstdev(s) / mean * 100) if mean and n > 1 else 0.0
    return {"n": n, "median": med, "mean": mean, "p95": p95, "min": s[0], "max": s[-1],
            "mad": mad, "cv": cv}


def paired_bootstrap(a, b, confidence=95.0, resamples=4000, seed=12345):
    """Ratio of medians (b/a) with a paired bootstrap CI: resample iteration indices, not loose values."""
    idx = [i for i in a if i in b]
    if len(idx) < 3:
        return None
    av = [a[i] for i in idx]
    bv = [b[i] for i in idx]
    rng = random.Random(seed)
    ratios = []
    for _ in range(resamples):
        pick = [rng.randrange(len(idx)) for _ in idx]
        sa = statistics.median([av[k] for k in pick])
        sb = statistics.median([bv[k] for k in pick])
        if sa:
            ratios.append(sb / sa)
    if not ratios:
        return None
    ratios.sort()
    lo = ratios[int(((100 - confidence) / 200) * len(ratios))]
    hi = ratios[int((1 - (100 - confidence) / 200) * len(ratios))]
    return {"ratio": statistics.median([sb / sa for sa, sb in zip(av, bv) if sa]),
            "ci": (lo, hi), "pairs": len(idx), "excludes_one": not (lo <= 1.0 <= hi)}


def fmt(v, unit=""):
    if v >= 1000:
        return "%.4g%s" % (v, unit)
    return "%.4g%s" % (v, unit)


def report(rows, baseline, confidence, noise_pairs=None):
    by = {}
    for cand, it, val in rows:
        by.setdefault(cand, {})[it] = val
    names = list(by)
    if baseline and baseline not in by:
        return "error: --baseline %r not among candidates %s" % (baseline, names), 2

    table = {n: stats_of(list(v.values())) for n, v in by.items()}
    lines = []
    noise = None
    if noise_pairs and len(noise_pairs) == 2 and all(p in by for p in noise_pairs):
        bs = paired_bootstrap(by[noise_pairs[0]], by[noise_pairs[1]], confidence)
        if bs:
            noise = abs(bs["ratio"] - 1.0)
            lines.append("noise floor (%s vs %s, same implementation): %.2f%% ratio spread at %d%% confidence"
                         % (noise_pairs[0], noise_pairs[1], noise * 100, confidence))
    if baseline:
        for n in names:
            if n == baseline:
                continue
            bs = paired_bootstrap(by[baseline], by[n], confidence)
            if not bs:
                lines.append("%s vs %s: cannot pair (need the same iteration indices in both)" % (baseline, n))
                continue
            verdict = "real difference" if bs["excludes_one"] else "INSIDE NOISE - inconclusive"
            if noise is not None and bs["excludes_one"] and noise > abs(bs["ratio"] - 1.0) / 2:
                verdict = "weak: gap is only ~%.1fx the noise floor" % ((abs(bs["ratio"] - 1.0) / noise) if noise else 0)
            lines.append("%-12s vs %-12s ratio %s  %d%% CI [%s, %s]  over %d pairs -> %s"
                         % (n, baseline, fmt(bs["ratio"]), confidence, fmt(bs["ci"][0]), fmt(bs["ci"][1]),
                            bs["pairs"], verdict))
        lines.append("")
    lines.append("| Candidate | n | Median | p95 | MAD | CV | Min | Max |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for n in sorted(names, key=lambda x: table[x]["median"]):
        t = table[n]
        lines.append("| %s | %d | %s | %s | %s | %.1f%% | %s | %s |"
                     % (n, t["n"], fmt(t["median"]), fmt(t["p95"]), fmt(t["mad"]), t["cv"],
                        fmt(t["min"]), fmt(t["max"])))
    lines.append("")
    lines.append("Unit = whatever the harness recorded. Report the mode, workload, environment and iterations "
                 "beside this table - these numbers mean nothing without them.")
    return "\n".join(lines), 0


def environment():
    """Best-effort snapshot; missing facts print as unknown rather than being guessed."""
    def probe(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            return ""
    cpu = (probe(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"])
           or probe(["bash", "-c", "grep -m1 'model name' /proc/cpuinfo | cut -d: -f2"])
           or platform.processor() or "")
    cpu = cpu.splitlines()[0].strip() if cpu.strip() else "unknown"
    posix = os.name != "nt"
    gov = probe(["bash", "-c", "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null"]) if posix else ""
    load = probe(["bash", "-c", "cut -d' ' -f1-3 /proc/loadavg"]) if posix else ""
    venv = os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX") or ""
    if not venv and os.environ.get("NODE_ENV"):
        venv = "NODE_ENV=%s (not an isolated install - say which prefix/node_modules the deps went into)" % os.environ["NODE_ENV"]
    if not venv and os.environ.get("GOPATH"):
        venv = "GOPATH set; state whether modules were vendored locally"
    lines = [
        "## Environment snapshot",
        "- os: %s %s (%s)" % (platform.system(), platform.release(), platform.machine()),
        "- python: %s" % platform.python_version(),
        "- cpu: %s" % cpu,
        "- logical cores (os): %s" % (os.cpu_count() or "unknown"),
        "- governor: %s" % (gov or "unknown (windows/mac: check power plan)"),
        "- load at snapshot: %s" % (load or "not reported on Windows (Git-Bash fakes /proc/loadavg)"),
        "- power: %s" % (probe(["powershell", "-NoProfile", "-Command",
                                "(Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue).BatteryStatus"])
                         or "unknown - probe returned nothing (desktop without a battery, or powershell blocked); "
                            "on a laptop this MUST be checked: battery changes clocks mid-run"),
        "- isolated env: %s" % (venv or "no venv/conda prefix active - if this run installed anything, name the "
                                       "sandbox it went into; global installs are a side effect to report"),
        "- manifests: <git diff of the project lockfiles must be empty - paste the check, not a claim>",
        "- versions of candidates: <fill in: runtime + library versions, build flags>",
        "- ultra controls applied: <list, or say 'normal mode: nothing was controlled'>",
        "- machine-wide settings: <before-value -> restored value, with the read-back proving the restore>",
        "- host: %s" % platform.node(),
        "- when: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ self-test

def selftest():
    checks = fails = 0

    def check(name, cond):
        nonlocal checks, fails
        checks += 1
        print("%-46s %s" % (name, "PASS" if cond else "FAIL"))
        fails += 0 if cond else 1

    txt, rc = iteration_math(300, 2.4, 0.2, 0.2)
    check("budget math reserves reporting time", rc == 0 and "reserve" in txt and "measured" in txt)
    txt2, _ = iteration_math(10, 2.4, 0.2, 0.2)
    check("tiny budget says 'too few iterations'", "too few" in txt2)

    rng = random.Random(7)
    base = {i: 10.0 + rng.gauss(0, 0.4) for i in range(40)}
    same = {i: 10.0 + rng.gauss(0, 0.4) for i in range(40)}
    fast = {i: 4.0 + rng.gauss(0, 0.2) for i in range(40)}
    rows = [("slow", i, v) for i, v in base.items()] + [("slow2", i, v) for i, v in same.items()] \
        + [("fast", i, v) for i, v in fast.items()]
    out, rc = report(rows, "slow", 95, ("slow", "slow2"))
    check("clear gap is called real", "real difference" in out)
    check("noise floor is reported", "noise floor" in out)
    check("markdown table emitted", "| Candidate |" in out)

    near = {i: 10.0 + rng.gauss(0, 0.4) for i in range(40)}
    rows2 = [("a", i, v) for i, v in base.items()] + [("b", i, v) for i, v in near.items()]
    out2, _ = report(rows2, "a", 95)
    check("equal candidates are called inconclusive", "inconclusive" in out2 or "INSIDE NOISE" in out2)

    _, rc_bad = report(rows, "missing", 95)
    check("unknown baseline is a usage error", rc_bad == 2)
    check("missing CSV columns rejected", _rejects_header())
    env = environment()
    check("environment reports isolation and restore",
          "isolated env" in env and "restored" in env and "manifests" in env)
    old = os.environ.get("VIRTUAL_ENV")
    os.environ["VIRTUAL_ENV"] = os.sep + "tmp" + os.sep + ".venv-bench"
    try:
        check("environment detects an active venv", ".venv-bench" in environment())
    finally:
        if old is None:
            del os.environ["VIRTUAL_ENV"]
        else:
            os.environ["VIRTUAL_ENV"] = old
    print("self-test: %d/%d checks passed" % (checks - fails, checks))
    return 0 if fails == 0 else 1


def _rejects_header():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as fh:
        fh.write("name,iteration,value\na,1,2\n")
        p = fh.name
    try:
        load_samples(p)
        return False
    except ValueError:
        return True
    finally:
        os.unlink(p)


def main(argv):
    ap = argparse.ArgumentParser(prog="bench_stats.py")
    ap.add_argument("--budget", type=float, help="total wall-clock seconds the user will allow")
    ap.add_argument("--per-iteration", type=float, help="seconds one iteration takes (measure it first)")
    ap.add_argument("--warmup-frac", type=float, default=0.2)
    ap.add_argument("--reserve", type=float, default=0.2, help="budget share kept for analysis/report")
    ap.add_argument("--samples", help="csv or json with candidate,iteration,value")
    ap.add_argument("--baseline", help="candidate to compare the others against")
    ap.add_argument("--confidence", type=float, default=95.0)
    ap.add_argument("--null", help="two labels of the SAME implementation, e.g. 'like,like2' -> noise floor")
    ap.add_argument("--environment", action="store_true")
    a = ap.parse_args(argv)

    if a.environment:
        print(environment())
        return 0
    if a.budget and a.per_iteration:
        txt, rc = iteration_math(a.budget, a.per_iteration, a.warmup_frac, a.reserve)
        print(txt)
        return rc
    if a.budget or a.per_iteration:
        print("error: --budget and --per-iteration go together")
        return 2
    if a.samples:
        if not os.path.exists(a.samples):
            print("error: no such file: %s" % a.samples)
            return 2
        try:
            rows = load_samples(a.samples)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            print("error: %s" % e)
            return 2
        pairs = tuple(x.strip() for x in a.null.split(",")) if a.null else None
        txt, rc = report(rows, a.baseline, a.confidence, pairs)
        print(txt)
        return rc
    return selftest()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
