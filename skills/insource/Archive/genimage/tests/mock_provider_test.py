"""Mock NezhaGate-style provider + end-to-end tests for genimage engine."""
import base64, json, os, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 8765
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
STATE = {"jobs": {}, "last_payload": None, "poll_count": {}}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, obj=None, raw=None, ctype="application/json"):
        body = raw if raw is not None else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n)
        if self.path == "/v1/images/generations":
            try: payload = json.loads(body)
            except Exception: payload = {"raw": body[:100].decode("latin1")}
            STATE["last_payload"] = payload
            if "multipart" in (self.headers.get("Content-Type") or ""):
                STATE["last_payload"] = {"multipart": True, "contains": [s for s in (b"prompt", b"image", b"base64") if s in body]}
            prompt = payload.get("prompt", "") if isinstance(payload, dict) else ""
            jid = f"job-{len(STATE['jobs'])}"
            if "fail" in str(prompt):
                STATE["jobs"][jid] = "will-fail"
            elif "expire" in str(prompt):
                STATE["jobs"][jid] = "expired-url"
            else:
                STATE["jobs"][jid] = "queued"
            self._send(202, {"id": jid, "object": "image.generation.job", "status": "queued", "model": payload.get("model")})
        elif self.path == "/v1/usage":
            self._send(200, {"balance_credits": 4200})
        else:
            self._send(404, {"error": "no route"})
    def do_GET(self):
        if self.path == "/v1/usage":
            self._send(200, {"balance_credits": 4200})
        elif self.path.startswith("/v1/images/jobs/"):
            jid = self.path.rsplit("/", 1)[1]
            c = STATE["poll_count"].setdefault(jid, 0) + 1
            STATE["poll_count"][jid] = c
            if STATE["jobs"].get(jid) == "will-fail":
                self._send(200, {"status": "failed", "error": {"message": "content policy (mock)"}})
                return
            if c < 2:
                self._send(200, {"status": "running"})
            elif STATE["jobs"].get(jid) == "expired-url":
                self._send(200, {"status": "succeeded",
                                 "data": [{"url": f"http://127.0.0.1:{PORT}/gone/{jid}.png"}],
                                 "usage": {"images": 1, "credits": 4, "model": "mock"}})
            else:
                self._send(200, {"status": "succeeded",
                                 "data": [{"url": f"http://127.0.0.1:{PORT}/i/{jid}.png"}],
                                 "usage": {"images": 1, "credits": 4, "model": "mock"}})
        elif self.path.startswith("/i/"):
            self._send(200, raw=PNG, ctype="image/png")
        else:
            self._send(404, {"error": "no route"})

srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.2)

ROOT = Path(sys.argv[1])          # skill dir
WORK = Path(sys.argv[2]); WORK.mkdir(parents=True, exist_ok=True)
ENGINE = str(ROOT / "scripts" / "genimage.py")
REG = WORK / "mock.csv"
import csv as _csv
def J(o): return json.dumps(o)
with open(REG, "w", newline="", encoding="utf-8") as f:
    w = _csv.writer(f)
    w.writerow(["provider_id", "priority", "base_url", "auth", "endpoints", "request",
                "response", "features", "models", "pricing", "docs", "status", "valid_as_of", "notes"])
    w.writerow(["mock", "1", f"http://127.0.0.1:{PORT}/v1",
                J({"header": "Authorization", "format": "Bearer {key}", "env": ["MOCK_IMG_KEY"]}),
                J({"generate": "/images/generations", "poll": "/images/jobs/{id}", "usage": "/usage"}),
                J({"builder": "openai_json", "mode": "submit-poll",
                   "param_map": {"prompt": "prompt", "model": "model", "size": "size", "resolution": "resolution"},
                   "image_field": "images", "image_format": "data_url"}),
                J({"job_id_path": "id", "status_path": "status", "succeeded": ["succeeded"],
                   "failed": ["failed"], "error_path": "error", "urls": ["data[0].url"], "usage_path": "usage"}),
                J({"t2i": True, "i2i": True, "edit": False, "n": False, "usage_endpoint": True,
                   "max_ref_images": 8, "max_concurrent": 50}),
                J({"default": "mock-model"}), J({}), J({}), "mock", "user-verified-here", "test"])

