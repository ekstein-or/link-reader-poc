# Safety & responsible disclosure

This repo executes attacker-authored shell commands by design. Treat it like live
malware tooling even though the canary is harmless.

## Hard rules

1. **Sandbox only.** Run inside a disposable VM or container you can delete. Never on
   your daily machine. The shell tool refuses unless `AGENTREACH_DEMO_SANDBOX=1`.
2. **Your own tool, your own machine, your own repo.** This targets the author's own
   Agent-Reach install reading the author's own public repo. Do not point it at anyone
   else's install, infra, or accounts.
3. **Harmless canary only.** The payload writes `~/.link-reader-poc/PWNED.txt`. Do not
   publish a version with a real/destructive payload or a reverse shell.
4. **Labeled bait.** `bait/payload.md` says in the open that it is a security demo.

## Disclosure first

Agent-Reach is actively maintained (`Panniantong/agent-reach`) and other people run
it. A public, working technique burns unpatched users. The responsible sequence:

1. Report F3 (no trust marker) and F2 (upstream text into the agent-obeyed `hint`)
   to the maintainer privately.
2. Let a fix ship (the `security/defensive-fixes` branch already adds a
   `content_trust` marker — the mitigation this demo flips to).
3. *Then* publish, framed as **"attack → fix in vX."** That's a stronger story and
   doesn't drop a live technique on people who can't defend yet.

## For the public post

- Say "prompt-injection → RCE via a reader with no trust boundary," not "RCE in the
  CLI." See EXPLAINER.md.
- Show the canary file as proof; show the SAFE outcome against the fixed build as the
  contrast. The before/after is the most convincing (and most responsible) frame.
