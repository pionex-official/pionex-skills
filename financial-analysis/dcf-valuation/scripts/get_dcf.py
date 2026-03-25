#!/usr/bin/env python3
"""
DCF (Discounted Cash Flow) valuation using SEC EDGAR + Yahoo Finance.

Usage:
    python get_dcf.py AAPL
    python get_dcf.py MSFT --terminal-growth 3.0 --projection-years 7

Output: JSON with intrinsic value, assumptions, and sensitivity table.

No pip dependencies. Uses SEC EDGAR for financials, Yahoo Finance for price/beta.
"""

import argparse
import json
import math
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from get_fundamentals import fetch_fundamentals
from get_quote import fetch_quote

# Constants
ERP = 5.5            # Equity Risk Premium (Damodaran)
DEFAULT_TAX_RATE = 0.21
DEFAULT_COST_OF_DEBT = 4.0
DEFAULT_TERMINAL_GROWTH = 2.5
DEFAULT_PROJECTION_YEARS = 5
DEFAULT_RISK_FREE_RATE = 4.0


def _get_risk_free_rate() -> float:
    """Fetch 10-year US Treasury yield from FRED CSV endpoint (no API key needed)."""
    import csv
    import io
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "finchat-skills contact@finchat.ai")
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode("utf-8")
        reader = csv.reader(io.StringIO(text))
        next(reader)  # skip header
        latest = None
        for row in reader:
            if len(row) >= 2 and row[1] != ".":
                try:
                    latest = float(row[1])
                except ValueError:
                    continue
        if latest is not None:
            return latest
    except Exception:
        pass
    return DEFAULT_RISK_FREE_RATE


def _calc_dcf(base_fcf, growth_rate, wacc, terminal_growth, years, debt, cash, shares):
    """Core DCF calculation. Returns (ev, equity_value, intrinsic_per_share)."""
    if wacc <= terminal_growth:
        return -1, -1, -1

    pv_fcf = 0.0
    fcf = base_fcf
    for i in range(1, years + 1):
        fcf *= (1 + growth_rate)
        pv_fcf += fcf / math.pow(1 + wacc, i - 0.5)  # mid-year convention

    # Terminal value (Gordon Growth Model)
    terminal_fcf = fcf * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    pv_terminal = terminal_value / math.pow(1 + wacc, years + 0.5)  # mid-year convention

    ev = pv_fcf + pv_terminal
    net_debt = debt - cash
    equity = max(0, ev - net_debt)
    intrinsic = equity / shares if shares > 0 else 0
    return ev, equity, intrinsic


def _historical_fcf_growth(periods: list[dict]) -> float:
    """Calculate mean annualized per-share UFCF growth from SEC EDGAR periods."""
    entries = []
    for p in periods:
        ocf = p.get("operating_cash_flow") or 0
        capex = p.get("capital_expenditure") or 0
        interest = p.get("interest_expense") or 0
        pretax = p.get("pretax_income") or 0
        tax_exp = p.get("income_tax_expense") or 0
        shares = p.get("shares_outstanding") or 0

        tr = DEFAULT_TAX_RATE
        if pretax > 0 and tax_exp > 0:
            tr = max(0.05, min(0.40, tax_exp / pretax))

        capex = abs(capex)
        fcf = ocf - capex + interest * (1 - tr)
        if fcf > 0 and shares > 0:
            entries.append({"year": p.get("fiscal_year", 0), "fcf_per_share": fcf / shares})

    if len(entries) < 2:
        return 3.0

    total = 0.0
    count = 0
    for i in range(len(entries) - 1):
        curr, prev = entries[i], entries[i + 1]
        span = curr["year"] - prev["year"]
        if span <= 0 or prev["fcf_per_share"] <= 0:
            continue
        annualized = (math.pow(curr["fcf_per_share"] / prev["fcf_per_share"], 1.0 / span) - 1) * 100
        total += annualized
        count += 1

    return round(total / count, 2) if count > 0 else 3.0


