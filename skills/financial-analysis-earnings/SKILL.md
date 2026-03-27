---
name: financial-analysis-earnings
description: >
  Quarterly earnings analysis for US stocks using SEC EDGAR financial data.
  Use when asked to: analyze a company's latest quarterly results; review Q1/Q2/Q3/Q4 earnings;
  check if a company beat or missed estimates; understand revenue, margin, or EPS trends;
  get a beat/miss breakdown; review guidance or management commentary after an earnings release.
  Triggers: "analyze AAPL earnings", "did MSFT beat estimates", "NVDA Q4 results",
  "earnings update for GOOGL", "how did Tesla do last quarter".
---

# Earnings Analysis

Analyze quarterly earnings for US-listed stocks. Combines SEC EDGAR XBRL filings with web search for consensus estimates, then produces a structured beat/miss report with trend analysis.

## Setup

No dependencies required. All scripts use Python standard library only.

## Workflow

### Step 1 — Identify the quarter and find consensus (web search)

**Always search first. Do NOT rely on training data for earnings results.**

**Search 0** — identify the most recently reported quarter:
- `[Company] [ticker] latest quarterly earnings results [current year]`

Cross-check against today's date (calendar fiscal year companies):
- Q1 results typically reported: Apr–May
- Q2 results typically reported: Jul–Aug
- Q3 results typically reported: Oct–Nov
- Q4 results typically reported: Jan–Feb

**Non-calendar fiscal years**: Check the company's fiscal year end from SEC EDGAR data before mapping quarters. Common examples: Apple FY ends September (Q1 = Oct–Dec), Microsoft FY ends June (Q1 = Jul–Sep). Use the `fiscal_year` and `fiscal_quarter` fields from `get_fundamentals.py` output.

If today's date falls after the typical window for the next quarter, search again — a newer quarter may have been reported.

After confirming the quarter, run two searches:

**Search A** — reported results:
- `[Company] [confirmed quarter] earnings results revenue EPS`

**Search B** — consensus estimates:
- `[Company] [confirmed quarter] earnings consensus estimate revenue EPS`
- `[Ticker] earnings beat miss [confirmed quarter]`

**Search C** (after A and B) — guidance:
- `[Company] [confirmed quarter] earnings guidance outlook next quarter [year]`

**Extract ALL of these before proceeding:**

| Field | Notes |
|---|---|
| Quarter reported (e.g. Q1 FY2026) | Verify the date — do not assume |
| Revenue (reported) | |
| Adj. EPS (reported) | |
| Revenue consensus estimate | Must be absolute dollar value (e.g. $27.2B) |
| Adj. EPS consensus estimate | Must be a dollar figure (e.g. $2.84) |
| Next quarter guidance | Revenue or EPS range; say "not provided" if absent |
| Full-year guidance | Raised / lowered / maintained vs. prior |
| Key management commentary | 2-3 key points |

If consensus is not found after two searches, run one more targeted search: `[Ticker] EPS estimate Q[X] [year] analyst consensus`. Only state "consensus not available" after three attempts.

---

### Step 2 — Pull financial data (scripts)

Run the all-in-one script. Run in parallel with Search A and B from Step 1.

```bash
bash run.sh <SYMBOL>
# With peer comparison:
bash run.sh <SYMBOL> --peers <PEER1> <PEER2>
```

Returns JSON with: current quote, 8 quarters of SEC EDGAR financials, 3 years of annual data, and optional peer comps.

**Important: 10-Q data from SEC EDGAR is YTD cumulative.** Derive standalone quarters by subtraction:
- Q1 standalone = Q1 YTD (no subtraction needed)
- Q2 standalone = H1 YTD − Q1 YTD
- Q3 standalone = 9M YTD − H1 YTD
- Q4 standalone = Full-year (10-K) − 9M YTD

Apply subtraction to revenue, gross profit, operating income, and net income. **Do NOT subtract EPS** — EPS is a per-share figure, not a running sum, so subtracting Q1 EPS from H1 EPS does not give Q2 EPS (share counts differ across periods). For Q2/Q3 standalone EPS, use the value from web search (Step 1) or compute as standalone net income / diluted shares.

**Q4 derivation note**: Q4 standalone = 10-K full year − Q3 9M YTD. If the Q3 10-Q is not within the 8 periods returned by the script (too old), use web search to fill in Q4 standalone figures.

You must produce a YTD-to-standalone derivation table for the current quarter — see **Section 3** in Output Format for the exact template and rules.

The all-in-one script (`bash run.sh`) is the preferred entry point. It aggregates quarterly, annual, quote, and peer data in a single call.

---

### Step 3 — Beat/miss analysis

Present a three-column table:

```
Metric        | Reported  | Consensus        | Beat/(Miss)
--------------|-----------|------------------|------------------
Revenue       | $X.XB     | $X.XB            | +$XXM (+X.X%)
Adj. EPS      | $X.XX     | $X.XX            | +$X.XX (+X.X%)
Gross Margin  | XX.X%     | XX.X% (if avail) | +XXbps
```

