---
name: pionex-bot
description: >
  Use when the user asks to create, query, adjust, reduce, or cancel Pionex
  Futures Grid Bot orders. Requires API credentials and bot permissions.
  Do NOT use for market data only (pionex-market), balance only (pionex-portfolio),
  or spot order placement/cancel (pionex-trade).
license: MIT
metadata:
  author: pionex
  version: "0.1.0"
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

# Pionex Futures Grid Bot Skill

Use this skill for Pionex Futures Grid Bot lifecycle actions: get, create, adjust, reduce, cancel.

## Routing

- Bot lifecycle (futures grid) -> **pionex-bot** (this skill)
- Market data -> **pionex-market**
- Spot balance -> **pionex-portfolio**
- Spot order placement/cancel -> **pionex-trade**

## Commands

| Command | Type | Description |
|---------|------|-------------|
| `pionex-trade-cli bot get --bu-order-id <id>` | READ | Query one futures grid bot order |
| `pionex-trade-cli bot create --base BTC --quote USDT --bu-order-data-json '<json>' [--dry-run]` | WRITE | Create futures grid bot |
| `pionex-trade-cli bot adjust_params --body-json '<json>' [--dry-run]` | WRITE | Add investment / modify range / trigger invest-in |
| `pionex-trade-cli bot reduce --body-json '<json>' [--dry-run]` | WRITE | Reduce bot position |
| `pionex-trade-cli bot cancel --bu-order-id <id> [--close-sell-model TO_QUOTE\\|TO_USDT] [--dry-run]` | WRITE | Cancel and close bot |

## Safety Rules

1. Confirm write intent for create/adjust/reduce/cancel before running without `--dry-run`.
2. Never infer `buOrderId`, leverage, range, or amount; require explicit user values.
3. If API rejects params, surface exact error and propose a corrected payload.

## Examples

```bash
# Read bot status
pionex-trade-cli bot get --bu-order-id 123456789

# Dry-run create
pionex-trade-cli bot create \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"top":"110000","bottom":"90000","row":100,"grid_type":"arithmetic","trend":"long","leverage":5,"extraMargin":"0","quoteInvestment":"100"}' \
  --dry-run

# Dry-run adjust
pionex-trade-cli bot adjust_params --body-json '{"buOrderId":"123456789","type":"invest_in","quoteInvestment":50,"extraMargin":false}' --dry-run
```
