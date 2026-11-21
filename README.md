# link-reader-poc — a malicious page that pops the agent that reads it

A self-contained, reproducible demo: a **public page** whose content, when read by
[Agent-Reach](https://github.com/Panniantong/agent-reach) **as-is**, prompt-injects
the **agent driving Agent-Reach** into running an attacker's shell command — i.e.
**remote code execution on the reader's machine**, triggered by nothing more than
"summarize this link."

The canary is harmless (it writes `~/.link-reader-poc/PWNED.txt`). Run it only in a
throwaway VM/container — see [SAFETY.md](SAFETY.md).

## The honest one-liner

> Agent-Reach returns fetched web/GitHub content to the calling agent **with no
> trust boundary**. An agent that trusts tool output then obeys instructions
> hidden in the page. Untrusted-content-in + an agent that can act + no signal to
> distrust it = the *lethal trifecta*.

**What this is NOT:** the `agent-reach` process does **not** eval/exec page content
(there is no `eval`/`exec`/`shell=True` on fetched text). The RCE happens in the
**agent**, because the tool hands it attacker text indistinguishable from trusted
input. See [EXPLAINER.md](EXPLAINER.md) for exactly whose fault each link in the
chain is — don't claim "the CLI self-pops," that's false and you'll get called out.

## Run it

```bash
# in a disposable VM/container:
export AGENTREACH_DEMO_SANDBOX=1
bash demo/run_demo.sh
```

- **Offline proof** (no network/key): feeds `bait/payload.md` to a modeled agent.
- **Install the tool from source** — `pip install "git+https://github.com/Panniantong/Agent-Reach"`.
  (`pip install agent-reach` on PyPI is an **unrelated** package with no `read` command.)
- **Live proof**: push this repo public, open an issue with `bait/payload.md` as its
  body, then `agent-reach read <issue-url>` through `demo/victim_agent.py`.
- `--mode llm` drives a real model (Anthropic). It may refuse — that refusal is the
  mitigation, not a bug in the demo.

## The fix (why this is responsible)

Agent-Reach's own `security/defensive-fixes` branch adds a `content_trust:
"untrusted-external"` marker to the result envelope and tells the agent, in the
skill, to treat it as data. With that marker present, the modeled agent **refuses**
— the demo flips to the SAFE outcome. Disclose first, let the fix ship, then publish
with "fixed in vX."

Built for authorized security research on the author's own install. Do not point this
at tools or machines you do not own.
