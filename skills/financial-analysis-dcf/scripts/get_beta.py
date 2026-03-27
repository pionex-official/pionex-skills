#!/usr/bin/env python3
"""
Calculate stock Beta using OLS regression on daily returns vs SPY.

Usage:
    python get_beta.py AAPL
    python get_beta.py MSFT --window 252

Uses Yahoo Finance historical prices (no API key needed).
Applies Blume adjustment: adjusted_beta = 0.67 * raw_beta + 0.33

Output: JSON with raw_beta, adjusted_beta, data_points, and period.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import time
from datetime import datetime, timedelta, timezone

BENCHMARK = "SPY"
DEFAULT_WINDOW = 1260  # ~5 years of trading days


def _fetch_daily_closes(symbol: str, days: int) -> dict[str, float]:
    """Fetch daily close prices from Yahoo Finance. Returns {date_str: close}."""
    end = int(time.time())
    # Add buffer days for weekends/holidays
    start = end - (days + 500) * 86400

    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={start}&period2={end}&interval=1d"
    )
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError):
        return {}

    result_data = data.get("chart", {}).get("result", [])
    if not result_data:
        return {}

    timestamps = result_data[0].get("timestamp", [])
    closes = result_data[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])

    closes_map = {}
    for ts, close in zip(timestamps, closes):
        if close is not None:
            day = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
            closes_map[day] = close

    return closes_map


def calculate_beta(symbol: str, window: int = DEFAULT_WINDOW) -> dict:
    """Calculate beta of symbol vs SPY."""
    symbol = symbol.upper()

    stock_closes = _fetch_daily_closes(symbol, window)
    if not stock_closes:
        return {"symbol": symbol, "error": f"Failed to fetch price data for {symbol}"}

    spy_closes = _fetch_daily_closes(BENCHMARK, window)
    if not spy_closes:
        return {"symbol": symbol, "error": "Failed to fetch SPY price data"}

    # Intersect dates
    common_dates = sorted(set(stock_closes.keys()) & set(spy_closes.keys()))
    if len(common_dates) < 11:
        return {"symbol": symbol, "raw_beta": 1.0, "adjusted_beta": 1.0,
                "data_points": len(common_dates), "note": "Insufficient data, defaulting to 1.0"}

    # Compute aligned daily returns
    stock_returns = []
    market_returns = []
    for i in range(1, len(common_dates)):
        prev, cur = common_dates[i - 1], common_dates[i]
        sp, sc = stock_closes[prev], stock_closes[cur]
        mp, mc = spy_closes[prev], spy_closes[cur]
        if sp <= 0 or mp <= 0:
            continue
        stock_returns.append((sc - sp) / sp)
        market_returns.append((mc - mp) / mp)

    m = len(stock_returns)
    if m < 10:
        return {"symbol": symbol, "raw_beta": 1.0, "adjusted_beta": 1.0,
                "data_points": m, "note": "Insufficient return data, defaulting to 1.0"}

    # OLS: beta = Cov(stock, market) / Var(market)
    mean_s = sum(stock_returns) / m
    mean_m = sum(market_returns) / m

    cov = 0.0
    var_m = 0.0
    for i in range(m):
        ds = stock_returns[i] - mean_s
        dm = market_returns[i] - mean_m
        cov += ds * dm
        var_m += dm * dm

    if var_m == 0:
        raw_beta = 1.0
    else:
        raw_beta = cov / var_m

    # Blume adjustment: shrinks toward 1.0 for better forward estimate
    adjusted_beta = 0.67 * raw_beta + 0.33

    return {
        "symbol": symbol,
        "benchmark": BENCHMARK,
        "raw_beta": round(raw_beta, 4),
        "adjusted_beta": round(adjusted_beta, 4),
        "data_points": m,
        "period": f"{common_dates[0]} to {common_dates[-1]}",
        "window_days": window,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate stock Beta vs SPY")
    parser.add_argument("symbol", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW,
                        help=f"Trading days for regression (default: {DEFAULT_WINDOW})")
    args = parser.parse_args()

    result = calculate_beta(args.symbol, args.window)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
