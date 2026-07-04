# QuantWave Trader — Connecting TradingView
QuantWaveTech · 04/07 v1

QuantWave Trader imports your **executed trades** and builds the journal,
R-distribution, sessions, equity curve and discipline metrics from them.

> **Beta note.** The in-app **Connect TradingView** button (OAuth one-click
> sync) is not live yet during the team beta. The working method today is the
> local import endpoint below — it is stable and used in production.

---

## The import endpoint

```
POST http://127.0.0.1:8903/api/import/tv
Content-Type: application/json
X-TZ-Offset: 3            # optional: your UTC offset in hours (e.g. 3 = UTC+3)
Authorization: Bearer <token>   # optional; omit = default local profile
```

The endpoint is **idempotent** — sending the same data twice never creates
duplicates. Response: `{"ok":true,"imported":N,"skipped_dupes":M}`.

You can send data in **either** of two shapes.

### A) Finished trades (from TradingView "List of Trades")

Easiest path. In TradingView open your strategy/paper-trading panel →
**List of Trades**, and map each row to:

```json
{
  "trades": [
    {
      "date": "2026-06-16", "time": "14:32:05",
      "instrument": "MNQ", "side": "long",
      "qty": 2, "entry": 21850.25, "exit": 21868.50,
      "pnl": 73.0
    }
  ]
}
```

`side` = long/short (or buy/sell). `pnl` in account currency. If you have an
epoch timestamp instead of date/time, send `"ts": 1751630400` and it is
converted using `X-TZ-Offset`.

### B) Raw executions (fills) — auto-paired into trades

For a live broker/bridge feed. Fills are deduplicated by `order_id` and paired
into round-turn trades FIFO by the instrument point value:

```json
{
  "executions": [
    {
      "order_id": "BRK-8837162",   // required, unique — dedup key
      "ts": 1751630400,            // required, epoch seconds (UTC)
      "instrument": "MNQ",         // required
      "side": "buy",               // required: buy|sell|long|short
      "qty": 2,                    // required, >0
      "price": 21850.25,           // required
      "commission": 0.74,          // optional
      "close_ts": 1751631000       // optional
    }
  ]
}
```

Re-send the same stream as often as you like — repeats (same `order_id`) are
skipped, trades are never doubled.

## Quick test with curl

```bash
curl -s -X POST http://127.0.0.1:8903/api/import/tv \
  -H 'Content-Type: application/json' \
  -H 'X-TZ-Offset: 3' \
  -d '{"trades":[{"date":"2026-06-16","time":"14:32:05","instrument":"MNQ","side":"long","qty":2,"entry":21850.25,"exit":21868.50,"pnl":73.0}]}'
# -> {"ok":true,"imported":1,"skipped_dupes":0}
```

Refresh **http://127.0.0.1:8903** — the trade appears in Journal, and the
Dashboard metrics update.

## Notes

- **R-multiple** needs a stop/risk per trade. Add `"stop"` (price) or
  `"risk_usd"` to each trade so the R-Multiple panel is meaningful; without it
  trades count as break-even for R.
- **Instruments/point value:** MNQ, NQ, ES, MES and common futures are known.
  Send `"point_value"` on a trade to override.
- All import is **local** — the request never leaves your machine.

Support: QuantWaveTech.
