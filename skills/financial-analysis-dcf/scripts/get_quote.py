#!/usr/bin/env python3
"""
Fetch current stock quote from Yahoo Finance.

Usage:
    python get_quote.py AAPL [MSFT GOOGL ...]

Output: JSON with current price, market cap, shares outstanding, PE, etc.

No pip dependencies — uses Yahoo Finance endpoints via urllib with cookie+crumb auth.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import http.cookiejar

YF_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
YF_CRUMB_URL = "https://query2.finance.yahoo.com/v1/test/getcrumb"
YF_SUMMARY_URL = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=price,defaultKeyStatistics,summaryDetail&crumb={crumb}"

_opener = None
_crumb = None


def _init_session():
    """Initialize cookie jar and fetch crumb (one-time per process)."""
    global _opener, _crumb
    if _opener is not None:
        return

    cj = http.cookiejar.CookieJar()
    _opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    _opener.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")]

    # Step 1: hit a Yahoo page to get cookies
    try:
        _opener.open("https://fc.yahoo.com/", timeout=10)
    except urllib.error.HTTPError:
        pass  # 404 is expected, but cookies are set
    except Exception:
        pass

    # Step 2: fetch crumb using those cookies
    try:
        resp = _opener.open(YF_CRUMB_URL, timeout=10)
        _crumb = resp.read().decode("utf-8").strip()
    except Exception:
        _crumb = None


def _yf_get(url: str, use_session: bool = False) -> dict | None:
    """Fetch JSON from Yahoo Finance."""
    try:
        if use_session and _opener:
            resp = _opener.open(url, timeout=10)
        else:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0")
            resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None


def _raw_val(obj):
    """Extract raw value from Yahoo Finance formatted object like {'raw': 1.23, 'fmt': '1.23'}."""
    if isinstance(obj, dict):
        return obj.get("raw")
    return obj


def fetch_quote(symbols: list[str]) -> dict:
    _init_session()
    quotes = []

    for sym in symbols:
        sym = sym.upper()
        try:
            # Chart endpoint for price (reliable, no auth needed)
            data = _yf_get(YF_CHART_URL.format(symbol=sym))
            if not data:
                quotes.append({"symbol": sym, "error": "Failed to fetch quote"})
                continue

            result_list = data.get("chart", {}).get("result")
            if not result_list:
                quotes.append({"symbol": sym, "error": "No chart data"})
                continue

            meta = result_list[0].get("meta", {})

            quote = {
                "symbol": sym,
                "name": meta.get("longName") or meta.get("shortName") or sym,
                "current_price": meta.get("regularMarketPrice"),
                "previous_close": meta.get("previousClose") or meta.get("chartPreviousClose"),
                "market_cap": None,
                "shares_outstanding": None,
                "enterprise_value": None,
                "volume": meta.get("regularMarketVolume"),
                "fifty_two_week_high": meta.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": meta.get("fiftyTwoWeekLow"),
                "pe_trailing": None,
                "pe_forward": None,
                "eps_trailing": None,
                "beta": None,
                "dividend_yield": None,
                "currency": meta.get("currency"),
                "exchange": meta.get("exchangeName"),
            }

            # Try quoteSummary with crumb for richer data
            if _crumb:
                summary = _yf_get(
                    YF_SUMMARY_URL.format(symbol=sym, crumb=urllib.request.quote(_crumb)),
                    use_session=True,
                )
                if summary:
                    modules = summary.get("quoteSummary", {}).get("result")
                    if modules:
                        mod = modules[0]
                        price = mod.get("price", {})
                        stats = mod.get("defaultKeyStatistics", {})
                        detail = mod.get("summaryDetail", {})

                        quote["name"] = _raw_val(price.get("longName")) or price.get("shortName") or quote["name"]
                        quote["market_cap"] = _raw_val(price.get("marketCap"))
                        quote["shares_outstanding"] = _raw_val(stats.get("sharesOutstanding")) or _raw_val(price.get("sharesOutstanding"))
                        quote["enterprise_value"] = _raw_val(stats.get("enterpriseValue"))
                        quote["pe_trailing"] = _raw_val(detail.get("trailingPE"))
                        quote["pe_forward"] = _raw_val(stats.get("forwardPE"))
                        quote["eps_trailing"] = _raw_val(stats.get("trailingEps"))
                        quote["beta"] = _raw_val(stats.get("beta"))
                        quote["dividend_yield"] = _raw_val(detail.get("dividendYield"))

            quotes.append(quote)

        except Exception as e:
            quotes.append({"symbol": sym, "error": str(e)})

    return {"quotes": quotes}


def main():
    parser = argparse.ArgumentParser(description="Fetch stock quotes")
    parser.add_argument("symbols", nargs="+", help="Stock symbols")
    args = parser.parse_args()

    result = fetch_quote([s.upper() for s in args.symbols])
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
