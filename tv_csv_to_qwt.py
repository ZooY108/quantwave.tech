#!/usr/bin/env python3
# QuantWave Trader — TradingView CSV -> journal importer  (QuantWaveTech, 05/07 v1)
#
# Turns a TradingView export (Account Manager "History" tab, or Strategy Tester
# "List of Trades") into the JSON QuantWave Trader expects and POSTs it to the
# local app at http://127.0.0.1:8903/api/import/tv .
#
#   python3 tv_csv_to_qwt.py FILE.csv [--tz 3] [--dry-run] [--url URL]
#
# Only the python3 standard library is used. Import is idempotent (safe to
# re-run). The file never leaves your machine.

import csv, sys, json, argparse, urllib.request, datetime, re

# --- flexible column matching: TradingView varies names across brokers/locales
def pick(row, *names):
    low = {k.lower().strip(): v for k, v in row.items() if k}
    for n in names:
        v = low.get(n.lower())
        if v not in (None, ""):
            return v
    return None

def to_float(x):
    if x in (None, ""):
        return None
    s = re.sub(r"[^0-9.\-]", "", str(x).replace(",", ""))
    try:
        return float(s)
    except ValueError:
        return None

def norm_side(s):
    if not s:
        return None
    s = str(s).strip().lower()
    if s in ("buy", "long", "b"):   return "long"
    if s in ("sell", "short", "s"): return "short"
    return s

def parse_dt(s):
    """Return (date 'YYYY-MM-DD', time 'HH:MM:SS') from common TV formats."""
    if not s:
        return None, None
    s = str(s).strip()
    fmts = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M",
            "%d.%m.%Y %H:%M:%S", "%Y-%m-%d")
    for f in fmts:
        try:
            dt = datetime.datetime.strptime(s, f)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
        except ValueError:
            continue
    # last resort: split on first space
    parts = s.split()
    return parts[0], (parts[1] if len(parts) > 1 else "00:00:00")


def convert(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096); f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        rows = list(csv.DictReader(f, dialect=dialect))

    trades, execs = [], []
    for r in rows:
        instrument = pick(r, "Symbol", "Instrument", "Ticker")
        side       = norm_side(pick(r, "Side", "Action", "Type", "Direction"))
        qty        = to_float(pick(r, "Qty", "Quantity", "Contracts", "Size", "Amount"))
        entry      = to_float(pick(r, "Entry", "Entry price", "Avg entry", "Open price"))
        exit_      = to_float(pick(r, "Exit", "Exit price", "Avg exit", "Close price"))
        pnl        = to_float(pick(r, "PnL", "Profit", "Realized P&L", "Net P&L", "P&L", "Realized PnL"))
        price      = to_float(pick(r, "Fill Price", "Price", "Avg Fill Price", "Filled Price"))
        commission = to_float(pick(r, "Commission", "Fee", "Commissions"))
        stop       = to_float(pick(r, "Stop", "Stop price", "Stop-loss", "SL"))
        order_id   = pick(r, "Order id", "Order ID", "Order", "Id", "Trade #", "Trade")
        when       = pick(r, "Time", "Close time", "Closing time", "Date/Time",
                             "Date", "Fill Time", "Placing Time")
        d, t = parse_dt(when)

        # A finished trade has entry+exit+pnl -> Shape 1
        if entry is not None and exit_ is not None and pnl is not None:
            tr = {"instrument": instrument, "side": side, "qty": qty,
                  "entry": entry, "exit": exit_, "pnl": pnl}
            if d: tr["date"], tr["time"] = d, t
            if commission is not None: tr["commission"] = commission
            if stop is not None: tr["stop"] = stop
            trades.append({k: v for k, v in tr.items() if v is not None})
        # otherwise it's a raw fill -> Shape 2 (paired FIFO by the app)
        elif price is not None and qty:
            ex = {"instrument": instrument, "side": norm_side(side) or side,
                  "qty": qty, "price": price}
            if order_id: ex["order_id"] = str(order_id)
            if commission is not None: ex["commission"] = commission
            if d:
                ts = int(datetime.datetime.strptime(d + " " + t,
                         "%Y-%m-%d %H:%M:%S").timestamp())
                ex["ts"] = ts
            execs.append({k: v for k, v in ex.items() if v is not None})

    payload = {}
    if trades: payload["trades"] = trades
    if execs:  payload["executions"] = execs
    return payload


def main():
    ap = argparse.ArgumentParser(description="TradingView CSV -> QuantWave Trader import")
    ap.add_argument("csv", help="TradingView export CSV")
    ap.add_argument("--url", default="http://127.0.0.1:8903")
    ap.add_argument("--tz", type=float, default=0.0, help="your UTC offset in hours")
    ap.add_argument("--dry-run", action="store_true", help="print JSON, do not send")
    a = ap.parse_args()

    payload = convert(a.csv)
    n = len(payload.get("trades", [])) + len(payload.get("executions", []))
    if n == 0:
        print("[qwt] no rows parsed — check the CSV came from TradingView "
              "Account Manager History or Strategy Tester List of Trades.")
        sys.exit(1)

    if a.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("[qwt] parsed %d rows (dry-run, nothing sent)" % n)
        return

    data = json.dumps(payload).encode()
    req = urllib.request.Request(a.url.rstrip("/") + "/api/import/tv", data=data,
        headers={"Content-Type": "application/json",
                 "X-TZ-Offset": str(a.tz)}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode())
    except Exception as e:
        print("[qwt] POST failed: %r  — is the app running? %s" % (e, a.url))
        sys.exit(1)

    print("[qwt] parsed %d rows -> imported %s, skipped_dupes %s"
          % (n, res.get("imported", "?"), res.get("skipped_dupes", "?")))


if __name__ == "__main__":
    main()