env = {**os.environ, "MOCK_IMG_KEY": "mk-test", "PYTHONIOENCODING": "utf-8"}
def run(*a, expect=0):
    p = subprocess.run([sys.executable, ENGINE, "--registry", str(REG), "--plain", *a],
                       capture_output=True, text=True, env=env, cwd=str(WORK), timeout=120)
    tag = "OK " if p.returncode == expect else "FAIL"
    print(f"{tag} genimage {' '.join(a)}  rc={p.returncode}")
    if p.returncode != expect:
        print("  stdout:", p.stdout[:800], "\n  stderr:", p.stderr[:800])
    return p

fails = 0
def check(cond, name):
    global fails
    print(("OK  " if cond else "FAIL") + f" assert: {name}")
    if not cond: fails += 1

# 1. single async job
p = run("--prompt", "a red apple", "--out", "out1/apple.png", "--poll-interval", "0.2", "--max-wait", "15")
check((WORK / "out1" / "apple.png").is_file() and (WORK / "out1" / "apple.png").read_bytes() == PNG, "single: png downloaded")
check("apple" in p.stdout and "|" in p.stdout, "single: table printed")

# 2. batch of 3
p = run("--prompt", "blue mug", "--batch", "3", "--concurrency", "3", "--out", "out2",
        "--poll-interval", "0.2", "--max-wait", "15")
outs = list((WORK / "out2").glob("*.png")) if (WORK / "out2").is_dir() else []
check(len(outs) == 3, f"batch: 3 files saved ({len(outs)})")
check(p.stdout.count("| blue mug") == 0 and "OK" in p.stdout, "batch: statuses shown")

# 3. one failing prompt in batch
(WORK / "pf.txt").write_text("green chair\nfail this one\nwood table\n", encoding="utf-8")
p = run("--prompts-file", "pf.txt", "--out", "out3", "--poll-interval", "0.2", "--max-wait", "15", expect=1)
check("FAIL" in p.stdout and "OK" in p.stdout, "mixed batch: fail + ok rows")
check(len(list((WORK / "out3").glob("*.png"))) == 2, "mixed batch: 2 saved")

# 4. context new then continue
p = run("--context", "new", "--system", "You design minimalist product assets.", "--label", "brand",
        "--prompt", "matte black speaker, minimal", "--out", "ctx1", "--poll-interval", "0.2", "--max-wait", "15")
cid = [w for w in p.stderr.replace("context created:", "|").split() if "|" in w]
import re as _re
m = _re.search(r"context created: (\w+)", p.stderr)
cid = m.group(1) if m else None
check(bool(cid), f"context: id returned ({cid})")
ctxfile = WORK / ".genimage" / "contexts" / f"{cid}.json"
check(ctxfile.is_file(), "context: file saved")
turns = json.loads(ctxfile.read_text(encoding="utf-8"))["turns"] if ctxfile.is_file() else []
check([t["role"] for t in turns] == ["system", "user", "assistant"], "context: system+user+assistant turns")
p = run("--context", cid, "--prompt", "now in brushed steel", "--out", "ctx2", "--poll-interval", "0.2", "--max-wait", "15")
ctx2 = json.loads(ctxfile.read_text(encoding="utf-8"))
check(len(ctx2["turns"]) == 5, f"context: history grows ({len(ctx2['turns'])} turns)")
check((WORK / "ctx2").is_dir() or any((WORK / "ctx2").glob("*.png")) if (WORK / "ctx2").is_dir() else False, "context: second run saved")

# 5. batch-context: shared snapshot, one summary turn
p = run("--context", cid, "--batch-context", "--prompt", "poster A", "--batch", "2", "--concurrency", "2",
        "--out", "ctx3", "--poll-interval", "0.2", "--max-wait", "15")
ctx3 = json.loads(ctxfile.read_text(encoding="utf-8"))
check(len(ctx3["turns"]) == 7, f"batch-context: single summary append ({len(ctx3['turns']) - 5} new turns)")
check(not list((WORK / ".genimage" / "contexts").glob(f"{cid}-j*")), "batch-context: no fork files")
# and default (no --batch-context) forks:
p = run("--context", cid, "--prompt", "tile B", "--batch", "2", "--concurrency", "2",
        "--out", "ctx4", "--poll-interval", "0.2", "--max-wait", "15")
check(len(list((WORK / ".genimage" / "contexts").glob(f"{cid}-j*"))) == 2, "default batch: forked branch contexts")

