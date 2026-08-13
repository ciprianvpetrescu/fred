# SETUP — build your own FRED

A step-by-step, provider-agnostic guide. Replace every `YOUR_*` value with your own.
This is the documented path the reference build took; adapt freely.

## 1. Hardware & OS

- Raspberry Pi 4 (2GB+) or Compute Module 4, or any always-on Linux box.
- 32GB+ SD card or eMMC, Raspberry Pi OS Lite (64-bit) recommended.
- A web browser on any device on the LAN for the UI. A USB mic/speaker on the Pi is
  optional — the UI supports browser-based hold-to-talk and typed messages, and TTS
  output can play on the client.

## 2. Base install

```bash
sudo apt update && sudo apt upgrade -y
# Node.js 22+ (install via nvm or distro package)
# Python 3.11+
```

Install the OpenClaw gateway (see the OpenClaw docs) and a model provider plugin.
This reference build uses DeepSeek with an OpenAI-compatible API.

## 3. Keys

Create a `.env` (never commit it):

```bash
LLM_API_KEY=YOUR_LLM_API_KEY
TTS_API_KEY=YOUR_TTS_API_KEY
GATEWAY_TOKEN=YOUR_LONG_RANDOM_TOKEN
```

`GATEWAY_TOKEN` should be generated with something like:

```bash
openssl rand -hex 32
```

## 4. Gateway & bridge

The reference architecture uses a layered bridge:

- **Web UI** (port 8765) — the frontend; hold-to-talk sends audio, typed messages send
  text, and both can interrupt an in-flight reply (barge-in).
- **Python bridge** — auth, session routing, the audio/speech queue, barge-in handling.
- **Node bridge** — a persistent connection to the OpenClaw gateway; forwards messages
  and streams replies back, and aborts runs on barge-in.
- **OpenClaw gateway** — sessions, memory indexing, scheduling, channel routing.

Start the gateway with your provider configured, verify it responds, then start the
bridges. See `examples/openclaw-gateway.service` for the unit template.

## 5. systemd units

Copy the units from `examples/` into `~/.config/systemd/user/` and adjust the
`Environment=` lines to point at your real key source (or use `EnvironmentFile=`):

```bash
systemctl --user daemon-reload
systemctl --user enable --now openclaw-gateway.service
systemctl --user enable --now fred-bridge.service   # your bridge unit
systemctl --user enable --now fred-watchdog.timer   # if you use the watchdog
```

## 6. Web UI

Serve the frontend on port 8765 (any static server or your bridge). The UI connects to
the bridge over a websocket; authenticate with the gateway token on connect.

## 7. Remote access (tunnels)

Expose the UI through a Cloudflare quick tunnel so it works outside the LAN:

```bash
cloudflared tunnel --url http://127.0.0.1:8765
```

Put the portal/auth layer in front — see [SECURITY.md](SECURITY.md). Update your
gateway's `allowedOrigins` whenever the tunnel hostname rotates.

## 8. Watchdog

`examples/fred-watchdog.py` is a reference self-healing checker:

- restarts systemd units that are not `active`
- rotates a session when it grows past a size threshold
- clears stale provider auth lockouts — **but only when no session has been written
  recently**, so it never kills an in-flight run
- verifies the provider key works before doing anything drastic

Schedule it every 2 minutes with a systemd timer (mirroring the reference build).

## 9. Troubleshooting

- **No reply / long silence**: check the gateway is reachable, then check the model
  idle timeout — slow reasoning models need `timeoutSeconds` raised on the provider
  (see the OpenClaw docs). Don't set a cron run timeout below the model's stall window.
- **Barge-in leaves the UI "speaking"**: the client must acknowledge the audio drain
  (`audio_done` event); otherwise the backend stays in speaking state.
- **Tunnel works on LAN but not remotely**: absolute-URL APIs break behind tunnels —
  use same-origin relative URLs everywhere in the frontend.
- **Session bloat**: rotate the session key in the bridge (the watchdog can do this
  automatically).
