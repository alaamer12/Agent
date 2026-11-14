"""Mock KovAPI/NezhaGate-style provider + end-to-end tests for generate engine (image + video)."""
import base64, json, os, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 8766
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
MP4 = b"\x00\x00\x00 ftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free"
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
        if self.path in ("/v1/images/generations", "/v1/videos/generations"):
            is_video = "videos" in self.path
            try: payload = json.loads(body)
            except Exception: payload = {"raw": body[:100].decode("latin1")}
            STATE["last_payload"] = payload
            prompt = payload.get("prompt", "") if isinstance(payload, dict) else ""
            prefix = "vid" if is_video else "img"
            jid = f"{prefix}-job-{len(STATE['jobs'])}"
            if "fail" in str(prompt):
                STATE["jobs"][jid] = "will-fail"
            elif "expire" in str(prompt):
                STATE["jobs"][jid] = "expired-url"
            else:
                STATE["jobs"][jid] = "queued"
            obj_type = "video.generation.job" if is_video else "image.generation.job"
            self._send(202, {"id": jid, "object": obj_type, "status": "queued", "model": payload.get("model")})
        elif self.path == "/v1/usage":
            self._send(200, {"balance_credits": 4200})
        else:
            self._send(404, {"error": "no route"})

    def do_GET(self):
        if self.path == "/v1/usage":
            self._send(200, {"balance_credits": 4200})
        elif self.path.startswith("/v1/images/jobs/") or self.path.startswith("/v1/videos/jobs/"):
            is_video = "/videos/" in self.path
            jid = self.path.rsplit("/", 1)[1]
            c = STATE["poll_count"].setdefault(jid, 0) + 1
            STATE["poll_count"][jid] = c
            if STATE["jobs"].get(jid) == "will-fail":
                self._send(200, {"status": "failed", "error": {"message": "content policy (mock)"}})
                return
            if c < 2:
                self._send(200, {"status": "running"})
            elif STATE["jobs"].get(jid) == "expired-url":
                ext = "mp4" if is_video else "png"
                self._send(200, {"status": "succeeded",
                                 "data": [{"url": f"http://127.0.0.1:{PORT}/gone/{jid}.{ext}"}],
                                 "usage": {"clips" if is_video else "images": 1, "credits": 4, "model": "mock"}})
            else:
                ext = "mp4" if is_video else "png"
                self._send(200, {"status": "succeeded",
                                 "data": [{"url": f"http://127.0.0.1:{PORT}/i/{jid}.{ext}"}],
                                 "usage": {"clips" if is_video else "images": 1, "credits": 4, "model": "mock"}})
        elif self.path.startswith("/i/"):
            if self.path.endswith(".mp4"):
                self._send(200, raw=MP4, ctype="video/mp4")
            else:
                self._send(200, raw=PNG, ctype="image/png")
        else:
            self._send(404, {"error": "no route"})

srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.2)

ROOT = Path(sys.argv[1])          # skill dir
WORK = Path(sys.argv[2]); WORK.mkdir(parents=True, exist_ok=True)
ENGINE = str(ROOT / "scripts" / "generate.py")
REG = WORK / "mock.csv"
import csv as _csv
def J(o): return json.dumps(o)

with open(REG, "w", newline="", encoding="utf-8") as f:
    w = _csv.writer(f)
    w.writerow(["provider_id", "media", "priority", "base_url", "auth", "endpoints", "request",
                "response", "features", "models", "pricing", "docs", "status", "valid_as_of", "notes"])
    # image row
    w.writerow(["mock", "image", "1", f"http://127.0.0.1:{PORT}/v1",
                J({"header": "Authorization", "format": "Bearer {key}", "env": ["MOCK_IMG_KEY"]}),
                J({"generate": "/images/generations", "poll": "/images/jobs/{id}", "usage": "/usage"}),
                J({"builder": "openai_json", "mode": "submit-poll",
                   "param_map": {"prompt": "prompt", "model": "model", "size": "size", "resolution": "resolution"},
                   "image_field": "images", "image_format": "data_url"}),
                J({"job_id_path": "id", "status_path": "status", "succeeded": ["succeeded"],
                   "failed": ["failed"], "error_path": "error", "urls": ["data[0].url"], "usage_path": "usage"}),
                J({"t2i": True, "i2i": True, "edit": False, "n": False, "usage_endpoint": True,
                   "max_ref_images": 8, "max_concurrent": 50}),
                J({"default": "mock-model"}), J({"credit_usd": 0.005}), J({}), "mock", "user-verified-here", "test"])
    # video row
    w.writerow(["mock", "video", "1", f"http://127.0.0.1:{PORT}/v1",
                J({"header": "Authorization", "format": "Bearer {key}", "env": ["MOCK_IMG_KEY"]}),
                J({"generate": "/videos/generations", "poll": "/videos/jobs/{id}", "usage": "/usage"}),
                J({"builder": "openai_json", "mode": "submit-poll",
                   "param_map": {"prompt": "prompt", "model": "model", "duration": "duration", "size": "size"},
                   "image_field": "images", "image_format": "url_array"}),
                J({"job_id_path": "id", "status_path": "status", "succeeded": ["succeeded"],
                   "failed": ["failed"], "error_path": "error", "urls": ["data[0].url"], "usage_path": "usage"}),
                J({"t2v": True, "i2v": True, "edit": False, "duration": True, "n": False, "usage_endpoint": True,
                   "max_ref_images": 8, "max_concurrent": 50}),
                J({"default": "mock-video-model", "default_duration": 5}), J({"credit_usd": 0.005}), J({}), "mock", "user-verified-here", "test"])