# 5b. multi-process context safety: two concurrent sessions on the SAME context id
procs = []
for tag in ("session-alpha", "session-beta"):
    procs.append(subprocess.Popen([sys.executable, ENGINE, "--registry", str(REG), "--plain",
                                   "--context", cid, "--batch-context", "--prompt", tag,
                                   "--out", f"mp-{tag}", "--poll-interval", "0.2", "--max-wait", "20"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  env=env, cwd=str(WORK)))
codes = [p.wait(timeout=90) for p in procs]
ctxmp = json.loads(ctxfile.read_text(encoding="utf-8"))  # must be valid JSON after concurrent writes
turns_txt = json.dumps(ctxmp)
check(all(c == 0 for c in codes), f"multiproc: both sessions rc=0 ({codes})")
check("session-alpha" in turns_txt and "session-beta" in turns_txt, "multiproc: BOTH sessions' turns kept (merge, not overwrite)")
check(not list((WORK / ".genimage" / "contexts").glob("*.lock")), "multiproc: no leftover lock files")

# 5c. stale lock is broken, not fatal
lock = ctxfile.with_suffix(".json.lock")
lock.write_text("pid=dead", encoding="utf-8")
os.utime(lock, (time.time() - 60, time.time() - 60))
p = run("--context", cid, "--prompt", "after stale lock", "--out", "stale1",
        "--poll-interval", "0.2", "--max-wait", "15")
check(p.returncode == 0 and "stale" in p.stderr, "stale lock: broken + warned + run completes")
check(not lock.exists(), "stale lock: cleaned up")

# 5d. live lock held by another session -> bounded wait then clear 'context busy'
env_busy = {**env, "GENIMAGE_LOCK_TIMEOUT": "1"}
lock.write_text("pid=alive", encoding="utf-8")
p = subprocess.run([sys.executable, ENGINE, "--registry", str(REG), "--context", cid,
                    "--prompt", "should not proceed"], capture_output=True, text=True,
                   env=env_busy, cwd=str(WORK), timeout=30)
check(p.returncode != 0 and "context busy" in p.stderr, "busy lock: refuses with clear message after timeout")
lock.unlink()

# 6. image input -> data_url base64 + context ref reuse
(WORK / "ref.png").write_bytes(PNG)
STATE["last_payload"] = None
p = run("--prompt", "style of this logo", "--image", "ref.png", "--out", "img1", "--poll-interval", "0.2", "--max-wait", "15")
# payload check via server state is cross-process; verify via dry-run instead:
p = run("--prompt", "x", "--image", "ref.png", "--dry-run")
check("data:image/png;base64," in p.stdout, "image input: base64 data_url in payload")
check("<redacted" in p.stdout and "mk-test" not in p.stdout, "dry-run: key redacted, never echoed")

# 6a. MULTIPLE input images (local file + URL) — structure + live run
p = run("--prompt", "combine styles", "--image", "ref.png",
        "--image", f"http://127.0.0.1:{PORT}/i/x.png", "--dry-run")
d = json.loads(p.stdout[p.stdout.index("{"):])
imgs = d["requests"][0]["payload"].get("images")
check(isinstance(imgs, list) and len(imgs) == 2, f"multi-image: file+URL both encoded into images list ({imgs if imgs is None else len(imgs)})")
p = run("--prompt", "combine live", "--image", "ref.png",
        "--image", f"http://127.0.0.1:{PORT}/i/x.png",
        "--out-dir", "multi", "--name-format", "{provider}-{index}-{n}-{date}",
        "--poll-interval", "0.2", "--max-wait", "15")
files = sorted((WORK / "multi").glob("*")) if (WORK / "multi").is_dir() else []
check(len(files) == 1 and files[0].name.startswith("mock-1-1-") and files[0].suffix == ".png",
      f"out-dir + name-format: {files[0].name if files else 'none'}")
check(not list((WORK / "multi").glob("*.tmp*")), "atomic save: no temp-file residue")
# single job into explicit dir still works via --out
p = run("--prompt", "dir mode single", "--out", "outdir/", "--poll-interval", "0.2", "--max-wait", "15")
check(any((WORK / "outdir").glob("*.png")), "out trailing-slash: directory mode for single job")

# 6b. --api-key flag: works without env key, sensitive display, raw key nowhere
env2 = dict(os.environ); env2.pop("MOCK_IMG_KEY", None)
p = subprocess.run([sys.executable, ENGINE, "--registry", str(REG), "--plain", "--provider", "mock",
                    "--api-key", "SKtopsecret999", "--prompt", "key via flag", "--out", "apikey",
                    "--poll-interval", "0.2", "--max-wait", "15"],
                   capture_output=True, text=True, env=env2, cwd=str(WORK), timeout=120)
check(p.returncode == 0, "api-key flag: generation works without env key")
check("SKtopsecret999" not in p.stdout + p.stderr, "api-key flag: raw key never printed")
check("SK…999" in p.stderr and "supplied via --api-key" in p.stderr, "api-key flag: masked sensitive display + warning")
check("SKtopsecret999" not in (WORK / ".genimage" / "usage.jsonl").read_text(encoding="utf-8"),
      "api-key flag: raw key absent from ledger")
p = subprocess.run([sys.executable, ENGINE, "--registry", str(REG), "--api-key", "x", "--prompt", "y"],
                   capture_output=True, text=True, env=env2, cwd=str(WORK))
check(p.returncode != 0 and "--provider" in p.stderr, "api-key flag: requires explicit --provider")

# 7. usage endpoint
p = run("--usage")
check("4200" in p.stdout, "usage: balance shown")

# 8. ledger
ledger = WORK / ".genimage" / "usage.jsonl"
lines = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines()] if ledger.is_file() else []
check(len(lines) >= 10 and any(l["status"] == "fail" for l in lines), f"ledger: {len(lines)} entries incl fail row")
check(any(l.get("usage", {}).get("credits") == 4 for l in lines if isinstance(l.get("usage"), dict)), "ledger: provider usage captured")

