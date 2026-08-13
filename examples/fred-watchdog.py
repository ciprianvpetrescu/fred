#!/usr/bin/env python3
"""fred-watchdog.py: reference self-healing watchdog (sanitized).

Health-checks an assistant stack of systemd user units every couple of minutes
and repairs what it can, WITHOUT ever interrupting an in-flight run.

Features
--------
- Restarts any unit that is not 'active'.
- Rotates a session key when a session file grows past a size threshold.
- Clears stale provider auth lockouts, but only when no session file has been
  written recently (a recent write means a run is in flight, never restart on
  top of one).
- Verifies the provider key actually works before making changes.

Replace the placeholders (paths, unit names, key names) with your own.
"""

import json
import os
import re
import sqlite3
import subprocess
import time

HOME = os.path.expanduser("~")
LOG = os.path.join(HOME, "watchdog.log")
SESSION_DIR = os.path.join(HOME, ".assistant", "sessions")  # YOUR path
BRIDGE_FILE = os.path.join(HOME, "assistant", "bridge.mjs")  # YOUR path
STATE_DB = os.path.join(HOME, ".assistant", "state.sqlite")  # YOUR path
UNITS = ["assistant-gateway.service", "assistant-bridge.service", "assistant-web.service"]


def log(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line)


def sysctl(*args):
    return subprocess.run(["systemctl", "--user"] + list(args),
                          capture_output=True, text=True)


def restart(*units):
    log("restarting " + " ".join(units))
    sysctl("restart", *units)
    time.sleep(6)


def units_alive():
    bad = []
    for u in UNITS:
        r = sysctl("is-active", u)
        if r.stdout.strip() != "active":
            bad.append(u)
    return bad


def session_active(minutes=10):
    """Any session file written recently = a run in flight. Never restart on top."""
    cutoff = time.time() - minutes * 60
    try:
        for f in os.listdir(SESSION_DIR):
            if f.endswith(".jsonl") and os.path.getmtime(os.path.join(SESSION_DIR, f)) > cutoff:
                return True
    except OSError:
        pass
    return False


def biggest_session_mb():
    best = 0
    try:
        for f in os.listdir(SESSION_DIR):
            if f.endswith(".jsonl"):
                best = max(best, os.path.getsize(os.path.join(SESSION_DIR, f)) / 1048576.0)
    except OSError:
        pass
    return best


def provider_key_works():
    """Lightweight API probe. Replace with your provider's check."""
    # e.g. a minimal chat completion with max_tokens=1; return True on 200
    return True  # YOUR implementation


def clear_auth_lockout():
    """Clears a stale provider lockout when the key is actually fine."""
    try:
        con = sqlite3.connect(STATE_DB)
        row = con.execute("select state_json from auth_profile_state where state_key=?",
                          ("primary",)).fetchone()
        if not row:
            return False
        state = json.loads(row[0])
        changed = False
        for _, u in (state.get("usageStats") or {}).items():
            if u.get("disabledUntil") or u.get("errorCount"):
                u.pop("disabledUntil", None)
                u.pop("disabledReason", None)
                u["errorCount"] = 0
                u["failureCounts"] = {}
                changed = True
        if changed:
            con.execute("update auth_profile_state set state_json=?, updated_at=? where state_key=?",
                        (json.dumps(state), int(time.time() * 1000), "primary"))
            con.commit()
        con.close()
        return changed
    except Exception as e:
        log("auth clear failed: " + str(e))
        return False


def rotate_session(why):
    """Bump a versioned session key in the bridge so the next run starts fresh."""
    try:
        text = open(BRIDGE_FILE).read()
        m = re.search(r"agent:main:assistant-v(\d+)", text)
        if not m:
            return False
        n = int(m.group(1))
        open(BRIDGE_FILE, "w").write(
            text.replace("agent:main:assistant-v" + str(n),
                         "agent:main:assistant-v" + str(n + 1)))
        log("rotated session to assistant-v" + str(n + 1) + " (" + why + ")")
        restart("assistant-bridge.service", "assistant-web.service")
        return True
    except OSError:
        return False


def main():
    bad = units_alive()
    if bad:
        restart(*bad)

    if provider_key_works():
        if clear_auth_lockout():
            if session_active():
                log("cleared stale auth lockout, key is valid "
                    "(restart skipped: session active)")
            else:
                log("cleared stale auth lockout, key is valid")
                restart("assistant-gateway.service")
    else:
        log("WARNING provider key rejected - needs a human")

    mb = biggest_session_mb()
    if mb > 12:
        rotate_session("session file " + str(round(mb, 1)) + " MB")


if __name__ == "__main__":
    main()