env = {**os.environ, "MOCK_IMG_KEY": "mk-test", "PYTHONIOENCODING": "utf-8"}
def run(*a, expect=0):
    p = subprocess.run([sys.executable, ENGINE, "--registry", str(REG), "--plain", *a],
                       capture_output=True, text=True, env=env, cwd=str(WORK), timeout=120)
    tag = "OK " if p.returncode == expect else "FAIL"
    print(f"{tag} generate {' '.join(a)}  rc={p.returncode}")
    if p.returncode != expect:
        print("  stdout:", p.stdout[:800], "\n  stderr:", p.stderr[:800])
    return p

fails = 0
def check(cond, name):
    global fails
    print(("OK  " if cond else "FAIL") + f" assert: {name}")
    if not cond: fails += 1

# 1. single async image job
p = run("--prompt", "a red apple", "--out", "out1/apple.png", "--poll-interval", "0.2", "--max-wait", "15")
check((WORK / "out1" / "apple.png").is_file() and (WORK / "out1" / "apple.png").read_bytes() == PNG, "single image: png downloaded")
check("apple" in p.stdout and "|" in p.stdout, "single image: table printed")

# 1b. single async video job
p = run("--video", "--prompt", "ocean waves", "--duration", "5", "--out", "out_vid/ocean.mp4",
        "--poll-interval", "0.2", "--max-wait", "15")
check((WORK / "out_vid" / "ocean.mp4").is_file() and (WORK / "out_vid" / "ocean.mp4").read_bytes() == MP4, "single video: mp4 downloaded")
check("video" in p.stdout and "ocean.mp4" in p.stdout, "single video: table printed with video media")

# 2. batch of 3 images
p = run("--prompt", "blue mug", "--batch", "3", "--concurrency", "3", "--out", "out2",
        "--poll-interval", "0.2", "--max-wait", "15")
outs = list((WORK / "out2").glob("*.png")) if (WORK / "out2").is_dir() else []
check(len(outs) == 3, f"batch: 3 files saved ({len(outs)})")

# 3. one failing prompt in batch
(WORK / "pf.txt").write_text("green chair\nfail this one\nwood table\n", encoding="utf-8")
p = run("--prompts-file", "pf.txt", "--out", "out3", "--poll-interval", "0.2", "--max-wait", "15", expect=1)
check("FAIL" in p.stdout and "OK" in p.stdout, "mixed batch: fail + ok rows")
check(len(list((WORK / "out3").glob("*.png"))) == 2, "mixed batch: 2 saved")

# 4. context new then continue
p = run("--context", "new", "--system", "You design minimalist product assets.", "--label", "brand",
        "--prompt", "matte black speaker, minimal", "--out", "ctx1", "--poll-interval", "0.2", "--max-wait", "15")
import re as _re
m = _re.search(r"context created: (\w+)", p.stderr)
cid = m.group(1) if m else None
check(bool(cid), f"context: id returned ({cid})")
ctxfile = WORK / ".generate" / "contexts" / f"{cid}.json"
check(ctxfile.is_file(), "context: file saved under .generate/contexts/")
turns = json.loads(ctxfile.read_text(encoding="utf-8"))["turns"] if ctxfile.is_file() else []
check([t["role"] for t in turns] == ["system", "user", "assistant"], "context: system+user+assistant turns")
p = run("--context", cid, "--prompt", "now in brushed steel", "--out", "ctx2", "--poll-interval", "0.2", "--max-wait", "15")
ctx2 = json.loads(ctxfile.read_text(encoding="utf-8"))
check(len(ctx2["turns"]) == 5, f"context: history grows ({len(ctx2['turns'])} turns)")

# 4b. context seeding explicit mode
(WORK / "seed_ref.png").write_bytes(PNG)
p = subprocess.run([sys.executable, ENGINE, "--registry", str(REG), "--context-seed", "custom-seed-42",
                    "--media", "video", "--system", "Director vision: high contrast cinematic",
                    "--prompt", "Anchor shot in rainy city", "--image", "seed_ref.png"],
                   capture_output=True, text=True, env=env, cwd=str(WORK))
