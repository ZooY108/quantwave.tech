# QuantWatch — Installation Guide
QuantWaveTech · Time & Focus Tracker · 05/07 v1

**License: $27 USD — one-time** (single purchase, not a subscription).

QuantWatch is a local time & focus tracker in the QuantWave design. It reads
your real desktop activity from **ActivityWatch** and adds focus/rest tools,
market countdowns and tickers. Everything runs locally — nothing is uploaded.

---

## 1. Requirements

- **Linux** desktop with a systemd user session (Mint / Ubuntu / Debian-based).
- **ActivityWatch** — the data engine. QuantWatch shows data **from** it.
  Install & run it first: https://activitywatch.net/downloads/
  (QuantWatch reads its local server at `localhost:5600`.)
- **python3** — the only extra dependency (standard library only, no pip).
- **Chrome / Chromium** — optional. If present, QuantWatch opens as its own
  app window; otherwise it opens in your default browser.

## 2. Install

```bash
tar -xzf quantwatch-dist.tar.gz
cd quantwatch-dist
./install.sh
```

The installer:
1. Copies the app to `~/.local/share/quantwatch/`.
2. Registers a systemd --user service (the live bridge `aw_live.py`) and enables
   **linger** so it starts on login and survives reboot.
3. Adds a menu entry **QuantWatch** with its icon.

If ActivityWatch is not running on `:5600`, the installer warns you — install
it, then re-run `./install.sh`.

Open **http://127.0.0.1:8902** or click **QuantWatch** in your applications menu.

## 3. What runs, and where

| Item | Value |
|------|-------|
| App URL | http://127.0.0.1:8902 (localhost only) |
| Data engine | ActivityWatch at http://localhost:5600 (installed separately) |
| Service | `quantwatch.service` (systemd --user) |
| App files | `~/.local/share/quantwatch/` |

## 4. Features

- **Summary** — active time, applications, windows, categories, session length
  (live from ActivityWatch).
- **Tools** — stopwatch, timer, alarm, countdown to US market open.
- **Tickers** — BTC, EUR/USD and more at a glance.
- **Focus Lock / Rest rhythm** — focus sessions, streaks, break scheduling.
- **Smart home & music** — Spotify + smart-home focus/break scenes.

> Note: the **Summary** tab is fully live. The Window/Browser/Editor breakdowns
> and Focus-Lock *Enforce* need extra ActivityWatch watchers (browser/editor)
> to be installed; without them those panels show demo/placeholder data.

## 5. Managing the app

```bash
systemctl --user status quantwatch.service
systemctl --user restart quantwatch.service
```

## 6. Uninstall

```bash
cd quantwatch-dist
./uninstall.sh
```

Removes the QuantWatch service, launcher and app files. **ActivityWatch and its
collected data are left untouched.**

## 7. Troubleshooting

- **Empty Summary** — ActivityWatch isn't running: start it, then
  `systemctl --user restart quantwatch.service`.
- **Opens in browser, not an app window** — Chrome/Chromium not found; install
  one to get the standalone window.
- **Port 8902 busy** — `systemctl --user restart quantwatch.service`.

Support: QuantWaveTech.
