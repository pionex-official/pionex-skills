---
name: pionex-wallet
description: >
  Use when the user asks for their total Pionex portfolio value, full balance
  overview across all account types (spot + bots + dual investment + trader
  account), USDT/BTC grand total, or wants to know how much they have in bots
  vs spot. Read-only; requires API credentials. For spot coin list only, use
  pionex-portfolio instead.
license: MIT
metadata:
  author: pionex
  version: "1.0.0"
  agent:
    requires:
      bins: ["pionex-trade-cli"]
    install:
      - id: npm
        kind: node
        package: "@pionex/pionex-ai-kit"
        bins: ["pionex-trade-cli", "pionex-ai-kit"]
        label: "Install pionex CLI (npm)"
---

# Pionex Wallet Skill

Query the full Pionex portfolio overview: total USDT/BTC value across all account types. Requires API credentials (`pionex-ai-kit onboard`).

## When to use

- User asks: total portfolio value, overall balance, "how much is my whole Pionex account worth", "spot + bot total", breakdown by account type (bots vs spot vs dual investment).
- User wants a consolidated view — not just spot coins, not just one bot.

## Command

| Command | Type | Description |
|---------|------|-------------|
| `pionex-trade-cli wallet balance_full` | READ | Full portfolio overview: USDT/BTC grand total + per-account-type breakdown. |
| `pionex-trade-cli wallet balance_full --app-lang en` | READ | Same, force English display names in `title` fields. |

No write operations — `--dry-run` is not applicable.

## Prerequisites

```bash
npm install -g @pionex/pionex-ai-kit
pionex-ai-kit onboard
```

## Output Structure

```json
{
  "result": true,
  "data": {
    "totalInUsdt": "<grand total in USDT>",
    "totalInBtc":  "<grand total in BTC>",
    "botAccount": {
      "totalInUsdt": "<all bot types combined>",
      "detail": [
        { "type": "futures_lite", "title": "Futures Lite",    "totalInUsdt": "...", "count": 1 },
        { "type": "spot",         "title": "Spot Balances",   "totalInUsdt": "..." },
        { "type": "dual_manual",  "title": "Dual investment", "totalInUsdt": "..." },
        { "type": "pionex_card",  "title": "Pionex Card",     "totalInUsdt": "..." }
      ]
    },
    "traderAccount": { "title": "Trader Account", "totalInUsdt": "..." },
    "extractBalances": {
      "propTrading":      { "totalInUsdt": "..." },
      "trialFundCoupon":  { "totalInUsdt": "..." }
    },
    "prices": { "btc": "...", "eth": "...", "usdt": "1", ... }
  }
}
```

### How to summarize the output

1. Report `data.totalInUsdt` and `data.totalInBtc` as the grand total.
2. For a breakdown, iterate `data.botAccount.detail` — report each `title` + `totalInUsdt`.
3. Include `data.traderAccount.totalInUsdt` if non-zero.
4. Skip `data.prices` and `data.extractBalances` unless the user explicitly asks.
5. Round to 2 decimal places for display.

## Skill routing

| Scope | Skill |
|-------|-------|
| Total portfolio / full overview | **pionex-wallet** (this skill) |
| Spot coin list (per-coin balances) | **pionex-portfolio** |
| Market prices only | **pionex-market** |
| Place / cancel spot orders | **pionex-trade** |
| Futures/Spot Grid Bot lifecycle | **pionex-bot** |

## Example

- User: "What's my total Pionex account value?"
- Agent: run `pionex-trade-cli wallet balance_full`, then report:
  > Total: **$3,958.80** (≈ 0.0494 BTC)
  > - Futures Lite bots: $3,928.24
  > - Spot Balances: $0.49
  > - Dual Investment: $30.06
  > - Pionex Card: $0.00