seed_file = WORK / ".generate" / "contexts" / "custom-seed-42.json"
check(p.returncode == 0 and seed_file.is_file(), "context-seed: created explicit context file")
sdata = json.loads(seed_file.read_text(encoding="utf-8"))
check(sdata["id"] == "custom-seed-42" and sdata["media"] == "video", "context-seed: explicit id and media preserved")
check(any(t.get("role") == "user" and t.get("images") and t["images"][0].startswith("data:image/png;base64,")
          for t in sdata.get("turns", [])), "context-seed: pre-encoded base64 data url in user turn")

# 5. batch-context: shared snapshot, one summary turn
p = run("--context", cid, "--batch-context", "--prompt", "poster A", "--batch", "2", "--concurrency", "2",
        "--out", "ctx3", "--poll-interval", "0.2", "--max-wait", "15")
ctx3 = json.loads(ctxfile.read_text(encoding="utf-8"))
check(len(ctx3["turns"]) == 7, f"batch-context: single summary append ({len(ctx3['turns']) - 5} new turns)")
check(not list((WORK / ".generate" / "contexts").glob(f"{cid}-j*")), "batch-context: no fork files")

# 5b. multi-process context safety: two concurrent sessions on the SAME context id
procs = []
for tag in ("session-alpha", "session-beta"):
    procs.append(subprocess.Popen([sys.executable, ENGINE, "--registry", str(REG), "--plain",
                                   "--context", cid, "--batch-context", "--prompt", tag,
                                   "--out", f"mp-{tag}", "--poll-interval", "0.2", "--max-wait", "20"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  env=env, cwd=str(WORK)))
codes = [proc.wait(timeout=90) for proc in procs]
ctxmp = json.loads(ctxfile.read_text(encoding="utf-8"))
turns_txt = json.dumps(ctxmp)
check(all(c == 0 for c in codes), f"multiproc: both sessions rc=0 ({codes})")
check("session-alpha" in turns_txt and "session-beta" in turns_txt, "multiproc: BOTH sessions' turns kept")
check(not list((WORK / ".generate" / "contexts").glob("*.lock")), "multiproc: no leftover lock files")

# 6. image input -> data_url base64
(WORK / "ref.png").write_bytes(PNG)
p = run("--prompt", "x", "--image", "ref.png", "--dry-run")
check("data:image/png;base64," in p.stdout, "image input: base64 data_url in payload")
check("<redacted" in p.stdout and "mk-test" not in p.stdout, "dry-run: key redacted, never echoed")

# 6b. --api-key flag: works without env key
env2 = dict(os.environ); env2.pop("MOCK_IMG_KEY", None)
p = subprocess.run([sys.executable, ENGINE, "--registry", str(REG), "--plain", "--provider", "mock",
                    "--api-key", "SKtopsecret999", "--prompt", "key via flag", "--out", "apikey",
                    "--poll-interval", "0.2", "--max-wait", "15"],
                   capture_output=True, text=True, env=env2, cwd=str(WORK), timeout=120)
check(p.returncode == 0, "api-key flag: generation works without env key")
check("SKtopsecret999" not in p.stdout + p.stderr, "api-key flag: raw key never printed")
check("SK…999" in p.stderr and "supplied via --api-key" in p.stderr, "api-key flag: masked sensitive display")
check("SKtopsecret999" not in (WORK / ".generate" / "usage.jsonl").read_text(encoding="utf-8"),
      "api-key flag: raw key absent from ledger")

# 7. usage endpoint
p = run("--usage")
check("4200" in p.stdout, "usage: balance shown")

# 8. ledger
ledger = WORK / ".generate" / "usage.jsonl"
lines = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines()] if ledger.is_file() else []
check(len(lines) >= 8 and any(l["status"] == "fail" for l in lines), f"ledger: {len(lines)} entries incl fail row")

# 9. URL manifest + salvage
mfile = WORK / ".generate" / "results.jsonl"
check(mfile.is_file(), "manifest: results.jsonl exists")
mrecs = [json.loads(l) for l in mfile.read_text(encoding="utf-8").splitlines()]
recv = [r for r in mrecs if r["kind"] == "received"]
done = [r for r in mrecs if r["kind"] == "done"]
check(recv and all(r.get("urls") for r in recv), f"manifest: received records carry URLs ({len(recv)})")

def resolve(s):
    p = Path(s)
    return p if p.is_absolute() else WORK / p
saved_files = [s for r in done for s in r.get("saved", []) if not str(s).startswith("http")]
victim = next((s for s in saved_files if resolve(s).is_file()), None)
if victim:
    resolve(victim).unlink()
p = run("--salvage")
check(victim is not None and resolve(victim).is_file() and str(victim) in p.stdout, "salvage: deleted file restored")
check(p.returncode == 0, "salvage: rc=0 after recovery")

# 10. default registry parses
p = subprocess.run([sys.executable, ENGINE, "--list-providers"], capture_output=True, text=True, env=env, cwd=str(WORK))
check(p.returncode == 0 and "kovapi" in p.stdout and "gemini" in p.stdout, "registry: real data.csv parses")

print("\nRESULT:", "ALL PASS" if fails == 0 else f"{fails} FAILURES")
sys.exit(1 if fails else 0)
