# FRED — Architecture

A high-level, sanitised view of the system. No credentials, hostnames or internal URLs
are included; this is a map of ideas, not a config dump.

## Stack overview

```
┌─────────────────────────────────────────────────────────────┐
│  Web UI (port 8765)                                          │
│  · chat panel + hold-to-talk mic button                      │
│  · native OpenClaw console embedded                          │
│  · Office / Cinema / FileBox / Hub sub-apps                  │
└───────────────┬─────────────────────────────────────────────┘
                │ (websocket)
┌───────────────▼─────────────────────────────────────────────┐
│  Python bridge (brain_fred_gateway.py)                       │
│  · auth, session routing, audio queue, barge-in             │
└───────────────┬─────────────────────────────────────────────┘
                │ (unix socket / websocket)
┌───────────────▼─────────────────────────────────────────────┐
│  Node bridge (fred_gateway.mjs)                              │
│  · persistent connection to the OpenClaw gateway            │
└───────────────┬─────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────┐
│  OpenClaw gateway (port 18900)                               │
│  · sessions, memory indexing, cron, channels                 │
│  · plugins: DeepSeek, Google, Fish Audio TTS, Telegram       │
└───────────────┬─────────────────────────────────────────────┘
                │
        ┌───────▼────────┐   ┌──────────────────┐
        │ DeepSeek (LLM) │   │ Fish Audio (TTS) │
        └────────────────┘   └──────────────────┘
```

## Key components

- **Brain**: DeepSeek model served through the OpenClaw gateway. Identity and
  personality live in markdown files (soul, identity, memory) that load at session
  start — the agent wakes fresh each session and reads its configuration from disk.
- **Memory**: long-term memory files give the agent continuity across sessions;
  scheduled tasks handle recurring work (reminders, routine jobs).
- **Speech**: Fish Audio TTS for voice replies; speech-to-text on the client (web)
  side, with hold-to-talk and barge-in (talking over FRED interrupts him).
- **Channels**: the web UI and Telegram share one conversation; Telegram replies can be
  voice notes via the TTS plugin.
- **Services** (all systemd user units on the Pi):
  - `fred.service` — Python assistant backend
  - `fred-gateway.service` — Node bridge
  - `openclaw-gateway.service` — the OpenClaw gateway
  - Office (8768), Cinema (8769), FileBox, Hub (8100), dashboard — self-built web apps
  - `fred-watchdog` — self-healing: restarts dead units, rotates bloated sessions,
    clears stale auth lockouts (and knows not to restart mid-run anymore)
- **Networking**: Cloudflare tunnels into the house; an auth portal (Caddy + portal
  service) in front; token auth on the gateway.

## Why it's interesting

It's a full home-grown assistant platform — not a skill on a commercial speaker, but a
from-scratch stack: UI, speech, brain, memory, cron, tunnels, self-healing — with every
layer owned and maintained in-house.
