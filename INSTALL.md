# QuantWave Trader — Installation Guide
QuantWaveTech · Trading Journal · 04/07 v1

A private, local-first trading journal. All data stays on your machine —
nothing is uploaded. Runs as a small local web app you open in your browser.

---

## 1. Requirements

- **OS:** Linux (tested on Linux Mint / Ubuntu, systemd-based).
- **python3** — the only hard dependency. Check: `python3 --version`.
  Standard library only, no `pip install` needed.
- **A web browser** (Chrome, Firefox — any).
- **systemd user session** (default on Mint/Ubuntu) — keeps the app running
  in the background and after reboot.
- The bundled activity engine (for the Discipline & Tilt panel) ships inside
  `bin/` — no separate download.

## 2. Install

```bash
tar -xzf quantwavetrader.tar.gz
cd quantwavetrader
./install.sh
```

The installer:
1. Copies the app to `~/.local/share/quantwavetrader/`.
2. Creates a launcher `~/.local/bin/quantwavetrader`.
3. Registers systemd --user services (backend + activity engine) and enables
   **linger** so they survive logout/reboot.
4. Adds a menu/desktop entry **QuantWave Trader** with the app icon.

When it finishes, open **http://127.0.0.1:8903** — or click the
**QuantWave Trader** icon in your applications menu.

## 3. What runs, and where

| Item | Value |
|------|-------|
| App URL | http://127.0.0.1:8903 (localhost only, not exposed) |
| Backend port | 8903 |
| Activity engine port | 5600 (localhost) |
| Your data (SQLite) | `~/.local/share/quantwavetrader/qwt.db` |
| Services | `qwt-server.service`, `qwt-aw-server.service`, `qwt-aw-watcher-*` |

The journal **starts empty**. Load your trades via the Import step — see
`CONNECT-TRADINGVIEW.md`.

## 4. Managing the app

```bash
# status
systemctl --user status qwt-server.service

# restart / stop / start
systemctl --user restart qwt-server.service
systemctl --user stop qwt-server.service
systemctl --user start qwt-server.service
```

## 5. Uninstall

```bash
cd quantwavetrader
./uninstall.sh
```

Removes services, launcher and app files. Your `qwt.db` is left in place
unless you delete `~/.local/share/quantwavetrader/` yourself.

## 6. Troubleshooting

- **Icon opens nothing / blank page** — backend not up yet:
  `systemctl --user start qwt-server.service`, wait 2s, refresh.
- **Port 8903 busy** — another copy is running:
  `systemctl --user restart qwt-server.service`.
- **Empty dashboard** — no trades imported yet. See `CONNECT-TRADINGVIEW.md`.
- **Discipline & Tilt empty** — the activity engine needs a few minutes of
  desktop activity to collect data; ensure `qwt-aw-server.service` is active.

Support: QuantWaveTech.
