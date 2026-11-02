"""Test localize.py against a local HTTP server (no external network)."""
import http.server
import os
import socketserver
import subprocess
import sys
import threading

root = os.path.dirname(os.path.abspath(__file__))
serve = os.path.join(root, "serve")
os.makedirs(serve, exist_ok=True)
with open(os.path.join(serve, "logo.png"), "wb") as f:
    f.write(open(os.path.join(root, "raw", "logo.png"), "rb").read())
with open(os.path.join(serve, "Inter.woff2"), "wb") as f:
    f.write(b"wOF2" + b"\x00" * 64)

os.chdir(serve)
handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
port = httpd.server_address[1]
thread = threading.Thread(target=httpd.serve_forever, daemon=True)
thread.start()

manifest = os.path.join(root, "vendor-local.txt")
with open(manifest, "w", encoding="utf-8") as f:
    f.write(f"http://127.0.0.1:{port}/logo.png icons/logo.png\n")
    f.write(f"http://127.0.0.1:{port}/Inter.woff2 fonts/Inter.woff2\n")

script = os.path.join(root, "..", "..", "Groups", "Design", "assets", "scripts", "localize.py")
result = subprocess.run(
    [sys.executable, script, "--manifest", manifest, "--out", os.path.join(root, "out", "vendor")],
    capture_output=True, text=True, cwd=root)
httpd.shutdown()

print(result.stdout)
print(result.stderr)
print("exit:", result.returncode)
for rel in ("icons/logo.png", "fonts/Inter.woff2"):
    path = os.path.join(root, "out", "vendor", rel)
    print(rel, "exists:", os.path.exists(path), "size:", os.path.getsize(path) if os.path.exists(path) else 0)
