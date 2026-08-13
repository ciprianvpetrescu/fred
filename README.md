# FRED — a self-hosted voice assistant platform

FRED is a from-scratch, self-hosted voice assistant platform built on a Raspberry Pi:
a web UI with hold-to-talk speech, a persistent agent brain, text-to-speech, memory
across sessions, scheduled tasks, and a family of self-built web services — all running
as systemd user services behind an auth portal and Cloudflare tunnels.

This repository documents the project from a development point of view: what it is,
how it's put together, and the stack behind it.

---

## Features

- **Web UI (port 8765)** — chat panel with hold-to-talk mic input, typed messages,
  barge-in (talk over the assistant to interrupt it), embedded native console.
- **Agent brain** — DeepSeek served through the OpenClaw gateway; personality and
  memory are loaded from markdown configuration files at session start, giving the
  agent durable identity and continuity across sessions.
- **Speech** — text-to-speech via Fish Audio; voice-note replies on Telegram.
- **Memory & scheduling** — long-term memory files, daily recurring tasks, reminders.
- **A house full of services** — self-built Office suite (Word/Excel web editors),
  Cinema (streaming player), FileBox, dashboard, and a home hub, all on one Pi.
- **Self-healing** — a watchdog that restarts dead units, rotates bloated sessions,
  clears stale auth lockouts, and knows not to restart mid-run.
- **Networking** — Cloudflare tunnels, token auth, an auth portal in front.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full stack.

```
Web UI (hold-to-talk) → Python bridge → Node bridge → OpenClaw gateway → DeepSeek
                              ↓
                    Fish Audio TTS → speech
```

## Stack

Raspberry Pi · Python · Node.js · OpenClaw gateway · DeepSeek · Fish Audio TTS ·
systemd (user units) · Cloudflare tunnels · Caddy · React-based web frontend.

## Repository layout

- `ARCHITECTURE.md` — sanitised system overview
- `LICENSE` — MIT

## License

MIT — see [LICENSE](LICENSE).
