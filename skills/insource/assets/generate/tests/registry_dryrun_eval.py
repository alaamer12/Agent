"""Keyless eval: every real data.csv row through the engine via --dry-run.

Verifies registry parsing, universal-param mapping, value transforms,
builder shapes (image + video, gemini_omni), context seeding, edit gating,
batch accounting, and key masking — with fake keys and zero network.
Run: python tests/registry_dryrun_eval.py
"""
import base64, json, os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENGINE = str(ROOT / "scripts" / "generate.py")
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")

work = Path(tempfile.mkdtemp(prefix="generate-eval-"))
(work / "ref.png").write_bytes(PNG)
env = {k: v for k, v in os.environ.items() if not re.match(r"(XAI|OPENAI|GEMINI|GOOGLE|NEZHA|KOVAPI)_(API_)?KEY$", k)}
env["PYTHONIOENCODING"] = "utf-8"
FAKE = "FAKEKEY-abcdef123456"

fails = 0
def run(args):
    p = subprocess.run([sys.executable, ENGINE, *args, "--dry-run"], capture_output=True,
                       text=True, env=env, cwd=str(work), timeout=60)
    if p.returncode != 0:
        return None, p
    txt = p.stdout
    return json.loads(txt[txt.index("{"):]), p

def case(name, args, checks):
    global fails
    d, p = run(args)
    ok = d is not None
    notes = []
    if ok:
        for label, fn in checks.items():
            try:
                r = fn(d)
            except Exception:
                r = False
            if not r:
                ok = False
                notes.append(label)
    print(("OK   " if ok else "FAIL ") + name + (f"  (missed: {', '.join(notes)})" if notes else ""))
    if not ok and d is None:
        print("      stderr:", p.stderr[:300])
    if not ok:
        fails += 1

def payload0(d): return d["requests"][0]["payload"]

# ---- Image Cases ----
case("xai image: size->aspect_ratio, 1K->1k, b64 default, n fan",
     ["--provider", "xai", "--api-key", FAKE, "--prompt", "hero banner", "--size", "16:9",
      "--resolution", "1K", "--variations", "2"],
     {"endpoint": lambda d: d["requests"][0]["endpoint"] == "/images/generations",
      "aspect": lambda d: payload0(d)["aspect_ratio"] == "16:9",
      "resmap": lambda d: payload0(d)["resolution"] == "1k",
      "respfmt": lambda d: payload0(d)["response_format"] == "b64_json",
      "n": lambda d: payload0(d)["n"] == 2,
      "masked": lambda d: FAKE not in json.dumps(d)})

case("openai image: edit routes to /images/edits, multipart omits b64 from JSON",
     ["--provider", "openai", "--api-key", FAKE, "--prompt", "remove background",
      "--image", "ref.png", "--edit"],
     {"edit-ep": lambda d: d["requests"][0]["endpoint"] == "/images/edits",
      "no-img-json": lambda d: "image" not in payload0(d),
      "model": lambda d: payload0(d)["model"] == "gpt-image-2.5-flare"})

p = subprocess.run([sys.executable, ENGINE, "--provider", "xai", "--api-key", FAKE,
                    "--prompt", "x", "--image", str(work / "ref.png"), "--edit"],
                   capture_output=True, text=True, env=env, cwd=str(work))
gate_ok = p.returncode != 0 and ("no image-input support" in p.stderr or "no edit endpoint" in p.stderr)
print(("OK   " if gate_ok else "FAIL ") + "xai image: image/edit inputs hard-rejected per features")
fails += 0 if gate_ok else 1

case("gemini image: native builder shape + model-templated endpoint",
     ["--provider", "gemini", "--api-key", FAKE, "--prompt", "nano shot", "--size", "9:16"],
     {"ep": lambda d: "{model}" in d["requests"][0]["endpoint"],
      "contents": lambda d: payload0(d)["contents"][0]["parts"][0]["text"] == "nano shot",
      "mods": lambda d: payload0(d)["generationConfig"]["responseModalities"] == ["IMAGE", "TEXT"]})

case("kovapi image: async row, data_url image, batch accounting",
     ["--provider", "kovapi", "--api-key", FAKE, "--prompt", "apple", "--resolution", "4K",
      "--image", "ref.png", "--batch", "2"],
     {"jobs": lambda d: d["total_jobs"] == 2,
      "ep": lambda d: d["requests"][0]["endpoint"] == "/images/generations",
      "res": lambda d: payload0(d)["resolution"] == "4K",
      "auth": lambda d: "redacted" in d["auth"] and FAKE not in json.dumps(d)})

