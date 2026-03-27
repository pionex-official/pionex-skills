---
name: financial-analysis-comps
description: >
  Comparable company analysis using SEC EDGAR financial data.
  Use when asked to: compare multiple stocks; analyze valuation multiples for a peer group;
  benchmark margins, growth, or valuation across companies; find the cheapest or most expensive
  stock in a group; see how a company stacks up against peers.
  Triggers: "compare AAPL vs MSFT vs GOOGL", "tech sector comps", "which mega-cap has best margins",
  "peer valuation analysis", "compare these stocks", "how does NVDA compare to AMD".
  Note: For discovering/screening stocks by theme or criteria, use stock-screening instead.
---

# Comparable Company Analysis

Institutional-grade peer benchmarking for US stocks. Compares financial metrics (margins, growth, ROE), valuation multiples (P/E, P/S, EV/EBITDA, EV/Revenue), and provides statistical context (median, percentiles, percentile ranks). Data from SEC EDGAR (financials) and Yahoo Finance (market data).

## Setup

No dependencies required. All scripts use Python standard library only.

## Workflow

### Step 1 — Run the comps script

```bash
bash run.sh <SYMBOL1> <SYMBOL2> <SYMBOL3> ...
```

Max 10 symbols. Returns JSON with:
- Financial metrics: revenue, margins (gross/operating/net), ROE, YoY growth
- Valuation multiples: P/E, P/S, EV/EBITDA, EV/Revenue
- Peer statistics: min, p25, median, p75, max for each metric
- Percentile ranks: each company's rank within the peer group (0=lowest, 100=highest)

For single-company deep dive, use fundamentals instead:
```bash
bash run.sh <SYMBOL>  # single company returns full metrics
```

### Step 2 — Section 1: Comparison Table

| Company | Revenue | Gross Margin | Op Margin | Net Margin | ROE   | Rev Growth | P/E   | EV/EBITDA |
|---------|---------|--------------|-----------|------------|-------|------------|-------|-----------|
| AAPL    | $416B   | 46.9%        | 32.0%     | 26.9%      | 157%  | +6.4%      | 33.0x | 25.1x     |
| MSFT    | $282B   | 68.8%        | 45.6%     | 36.1%      | 35%   | +14.9%     | 27.2x | 21.5x     |

Include all available multiples. If EV/EBITDA is shown, note that EBITDA is approximated as operating income (D&A not available from SEC EDGAR).

**Yahoo Finance unavailable**: If P/E, P/S, EV/EBITDA, and EV/Revenue are null for all companies (Yahoo Finance endpoint failed), omit those columns from the table and add a note: "Valuation multiples unavailable — Yahoo Finance data could not be retrieved. Comparison is based on SEC EDGAR fundamentals only (margins, growth, ROE)." Rank by margins and growth instead.

### Step 3 — Section 2: Statistical Summary

Use the `peer_statistics` from script output. Present as summary rows below the table:

| Stat   | Gross Margin | Op Margin | Net Margin | ROE  | Rev Growth | P/E   | EV/EBITDA |
|--------|--------------|-----------|------------|------|------------|-------|-----------|
| Max    | 68.8%        | 45.6%     | 36.1%      | 157% | +14.9%     | 33.0x | 25.1x     |
| Median | 57.9%        | 38.8%     | 31.5%      | 96%  | +10.7%     | 30.1x | 23.3x     |
| Min    | 46.9%        | 32.0%     | 26.9%      | 35%  | +6.4%      | 27.2x | 21.5x     |

If 5+ companies, include p25 and p75 rows — with fewer than 5 data points, percentiles are not statistically meaningful and can mislead (e.g. p25 of 3 values is just near the min). Only include columns in the statistics table that have data for at least 2 companies — omit any column that is entirely null.

### Step 4 — Section 3: Investment Interpretation

Use the `percentile_ranks` from script output. For each company, highlight where it stands relative to peers:

```
AAPL: Margins below median (p27), cheapest valuation (P/E p0), slowest growth (p0)
MSFT: Highest margins (p100), fastest growth (p100), richer valuation (P/E p100)
```

Focus on outliers — metrics where a company is notably above p75 or below p25 vs peers.

Then synthesize findings:
- **Premium vs. discount**: which companies trade at a premium/discount to peer median on multiples, and is it justified by growth or margins?
- **Best positioned**: which offers the best combination of growth + margins at reasonable valuation?
- **Watch out**: any company where valuation is high but fundamentals are deteriorating?

---

## Formatting Rules

- Revenue/Net Income: B or M, e.g. "$416.2B"
- EPS: plain decimal, e.g. "$7.46"
- Margins, growth, ROE: one decimal percent, e.g. "26.9%"
- Multiples: one decimal, e.g. "28.4x"
- Percentile: integer, e.g. "p75"

## Limitations

- **US stocks only**: SEC EDGAR covers US-listed equities
- **Annual data**: uses 10-K filings; quarterly shifts may not be reflected
- **EV/EBITDA approximation**: uses operating income as EBITDA proxy (D&A not in EDGAR XBRL)
- **No analyst estimates**: reported actuals only, not consensus forecasts
