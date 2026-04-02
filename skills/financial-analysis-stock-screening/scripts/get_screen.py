#!/usr/bin/env python3
"""
Stock screener with composite scoring and threshold filtering.

Usage:
    python get_screen.py AAPL MSFT GOOGL NVDA META
    python get_screen.py NVDA AMD AVGO QCOM --style growth
    python get_screen.py AAPL MSFT GOOGL --style value --min-margin 20 --max-pe 35

Styles: growth (default), value, quality
Output: JSON with scored and ranked companies.

No pip dependencies — uses SEC EDGAR + Yahoo Finance via urllib.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from get_fundamentals import fetch_fundamentals
from get_quote import fetch_quote


def _normalize_score(value: float, values: list[float], higher_is_better: bool = True) -> float:
    """Normalize value to 0-100 score within the group."""
    if not values or len(values) < 2:
        return 50.0
    lo, hi = min(values), max(values)
    if hi == lo:
        return 50.0
    raw = (value - lo) / (hi - lo) * 100
    return round(raw if higher_is_better else 100 - raw, 1)


def fetch_screen(symbols: list[str], style: str = "growth",
                 min_growth: float | None = None, min_margin: float | None = None,
                 max_pe: float | None = None) -> dict:
    if len(symbols) > 10:
        return {"error": "Maximum 10 symbols allowed", "companies": []}

    # Batch fetch quotes
    quote_map = {}
    try:
        quote_result = fetch_quote([s.upper() for s in symbols])
        for q in quote_result.get("quotes", []):
            if "error" not in q:
                quote_map[q["symbol"]] = q
    except Exception:
        pass

    raw_companies = []

    for sym in symbols:
        sym = sym.upper()
        try:
            data = fetch_fundamentals(sym, form="10-K", periods=2)
            if data.get("error"):
                raw_companies.append({"symbol": sym, "error": data["error"]})
                continue

            periods = data.get("periods", [])
            if not periods:
                raw_companies.append({"symbol": sym, "error": "No annual data"})
                continue

            latest = periods[0]
            prior = periods[1] if len(periods) > 1 else None

            revenue = latest.get("revenue")
            operating_income = latest.get("operating_income")
            net_income = latest.get("net_income")
            eps = latest.get("eps_diluted")

            gross_profit = latest.get("gross_profit")
            gross_margin = (gross_profit / revenue * 100) if revenue and gross_profit else None
            op_margin = (operating_income / revenue * 100) if revenue and operating_income else None
            net_margin = (net_income / revenue * 100) if revenue and net_income else None

            prior_rev = prior.get("revenue") if prior else None
            prior_ni = prior.get("net_income") if prior else None
            rev_growth = ((revenue - prior_rev) / abs(prior_rev) * 100) if revenue and prior_rev and prior_rev != 0 else None
            ni_growth = ((net_income - prior_ni) / abs(prior_ni) * 100) if net_income is not None and prior_ni and prior_ni != 0 else None

            q = quote_map.get(sym, {})
            market_cap = q.get("market_cap")
            pe = (market_cap / net_income) if market_cap and net_income and net_income > 0 else None
            ps = (market_cap / revenue) if market_cap and revenue and revenue > 0 else None

            raw_companies.append({
                "symbol": sym,
                "entity_name": data.get("entity_name", sym),
                "fiscal_year": latest.get("fiscal_year"),
                "market_cap": market_cap,
                "revenue": revenue,
                "net_income": net_income,
                "eps_diluted": eps,
                "gross_margin_pct": round(gross_margin, 1) if gross_margin is not None else None,
                "operating_margin_pct": round(op_margin, 1) if op_margin is not None else None,
                "net_margin_pct": round(net_margin, 1) if net_margin is not None else None,
                "revenue_growth_yoy_pct": round(rev_growth, 1) if rev_growth is not None else None,
                "net_income_growth_yoy_pct": round(ni_growth, 1) if ni_growth is not None else None,
                "pe_ratio": round(pe, 1) if pe is not None else None,
                "ps_ratio": round(ps, 1) if ps is not None else None,
            })

        except Exception as e:
            raw_companies.append({"symbol": sym, "error": str(e)})

    # Separate valid companies from errors
    valid = [c for c in raw_companies if "error" not in c]
    errors = [c for c in raw_companies if "error" in c]

    # Apply threshold filters
    filtered_out = []
    passed = []
    for c in valid:
        reasons = []
        if min_growth is not None and (c["revenue_growth_yoy_pct"] is None or c["revenue_growth_yoy_pct"] < min_growth):
            reasons.append(f"rev growth {c['revenue_growth_yoy_pct']}% < {min_growth}%")
        if min_margin is not None and (c["net_margin_pct"] is None or c["net_margin_pct"] < min_margin):
            reasons.append(f"net margin {c['net_margin_pct']}% < {min_margin}%")
        if max_pe is not None and c["pe_ratio"] is not None and c["pe_ratio"] > max_pe:
            reasons.append(f"P/E {c['pe_ratio']}x > {max_pe}x")
        if reasons:
            filtered_out.append({"symbol": c["symbol"], "reasons": reasons})
        else:
            passed.append(c)

    # Compute scores for passed companies
    if passed:
        rev_growths = [c["revenue_growth_yoy_pct"] for c in passed if c["revenue_growth_yoy_pct"] is not None]
        ni_growths = [c["net_income_growth_yoy_pct"] for c in passed if c["net_income_growth_yoy_pct"] is not None]
        net_margins = [c["net_margin_pct"] for c in passed if c["net_margin_pct"] is not None]
        op_margins = [c["operating_margin_pct"] for c in passed if c["operating_margin_pct"] is not None]
        pes = [c["pe_ratio"] for c in passed if c["pe_ratio"] is not None]
        pss = [c["ps_ratio"] for c in passed if c["ps_ratio"] is not None]

        for c in passed:
            # Growth score (higher growth = better)
            g1 = _normalize_score(c["revenue_growth_yoy_pct"], rev_growths) if c["revenue_growth_yoy_pct"] is not None else 50
            g2 = _normalize_score(c["net_income_growth_yoy_pct"], ni_growths) if c["net_income_growth_yoy_pct"] is not None else 50
            growth_score = round(g1 * 0.6 + g2 * 0.4, 1)

            # Value score (lower multiples = better)
            v1 = _normalize_score(c["pe_ratio"], pes, higher_is_better=False) if c["pe_ratio"] is not None else 50
            v2 = _normalize_score(c["ps_ratio"], pss, higher_is_better=False) if c["ps_ratio"] is not None else 50
            value_score = round(v1 * 0.5 + v2 * 0.5, 1)

            # Quality score (higher margins = better)
            q1 = _normalize_score(c["net_margin_pct"], net_margins) if c["net_margin_pct"] is not None else 50
            q2 = _normalize_score(c["operating_margin_pct"], op_margins) if c["operating_margin_pct"] is not None else 50
            quality_score = round(q1 * 0.5 + q2 * 0.5, 1)

            # Composite score weighted by style
            if style == "growth":
                composite = growth_score * 0.50 + quality_score * 0.30 + value_score * 0.20
            elif style == "value":
                composite = value_score * 0.50 + quality_score * 0.30 + growth_score * 0.20
            elif style == "quality":
                composite = quality_score * 0.50 + growth_score * 0.30 + value_score * 0.20
            else:
                composite = growth_score * 0.34 + quality_score * 0.33 + value_score * 0.33

            c["scores"] = {
                "growth": growth_score,
                "value": value_score,
                "quality": quality_score,
                "composite": round(composite, 1),
            }

        # Sort by composite score descending
        passed.sort(key=lambda c: c["scores"]["composite"], reverse=True)

        # Add rank
        for i, c in enumerate(passed):
            c["rank"] = i + 1

    return {
        "style": style,
        "filters_applied": {
            "min_revenue_growth_pct": min_growth,
            "min_net_margin_pct": min_margin,
            "max_pe_ratio": max_pe,
        },
        "total_candidates": len(symbols),
        "passed_filters": len(passed),
        "ranked_companies": passed,
        "filtered_out": filtered_out,
        "errors": errors,
        "scoring_weights": {
            "growth": {"revenue_growth": 0.6, "ni_growth": 0.4},
            "value": {"pe_ratio": 0.5, "ps_ratio": 0.5},
            "quality": {"net_margin": 0.5, "operating_margin": 0.5},
            "composite": (
                "growth 50% + quality 30% + value 20%" if style == "growth"
                else "value 50% + quality 30% + growth 20%" if style == "value"
                else "quality 50% + growth 30% + value 20%" if style == "quality"
                else "equal weight ~33% each"
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Stock screener with scoring (SEC EDGAR + Yahoo Finance)")
    parser.add_argument("symbols", nargs="+", help="Stock symbols (e.g., AAPL MSFT GOOGL)")
    parser.add_argument("--style", choices=["growth", "value", "quality"], default="growth",
                        help="Screening style (default: growth)")
    parser.add_argument("--min-growth", type=float, default=None,
                        help="Minimum revenue growth YoY %% (e.g., 10)")
    parser.add_argument("--min-margin", type=float, default=None,
                        help="Minimum net margin %% (e.g., 20)")
    parser.add_argument("--max-pe", type=float, default=None,
                        help="Maximum P/E ratio (e.g., 35)")

    args = parser.parse_args()
    result = fetch_screen(
        [s.upper() for s in args.symbols],
        style=args.style,
        min_growth=args.min_growth,
        min_margin=args.min_margin,
        max_pe=args.max_pe,
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
