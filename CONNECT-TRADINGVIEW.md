# QuantWave Trader — Connecting TradingView
QuantWaveTech · 05/07 v2

QuantWave Trader builds your journal, R-distribution, sessions, equity curve
and discipline metrics from your **executed trades**. So the first job is to
get your trade history **out of TradingView**, then load it into the app.

> **Beta note.** The in-app **Connect TradingView** button (OAuth one-click
> sync) is not live yet. The method below is the working path today — it is
> stable and used in production.

---

# STEP 1 — Get your trade history out of TradingView  (required)

TradingView keeps your fills/trades in the **Account Manager** (the panel at
the bottom of the chart). You export it to a CSV file. Two cases:

## A) Broker / Paper Trading  (live or paper futures — the usual case)

This is how you trade NQ / ES / MNQ through a connected or paper broker.

1. Open your chart and show the **Account Manager** panel at the bottom
   (Trading panel). Make sure the right account is selected.
2. Click the **broker name dropdown** at the top-left of that panel.
3. Choose **"Export data…"**.
4. Each tab exports **separately**. Select the **History** tab (filled/closed
   orders) and export → you get a **CSV** file. (Repeat for other tabs if you
   want Positions/Orders too, but **History** is what the journal needs.)

Reference (TradingView official): *How can I export trading data?* — "click the
Export data… button in the broker's dropdown menu; each tab is exported
individually."

## B) Strategy Tester  (backtested / strategy trades)

If your trades come from a Pine strategy, not a broker:

1. Open the **Strategy Tester** panel → **List of Trades** tab.
2. Click the **export / download icon** on that tab.
3. Choose **CSV** (list of trades) — or XLSX for the full report.

---

# STEP 2 — Load the CSV into QuantWave Trader

The app takes JSON on a local endpoint. Use the bundled converter to turn the
TradingView CSV into that JSON and post it in one command.

## Easiest: the bundled converter

Inside this folder is **`tv_csv_to_qwt.py`**. Run it on the CSV you exported:

```bash
python3 tv_csv_to_qwt.py ~/Downloads/your_tradingview_export.csv
```

It auto-detects the TradingView columns (Symbol, Side, Qty, Fill/Price, Time,
Commission, and Entry/Exit/PnL if present), builds the JSON and POSTs it to
`http://127.0.0.1:8903/api/import/tv`. It prints, e.g.:

```
[qwt] parsed 132 rows -> imported 132, skipped_dupes 0
```

Re-running the same file never creates duplicates (dedup by order id / trade
signature). Refresh **http://127.0.0.1:8903** — the trades appear in Journal
and every metric updates.

Options:
```
python3 tv_csv_to_qwt.py FILE.csv --tz 3        # your UTC offset in hours
python3 tv_csv_to_qwt.py FILE.csv --dry-run     # print JSON, do not send
python3 tv_csv_to_qwt.py FILE.csv --url http://127.0.0.1:8903
```

---

## Reference — the import endpoint (for manual / bridge use)

```
POST http://127.0.0.1:8903/api/import/tv
Content-Type: application/json
X-TZ-Offset: 3                     # optional: your UTC offset in hours
Authorization: Bearer <token>      # optional; omit = default local profile
```
Idempotent. Response: `{"ok":true,"imported":N,"skipped_dupes":M}`.

**Shape 1 — finished trades** (from Strategy Tester "List of Trades"):
```json
{"trades":[
  {"date":"2026-06-16","time":"14:32:05","instrument":"MNQ",
   "side":"long","qty":2,"entry":21850.25,"exit":21868.50,"pnl":73.0}
]}
```

**Shape 2 — raw executions/fills** (from broker History; paired FIFO):
```json
{"executions":[
  {"order_id":"BRK-8837162","ts":1751630400,"instrument":"MNQ",
   "side":"buy","qty":2,"price":21850.25,"commission":0.74}
]}
```
`order_id` is the dedup key for a live stream — resend freely, no doubles.

Quick manual test:
```bash
curl -s -X POST http://127.0.0.1:8903/api/import/tv \
  -H 'Content-Type: application/json' -H 'X-TZ-Offset: 3' \
  -d '{"trades":[{"date":"2026-06-16","time":"14:32:05","instrument":"MNQ","side":"long","qty":2,"entry":21850.25,"exit":21868.50,"pnl":73.0}]}'
```

## Notes
- **R-multiple** needs a stop/risk per trade. If your export has no stop, add
  `"stop"` (price) or `"risk_usd"` per trade so the R-Multiple panel is
  meaningful; otherwise those trades count as break-even for R.
- **Instruments:** MNQ, NQ, ES, MES and common futures are known. Add
  `"point_value"` on a trade to override.
- Everything is **local** — the CSV and the import never leave your machine.

Support: QuantWaveTech.
