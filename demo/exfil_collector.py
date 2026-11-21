#!/usr/bin/env python3
"""Localhost 'attacker drop point' for the cookie-exfil demo.

Captures whatever is POSTed to it and prints it. This stands in for an
attacker-controlled server WITHOUT any data leaving the machine -- it binds to
127.0.0.1 only. A real attacker would hardcode their own https URL in the bait.

RUN IN THE THROWAWAY SANDBOX ONLY. The whole point is to show that an injection
can read Agent-Reach's plaintext session cookies (F5) and egress them.

    python3 demo/exfil_collector.py &      # start the sink
    # ... run the exfil bait through victim_agent.py ...
"""
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode("utf-8", "replace")
        print("\n*** EXFIL RECEIVED ***")
        print(f"[collector] {len(body)} bytes stolen from the reader and sent to the "
              f"attacker sink ({self.path}):")
        print(body)
        proof = os.environ.get("EXFIL_PROOF_FILE")
        if proof:
            try:
                with open(proof, "w", encoding="utf-8") as fh:
                    fh.write(body)
            except OSError:
                pass
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a) -> None:  # silence default request logging
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    print(f"[collector] attacker sink listening on http://localhost:{port}/collect")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
