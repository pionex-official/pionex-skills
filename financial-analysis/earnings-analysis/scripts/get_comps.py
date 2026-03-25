#!/usr/bin/env python3
"""
Comparable company analysis using SEC EDGAR data.

Usage:
    python get_comps.py AAPL MSFT GOOGL META

Output: JSON with financial metrics for each company (margins, growth, multiples).
        P/E and P/S require market cap from Yahoo Finance (optional dependency).

No required dependencies — uses SEC EDGAR (stdlib only).
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from get_fundamentals import fetch_fundamentals


def _try_get_market_cap(symbol: str):
    """Try to get market cap from Yahoo Finance. Returns None if unavailable."""
    try:
        from get_quote import fetch_quote
        result = fetch_quote([symbol])
        quotes = result.get("quotes", [])
        if quotes and "market_cap" in quotes[0]:
            return quotes[0].get("market_cap")
    except Exception:
        pass
    return None


def fetch_comps(symbols: list[str]) -> dict:
    if len(symbols) > 10:
        return {"error": "Maximum 10 symbols allowed", "companies": []}

    companies = []

    for sym in symbols:
        sym = sym.upper()
        try:
            # Get 2 years of annual data for YoY growth
            data = fetch_fundamentals(sym, form="10-K", periods=2)
            if data.get("error"):
                companies.append({"symbol": sym, "error": data["error"]})
                continue

            periods = data.get("periods", [])
            if not periods:
                companies.append({"symbol": sym, "entity_name": data.get("entity_name", sym), "error": "No annual data"})
                continue

            latest = periods[0]
            prior = periods[1] if len(periods) > 1 else None

            revenue = latest.get("revenue")
            gross_profit = latest.get("gross_profit")
            operating_income = latest.get("operating_income")
            net_income = latest.get("net_income")
            eps = latest.get("eps_diluted")

            # Margins
            gross_margin = (gross_profit / revenue * 100) if revenue and gross_profit else None
            op_margin = (operating_income / revenue * 100) if revenue and operating_income else None
            net_margin = (net_income / revenue * 100) if revenue and net_income else None

            # YoY growth
            prior_rev = prior.get("revenue") if prior else None
            prior_ni = prior.get("net_income") if prior else None
            rev_growth = ((revenue - prior_rev) / abs(prior_rev) * 100) if revenue and prior_rev and prior_rev != 0 else None
            ni_growth = ((net_income - prior_ni) / abs(prior_ni) * 100) if net_income is not None and prior_ni and prior_ni != 0 else None

            # Try to get market cap for multiples
            market_cap = _try_get_market_cap(sym)
            pe = (market_cap / net_income) if market_cap and net_income and net_income > 0 else None
            ps = (market_cap / revenue) if market_cap and revenue and revenue > 0 else None

            comp = {
                "symbol": sym,
                "entity_name": data.get("entity_name", sym),
                "fiscal_year": latest.get("fiscal_year"),
                "market_cap": market_cap,
                "revenue": revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "eps_diluted": eps,
                "gross_margin_pct": round(gross_margin, 1) if gross_margin is not None else None,
                "operating_margin_pct": round(op_margin, 1) if op_margin is not None else None,
                "net_margin_pct": round(net_margin, 1) if net_margin is not None else None,
                "revenue_growth_yoy_pct": round(rev_growth, 1) if rev_growth is not None else None,
                "net_income_growth_yoy_pct": round(ni_growth, 1) if ni_growth is not None else None,
                "pe_ratio": round(pe, 1) if pe is not None else None,
                "ps_ratio": round(ps, 1) if ps is not None else None,
            }
            companies.append(comp)

        except Exception as e:
            companies.append({"symbol": sym, "error": str(e)})

    return {"companies": companies}


def main():
    parser = argparse.ArgumentParser(description="Comparable company analysis via SEC EDGAR")
    parser.add_argument("symbols", nargs="+", help="Stock symbols (e.g., AAPL MSFT GOOGL)")
    args = parser.parse_args()

    result = fetch_comps([s.upper() for s in args.symbols])
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