# 7b. URL manifest + salvage (durability when links/files are lost)
mfile = WORK / ".genimage" / "results.jsonl"
check(mfile.is_file(), "manifest: results.jsonl exists")
mrecs = [json.loads(l) for l in mfile.read_text(encoding="utf-8").splitlines()]
recv = [r for r in mrecs if r["kind"] == "received"]
done = [r for r in mrecs if r["kind"] == "done"]
check(recv and all(r.get("urls") for r in recv), f"manifest: received records carry provider URLs ({len(recv)})")
# received-before-done ordering per job
order_ok = all(mrecs.index(r) < len(mrecs) for r in recv)
jobs_done = {r["job"] for r in done}
check(all(any(rr["job"] == r["job"] for rr in recv) for r in done if r["job"] and r.get("urls")),
      "manifest: every successful job with URLs had a prior received record")
# delete one saved file -> salvage must restore it from the manifest URL
def resolve(s):
    p = Path(s)
    return p if p.is_absolute() else WORK / p
saved_files = [s for r in done for s in r.get("saved", []) if not str(s).startswith("http")]
victim = next((s for s in saved_files if resolve(s).is_file()), None)
if victim:
    resolve(victim).unlink()
p = run("--salvage")
check(victim is not None and resolve(victim).is_file() and str(victim) in p.stdout, "salvage: deleted file restored from manifest URL")
check(p.returncode == 0, "salvage: rc=0 after full recovery")
# dead link -> honest unrecoverable, recorded
dead_rec = {"kind": "done", "provider": "mock", "model": "mock-model", "job": "job-dead-9",
            "status": "ok", "urls": [f"http://127.0.0.1:{PORT}/gone/expired.png"],
            "saved": [str(WORK / "lost-forever.png")], "prompt": "gone", "ts": "now"}
with open(mfile, "a", encoding="utf-8") as f:
    f.write(json.dumps(dead_rec) + "\n")
p = run("--salvage", expect=1)
check("1 unrecoverable" in p.stdout, "salvage: dead link reported honestly, rc=1")
after = [json.loads(l) for l in mfile.read_text(encoding="utf-8").splitlines()]
check(any(r.get("kind") == "salvaged" and r.get("job") == "job-dead-9" and r.get("status") == "error" for r in after),
      "salvage: attempt recorded in manifest")
# success whose URL is NOT downloadable must not return happily: rc=1 + pending notice
p = run("--prompt", "expire this asset", "--out", "exp/", "--poll-interval", "0.2", "--max-wait", "15", expect=1)
check("NOT complete: 1" in p.stdout, "pending urls: run flags incomplete download, rc=1")
p = run("--salvage", expect=1)
check("unrecoverable" in p.stdout, "pending urls: salvage reports the dead one honestly")

# 9. default registry parses
p = subprocess.run([sys.executable, ENGINE, "--list-providers"], capture_output=True, text=True, env=env, cwd=str(WORK))
check(p.returncode == 0 and "nezha-gate" in p.stdout and "gemini" in p.stdout, "registry: real data.csv parses")

print("\nRESULT:", "ALL PASS" if fails == 0 else f"{fails} FAILURES")
sys.exit(1 if fails else 0)
