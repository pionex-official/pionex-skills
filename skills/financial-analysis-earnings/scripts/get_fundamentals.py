#!/usr/bin/env python3
"""
Fetch quarterly and annual financial statements from SEC EDGAR XBRL API.

Usage:
    python get_fundamentals.py <SYMBOL> [--form 10-K|10-Q] [--periods N]

Output: JSON with an array of financial periods.

Data source: SEC EDGAR (https://data.sec.gov)
No API key required. No external dependencies.
Rate limited to ~8 req/s per SEC guidelines.

Important: 10-Q data is YTD cumulative. Derive standalone quarters by subtraction:
  Q1 standalone = Q1 YTD
  Q2 standalone = H1 YTD - Q1 YTD
  Q3 standalone = 9M YTD - H1 YTD
  Q4 standalone = Full-year (10-K) - 9M YTD
"""

import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime

BASE_URL = "https://data.sec.gov"
TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
USER_AGENT = "finchat-skills contact@finchat.ai"
MIN_REQUEST_INTERVAL = 0.12  # ~8 req/s

_last_request_at = 0.0
_ticker_cik_map = None


def _throttle():
    global _last_request_at
    elapsed = time.time() - _last_request_at
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_at = time.time()


def _get_json(url: str) -> dict:
    _throttle()
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except (urllib.request.URLError, urllib.error.HTTPError) as e:
        raise RuntimeError(f"SEC EDGAR request failed for {url}: {e}")


def _ensure_ticker_map() -> dict[str, int]:
    global _ticker_cik_map
    if _ticker_cik_map is not None:
        return _ticker_cik_map
    raw = _get_json(TICKER_URL)
    _ticker_cik_map = {}
    for entry in raw.values():
        _ticker_cik_map[entry["ticker"].upper()] = entry["cik_str"]
    return _ticker_cik_map


def _lookup_cik(ticker: str) -> int:
    m = _ensure_ticker_map()
    cik = m.get(ticker.upper())
    if cik is None:
        raise ValueError(f"Ticker {ticker!r} not found in SEC EDGAR")
    return int(cik)


# ── XBRL parsing ──


def _first_concept(usgaap: dict, *names: str):
    """Return the concept with the most recent data among the given names."""
    best = None
    best_end = ""
    for name in names:
        concept = usgaap.get(name)
        if not concept:
            continue
        units = concept.get("units", {})
        for unit_facts in units.values():
            for f in unit_facts:
                end = f.get("end", "")
                if end > best_end:
                    best_end = end
                    best = concept
            break
    return best


def _facts_for_form(concept, form: str) -> dict[str, float]:
    """Extract period_end -> value map for a filing form type."""
    m = {}
    if not concept:
        return m
    units = concept.get("units", {})
    for unit_facts in units.values():
        for f in unit_facts:
            if f.get("form") == form:
                end = f.get("end", "")
                if end not in m:
                    m[end] = f.get("val", 0)
        break
    return m


def _anchor_periods(concept, form: str, n: int) -> list[dict]:
    """Return the most recent N filing facts for a form type."""
    if not concept:
        return []
    facts = []
    units = concept.get("units", {})
    for unit_facts in units.values():
        for f in unit_facts:
            if f.get("form") == form:
                facts.append(f)
        break
    facts.sort(key=lambda f: f.get("end", ""), reverse=True)
    seen = set()
    deduped = []
    for f in facts:
        end = f.get("end", "")
        if end not in seen:
            seen.add(end)
            deduped.append(f)
    return deduped[:n] if n > 0 else deduped


def _fiscal_quarter_from_period(start: str, end: str, form: str) -> tuple[int, bool]:
    """Derive fiscal quarter and YTD flag from filing dates.
    10-K -> quarter=4, isYTD=False
    10-Q ~3mo -> Q1, ~6mo -> Q2, ~9mo -> Q3, all isYTD=True
    """
    if form == "10-K":
        return 4, False
    if not start or not end:
        return 0, True
    try:
        t0 = datetime.strptime(start, "%Y-%m-%d")
        t1 = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return 0, True
    days = (t1 - t0).days
    if days < 105:
        return 1, True
    elif days < 196:
        return 2, True
    else:
        return 3, True


def _period_label(start: str, end: str, fy: int, fq: int, form: str) -> str:
    """Build human-readable label, e.g. 'FY2025 Q1 (Oct-Dec 2024)'."""
    if not start or not end:
        return f"FY{fy} Annual" if form == "10-K" else f"FY{fy} Q{fq}"
    try:
        t0 = datetime.strptime(start, "%Y-%m-%d")
        t1 = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return f"FY{fy} Annual" if form == "10-K" else f"FY{fy} Q{fq}"
    s = t0.strftime("%b %Y")
    e = t1.strftime("%b %Y")
    if form == "10-K":
        return f"FY{fy} Annual ({s}\u2013{e})"
    return f"FY{fy} Q{fq} ({s}\u2013{e})"


def _eps_for_period(eps: float, is_ytd: bool, quarter: int):
    """Return EPS only when directly usable as standalone figure.
    Q2/Q3 YTD EPS is NOT additive — zeroed to prevent misuse."""
    if not is_ytd:
        return eps  # 10-K full-year
    if quarter == 1:
        return eps  # Q1 YTD == Q1 standalone
    return None  # Q2/Q3: must compute from standalone net_income / shares


def _derived_gross_profit(gp, revenue, cost_of_revenue):
    if gp is not None:
        return gp
    if revenue and cost_of_revenue:
        return revenue - cost_of_revenue
    return None


