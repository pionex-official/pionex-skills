#!/usr/bin/env python3
"""
Comparable company analysis with statistical benchmarking.

Usage:
    python get_comps.py AAPL MSFT GOOGL META

Output: JSON with financial metrics, valuation multiples, and peer group statistics
        (median, percentile rank) for each company.

No pip dependencies — uses SEC EDGAR + Yahoo Finance via urllib.
"""

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from get_fundamentals import fetch_fundamentals
from get_quote import fetch_quote


def _percentile(values: list[float], p: float) -> float:
    """Calculate p-th percentile (0-100) using linear interpolation."""
    if not values:
        return 0
    s = sorted(values)
    k = (p / 100) * (len(s) - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def _rank_percentile(value: float, values: list[float]) -> float:
    """Return percentile rank of value within the list (0 = lowest, 100 = highest)."""
    if not values or len(values) < 2:
        return 50.0
    below = sum(1 for v in values if v < value)
    equal = sum(1 for v in values if v == value)
    return round((below + equal * 0.5) / len(values) * 100, 1)


def fetch_comps(symbols: list[str]) -> dict:
    if len(symbols) > 10:
        return {"error": "Maximum 10 symbols allowed", "companies": []}

    # Batch fetch quotes for all symbols (single session init)
    quote_map = {}
    try:
        quote_result = fetch_quote([s.upper() for s in symbols])
        for q in quote_result.get("quotes", []):
            if "error" not in q:
                quote_map[q["symbol"]] = q
    except Exception:
        pass

    companies = []

    for sym in symbols:
        sym = sym.upper()
        try:
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
            equity = latest.get("shareholders_equity")

            # Margins
            gross_margin = (gross_profit / revenue * 100) if revenue and gross_profit else None
            op_margin = (operating_income / revenue * 100) if revenue and operating_income else None
            net_margin = (net_income / revenue * 100) if revenue and net_income else None

            # ROE
            roe = (net_income / equity * 100) if net_income and equity and equity > 0 else None

            # YoY growth
            prior_rev = prior.get("revenue") if prior else None
            prior_ni = prior.get("net_income") if prior else None
            rev_growth = ((revenue - prior_rev) / abs(prior_rev) * 100) if revenue and prior_rev and prior_rev != 0 else None
            ni_growth = ((net_income - prior_ni) / abs(prior_ni) * 100) if net_income is not None and prior_ni and prior_ni != 0 else None

            # Market data from quote
            q = quote_map.get(sym, {})
            market_cap = q.get("market_cap")
            ev = q.get("enterprise_value")

            # Valuation multiples
            pe = (market_cap / net_income) if market_cap and net_income and net_income > 0 else None
            ps = (market_cap / revenue) if market_cap and revenue and revenue > 0 else None

            # EV-based multiples
            ebitda = None
            if operating_income:
                # Approximate EBITDA = operating income (D&A not in EDGAR; note in output)
                ebitda = operating_income
            ev_ebitda = (ev / ebitda) if ev and ebitda and ebitda > 0 else None
            ev_revenue = (ev / revenue) if ev and revenue and revenue > 0 else None

            comp = {
                "symbol": sym,
                "entity_name": data.get("entity_name", sym),
                "fiscal_year": latest.get("fiscal_year"),
                "market_cap": market_cap,
                "enterprise_value": ev,
                "revenue": revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "eps_diluted": eps,
                "shareholders_equity": equity,
                "gross_margin_pct": round(gross_margin, 1) if gross_margin is not None else None,
                "operating_margin_pct": round(op_margin, 1) if op_margin is not None else None,
                "net_margin_pct": round(net_margin, 1) if net_margin is not None else None,
                "roe_pct": round(roe, 1) if roe is not None else None,
                "revenue_growth_yoy_pct": round(rev_growth, 1) if rev_growth is not None else None,
                "net_income_growth_yoy_pct": round(ni_growth, 1) if ni_growth is not None else None,
                "pe_ratio": round(pe, 1) if pe is not None else None,
                "ps_ratio": round(ps, 1) if ps is not None else None,
                "ev_ebitda": round(ev_ebitda, 1) if ev_ebitda is not None else None,
                "ev_revenue": round(ev_revenue, 1) if ev_revenue is not None else None,
            }
            companies.append(comp)

        except Exception as e:
            companies.append({"symbol": sym, "error": str(e)})

    # Compute peer group statistics and percentile ranks
    valid = [c for c in companies if "error" not in c]
    stat_fields = [
        "gross_margin_pct", "operating_margin_pct", "net_margin_pct", "roe_pct",
        "revenue_growth_yoy_pct", "net_income_growth_yoy_pct",
        "pe_ratio", "ps_ratio", "ev_ebitda", "ev_revenue",
    ]

    stats = {}
    field_values = {}
    for field in stat_fields:
        vals = [c[field] for c in valid if c.get(field) is not None]
        field_values[field] = vals
        if vals:
            stats[field] = {
                "min": round(min(vals), 1),
                "p25": round(_percentile(vals, 25), 1),
                "median": round(_percentile(vals, 50), 1),
                "p75": round(_percentile(vals, 75), 1),
                "max": round(max(vals), 1),
                "count": len(vals),
            }

    # Add percentile rank to each company
    for c in valid:
        ranks = {}
        for field in stat_fields:
            v = c.get(field)
            if v is not None and field_values[field]:
                ranks[field] = _rank_percentile(v, field_values[field])
        c["percentile_ranks"] = ranks

    return {
        "companies": companies,
        "peer_statistics": stats,
        "notes": {
            "ev_ebitda": "EBITDA approximated as operating income (D&A not available from SEC EDGAR XBRL)",
            "percentile_ranks": "0 = lowest in peer group, 100 = highest",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Comparable company analysis via SEC EDGAR")
    parser.add_argument("symbols", nargs="+", help="Stock symbols (e.g., AAPL MSFT GOOGL)")
    args = parser.parse_args()

    result = fetch_comps([s.upper() for s in args.symbols])
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
