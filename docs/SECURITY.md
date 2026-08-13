# SECURITY — threat model and hardening

The reference build runs an always-on assistant with remote access, so security is a
first-class layer, not an afterthought. This is the model it follows.

## Assets

- The gateway (holds the LLM/TTS keys, session history)
- The web UI and its tunnels (exposed to the internet)
- The host itself (a Linux box on a home LAN)

## Layers

```
Internet → Cloudflare tunnel → auth portal (Caddy) → web UI (8765)
                                                        │
                                                     bridge → gateway (18900, token auth)
```

1. **Token auth on the gateway** — the gateway is bound to the LAN/loopback and
   requires a long random token on every connection. Never expose it in the UI bundle
   or logs.
2. **Auth portal in front of the web UI** — a reverse proxy (Caddy) with its own auth
   challenge sits between the tunnel and the UI, so the tunnel alone is never enough
   to reach the assistant.
3. **Secrets live in env files, never in repos** — keys go in `.env` /
   `EnvironmentFile`, gitignored. Committed examples use `YOUR_*` placeholders only.
4. **Tunnels** — quick tunnels give a rotating public hostname; the portal auth is
   the real gate, so hostname rotation is a nuisance, not a breach.

## Practices

- **Never log secrets.** Bridge logs contain message traffic; keep keys out of them.
- **Rotate the gateway token** after any exposure, and rotate tunnel hostnames
  regularly so stale links die.
- **The watchdog must not kill runs.** Before restarting anything, check for recent
  session activity (file mtimes in the session dir). A restart on top of an in-flight
  run loses work — the reference watchdog deliberately skips restarts when a session
  was written in the last 10 minutes.
- **Keep the OS patched**, restrict SSH to keys only, and run the assistant under an
  unprivileged user.
- **Cron jobs that run isolated agents** should use `delivery: none` and alert only on
  failure, so routine work never spams channels.

## If you publish anything

- Redact IPs, hostnames, names, and API keys before committing — including git
  history (rewrite it, don't just delete files).
- Keep personal content (journals, letters, photos) out of public repos entirely.
- Use placeholders in every example file.
