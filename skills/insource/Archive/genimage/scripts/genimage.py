#!/usr/bin/env python3
"""genimage — universal, registry-driven image generation engine (stdlib only).

Providers are DATA, not code: every vendor lives as a row in ../data.csv
(endpoints, param mapping, async pattern, features, pricing). Any RESTful
provider that matches a known builder (openai_json | gemini_json) works with
zero code changes; genuinely different shapes are added as a new builder
function. See references/provider-onboarding.md.

Capabilities
  --provider/--model/--size/--resolution/--quality/--variations   universal params, mapped per row
  --batch N --concurrency C [--prompts-file F]                     concurrent requests, progress bar
  --context new|<id> [--system T]                                  persisted system+user+assistant context
  --batch-context                                                  batch shares one base context snapshot
  --image SRC (repeatable)                                         URL or local file -> base64 per provider format
  --edit                                                           route to the provider's edit endpoint (if feature)
  --usage / --list-providers / --dry-run / --json / --plain
  usage ledger ./.genimage/usage.jsonl + per-request cost estimates

Never prints API keys; --dry-run redacts auth. Failed jobs are recorded,
not silently dropped.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import csv
import json
import mimetypes
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REGISTRY = SCRIPT_DIR.parent / "data.csv"
STATE_DIR_DEFAULT = Path(".genimage")  # contexts/, usage.jsonl under cwd

# ---------------------------------------------------------------- registry

def load_registry(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            if not raw.get("provider_id"):
                continue
            row = {k: (v.strip() if isinstance(v, str) else v) for k, v in raw.items()}
            for col in ("auth", "endpoints", "request", "response", "features", "models", "pricing"):
                try:
                    row[col] = json.loads(row[col]) if row[col] else {}
                except json.JSONDecodeError as e:
                    sys.exit(f"registry: bad JSON in row '{row['provider_id']}' column {col}: {e}")
            row["priority"] = int(row.get("priority") or 100)
            rows.append(row)
    return rows


def pick_provider(rows, requested=None, override_key=None, quiet=False):
    if requested:
        for r in rows:
            if r["provider_id"] == requested:
                key = override_key or env_key(r)
                if not key:
                    sys.exit(f"provider '{requested}' needs --api-key or one of env keys: {r['auth']['env']}")
                return r, key
        sys.exit(f"provider '{requested}' not in registry ({', '.join(r['provider_id'] for r in rows)})")
    if override_key:
        sys.exit("--api-key needs an explicit --provider (so we know which endpoint to send it to); "
                 "without --api-key the provider is chosen from env keys in registry priority order.")
    for r in sorted(rows, key=lambda x: x["priority"]):
        key = env_key(r)
        if key:
            if not quiet:
                warn(f"provider: {r['provider_id']} (key found)")
            return r, key
    sys.exit("no provider has an API key in the environment. Run --list-providers.")


def mask_key(k):
    if not k:
        return "****"
    return f"{k[:2]}…{k[-3:]}" if len(k) > 8 else "****"


def env_key(row):
    for name in row["auth"]["env"]:
        v = os.environ.get(name)
        if v:
            return v
    return None

# ---------------------------------------------------------------- helpers

def dig(obj, path):
    """Resolve 'data[0].url' style paths; None when absent."""
    cur = obj
    for m in re.finditer(r"([^.\[\]]+)|\[(\d+)\]", path or ""):
        k, i = m.group(1), m.group(2)
        try:
            cur = cur[k] if k is not None else cur[int(i)]
        except (KeyError, IndexError, TypeError):
            return None
    return cur


def assign(target, dotted, value):
    parts = dotted.split(".")
    cur = target
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value


def warn(msg):
    print(f"[genimage] {msg}", file=sys.stderr, flush=True)


def slugify(text, maxlen=40):
    words = re.sub(r"[^a-z0-9 ]", " ", text.lower()).split()
    return "-".join(words[:6])[:maxlen] or "image"


def now_ts():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def same_host(url, base):
    try:
        return urllib.parse.urlparse(url).netloc == urllib.parse.urlparse(base).netloc
    except ValueError:
        return False


def append_manifest(state_dir, record):
    """Durability first: provider URLs land here the moment they are received,
    before any download attempt — nothing downstream can lose them."""
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    record["ts"] = now_ts()
    with open(state_dir / "results.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

# ---------------------------------------------------------------- http

def http_request(url, headers, body=None, method=None, timeout=120, retries=2):
    """JSON in/out, binary out for non-JSON. Retries 429/5xx with backoff."""
    data = None
    if body is not None:
        if isinstance(body, (bytes, bytearray)):
            data = bytes(body)
        else:
            data = json.dumps(body).encode("utf-8")
            headers = {**headers, "Content-Type": "application/json"}
    last = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "genimage/2", **headers}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            raw = e.read()
            if e.code in (429,) or e.code >= 500:
                if attempt < retries:
                    time.sleep(min(2 ** attempt * 2, int(e.headers.get("Retry-After") or 8)))
                    continue
            return e.code, _parse(raw), dict(e.headers)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = e
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return 0, {"error": f"network: {e}"}, {}
        return resp.status, _parse(raw), {}
    return 0, {"error": f"network: {last or 'retries exhausted'}"}, {}


def _parse(raw):
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return raw


def fetch_bytes(url, headers=None, timeout=120):
    code, body, _ = http_request(url, headers or {}, timeout=timeout)
    if code == 200 and isinstance(body, (bytes, bytearray)):
        return bytes(body)
    if code == 200 and isinstance(body, dict):
        return json.dumps(body).encode()
    return None

# ---------------------------------------------------------------- images in

def load_image(src: str) -> tuple[str, str]:
    """URL or filesystem path -> (mime, raw bytes)."""
    if re.match(r"^https?://", src):
        data = fetch_bytes(src)
        if data is None:
            sys.exit(f"input image: could not download {src}")
        mime = "image/png"
    else:
        p = Path(src)
        if not p.is_file():
            sys.exit(f"input image: not found: {src}")
        data = p.read_bytes()
        mime = mimetypes.guess_type(str(p))[0] or "image/png"
    return mime, data

# ---------------------------------------------------------------- builders

def render_endpoint(tpl, row_unused=None, **fmt):
    return tpl.format(**{k: v for k, v in fmt.items() if v is not None})


def auth_headers(row, key):
    return {row["auth"]["header"]: row["auth"]["format"].replace("{key}", key)}


def encode_images(images, fmt, field):
    """Return value for the provider's image field, per its image_format."""
    out = []
    for mime, data in images:
        b64 = base64.b64encode(data).decode()
        if fmt == "data_url":
            out.append(f"data:{mime};base64,{b64}")
        elif fmt == "b64":
            out.append(b64)
        elif fmt == "inline_b64":
            out.append({"mime_type": mime, "data": b64})
        else:  # multipart carries raw bytes, still needed for size caps etc.
            out.append(b64)
    return out


