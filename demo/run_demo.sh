#!/usr/bin/env bash
# Guided runner for the Agent-Reach prompt-injection -> RCE demo.
# RUN THIS IN A THROWAWAY VM / CONTAINER ONLY. It executes attacker-authored
# content. The canary is harmless, but the whole point is arbitrary execution.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"

echo "== Agent-Reach RCE demo =="
echo

if [[ "${AGENTREACH_DEMO_SANDBOX:-}" != "1" ]]; then
  cat <<'EOF'
[!] Safety gate: the shell tool is DISABLED.
    This demo runs attacker-authored commands. Only enable it inside a
    disposable VM or container you can throw away afterwards:

        export AGENTREACH_DEMO_SANDBOX=1

    Re-run this script there. Without it you will see the (safe) no-exec path.
EOF
  echo
fi

echo "--- Step 1: offline proof (no network, no API key) -------------------"
echo "Feeds the bait straight to the modeled agent to show the chain locally."
python3 "$HERE/demo/victim_agent.py" --local "$HERE/bait/payload.md" --mode modeled
echo

cat <<EOF
--- Step 2: live proof against the PUBLIC repo (Agent-Reach as-is) ----------
Prereqs:
  * Agent-Reach installed from UPSTREAM (unmodified), from SOURCE:
        pip install "git+https://github.com/Panniantong/Agent-Reach"
    (NOTE: 'pip install agent-reach' on PyPI is an UNRELATED package with no
    'read' command -- do not use it.) The 'read' must NOT emit meta.content_trust.
    If you built from the security/defensive-fixes branch, that fix is present and
    the demo is (correctly) blunted -- use a clean upstream install.
  * This repo pushed public, and an issue opened with bait/payload.md as its body
    (or just serve the raw file).

Then, in your sandbox:
  # (a) repo README / issue read path:
  python3 demo/victim_agent.py --target "https://github.com/<you>/link-reader-poc/issues/1" --mode modeled
  # (b) generic web read of the raw file:
  python3 demo/victim_agent.py --target "https://raw.githubusercontent.com/<you>/link-reader-poc/main/bait/payload.md" --mode modeled

Swap --mode modeled for --mode llm (needs ANTHROPIC_API_KEY + 'pip install anthropic')
to drive a real model. A hardened model may refuse -- that refusal IS the fix.

Proof of execution lands in ~/.link-reader-poc/PWNED.txt
EOF