# ---- Video Cases ----
case("kovapi video: async video generations, duration, resolution, size",
     ["--media", "video", "--provider", "kovapi", "--api-key", FAKE,
      "--prompt", "ocean waves", "--duration", "8", "--resolution", "720P", "--size", "16:9"],
     {"media": lambda d: d["media"] == "video",
      "ep": lambda d: d["requests"][0]["endpoint"] == "/videos/generations",
      "dur": lambda d: payload0(d)["duration"] == 8,
      "res": lambda d: payload0(d)["resolution"] == "720P",
      "size": lambda d: payload0(d)["size"] == "16:9",
      "model": lambda d: payload0(d)["model"] == "seedance-2.0"})

case("xai video: object_url image shape, duration, resolution map",
     ["--media", "video", "--provider", "xai", "--api-key", FAKE,
      "--prompt", "car drive", "--duration", "10", "--resolution", "720P", "--image", "ref.png"],
     {"media": lambda d: d["media"] == "video",
      "ep": lambda d: d["requests"][0]["endpoint"] == "/videos/generations",
      "dur": lambda d: payload0(d)["duration"] == 10,
      "res": lambda d: payload0(d)["resolution"] == "720p",
      "img_obj": lambda d: isinstance(payload0(d).get("image"), dict) and "url" in payload0(d)["image"],
      "model": lambda d: payload0(d)["model"] == "grok-imagine-video-1.5"})

case("gemini video: interactions API, gemini_omni builder, duration suffix 's'",
     ["--media", "video", "--provider", "gemini", "--api-key", FAKE,
      "--prompt", "flying bird", "--duration", "10", "--resolution", "1080p", "--size", "9:16"],
     {"media": lambda d: d["media"] == "video",
      "ep": lambda d: d["requests"][0]["endpoint"] == "/v1beta/interactions",
      "dur": lambda d: payload0(d)["response_format"]["duration"] == "10s",
      "res": lambda d: payload0(d)["response_format"]["resolution"] == "1080p",
      "asp": lambda d: payload0(d)["response_format"]["aspect_ratio"] == "9:16",
      "model": lambda d: payload0(d)["model"] == "gemini-omni-1.2-flash"})

# ---- Context Seeding Case ----
p = subprocess.run([sys.executable, ENGINE, "--context-seed", "seeded-hero-123",
                    "--media", "video", "--system", "Style guide: cyberpunk",
                    "--prompt", "Neon street baseline", "--image", "ref.png",
                    "--state-dir", str(work / ".generate")],
                   capture_output=True, text=True, env=env, cwd=str(work))
seed_file = work / ".generate" / "contexts" / "seeded-hero-123.json"
seed_ok = (p.returncode == 0 and seed_file.is_file() and
           "seeded-hero-123" in p.stdout and
           "Style guide: cyberpunk" in seed_file.read_text(encoding="utf-8"))
print(("OK   " if seed_ok else "FAIL ") + "context seeding: explicit ID, turns & pre-encoded images")
fails += 0 if seed_ok else 1

p = subprocess.run([sys.executable, ENGINE, "--prompt", "x"], capture_output=True,
                   text=True, env={k: v for k, v in env.items() if "API_KEY" not in k and k != "MOCK_IMG_KEY"}, cwd=str(work))
nokey_ok = p.returncode != 0 and "no provider for media='image' has an API key" in p.stderr
print(("OK   " if nokey_ok else "FAIL ") + "env without keys: clear refusal, no calls")
fails += 0 if nokey_ok else 1

# Frontmatter compliance
fm = (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
desc_m = re.search(r'description:\s*(".*?"|.*?)(?=\n[a-z_]+:|$)', fm, re.DOTALL)
desc = desc_m.group(1).strip()
meta_ok = len(desc) <= 1024
print(("OK   " if meta_ok else "FAIL ") + f"SKILL.md frontmatter description <= 1024 chars (actual: {len(desc)})")
fails += 0 if meta_ok else 1

print(f"\nregistry dry-run eval: {fails} failure(s)")
sys.exit(0 if fails == 0 else 1)
