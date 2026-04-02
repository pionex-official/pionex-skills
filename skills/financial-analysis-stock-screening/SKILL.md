---
name: financial-analysis-stock-screening
description: >
  Stock screening and ranking for US equities using SEC EDGAR data.
  Use when asked to: find stocks by sector or theme; rank stocks by valuation,
  growth, or quality metrics; surface investment ideas; screen for stocks meeting
  specific criteria; find the best growth/value/quality stocks in a group.
  Triggers: "best AI stocks", "cheap healthcare stocks", "fastest growing semiconductors",
  "find me value stocks", "screen for high-growth tech", "rank these stocks by quality",
  "which of these is the best growth stock".
  Note: For side-by-side peer benchmarking with statistical analysis, use comps-analysis instead.
---

# Stock Screening

Quantitative stock screener with composite scoring. Discovers candidates via web search, filters by thresholds, scores on growth/value/quality dimensions, and returns a ranked list with actionable picks. Data from SEC EDGAR (financials), Yahoo Finance (market data), and web search (universe discovery).

**IMPORTANT: This skill requires running `bash run.sh` to produce scores. You MUST execute the script and use its JSON output — do not skip it or compute metrics manually. The script returns growth/value/quality scores (0-100) and composite rankings that must appear in the output.**

## Setup

No dependencies required. All scripts use Python standard library only.

## Workflow

### Step 1 — Clarify criteria

Before running any script, understand:
- **Universe**: sector, theme, or broad market?
- **Style**: growth (high revenue/earnings growth), value (cheap multiples), or quality (high margins)?
- **Thresholds**: e.g. "revenue growth >20%", "P/E below 25x", "margin >30%"

If the user gives a vague request like "find me good tech stocks", default to **growth** style and state the assumption. If the user remains vague after clarification (no specific style or thresholds), default to **growth + quality**: rank by revenue growth first, then net margin as tiebreaker. State this explicitly so the user can adjust.

### Step 2 — Build the candidate universe

Use **web search** to identify the relevant stock universe:
- `top [sector] stocks by market cap [year]`
- `[theme] stocks list [year]` (e.g. "AI stocks list 2026")
- `S&P 500 [sector] constituents`

Common universes for reference:

| Theme | Example symbols |
|-------|----------------|
| Magnificent 7 | AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA |
| Semiconductors | NVDA, AMD, INTC, AVGO, QCOM, TXN, MRVL, MU |
| AI concept | NVDA, MSFT, GOOGL, META, AMZN, CRM, PLTR, SNOW |
| EV / Clean Energy | TSLA, RIVN, LCID, NIO, ENPH, FSLR, PLUG |

These are reference examples — always verify via web search for the current year, as index constituents and thematic groupings change over time.

Narrow to **max 10 symbols** before running the screener. State which symbols were excluded and why.

### Step 3 — Run the screener

**Always run the screener script** — do not compute scores or filter manually. The script produces standardized scores, rankings, and filter results that must be used in Step 4.

```bash
bash run.sh <SYM1> <SYM2> ... <SYM10> --style <growth|value|quality>
# With filters:
bash run.sh <SYMS> --style growth --min-growth 10 --min-margin 15 --max-pe 40
```

**Scoring system:**

Each company is scored 0-100 on three dimensions:
- **Growth score** (60% revenue growth + 40% net income growth)
- **Value score** (50% P/E + 50% P/S — lower multiples score higher)
- **Quality score** (50% net margin + 50% operating margin)

Composite score is weighted by style:
- `growth`: 50% growth + 30% quality + 20% value
- `value`: 50% value + 30% quality + 20% growth
- `quality`: 50% quality + 30% growth + 20% value

**Threshold filters** (optional):
- `--min-growth N`: exclude companies with revenue growth < N%
- `--min-margin N`: exclude companies with net margin < N%
- `--max-pe N`: exclude companies with P/E > Nx

### Step 4 — Present ranked results

Use the JSON output from `get_screen.py` directly — present the `scores`, `rank`, and `filtered_out` fields as-is. Do not invent your own scoring system (no star ratings, no PEG-based rankings). The script's composite score is the authoritative ranking.

**Lead with screen summary:**
```
Screen: [Style] — [Sector/Theme]
Universe: [N] candidates → [M] passed filters
Ranked by: composite score ([style] weighted)
```

**Then ranked table (sorted by composite score):**

| Rank | Symbol | Revenue | Rev Growth | Net Margin | P/E   | Growth | Value | Quality | Composite |
|------|--------|---------|------------|------------|-------|--------|-------|---------|-----------|
| 1    | NVDA   | $130B   | +114%      | 55.8%      | 35.8x | 98.2   | 42.1  | 89.5    | 84.7      |
| 2    | META   | $162B   | +22%       | 35.6%      | 25.4x | 72.1   | 68.3  | 72.0    | 71.2      |

**Then Top 3 picks:**
```
1. [TICKER] — [One-line thesis]  (Composite: XX.X)
   [Why it ranks highest — which scores drive the result]
   [Key risk or caveat]
```

**Filtered out (if any):**
```
Excluded: [TICKER] (rev growth 5.2% < 10% threshold)
```

### Step 5 — Deep dive (if user wants)

For top picks, validate with historical trend:
```bash
bash run.sh <SYMBOL> --style quality  # re-run with single symbol for detail
```

Check: is the metric improving over time or a one-time event?

Optionally, validate the pick against its sector peers using the **comps-analysis** skill for full statistical benchmarking.

---

## Output Format

Sections in order:
1. Screen summary box
2. Ranked table with scores
3. Top 3 picks with thesis
4. Filtered out / excluded (if any)
5. Caveats

**Close with caveats:**
- Scores are relative within this peer group — adding/removing a company changes all scores
- Screens surface candidates, not conclusions — each pick needs further validation
- SEC data is annual (10-K); recent quarterly shifts may not be reflected

---

## Formatting Rules

- Revenue: B or M, e.g. "$416B"
- Margins and growth: one decimal, e.g. "26.9%", "+15.7%"
- Multiples: one decimal, e.g. "28.4x"
- Scores: one decimal, e.g. "84.7"

## Limitations

- **Relative scoring**: scores are only meaningful within the screened group, not absolute
- **No real-time price data**: P/E and P/S depend on Yahoo Finance availability
- **US stocks only**: SEC EDGAR covers US-listed equities
- **Annual data**: 10-K by default; quarterly shifts may not be reflected
- **No dividend data**: For income-style screening, dividend yield must come from web search
