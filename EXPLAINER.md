# How the chain works — and whose fault each link is

The demo deliberately separates "what Agent-Reach does" from "what the agent does,"
because a credible public post has to get this right.

## The chain

1. **You ask an agent an innocent thing:** *"Use agent-reach to read and summarize
   `github.com/<you>/link-reader-poc/issues/1`."*
2. **Agent-Reach (unmodified) fetches it.** `agent-reach read <url>` auto-routes to
   the GitHub channel, which returns the issue **body + every comment** as
   `items[].text`, or a repo's README as `text`. Any public URL works via the web
   channel too.
3. **Agent-Reach returns it with no trust boundary.** The result envelope's `meta`
   has `elapsed_ms`/`attempts` and **no `content_trust` field** on upstream. Nothing
   tells the agent "this text is attacker-controlled."
4. **The agent trusts tool output** (as most agents do) and reads the injected
   "required pre-step" as if the operator wrote it.
5. **The agent runs the command with its shell** → the canary writes
   `~/.link-reader-poc/PWNED.txt` containing `id` / `hostname`. Swap in anything =
   arbitrary code execution on the reader's box.

## Whose fault is each link

| Link | Owner | Verdict |
|---|---|---|
| 2. fetches arbitrary attacker content | Agent-Reach | by design (it's a reader) |
| 3. returns it with **no trust marker** | **Agent-Reach** | **the defect (F3)** |
| (also) routes attacker text into an agent-obeyed `hint` field | **Agent-Reach** | **F2** |
| 4–5. obeys + executes untrusted text | the **agent/harness** | the agent's trust model |

So Agent-Reach is the **enabling conduit**, not a binary with a memory-corruption
RCE. The honest headline is *"prompt-injection → RCE via a reader tool with no trust
boundary,"* not *"agent-reach has an RCE."*

## What would break the chain (and does, in `--mode modeled`)

- **Trust marker (F3 fix):** if the envelope says `content_trust: "untrusted-external"`
  and the skill tells the agent to treat it as data, the modeled agent refuses. The
  demo shows this: run it against an upstream build (no marker → pop) vs the
  `security/defensive-fixes` build (marker → safe).
- **A hardened LLM** may refuse the injection on its own in `--mode llm`. Good — but
  relying on the model's goodwill is not a substitute for the tool marking its output.

## Limits / honesty

- `--mode modeled` is a faithful model of a trust-boundary-less agent (it incorporates
  tool output into its instructions, which is what naive agent loops do). It is not a
  claim that *every* agent is exploitable — only that Agent-Reach gives the agent
  nothing to distinguish this content as hostile.
- `--mode llm`'s outcome depends on the model and framing. Report what actually
  happened; don't cherry-pick.