def run_dcf(symbol: str, fcf_growth_override: float | None = None, terminal_growth: float = DEFAULT_TERMINAL_GROWTH,
            projection_years: int = DEFAULT_PROJECTION_YEARS) -> dict:
    symbol = symbol.upper()

    # 1. Fetch 5 years of annual financials
    data = fetch_fundamentals(symbol, form="10-K", periods=5)
    if data.get("error"):
        return {"symbol": symbol, "error": data["error"]}
    periods = data.get("periods", [])
    if not periods:
        return {"symbol": symbol, "error": "No annual data available"}

    entity_name = data.get("entity_name", symbol)
    latest = periods[0]

    # 2. Tax rate and cost of debt
    ltd = latest.get("long_term_debt") or 0
    interest = latest.get("interest_expense") or 0
    pretax = latest.get("pretax_income") or 0
    tax_exp = latest.get("income_tax_expense") or 0

    kd = DEFAULT_COST_OF_DEBT
    if ltd > 0 and interest > 0:
        kd = max(1, min(15, (interest / ltd) * 100))

    tax_rate = DEFAULT_TAX_RATE
    if pretax > 0 and tax_exp > 0:
        tax_rate = max(0.05, min(0.40, tax_exp / pretax))

    # 3. Base FCF (unlevered)
    ocf = latest.get("operating_cash_flow") or 0
    capex = abs(latest.get("capital_expenditure") or 0)
    interest_addback = interest * (1 - tax_rate)
    base_fcf = ocf - capex + interest_addback

    if base_fcf <= 0:
        return {"symbol": symbol, "error": f"Negative FCF (OCF={ocf}, CapEx={capex}). DCF requires positive FCF."}

    # 4. FCF growth rate
    fcf_growth = fcf_growth_override if fcf_growth_override is not None else _historical_fcf_growth(periods)
    fcf_growth = max(-20, min(50, fcf_growth))

    # 5. Risk-free rate
    rf_rate = _get_risk_free_rate()

    # 6. Beta (OLS regression vs SPY, Blume-adjusted) and current price
    from get_beta import calculate_beta
    beta_result = calculate_beta(symbol)
    beta = beta_result.get("adjusted_beta") or 1.0

    quote_data = fetch_quote([symbol])
    quote = quote_data["quotes"][0] if quote_data.get("quotes") else {}
    current_price = quote.get("current_price") or 0
    market_cap = quote.get("market_cap") or 0

    # 7. Cost of equity (CAPM)
    ke = rf_rate + beta * ERP

    # 8. Shares — prefer Yahoo Finance (more current), fallback to SEC EDGAR
    shares = quote.get("shares_outstanding") or latest.get("shares_outstanding") or 0
    if shares <= 0 and current_price > 0 and market_cap > 0:
        shares = market_cap / current_price

    # 9. WACC
    if market_cap <= 0 and current_price > 0 and shares > 0:
        market_cap = current_price * shares
    debt = ltd
    total_capital = market_cap + debt
    we = market_cap / total_capital if total_capital > 0 else 1.0
    wd = debt / total_capital if total_capital > 0 else 0.0
    wacc = round(ke * we + kd * (1 - tax_rate) * wd, 2)

    # 10. DCF calculation
    ev, equity, intrinsic = _calc_dcf(
        base_fcf, fcf_growth / 100, wacc / 100, terminal_growth / 100,
        projection_years, debt, latest.get("cash_and_equivalents") or 0, shares
    )
    upside = round((intrinsic / current_price - 1) * 100, 2) if current_price > 0 and intrinsic > 0 else 0

    # 11. Sensitivity table
    wacc_range = [wacc - 1, wacc - 0.5, wacc, wacc + 0.5, wacc + 1]
    tg_range = [terminal_growth - 1, terminal_growth - 0.5, terminal_growth, terminal_growth + 0.5, terminal_growth + 1]

    sensitivity = []
    for w in wacc_range:
        row = {"wacc_pct": round(w, 1), "intrinsic_by_terminal_growth": {}}
        for tg in tg_range:
            _, _, iv = _calc_dcf(
                base_fcf, fcf_growth / 100, w / 100, tg / 100,
                projection_years, debt, latest.get("cash_and_equivalents") or 0, shares
            )
            key = f"{tg:.1f}%"
            row["intrinsic_by_terminal_growth"][key] = round(iv, 2) if iv >= 0 else None
        sensitivity.append(row)

    return {
        "symbol": symbol,
        "entity_name": entity_name,
        "current_price": round(current_price, 2),
        "intrinsic_value_per_share": round(intrinsic, 2),
        "upside_downside_pct": upside,
        "enterprise_value": round(ev),
        "equity_value": round(equity),
        "shares_outstanding": round(shares),
        "assumptions": {
            "risk_free_rate_pct": round(rf_rate, 2),
            "beta": round(beta, 2),
            "beta_data_points": beta_result.get("data_points"),
            "beta_period": beta_result.get("period"),
            "equity_risk_premium_pct": ERP,
            "cost_of_equity_pct": round(ke, 2),
            "cost_of_debt_pct": round(kd, 2),
            "tax_rate_pct": round(tax_rate * 100, 2),
            "wacc_pct": wacc,
            "fcf_growth_rate_pct": round(fcf_growth, 2),
            "terminal_growth_rate_pct": terminal_growth,
            "projection_years": projection_years,
            "base_fcf": round(base_fcf),
        },
        "sensitivity_wacc_vs_terminal_growth": sensitivity,
        "sources": {
            "financials": "SEC EDGAR (XBRL)",
            "risk_free_rate": "FRED (DGS10)",
            "beta": "OLS regression vs SPY (Blume-adjusted)",
            "price": "Yahoo Finance",
        },
        "note": "Intrinsic value is highly sensitive to WACC and growth assumptions. Use the sensitivity table for a range of outcomes. null in the table means WACC <= terminal growth (undefined).",
    }


def main():
    parser = argparse.ArgumentParser(description="DCF valuation (SEC EDGAR + Yahoo Finance)")
    parser.add_argument("symbol", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--fcf-growth", type=float, default=None, help="Override FCF growth rate (%%)")
    parser.add_argument("--terminal-growth", type=float, default=DEFAULT_TERMINAL_GROWTH, help="Terminal growth rate (%%)")
    parser.add_argument("--projection-years", type=int, default=DEFAULT_PROJECTION_YEARS, help="Projection years")

    args = parser.parse_args()
    result = run_dcf(args.symbol, args.fcf_growth, args.terminal_growth, args.projection_years)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
