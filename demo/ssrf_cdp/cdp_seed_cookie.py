#!/usr/bin/env python3
"""Victim side: set a DECOY session cookie in the Chrome that Agent-Reach drives,
to stand in for a real logged-in session. Values are obviously fake.

SANDBOX ONLY.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cdp import CDP  # noqa: E402

c = CDP()
c.call("Network.enable")
r = c.call("Network.setCookie", {
    "name": "SESSDATA",
    "value": "FAKE-SESSION-DEMO-not-a-real-token",
    "url": "https://www.bilibili.com/",
    "httpOnly": True,
    "secure": True,
})
ok = r.get("result", {}).get("success", r.get("result"))
print(f"[victim] decoy session cookie planted in the browser (success={ok})")
c.close()
