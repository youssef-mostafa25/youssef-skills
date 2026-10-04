#!/usr/bin/env python3
"""Ephemeral localhost log sink for the debug-log-sink skill — zero deps (stdlib).

Copy this to the PROJECT ROOT and run it; do not write one from scratch. It
implements the skill spec: binds 127.0.0.1:9988 only, exposes POST/OPTIONS
/debug-log-sink/log with permissive CORS, appends one flushed line per request
to debug-log-sink.log and writes debug-log-sink.pid next to this script. Tolerant:
never returns 4xx/5xx (a debug logger must never break client code).

Start:  nohup python3 debug-log-sink.py > /dev/null 2>&1 &
Files are prefixed debug-log-sink.* so `rm -f debug-log-sink.*` is a total teardown.
Never commit; keep at the project root. If 9988 is taken, change PORT below but
KEEP the URL path/marker so cleanup grep still finds every call site.
"""
import json
import os
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = "127.0.0.1", 9988
ROOT = os.path.dirname(os.path.abspath(__file__))  # the project root it was copied to
LOG = os.path.join(ROOT, "debug-log-sink.log")
PID = os.path.join(ROOT, "debug-log-sink.pid")
_fh = open(LOG, "a", buffering=1)  # line-buffered so logs survive a hard kill


class Handler(BaseHTTPRequestHandler):
    def _respond(self, code=204):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._respond(204)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}") if n else {}
        except Exception:
            payload = {}
        try:
            ts = datetime.now().isoformat()
            line = f"{ts} [{payload.get('level', 'info')}] [{payload.get('source', '?')}] {payload.get('message', '')}"
            if payload.get("data") is not None:
                line += " | data=" + json.dumps(payload["data"], default=str)
            _fh.write(line + "\n")
            _fh.flush()
        except Exception:
            pass
        self._respond(204)

    def log_message(self, *args):  # silence per-request stderr access logs
        pass


def main():
    # Bind before writing the PID so a port clash leaves no stale PID file behind.
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    with open(PID, "w") as f:
        f.write(str(os.getpid()))
    sys.stderr.write(f"debug-log-sink listening on http://{HOST}:{PORT}/debug-log-sink/log -> {LOG}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