def _normalize_shares_scale(shares, net_income, eps):
    """Correct for companies reporting shares in thousands or millions."""
    if not shares or shares <= 0 or not eps or not net_income:
        return shares if shares else None
    implied = abs(net_income) / abs(eps)
    ratio = implied / shares
    if 500 <= ratio < 5000:
        return shares * 1000
    elif 500_000 <= ratio < 5_000_000:
        return shares * 1_000_000
    return shares


# ── Main fetch ──


def fetch_fundamentals(symbol: str, form: str = "10-K", periods: int = 4) -> dict:
    symbol = symbol.upper()
    if periods <= 0:
        periods = 4
    elif periods > 8:
        periods = 8

    cik = _lookup_cik(symbol)
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik:010d}.json"
    raw = _get_json(url)

    entity_name = raw.get("entityName", symbol)
    usgaap = raw.get("facts", {}).get("us-gaap")
    if not usgaap:
        return {"symbol": symbol, "entity_name": entity_name, "error": "No US-GAAP data available", "periods": []}

    rev_concept = _first_concept(usgaap,
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
    )

    anchor_concept = rev_concept or usgaap.get("NetIncomeLoss")
    if not anchor_concept:
        return {"symbol": symbol, "entity_name": entity_name, "error": "No financial data found", "periods": []}

    anchors = _anchor_periods(anchor_concept, form, periods)
    if not anchors:
        return {"symbol": symbol, "entity_name": entity_name, "error": f"No {form} filings found", "periods": []}

    # Build period->value lookup maps
    rev_map = _facts_for_form(rev_concept, form)
    ni_map = _facts_for_form(_first_concept(usgaap, "NetIncomeLoss", "NetIncomeLossAttributableToParent", "ProfitLoss"), form)
    gp_map = _facts_for_form(_first_concept(usgaap, "GrossProfit", "GrossProfitLoss"), form)
    cor_map = _facts_for_form(_first_concept(usgaap, "CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"), form)
    oi_map = _facts_for_form(_first_concept(usgaap, "OperatingIncomeLoss"), form)
    eps_map = _facts_for_form(_first_concept(usgaap, "EarningsPerShareDiluted"), form)
    ocf_map = _facts_for_form(_first_concept(usgaap, "NetCashProvidedByUsedInOperatingActivities"), form)
    capex_map = _facts_for_form(_first_concept(usgaap,
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsForCapitalImprovements",
        "PaymentsToAcquireOtherProductiveAssets",
    ), form)
    assets_map = _facts_for_form(usgaap.get("Assets"), form)
    liab_map = _facts_for_form(usgaap.get("Liabilities"), form)
    equity_map = _facts_for_form(_first_concept(usgaap,
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ), form)
    ltd_map = _facts_for_form(_first_concept(usgaap, "LongTermDebt", "LongTermDebtNoncurrent"), form)
    interest_map = _facts_for_form(_first_concept(usgaap, "InterestExpense", "InterestAndDebtExpense"), form)
    tax_map = _facts_for_form(_first_concept(usgaap, "IncomeTaxExpenseBenefit"), form)
    pretax_map = _facts_for_form(_first_concept(usgaap,
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
    ), form)
    cash_map = _facts_for_form(_first_concept(usgaap,
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsAndShortTermInvestments",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ), form)
    shares_map = _facts_for_form(_first_concept(usgaap,
        "CommonStockSharesOutstanding",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
    ), form)

    results = []
    for af in anchors:
        end = af.get("end", "")
        start = af.get("start", "")
        fy = af.get("fy", 0)

        q, is_ytd = _fiscal_quarter_from_period(start, end, form)
        raw_eps = eps_map.get(end, 0)
        eps = _eps_for_period(raw_eps, is_ytd, q)
        net_income = ni_map.get(end, 0)
        shares = _normalize_shares_scale(shares_map.get(end, 0), net_income, raw_eps)
        revenue = rev_map.get(end, 0)
        gross_profit = _derived_gross_profit(gp_map.get(end), revenue, cor_map.get(end, 0))

        period = {
            "period": end,
            "form": form,
            "fiscal_year": fy,
            "fiscal_quarter": q,
            "is_ytd": is_ytd,
            "period_label": _period_label(start, end, fy, q, form),
            "revenue": revenue if revenue else None,
            "gross_profit": gross_profit,
            "operating_income": oi_map.get(end),
            "net_income": net_income if net_income else None,
            "eps_diluted": eps,
            "pretax_income": pretax_map.get(end),
            "interest_expense": interest_map.get(end),
            "income_tax_expense": tax_map.get(end),
            "total_assets": assets_map.get(end),
            "total_liabilities": liab_map.get(end),
            "shareholders_equity": equity_map.get(end),
            "cash_and_equivalents": cash_map.get(end),
            "long_term_debt": ltd_map.get(end),
            "shares_outstanding": shares,
            "operating_cash_flow": ocf_map.get(end),
            "capital_expenditure": capex_map.get(end),
        }
        results.append(period)

    return {
        "symbol": symbol,
        "entity_name": entity_name,
        "form": form,
        "periods": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch financial fundamentals from SEC EDGAR")
    parser.add_argument("symbol", help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--form", choices=["10-K", "10-Q"], default="10-K", help="Filing type (default: 10-K)")
    parser.add_argument("--periods", type=int, default=4, help="Number of periods to fetch (default: 4)")

    args = parser.parse_args()
    result = fetch_fundamentals(args.symbol.upper(), args.form, args.periods)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
