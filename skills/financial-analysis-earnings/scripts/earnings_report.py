#!/usr/bin/env python3
"""
One-command earnings data aggregator.

Usage:
    python earnings_report.py AAPL
    python earnings_report.py MSFT --peers AAPL GOOGL

Output: JSON with quarterly financials (SEC EDGAR), current quote, and optional peer comparison.

No pip dependencies required (SEC EDGAR uses stdlib; Yahoo Finance quote uses urllib).
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from get_fundamentals import fetch_fundamentals
from get_quote import fetch_quote
from get_comps import fetch_comps


def run_earnings_report(symbol: str, peers: list[str] | None = None) -> dict:
    symbol = symbol.upper()

    try:
        quarterly = fetch_fundamentals(symbol, form="10-Q", periods=8)
    except Exception as e:
        quarterly = {"entity_name": symbol, "periods": [], "error": str(e)}

    try:
        annual = fetch_fundamentals(symbol, form="10-K", periods=3)
    except Exception as e:
        annual = {"periods": [], "error": str(e)}

    try:
        quote = fetch_quote([symbol])
        quote_obj = quote["quotes"][0] if quote.get("quotes") and len(quote["quotes"]) > 0 else None
    except Exception:
        quote_obj = None

    result = {
        "symbol": symbol,
        "entity_name": quarterly.get("entity_name", symbol),
        "quote": quote_obj,
        "quarterly_financials": quarterly.get("periods", []),
        "annual_financials": annual.get("periods", []),
    }

    if peers:
        all_symbols = [symbol] + [p.upper() for p in peers]
        try:
            comps = fetch_comps(all_symbols)
            result["peer_comparison"] = comps.get("companies", [])
        except Exception as e:
            result["peer_comparison"] = {"error": str(e)}

    return result


def main():
    parser = argparse.ArgumentParser(description="Earnings data aggregator (SEC EDGAR + Yahoo Finance)")
    parser.add_argument("symbol", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--peers", nargs="+", help="Peer symbols for comparison (e.g., MSFT GOOGL)")

    args = parser.parse_args()
    result = run_earnings_report(args.symbol, args.peers)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
