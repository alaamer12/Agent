#!/usr/bin/env python3
"""Serve an Inquire page on localhost and print the user's answers to the console.

usage: serve.py page.html [--port 0] [--timeout 1800] [--out answers.json] [--no-open]

Output markers the agent should look for:
  INQUIRE_URL=<url>                         printed once the server is up
  INQUIRE_ANSWERS_BEGIN ... INQUIRE_ANSWERS_END   the JSON, on Submit or Skip
  INQUIRE_SKIPPED                           printed before the JSON when the user skipped
Exit codes: 0 answered/skipped, 2 timed out.
"""
import argparse, http.server, json, pathlib, sys, threading, webbrowser


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--out", default="answers.json")
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args()
    page = pathlib.Path(a.page).read_bytes()
    done = threading.Event()
    result = {}

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep the console clean for the agent
            pass

        def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path.split("?")[0] in ("/", "/index.html"):
                self._send(200, page, "text/html; charset=utf-8")
            else:
                self._send(404, b"not found")

        def do_POST(self):
            if self.path != "/submit":
                return self._send(404, b"not found")
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            try:
                data = json.loads(raw.decode("utf-8"))
            except Exception:
                return self._send(400, b"invalid json")
            self._send(200, b"ok")
            result["data"] = data
            done.set()

    srv = http.server.ThreadingHTTPServer((a.host, a.port), H)
    url = f"http://{a.host}:{srv.server_address[1]}/"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"INQUIRE_URL={url}", flush=True)
    if not a.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    if not done.wait(a.timeout):
        print("INQUIRE_TIMEOUT", flush=True)
        srv.shutdown()
        sys.exit(2)
    data = result["data"]
    pathlib.Path(a.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if data.get("skipped"):
        print("INQUIRE_SKIPPED", flush=True)
    print("INQUIRE_ANSWERS_BEGIN")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("INQUIRE_ANSWERS_END", flush=True)
    srv.shutdown()


if __name__ == "__main__":
    main()
