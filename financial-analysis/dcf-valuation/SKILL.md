---
name: dcf-valuation
description: >
  DCF (Discounted Cash Flow) valuation for US stocks using SEC EDGAR financials.
  Use when asked to: estimate intrinsic value or fair value of a US stock;
  determine if a stock is overvalued or undervalued; run a discounted cash flow analysis;
  calculate upside/downside from current price.
  Triggers: "what is AAPL worth", "DCF MSFT", "is NVDA overvalued",
  "intrinsic value of GOOGL", "fair value Tesla".
---

# DCF Valuation

Estimate intrinsic value per share using a discounted cash flow model. Data from SEC EDGAR (financials), FRED (risk-free rate), and Yahoo Finance (price, beta).

## Setup

No dependencies required. All scripts use Python standard library only.

## Workflow

### Step 1 — Run the DCF script

```bash
bash run.sh <SYMBOL>
# With custom assumptions:
bash run.sh <SYMBOL> --terminal-growth 3.0 --fcf-growth 15 --projection-years 7
```

The script:
1. Fetches 5 years of 10-K data from SEC EDGAR
2. Computes unlevered FCF = OCF − CapEx + InterestExpense × (1−T)
3. Derives historical FCF growth rate (or uses override)
4. Gets risk-free rate from FRED (10Y Treasury)
5. Gets beta and current price from Yahoo Finance
6. Calculates WACC = Ke × E/V + Kd × (1−T) × D/V
7. Projects FCFs, computes terminal value (Gordon Growth Model)
8. Generates 5×5 sensitivity table (WACC vs terminal growth)

### Step 2 — Section 1: Summary

**First output must be this summary box:**

```
[TICKER] — DCF VALUATION

Intrinsic value:  $XXX.XX  |  Current price: $XXX.XX  |  ▲/▼ XX.X%
WACC:             X.X%     |  Terminal growth: X.X%   |  FCF base: $X.XB
```

### Step 3 — Section 2: Sensitivity Table

Show the full 5×5 sensitivity table from the JSON output:

```
Terminal Growth \\ WACC  |  8.2%   |  9.2%   |  10.2%
------------------------|---------|---------|--------
1.5%                    | $198.4  | $176.2  | $158.1
2.5%                    | $221.3  | $194.5  | $172.6
3.5%                    | $251.7  | $218.0  | $191.4
```

Display `N/A` for null values (WACC ≤ terminal growth).

### Step 4 — Section 3: Interpretation

Note key assumptions and their impact:
- Which inputs drive the most variance (usually WACC and growth rate)
- Whether the beta seems reasonable for the company
- How the historical FCF growth rate compares to analyst expectations
- Any red flags (negative FCF years, volatile cash flows, high debt)

**Disclaimer**: DCF output is highly sensitive to WACC and growth assumptions. It should be used as one input among many, not as a definitive price target. Always present the sensitivity table alongside the point estimate.

---

## Model Assumptions

- **ERP**: 5.5% (Damodaran market average)
- **Tax rate**: derived from SEC filings (IncomeTaxExpense / PreTaxIncome); fallback 21%
- **Cost of debt**: derived from SEC filings (InterestExpense / LongTermDebt); fallback 4%
- **FCF**: Unlevered = OCF − CapEx + InterestExpense × (1−T) from most recent 10-K
- **FCF growth**: per-share UFCF CAGR from historical 10-K data (accounts for buybacks); fallback 3% if insufficient data
- **Beta**: OLS regression on daily returns vs SPY (~5 years); Blume adjustment applied (adjusted = 0.67 × raw + 0.33)
- **Shares outstanding**: from SEC EDGAR; fallback to market cap / price
- **Mid-year convention**: FCFs and terminal value both discounted at mid-year

## Formatting Rules

- Intrinsic value and current price: "$XXX.XX"
- Upside/downside: "▲ +XX.X%" or "▼ −XX.X%"
- WACC and growth rates: one decimal, e.g. "9.2%"
- FCF: B or M, e.g. "$12.3B"

## When NOT to Use

- **Negative or volatile FCF**: companies with negative free cash flow cannot be valued via DCF — the model requires a positive base FCF to project forward
- **Banks and financial institutions**: revenue and cash flow structures differ fundamentally (interest income vs. operating revenue); use price-to-book or dividend discount models instead
- **Insurance companies**: similar to banks — earnings driven by underwriting and investment income, not operating cash flow
- **Pre-revenue or early-stage companies**: no meaningful FCF history to extrapolate

## Limitations

- **US stocks only**: SEC EDGAR data for US-listed equities
- **Backward-looking**: uses historical financials — future may differ significantly
- **No analyst estimates**: growth rates extrapolated from historical data unless user provides one
