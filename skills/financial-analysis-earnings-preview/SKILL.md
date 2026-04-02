---
name: financial-analysis-earnings-preview
description: >
  Pre-earnings preview workflow for US stocks.
  Use when asked to: preview upcoming earnings; set expectations for next quarter;
  build bull/base/bear scenarios ahead of earnings; prepare for earnings release;
  understand what Wall Street expects.
  Triggers: "preview AAPL earnings", "what to expect from NVDA next quarter",
  "earnings preview MSFT", "build scenarios for GOOGL earnings",
  "prepare for Tesla earnings release".
  Note: For POST-earnings analysis (after results are out), use earnings-analysis skill instead.
---

# Earnings Preview

Build a pre-earnings preview with consensus estimates, historical trend, scenarios, and catalyst checklist. Uses SEC EDGAR for historical financials and web search for consensus/dates.

## Setup

No dependencies required. All scripts use Python standard library only.

## Workflow

### Step 1 — Find earnings date and consensus (web search)

**Always search first. Do NOT rely on training data for consensus estimates.**

**Search A** — earnings date:
- `[Company] [ticker] earnings date Q[X] FY[YYYY]`
- `[Ticker] earnings release date when`

**Search B** — consensus estimates (run in parallel with Step 2):
- `[Company] Q[X] FY[YYYY] earnings preview consensus estimate revenue EPS`
- `[Ticker] earnings estimates Wall Street expectations Q[X] FY[YYYY]`

If Search B returns only vague language without absolute dollar figures, run:
- `[Ticker] Q[X] FY[YYYY] revenue estimate $B analyst consensus`

**Extract ALL before proceeding:**

| Field | Notes |
|---|---|
| Earnings date | Exact date; "date not confirmed" if unavailable |
| Quarter being reported (e.g. Q2 FY2026) | Explicit fiscal quarter — not "next quarter" |
| Revenue consensus estimate | Must be absolute dollar value (e.g. "$29.3B") |
| Adj. EPS consensus estimate | Must be a dollar figure (e.g. "$2.18") |
| Prior guidance range | Company's guidance for this period |
| Key analyst themes | 2-3 expectations or concerns |

**Verify the earnings date is in the future.** If it has passed, that quarter is already reported — search for the next upcoming date instead.

---

### Step 2 — Pull historical trend (scripts)

Run in parallel with Search B:

```bash
bash run.sh <SYMBOL> --form 10-Q --periods 8
bash run.sh <SYMBOL> --form 10-K --periods 3
```

**10-Q data is YTD cumulative.** Derive standalone quarters by subtraction:
- Q1 = Q1 YTD
- Q2 = H1 YTD − Q1 YTD
- Q3 = 9M YTD − H1 YTD
- Q4 = Full-year (10-K) − 9M YTD

**Present as mandatory trend table** (minimum 4 quarters + estimate row):

| Quarter | Revenue | YoY  | Gross Margin | Op. Margin | Diluted EPS |
|---------|---------|------|--------------|------------|-------------|
| Q[X-3] FY[YYYY] A | $X.XB  | +X%  | XX.X%        | XX.X%      | $X.XX       |
| Q[X] FY[YYYY] E   | $X.XB(E)| +X%E| —            | —          | $X.XX(E)    |

The last row "Q[X] FY[YYYY] E" is consensus from Step 1 — mark as "(E)" for estimate.

---

### Step 3 — Build scenarios

| | **Bull** | **Base** | **Bear** |
|---|---|---|---|
| Revenue | Beat consensus by ~X% | In-line | Miss by ~X% |
| Adj. EPS | Beat | In-line | Miss |
| Gross margin | Expansion vs prior year | Flat | Compression |
| Key driver | Upside in [segment] | Steady execution | Weakness in [risk] |

**Anchor to history**: Use the company's historical beat/miss magnitude from the trend table to size the bull and bear scenarios. For example, if the company has beaten revenue consensus by ~10% in recent quarters (e.g. NVDA), use ~8-12% for bull — not a generic 2-4%. For mature companies with consistent ~1% beats, use ~1-3%. State the primary trigger for each scenario.

---

### Step 4 — Catalyst checklist

List 3-5 watchpoints:

```
[ ] Key question (e.g. "Does [segment] revenue accelerate above X%?")
    Why it matters: [1-2 sentences]
    What to look for: [specific metric or commentary]
```

Focus on: key segment variance, margin trajectory, forward guidance, prior quarter risks.

---

## Output Format

**Header box (mandatory, always first):**
```
[COMPANY] ([TICKER]) — Q[X] FY[YYYY] EARNINGS PREVIEW
Earnings date: [exact date or "TBC"]

Consensus:   Revenue $X.XB (+X% YoY)  |  Adj. EPS $X.XX (+X% YoY)
Prior guidance: [range or "not provided"]
Source: [source name, retrieved YYYY-MM-DD]
```

**Section 1 — Trend table** (mandatory, min 4 quarters + estimate row)

**Section 2 — Trend commentary** (3-5 sentences)

**Section 3 — What the Street expects**

**Section 4 — Scenarios** (Bull / Base / Bear table)

**Section 5 — Catalyst checklist** (3-5 watchpoints)

**Closing caveat:**
> Earnings previews are based on consensus estimates from public sources and historical reported data. Actual results may differ materially. This is not investment advice.

---

## Formatting Rules

- Revenue / profit: B or M, e.g. "$29.3B"
- Margins: one decimal percent, e.g. "48.2%"
- EPS: two decimals, e.g. "$2.18"
- Growth rates: one decimal, e.g. "+12.4% YoY"

## Limitations

- **No real-time consensus**: estimates from web search — always note source and date
- **SEC EDGAR lag**: filed data may not include most recent quarter
- **10-Q is cumulative YTD**: always subtract prior periods for standalone quarters
- **US stocks only**: SEC EDGAR covers US-listed equities only