def build_openai(row, prompt, model, params, images_enc, n, edit):
    payload = {"prompt": prompt, "model": model}
    req = row["request"]
    pmap = req.get("param_map", {})
    vmaps = req.get("value_maps", {})
    for uni, prov in pmap.items():
        if not prov or uni in ("prompt", "model", "variations"):
            continue
        if uni in params and params[uni] is not None:
            v = params[uni]
            vm = {k.lower(): k for k in vmaps.get(uni, {})}
            if uni in vmaps and str(v).lower() in {k.lower() for k in vmaps[uni]}:
                v = vmaps[uni][vm[str(v).lower()]]
            assign(payload, prov, v)
    for k, v in (req.get("extra_defaults") or {}).items():
        payload.setdefault(k, v)
    if images_enc and req.get("image_format") != "multipart":
        field = req.get("edit_image_field", "image") if edit else req.get("image_field", "image")
        payload[field] = images_enc if len(images_enc) > 1 else images_enc[0]
    if n > 1:
        nprov = pmap.get("variations", "n")
        if nprov:
            assign(payload, nprov, n)
    return payload


def build_gemini(row, prompt, model, params, images_enc, n, edit):
    parts = [{"text": prompt}]
    for e in images_enc:
        parts.append({"inline_data": {"mime_type": e.get("mime_type", "image/png") if isinstance(e, dict) else "image/png",
                                      "data": e.get("data", e) if isinstance(e, dict) else e}})
    body = {"contents": [{"role": "user", "parts": parts}]}
    for k, v in (row["request"].get("extra_defaults") or {}).items():
        body[k] = v
    if params.get("size"):
        gc = body.setdefault("generationConfig", {})
        gc.setdefault("imageConfig", {})["aspectRatio"] = params["size"]
    return body


BUILDERS = {"openai_json": build_openai, "gemini_json": build_gemini}


def multipart_body(fields, files):
    """fields: dict; files: list of (field_name, filename, mime, bytes)."""
    boundary = uuid.uuid4().hex
    buf = bytearray()
    for k, v in fields.items():
        if v is None:
            continue
        buf += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for name, fname, mime, data in files:
        buf += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{fname}"\r\nContent-Type: {mime}\r\n\r\n'.encode()
        buf += data + b"\r\n"
    buf += f"--{boundary}--\r\n".encode()
    return bytes(buf), boundary

# ---------------------------------------------------------------- provider call

def extract_assets(resp_obj, rcfg):
    assets = []
    for p in rcfg.get("urls", []):
        v = dig(resp_obj, p)
        if isinstance(v, str) and v.startswith("http"):
            assets.append({"kind": "url", "value": v})
    for p in rcfg.get("b64", []):
        v = dig(resp_obj, p)
        if isinstance(v, str) and v:
            assets.append({"kind": "b64", "value": v, "mime": "image/png"})
    parts = dig(resp_obj, rcfg["parts_path"]) if rcfg.get("parts_path") else None
    if isinstance(parts, list):
        for part in parts:
            inline = part.get("inlineData") or part.get("inline_data") if isinstance(part, dict) else None
            if inline and inline.get("data"):
                assets.append({"kind": "b64", "value": inline["data"],
                               "mime": inline.get("mimeType") or inline.get("mime_type") or "image/png"})
    return assets