If consensus is unavailable, write "n/a — consensus not found". Do not omit the row.

For each beat or miss, write one sentence explaining **why** — segment mix, pricing, cost changes, one-time items, etc.

---

### Step 4 — Trend analysis

Use standalone quarterly figures derived in Step 2 — not YTD cumulative, which would inflate recent quarters and distort YoY comparisons. Show the last 8 quarters of actual reported results. The quarter being analyzed must appear as the last (most recent) row.

**Data source requirement:** For each quarter in the table, mark the data source:
- **(SEC)** — derived from SEC EDGAR filing (preferred)
- **(web)** — from web search (only if SEC filing not yet available)

Do NOT use web search data if SEC data is available. SEC EDGAR is the primary source of truth.

If the reported quarter's 10-Q/10-K has not yet been filed on SEC EDGAR, use figures from web search (Step 1) and mark the row with **(web)**.

| Quarter | Revenue | YoY  | Gross Margin | Op. Margin | Diluted EPS | Source |
|---------|---------|------|--------------|------------|-------------|--------|
| Q[X-7]  | $X.XB   | +X%  | XX.X%        | XX.X%      | $X.XX       | SEC    |
| ...     | ...     | ...  | ...          | ...        | ...         | ...    |
| Q[X]    | $X.XB   | +X%  | XX.X%        | XX.X%      | $X.XX       | SEC/web|

YoY must always be computed if both current and prior-year quarter are available.

After the table, comment on:
- Margin expansion or compression trend
- EPS growth vs. revenue growth (buyback effect or margin improvement?)
- Acceleration or deceleration in the last 2-3 quarters

---

### Step 5 — Guidance and outlook

**Mandatory.**
- **Next quarter guidance**: metric, range, above/below/in-line with Street
- **Full-year guidance**: raised / lowered / maintained vs. prior — quantify the change
- **If no guidance provided**: state explicitly, then give a forward read based on trend data

---

### Step 6 — Comparable valuation (only if user asks)

```bash
bash run.sh <SYMBOL> --peers <PEER1> <PEER2> ...
```

Returns revenue, margins, growth, P/E, P/S for up to 10 companies.

---

## Output Format

**Section 1 — Summary box (mandatory, always first):**

```
[COMPANY] ([TICKER]) — Q[X] FY[YYYY] EARNINGS   Result: BEAT / INLINE / MISS / N/A

Revenue:      $X.XB   (consensus: $X.XB  |  beat by +$XXM, +X.X%)
Adj. EPS:     $X.XX   (consensus: $X.XX  |  beat by +$X.XX, +X.X%)
Gross Margin: XX.X%   (vs. XX.X% a year ago, +XXbps YoY)
```

All figures in the Summary box must be **standalone quarterly** values — never full-year or YTD.

Set Result to `N/A` if consensus is unavailable for both Revenue and Adj. EPS.

**Section 2 — Key takeaways** (3-5 bullets). Lead with a number: "Revenue grew 15.7% to $143.8B" not "Strong revenue performance".

**Section 3 — SEC Data Derivation** (mandatory)

Show the YTD-to-standalone derivation table for the current quarter — this is the audit trail proving figures came from the SEC filing, not a web source. Without it, the reader cannot verify the math. Use this format:

```
SEC EDGAR Derivation: Q4 FY2025 Standalone
| Metric       | FY Annual   | − Q3 YTD    | = Q4 Standalone |
|--------------|-------------|-------------|-----------------|
| Revenue      | $XXX.XB     | $XXX.XB     | $XX.XB ✓        |
| Net Income   | $XX.XB      | $XX.XB      | $XX.XB          |
```

Only show Revenue and Net Income (the two most critical metrics). The ✓ indicates cross-validation with web search results. This table must appear before presenting any standalone quarterly figures.

**Section 4 — Revenue & segment analysis**

**Section 5 — Margin analysis**

**Section 6 — 8-quarter trend table** (mandatory — from Step 4, must include Source column)

**Section 7 — Guidance** (mandatory — from Step 5)

**Section 8 — Valuation** (only if requested)

Deliver all mandatory sections before offering follow-up options.

---

## Formatting Rules

- Revenue / profit: B or M, e.g. "$143.8B", "$890M"
- Margins: one decimal percent, e.g. "48.2%"
- Margin changes: basis points, e.g. "+130bps YoY"
- EPS: two decimals, e.g. "$2.84"
- Growth rates: one decimal, e.g. "+15.7% YoY"

## Limitations

- **SEC EDGAR lag**: filed data may lag 2-5 days after earnings release; use web search figures for the latest quarter if filing is unavailable
- **10-Q is cumulative YTD**: always subtract prior periods to derive standalone quarters (see Step 2)
- **No earnings call transcript**: summarize management commentary from web search only
- **US stocks only**: SEC EDGAR covers US-listed equities only
- **Consensus from web search**: always note the source; if unavailable after three attempts, say so explicitly
