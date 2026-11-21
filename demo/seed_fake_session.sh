#!/usr/bin/env bash
# Seed a FAKE Agent-Reach session-cookie jar at the REAL on-disk location, so the
# cookie-exfil demo targets exactly what a real attacker would read.
#
# Agent-Reach stores logged-in session cookies as plaintext JSON at
#   ~/.agent-reach/sessions/<channel>-cloak/profile/reach-session.json
# (session_reuse.py:88; browser.py:699 comment: "plaintext JSON, 0600 but unencrypted").
# That is finding F5.
#
# The values written here are OBVIOUSLY FAKE. Even so:
#   RUN IN THE THROWAWAY SANDBOX ONLY -- never on a real machine, because the path
#   it writes to is your actual Agent-Reach profile directory.
set -euo pipefail

CH="${1:-twitter}"
DIR="$HOME/.agent-reach/sessions/${CH}-cloak/profile"
mkdir -p "$DIR"
cat > "$DIR/reach-session.json" <<'JSON'
{
  "cookies": [
    {"name": "auth_token", "value": "FAKE-auth-DEMO-ONLY-not-a-real-token", "domain": ".x.com", "path": "/", "httpOnly": true, "secure": true},
    {"name": "ct0", "value": "FAKE-csrf-DEMO-ONLY", "domain": ".x.com", "path": "/", "secure": true}
  ]
}
JSON
chmod 600 "$DIR/reach-session.json"
echo "[seed] wrote FAKE session jar at: $DIR/reach-session.json"
echo "[seed] (these are decoy values; a real install would have live login cookies here)"