class Cfg:
    pass


def submit_and_track(row, key, payload, cfg):
    """One request through submit (async or sync) + poll; returns result dict."""
    ep = row["endpoints"]["edit" if cfg.edit else "generate"]
    url = row["base_url"].rstrip("/") + render_endpoint(ep, model=cfg.model)
    headers = auth_headers(row, key)
    t0 = time.time()
    if cfg.multipart_files is not None:
        body, boundary = multipart_body(payload, cfg.multipart_files)
        code, resp, _ = http_request(url, {**headers, "Content-Type": f"multipart/form-data; boundary={boundary}"},
                                     body=body, timeout=cfg.timeout)
    else:
        code, resp, _ = http_request(url, headers, body=payload, timeout=cfg.timeout)
    out = {"http": code, "error": None, "job_id": None, "status": None, "assets": [], "usage": None}
    if not isinstance(resp, dict):
        resp = {"raw": str(resp)[:400]}
    if code not in (200, 201, 202):
        out["error"] = f"HTTP {code}: {json.dumps(resp, default=str)[:300]}"
        return out
    rcfg = row["response"]
    out["usage"] = dig(resp, rcfg["usage_path"]) if rcfg.get("usage_path") else None
    out["assets"] = extract_assets(resp, rcfg)
    if row["request"]["mode"] == "submit-poll" and not out["assets"]:
        job_id = dig(resp, rcfg.get("job_id_path", "id"))
        out["job_id"] = job_id
        if not job_id:
            out["error"] = f"no job id in submit response: {json.dumps(resp, default=str)[:300]}"
            return out
        poll_url_tpl = row["endpoints"]["poll"]
        deadline = t0 + cfg.max_wait
        statuses = set()
        while time.time() < deadline:
            time.sleep(cfg.poll_interval)
            code2, pr, _ = http_request(row["base_url"].rstrip("/") + poll_url_tpl.replace("{id}", str(job_id)),
                                        headers, timeout=cfg.timeout)
            if code2 not in (200, 202) or not isinstance(pr, dict):
                out["error"] = f"poll HTTP {code2}"
                return out
            st = dig(pr, rcfg.get("status_path", "status"))
            if st not in statuses:
                statuses.add(st)
                cfg.report_state(cfg, out, st, time.time() - t0)
            if st in rcfg.get("failed", []):
                err = dig(pr, rcfg.get("error_path", "error")) if rcfg.get("error_path") else None
                out["error"] = f"job failed: {json.dumps(err, default=str)[:300] if err else st}"
                out["status"] = st
                return out
            if st in rcfg.get("succeeded", []):
                out["status"] = st
                out["usage"] = dig(pr, rcfg["usage_path"]) if rcfg.get("usage_path") else out["usage"]
                out["assets"] = extract_assets(pr, rcfg)
                if not out["assets"]:
                    out["error"] = "job succeeded but no image found in response"
                return out
        out["error"] = f"poll timeout after {cfg.max_wait}s (last status: {sorted(statuses)[-1] if statuses else 'none'})"
        return out
    out["status"] = out["status"] or "succeeded"
    if not out["assets"] and not out["error"]:
        out["error"] = f"no image in response: {json.dumps(resp, default=str)[:300]}"
    return out

# ---------------------------------------------------------------- context

def context_path(state_dir, cid):
    return state_dir / "contexts" / f"{cid}.json"


def new_context(system_text, label):
    return {"id": uuid.uuid4().hex[:8], "label": label, "system": system_text,
            "created": now_ts(), "updated": now_ts(),
            "turns": [{"role": "system", "content": system_text}] if system_text else []}


def atomic_write_json(path: Path, obj):
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)  # atomic on Windows + POSIX: readers see old or new, never partial


class ContextLock:
    """Cross-process advisory lock (O_CREAT|O_EXCL), stale-broken after 30s,
    gives up with a clear message after 15s so a wedged terminal can't hang a run."""
    TIMEOUT, STALE = 15.0, 30.0

    def __init__(self, target: Path):
        self.path = Path(str(target) + ".lock")
        self.fd = None
        self.timeout = float(os.environ.get("GENIMAGE_LOCK_TIMEOUT", self.TIMEOUT))

    def __enter__(self):
        t0 = time.time()
        while True:
            try:
                self.fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, f"pid={os.getpid()} ts={now_ts()}".encode())
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(str(self.path)) > self.STALE:
                        os.unlink(str(self.path))
                        warn(f"broke stale context lock (>{self.STALE:.0f}s): {self.path.name}")
                        continue
                except OSError:
                    continue
                if time.time() - t0 > self.timeout:
                    sys.exit(f"context busy: {self.path.name} locked by another process "
                             f"for >{self.timeout:.0f}s — finish or close the other session")
                time.sleep(0.1)

    def __exit__(self, *exc):
        try:
            if self.fd is not None:
                os.close(self.fd)
            os.unlink(str(self.path))
        except OSError:
            pass
        return False


