#!/usr/bin/env python3
"""Minimal Chrome DevTools Protocol client over the UNAUTHENTICATED debug port.

The debug port needs no credentials: fetch the target list over plain HTTP
(`/json`), open the page's WebSocket, and send CDP commands. That lack of auth is
finding F7.

Requires: pip install websocket-client. SANDBOX ONLY.
"""
import json
import urllib.request

from websocket import create_connection


def _ws_url(host: str, port: int) -> str:
    data = json.loads(urllib.request.urlopen(f"http://{host}:{port}/json", timeout=5).read())
    pages = [t for t in data if t.get("type") == "page"] or data
    if not pages:
        raise SystemExit(f"[cdp] no targets at {host}:{port}; is Chrome up with "
                         f"--remote-debugging-port={port}?")
    return pages[0]["webSocketDebuggerUrl"]


class CDP:
    def __init__(self, host: str = "127.0.0.1", port: int = 9222):
        self.ws = create_connection(_ws_url(host, port), timeout=5)
        self._id = 0

    def call(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                return msg

    def close(self) -> None:
        try:
            self.ws.close()
        except Exception:
            pass
