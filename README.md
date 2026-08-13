# FRED: a self-hosted voice assistant platform

FRED is a from-scratch, self-hosted voice assistant platform built on a Raspberry Pi:
a web UI with hold-to-talk speech, a persistent agent brain, text-to-speech, memory
across sessions, scheduled tasks, and a family of self-built web services, all running
as systemd user services behind an auth portal and Cloudflare tunnels.

This repository is the project's public documentation and reference: what it is, how
it's put together, and sanitized example implementations you can adapt for your own
build. The live codebase is private; everything here is written so you can understand
and rebuild the concepts.

---

## Features

- **Web UI (port 8765)**: chat panel with hold-to-talk mic input, typed messages,
  barge-in (talk over the assistant to interrupt it), embedded native console.
- **Agent brain**: DeepSeek served through the OpenClaw gateway; identity and
  personality live in markdown files loaded at session start, giving the agent durable
  continuity across sessions.
- **Speech**: text-to-speech via a cloud TTS provider; voice-note replies on
  messaging channels.
- **Memory & scheduling**: long-term memory files, daily recurring tasks, reminders.
- **A house full of services**: self-built Office suite (Word/Excel web editors),
  Cinema (streaming player), FileBox, dashboard, and a home hub, all on one Pi.
- **Self-healing**: a watchdog that restarts dead units, rotates bloated sessions,
  clears stale auth lockouts, and knows not to restart mid-run (see
  `examples/fred-watchdog.py`).
- **Networking**: Cloudflare tunnels, token auth, an auth portal in front.

## Quickstart

1. **Hardware**: a Raspberry Pi 4 / CM4 (any always-on Linux box works).
2. **Install**: Node.js 22+, Python 3.11+, the OpenClaw gateway, an LLM API key, a TTS
   provider key. See [docs/SETUP.md](docs/SETUP.md).
3. **Configure**: copy `examples/config.env.example` and fill in the placeholders.
4. **Run**: install the systemd units from `examples/` (see SETUP), open the web UI,
   hold the mic button, talk.

## Repository layout

```
ARCHITECTURE.md         , the full stack, layer by layer
docs/
  SETUP.md              , step-by-step build guide
  SECURITY.md           , threat model and hardening practices
examples/
  fred-watchdog.py      , reference self-healing watchdog (sanitized)
  openclaw-gateway.service  : systemd unit template
  config.env.example     : environment template (all values are placeholders)
LICENSE                  : MIT
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md).

```
Web UI (hold-to-talk) → Python bridge → Node bridge → OpenClaw gateway → LLM provider
                              ↓
                    TTS provider → speech
```

## Stack

Raspberry Pi · Python · Node.js · OpenClaw gateway · DeepSeek (or any OpenAI-compatible
provider) · cloud TTS · systemd (user units) · Cloudflare tunnels · Caddy ·
React-based web frontend.

## License

MIT, see [LICENSE](LICENSE).