def save_context(state_dir, ctx):
    """Full replace — only for creating a context or sole-owner rewrites."""
    state_dir = Path(state_dir)
    (state_dir / "contexts").mkdir(parents=True, exist_ok=True)
    with ContextLock(context_path(state_dir, ctx["id"])):
        ctx["updated"] = now_ts()
        atomic_write_json(context_path(state_dir, ctx["id"]), ctx)


def append_turns(state_dir, cid, turns):
    """Multi-process-safe writeback: reload under lock, merge turns, atomic save.
    Concurrent sessions keep each other's history instead of overwriting."""
    state_dir = Path(state_dir)
    p = context_path(state_dir, cid)
    with ContextLock(p):
        disk = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else new_context(None, cid)
        disk["turns"] = disk.get("turns", []) + turns
        disk["updated"] = now_ts()
        atomic_write_json(p, disk)


def create_context_unique(state_dir, system_text, label):
    """New id, never clobbering an existing file even if two --context new race."""
    state_dir = Path(state_dir)
    (state_dir / "contexts").mkdir(parents=True, exist_ok=True)
    for _ in range(5):
        ctx = new_context(system_text, label)
        p = context_path(state_dir, ctx["id"])
        with ContextLock(p):
            if p.exists():
                continue
            ctx["updated"] = now_ts()
            atomic_write_json(p, ctx)
            return ctx
    sys.exit("could not allocate a fresh context id (repeated collisions)")


def save_branch_context(state_dir, branch):
    """Fork branches get their own file; on cross-run id collision bump a suffix."""
    state_dir = Path(state_dir)
    base_id = branch["id"]
    for n in range(2, 30):
        cid = base_id if n == 2 else f"{base_id}-b{n}"
        branch["id"] = cid
        p = context_path(state_dir, cid)
        with ContextLock(p):
            if not p.exists():
                branch["updated"] = now_ts()
                atomic_write_json(p, branch)
                return cid
    sys.exit(f"too many existing branch contexts for {base_id}")


def load_context(state_dir, cid):
    p = context_path(Path(state_dir), cid)
    if not p.is_file():
        sys.exit(f"context '{cid}' not found at {p}")
    with ContextLock(p):  # read a consistent snapshot even mid-write
        return json.loads(p.read_text(encoding="utf-8"))


def compose_prompt(ctx, prompt, depth=3):
    """Flatten saved context into an image-capable prompt; prior turns as brief history."""
    if not ctx:
        return prompt
    lines = []
    for t in ctx["turns"][-depth:]:
        if t["role"] == "assistant":
            lines.append(f"[earlier result] {t['content'][:200]}")
        elif t["role"] == "user":
            lines.append(f"[earlier request] {t['content'][:200]}")
    hist = "\n".join(lines)
    sysp = ctx.get("system") or ""
    parts = [p for p in (sysp.strip(), hist, f"[new request] {prompt}") if p]
    return "\n\n".join(parts)


def context_ref_images(ctx, cap):
    imgs = []
    for t in reversed(ctx["turns"]):
        for img in t.get("images", []):
            if t["role"] == "assistant":
                imgs.append(img)
    return imgs[:cap]

# ---------------------------------------------------------------- output

def render_table(results):
    hdr = ["#", "job", "model", "status", "time", "cost(est)", "output", "error"]
    rows = []
    for i, r in enumerate(results, 1):
        rows.append([str(i), r.get("job_id") or "-", r.get("model") or "-",
                     "OK" if not r.get("error") else "FAIL",
                     f"{r.get('elapsed', 0):.1f}s", r.get("cost") or "-",
                     r.get("out") or "-", (r.get("error") or "")[:80]])
    w = [max(len(hdr[c]), *(len(row[c]) for row in rows)) if rows else len(hdr[c]) for c in range(len(hdr))]
    line = lambda cells: "| " + " | ".join(c.ljust(w[i]) for i, c in enumerate(cells)) + " |"
    sep = "|" + "|".join("-" * (w[i] + 2) for i in range(len(hdr))) + "|"
    return "\n".join([line(hdr), sep, *[line(r) for r in rows]])


def progress_bar(done, total, ok, fail, running, elapsed, enabled, state):
    if total <= 0:
        return
    width = 24
    filled = int(width * done / total)
    bar = "#" * filled + "." * (width - filled)
    eta = "-"
    if done:
        eta = f"~{int((total - done) * (elapsed / done))}s"
    txt = f"\r[{bar}] {done}/{total} done | ok {ok} | fail {fail} | running {running} | {elapsed:.0f}s eta {eta}"
    if enabled:
        sys.stderr.write("\r" + " " * state.get("last_w", 0) + "\r")
        sys.stderr.write(txt)
        sys.stderr.flush()
        state["last_w"] = len(txt)
    elif time.time() - state.get("last_print", 0) > 15:
        state["last_print"] = time.time()
        warn(txt.lstrip("\r"))

# ---------------------------------------------------------------- cost

