#!/usr/bin/env python3
"""F6 blind-SSRF proof: a loopback "internal service" that logs any request it
receives and stands in for a sensitive loopback endpoint (the Chrome DevTools
debug port, or a cloud metadata service).

If Agent-Reach's bilibili resolver can be steered to issue a request here, then the
naive `"b23.tv/" in t` substring gate let attacker-controlled input pivot a
server-side request into a loopback target the tool should never contact (SSRF).

SANDBOX ONLY.
"""
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

BODY = b"internal-service-content (a real CDP/metadata endpoint would return secrets here)"


class Handler(BaseHTTPRequestHandler):
    def _hit(self, with_body: bool) -> None:
        print("\n*** SSRF LANDED ***")
        print(f"[target] Agent-Reach issued a {self.command} to this internal service "
              f"it should never reach:")
        print(f"  {self.command} {self.path}")
        print(f"  User-Agent: {self.headers.get('User-Agent')}")
        self.send_response(200)
        self.send_header("Content-Length", str(len(BODY)) if with_body else "0")
        self.end_headers()
        if with_body:
            self.wfile.write(BODY)

    def do_HEAD(self) -> None:
        self._hit(with_body=False)

    def do_GET(self) -> None:
        self._hit(with_body=True)

    def log_message(self, *a) -> None:
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9222
    print(f"[target] fake INTERNAL service (CDP/metadata stand-in) on http://127.0.0.1:{port}")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