def estimate_cost(row, result):
    pricing = row.get("pricing", {})
    usage = result.get("usage") if isinstance(result.get("usage"), dict) else {}
    bits, est = [], None
    credits = usage.get("credits_used", usage.get("credits"))
    if credits is not None and pricing.get("credit_usd"):
        try:
            est = float(credits) * float(pricing["credit_usd"])
            bits.append(f"${est:.4f}")
        except (TypeError, ValueError):
            pass
    tokens = usage.get("total_tokens") or usage.get("tokens") or dig(usage, "usage.total_tokens")
    if tokens:
        bits.append(f"{tokens} tok")
    if est is None and not result.get("error"):
        rates = pricing.get("rates") or {}
        model = result.get("model") or ""
        rate = rates.get(f"{model}|{result.get('resolution')}") or rates.get(model)
        if rate is not None:
            est = float(rate) * max(1, result.get("n_results", 1))
            bits.insert(0, f"~${est:.4f}")
        elif not bits:
            return "-" if result.get("error") else "n/a"
    return " ".join(bits) if bits else ("-" if result.get("error") else "n/a")

# ---------------------------------------------------------------- ledger

def write_ledger(state_dir, entry):
    state_dir.mkdir(parents=True, exist_ok=True)
    with open(state_dir / "usage.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="genimage", description="Universal registry-driven image generation (see module docstring)")
    ap.add_argument("--prompt")
    ap.add_argument("--prompts-file", help="one prompt per line; used with --batch")
    ap.add_argument("--provider")
    ap.add_argument("--api-key", dest="api_key", metavar="KEY",
                    help="explicit API key (env var is preferred; the value is never echoed — "
                         "CLI args are visible in process lists and shell history)")
    ap.add_argument("--model")
    ap.add_argument("--size")
    ap.add_argument("--resolution")
    ap.add_argument("--quality")
    ap.add_argument("--variations", type=int, default=1)
    ap.add_argument("--image", action="append", default=[], help="URL or path; repeatable")
    ap.add_argument("--edit", action="store_true")
    ap.add_argument("--batch", type=int, default=0, help="run N requests concurrently")
    ap.add_argument("--concurrency", type=int, default=0)
    ap.add_argument("--context", help="'new' to start a context, or an existing context id")
    ap.add_argument("--batch-context", action="store_true", help="batch shares the given context as base")
    ap.add_argument("--system", default=None, help="system prompt when starting a context")
    ap.add_argument("--label", default=None, help="context label")
    ap.add_argument("--state-dir", default=None, help="default ./.genimage (contexts/ + usage.jsonl)")
    ap.add_argument("--registry", default=None)
    ap.add_argument("--out", default="./genimage-out", help="file (single job) or directory")
    ap.add_argument("--out-dir", default=None, help="explicit output directory (wins over --out)")
    ap.add_argument("--name-format", default=None,
                    help="filename template in dir mode; placeholders: {slug} {index} {n} {provider} "
                         "{model} {ext} {date} {time} {ts}  (default '{slug}-{index}', extension appended)")
    ap.add_argument("--no-download", action="store_true", help="keep remote URLs instead of saving bytes")
    ap.add_argument("--poll-interval", type=float, default=3.0)
    ap.add_argument("--max-wait", type=float, default=600.0)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--plain", action="store_true", help="no animated progress (CI/logs)")
    ap.add_argument("--json", action="store_true", help="machine-readable result on stdout")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--usage", action="store_true", help="query provider usage/balance endpoint")
    ap.add_argument("--salvage", action="store_true",
                    help="re-download lost/missing results from .genimage/results.jsonl URLs (never rely on memory)")
    ap.add_argument("--list-providers", action="store_true")
    args = ap.parse_args()

    reg_path = Path(args.registry) if args.registry else DEFAULT_REGISTRY
    if not reg_path.is_file():
        sys.exit(f"registry not found: {reg_path}")
    rows = load_registry(reg_path)
    state_dir = Path(args.state_dir or STATE_DIR_DEFAULT)

    if args.list_providers:
        for r in sorted(rows, key=lambda x: x["priority"]):
            feats = ", ".join(k for k, v in r["features"].items() if v is True)
            ek = env_key(r)
            print(f"{r['provider_id']:12} priority {r['priority']:>3}  keys: {' '.join(r['auth']['env']):38} "
                  f"{('KEY ' + mask_key(ek)) if ek else '      '}  features: {feats}")
            print(f"{'':12} models: {', '.join(r['models'].get('known', [])[:6])}")
        return 0

    row, key = pick_provider(rows, args.provider, override_key=args.api_key)
    if args.api_key:
        key_source = f"--api-key (masked: {mask_key(args.api_key)})"
        warn(f"api key supplied via --api-key: {mask_key(args.api_key)} — prefer the env var "
             f"({row['auth']['env'][0]}) so the key stays out of process listings")
    else:
        key_source = "env " + next((n for n in row["auth"]["env"] if os.environ.get(n)), row["auth"]["env"][0])
    feats = row["features"]
    model = args.model or row["models"].get("default")
    if not model:
        sys.exit(f"provider {row['provider_id']} has no default model; pass --model")

    if args.usage:
        if not feats.get("usage_endpoint") or "usage" not in row["endpoints"]:
            sys.exit(f"provider {row['provider_id']} has no usage endpoint (features.usage_endpoint=false)")
        code, resp, _ = http_request(row["base_url"].rstrip("/") + row["endpoints"]["usage"], auth_headers(row, key))
        print(json.dumps(resp, indent=2, default=str) if isinstance(resp, dict) else resp)
        return 0 if code == 200 else 1

    if args.salvage:
        # Recover files from the durable URL manifest — never from memory.
        mfile = state_dir / "results.jsonl"
        if not mfile.is_file():
            sys.exit(f"no results manifest at {mfile} — nothing to salvage")
        last = {}
        for line in mfile.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("job") and rec.get("kind") in ("received", "done"):
                if rec["kind"] == "done" or rec["job"] not in last:
                    last[rec["job"]] = rec
        rows_by_id = {r["provider_id"]: r for r in rows}
        need = []
        for jid, rec in last.items():
            saved = rec.get("saved") or []
            for i, u in enumerate(rec.get("urls") or []):
                s = saved[i] if i < len(saved) else None
                if not (s and not str(s).startswith("http") and Path(s).is_file()):
                    need.append((jid, rec, i, u, s))
        if not need:
            print("salvage: every recorded URL already has its file on disk — nothing to do")
            return 0
        out_dir = Path(args.out_dir or args.out)
        got, lost = [], []
        for jid, rec, i, u, s in need:
            prow = rows_by_id.get(rec.get("provider") or "")
            pkey = (args.api_key or env_key(prow)) if prow else None
            dest = Path(s) if s and not str(s).startswith("http") \
                else out_dir / f"{slugify(rec.get('prompt') or 'image')}-{jid}-{i + 1}.png"
            data = fetch_bytes(u, auth_headers(prow, pkey) if prow and pkey and same_host(u, prow["base_url"]) else None)
            rec_kind = {"kind": "salvaged", "provider": rec.get("provider"), "job": jid,
                        "urls": [u], "saved": [str(dest)] if data else [],
                        "status": "ok" if data else "error"}
            if data:
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_name(dest.name + f".tmp.{os.getpid()}")
                tmp.write_bytes(data)
                os.replace(tmp, dest)
                got.append(str(dest))
            else:
                rec_kind["error"] = "url dead or expired"
                lost.append(u)
            append_manifest(state_dir, rec_kind)
        for o in got:
            print(f"recovered: {o}")
        for u in lost:
            warn(f"salvage failed (link dead or expired): {u}")
        print(f"\nsalvage: {len(got)} recovered, {len(lost)} unrecoverable")
        return 0 if not lost else 1

    # ---- build job list -----------------------------------------------------
    prompts = []
    if args.prompts_file:
        prompts = [l.strip() for l in Path(args.prompts_file).read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.prompt:
        prompts.insert(0, args.prompt) if args.prompt not in prompts else None
    if not prompts:
        sys.exit("nothing to do: pass --prompt and/or --prompts-file")
    n_units = 1
    if args.variations > 1:
        if feats.get("n"):
            n_units = -1  # provider-side batch in one request
        # else: client-side fan-out handled below
    jobs = []
    for p in prompts:
        reps = 1 if n_units == -1 else (args.variations if args.variations > 1 else 1)
        jobs.extend([p] * reps)
    if args.batch:
        if not args.prompts_file and args.variations <= 1 and args.batch > len(jobs):
            jobs = prompts * args.batch  # --batch N on one prompt = N concurrent variations
        jobs = jobs[:args.batch] if args.batch < len(jobs) else jobs
    if n_units == -1 and len(jobs) > 1:
        jobs = jobs  # each request carries n=variations

    # ---- images -------------------------------------------------------------
    images = [load_image(s) for s in args.image]
    if images and not (feats.get("i2i") or feats.get("edit")):
        sys.exit(f"provider {row['provider_id']} declares no image-input support (features.i2i/edit). "
                 f"Choose another provider with --list-providers.")
    if args.edit and not feats.get("edit"):
        sys.exit(f"provider {row['provider_id']} has no edit endpoint. Supports: "
                 f"{'i2i' if feats.get('i2i') else ''}t2i — see --list-providers.")
    cap = feats.get("max_ref_images") or 1
    if len(images) > cap:
        warn(f"trimming {len(images)} input images to provider cap of {cap}")
        images = images[:cap]

    # ---- context ------------------------------------------------------------
    ctx = None
    if args.context == "new":
        ctx = create_context_unique(state_dir, args.system, args.label or (jobs[0][:40] if jobs else "ctx"))
        warn(f"context created: {ctx['id']}")
    elif args.context:
        ctx = load_context(state_dir, args.context)
    if ctx:
        ctx = json.loads(json.dumps(ctx))  # immutable snapshot: workers only read

    params = {"size": args.size, "resolution": args.resolution, "quality": args.quality}

    # ---- dry-run ------------------------------------------------------------
    if args.dry_run:
        def shrink(o):
            if isinstance(o, str) and len(o) > 72:
                return o[:58] + f"…<len {len(o)}>"
            if isinstance(o, dict):
                return {k: shrink(v) for k, v in o.items()}
            if isinstance(o, list):
                return [shrink(v) for v in o]
            return o
        preview_ctx = ctx
        shown = []
        for j, p in enumerate(jobs[:3]):
            eff_prompt = compose_prompt(preview_ctx, p) if preview_ctx else p
            payload = BUILDERS[row["request"]["builder"]](row, eff_prompt, model, params,
                                                          encode_images(images, row["request"].get("image_format", "b64"), None),
                                                          max(args.variations, 1), args.edit)
            shown.append({"job": j + 1, "endpoint": row["endpoints"]["edit" if args.edit else "generate"],
                          "model": model, "payload": shrink(payload)})
        print(json.dumps({"provider": row["provider_id"],
                          "auth": row["auth"]["header"] + f": <redacted — {key_source}>",
                          "requests": shown,
                          "total_jobs": len(jobs), "context": (ctx or {}).get("id")},
                         indent=2, default=str))
        return 0

    # ---- run ----------------------------------------------------------------
    results = [None] * len(jobs)
    lock = threading.Lock()
    state = {"done": 0, "ok": 0, "fail": 0, "t0": time.time()}
    is_tty = sys.stderr.isatty() and not args.plain and len(jobs) > 1
    bar_state = {}

    def report_state(cfg, out, st, elapsed):
        if len(jobs) == 1:
            warn(f"job {out.get('job_id') or ''} status={st} elapsed={elapsed:.0f}s")

    # attach report_state via cfg? simpler: closure poll prints inside submit via cfg hook
    def run_job(idx, prompt):
        cfg = Cfg()
        cfg.edit = bool(args.edit)
        cfg.model = model
        cfg.timeout = args.timeout
        cfg.max_wait = args.max_wait
        cfg.poll_interval = args.poll_interval
        cfg.multipart_files = None
        cfg.report_state = lambda c, o, st, el: (len(jobs) == 1 and warn(f"status={st} elapsed={el:.0f}s")) or None
        job_ctx = ctx  # snapshot base; --batch-context and single-context both read this

        eff_prompt = compose_prompt(job_ctx, prompt) if job_ctx else prompt
        enc = encode_images(images, row["request"].get("image_format", "b64"), None)
        if job_ctx:
            for src in context_ref_images(job_ctx, max(cap - len(images), 0)):
                mime, data = load_image(src)
                enc.append({"mime_type": mime, "data": base64.b64encode(data).decode()}
                           if row["request"].get("image_format") == "inline_b64"
                           else f"data:{mime};base64," + base64.b64encode(data).decode())
        payload = BUILDERS[row["request"]["builder"]](row, eff_prompt, model, params, enc,
                                                      args.variations if n_units == -1 else 1, cfg.edit)
        if row["request"].get("image_format") == "multipart" and images:
            files = [(row["request"].get("edit_image_field", "image"), f"img{i}.png", mime, data)
                     for i, (mime, data) in enumerate(images)]
            cfg.multipart_files = files
        t_start = time.time()
        res = submit_and_track(row, key, payload, cfg)
        res["model"] = model
        res["resolution"] = args.resolution
        res["elapsed"] = time.time() - t_start
        asset_urls = [a["value"] for a in res["assets"] if a["kind"] == "url"]
        if asset_urls:
            # record BEFORE saving: if the process dies or links expire later,
            # the URLs are already on disk
            append_manifest(state_dir, {"kind": "received", "provider": row["provider_id"], "model": model,
                                        "job": res.get("job_id"), "urls": asset_urls, "prompt": prompt[:160]})
        # save outputs (atomic: bytes land in a temp file, then os.replace to final name)
        n_ok = 0
        outs = []
        base_out = args.out_dir or args.out
        KNOWN_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        for a in res["assets"]:
            if args.no_download and a["kind"] == "url":
                outs.append(a["value"])
                n_ok += 1
                continue
            explicit_file = (len(jobs) == 1 and not args.out_dir and args.name_format is None
                             and str(base_out).strip() and not str(base_out).endswith(("/", os.sep))
                             and Path(base_out).suffix.lower() in KNOWN_EXT)
            if explicit_file:
                dest = Path(base_out)
            else:
                d = Path(base_out)
                fmt = args.name_format or "{slug}-{index}"
                try:
                    name = fmt.format(slug=slugify(prompt), index=idx + 1, n=n_ok + 1,
                                      provider=row["provider_id"],
                                      model=re.sub(r"[^A-Za-z0-9._-]", "-", str(model)),
                                      ext="png", date=time.strftime("%Y%m%d"),
                                      time=time.strftime("%H%M%S"), ts=int(time.time()))
                except KeyError as e:
                    sys.exit(f"--name-format: unknown placeholder {e} (allowed: slug index n provider model ext date time ts)")
                if Path(name).suffix.lower() not in KNOWN_EXT:
                    name += ".png"
                dest = d / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = None
            if a["kind"] == "url":
                data = fetch_bytes(a["value"], auth_headers(row, key) if same_host(a["value"], row["base_url"]) else None)
                if data is None:
                    warn(f"download failed, keeping URL: {a['value']}")
                    outs.append(a["value"])
                    res.setdefault("pending_urls", []).append(a["value"])
                    n_ok += 1
                    continue
            else:
                data = base64.b64decode(a["value"])
            tmp = dest.with_name(dest.name + f".tmp.{os.getpid()}.{n_ok}")
            try:
                tmp.write_bytes(data)
                os.replace(tmp, dest)  # atomic rename: no torn/partial final files
                outs.append(str(dest))
            except OSError as e:
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
                res["error"] = res["error"] or f"save failed for {dest}: {e}"
            n_ok += 1
        res["out"] = outs[0] if len(outs) == 1 else ("; ".join(outs) if outs else None)
        res["outs"] = outs
        res["n_results"] = n_ok
        res["cost"] = estimate_cost(row, res)
        if res["error"] is None and n_ok == 0:
            res["error"] = "no image bytes saved"
        with lock:
            results[idx] = res
            state["done"] += 1
            state["ok" if not res["error"] else "fail"] += 1
            progress_bar(state["done"], len(jobs), state["ok"], state["fail"],
                         max(0, min(concurrency, len(jobs) - state["done"])),
                         time.time() - state["t0"], is_tty, bar_state)
            write_ledger(state_dir, {"ts": now_ts(), "provider": row["provider_id"], "model": model,
                                     "job": res.get("job_id"), "status": "ok" if not res["error"] else "fail",
                                     "prompt": prompt[:160], "cost": res.get("cost"), "usage": res.get("usage"),
                                     "urls": asset_urls, "out": outs, "error": res.get("error")})
            append_manifest(state_dir, {"kind": "done", "provider": row["provider_id"], "model": model,
                                        "job": res.get("job_id"), "status": "ok" if not res["error"] else "error",
                                        "urls": asset_urls, "saved": outs, "prompt": prompt[:160],
                                        "error": res.get("error")})
        return res

    concurrency = args.concurrency or min(len(jobs), feats.get("max_concurrent") or 10, 10)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, concurrency)) as ex:
        futs = [ex.submit(run_job, i, p) for i, p in enumerate(jobs)]
        for f in concurrent.futures.as_completed(futs):
            f.result()  # surface thread crashes
    if is_tty:
        sys.stderr.write("\n")

    # ---- context write-back --------------------------------------------------
    if ctx:
        ok = [r for r in results if r and not r["error"]]
        if len(jobs) == 1 or args.batch_context or feats.get("n"):
            # merge-append under lock: a concurrent session's turns survive
            user_turn = {"role": "user", "content": jobs[0] if len(jobs) == 1 else f"batch of {len(jobs)}",
                         "images": args.image}
            summary = (f"generated {len(ok)} image(s) via {row['provider_id']}/{model}"
                       + (f"; outputs: {[r['out'] for r in ok][:3]}" if ok else ""))
            assistant_turn = {"role": "assistant", "content": summary,
                              "images": [o for r in ok for o in r.get("outs", [])]}
            append_turns(state_dir, ctx["id"], [user_turn, assistant_turn])
        else:
            # independent per-job branches of the same base context
            for i, r in enumerate(results):
                if not r:
                    continue
                branch = json.loads(json.dumps(ctx))
                branch["id"] = f"{ctx['id']}-j{i + 1}"
                branch["turns"] += [{"role": "user", "content": jobs[i]},
                                    {"role": "assistant", "content": r.get("out") or r.get("error"),
                                     "images": r.get("outs", [])}]
                save_branch_context(state_dir, branch)
        warn(f"context {ctx['id']} updated")

    # ---- final report --------------------------------------------------------
    totals = {"jobs": len(results), "ok": sum(1 for r in results if r and not r["error"]),
              "images": sum(r.get("n_results", 0) for r in results if r)}
    pending = [u for r in results if r for u in r.get("pending_urls", [])]
    if args.json:
        print(json.dumps({"provider": row["provider_id"], "model": model, "context": (ctx or {}).get("id"),
                          "totals": {**totals, "pending_urls": len(pending)}, "results": [{k: v for k, v in r.items() if k != 'usage'} for r in results]},
                         indent=2, default=str))
    else:
        print()
        print(render_table([r or {"error": "not executed"} for r in results]))
        print(f"\nprovider {row['provider_id']} · model {model} · {totals['ok']}/{totals['jobs']} ok "
              f"· {totals['images']} images · context {(ctx or {}).get('id', '-')}")
        print(f"ledger: {state_dir / 'usage.jsonl'}")
        print(f"url manifest: {state_dir / 'results.jsonl'} — every provider URL recorded at receipt; "
              f"re-download anything lost later with --salvage")
        if pending:
            print(f"NOT complete: {len(pending)} result URL(s) not downloadable — kept in the manifest; "
                  f"retry with --salvage or accept the loss")
        if row["pricing"].get("notes"):
            print(f"pricing note: {row['pricing']['notes']}")
    return 0 if totals["ok"] == totals["jobs"] and not pending else 1


if __name__ == "__main__":
    sys.exit(main())
