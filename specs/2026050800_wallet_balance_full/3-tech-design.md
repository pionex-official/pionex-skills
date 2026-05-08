# Tech Design: pionex-wallet Skill

## Overview

Add a new skill `pionex-wallet` that wraps the `wallet balance_full` CLI command. This is a read-only skill with no write operations.

## Files to Create / Modify

| File | Change |
|------|--------|
| `skills/pionex-wallet/SKILL.md` | **CREATE** — new skill file |
| `README.md` | **MODIFY** — add row to Skills table |
| `CLAUDE.md` | **MODIFY** — add row to Skill Routing Map |
| `docs/requirements-overview.md` | **MODIFY** — add skill section + iteration history |
| `docs/tech-memory-overview.md` | **MODIFY** — append iteration entry |
| `docs/tech-api-overview.yaml` | **MODIFY** — add wallet balance_full command |

## Skill File Design

```yaml
---
name: pionex-wallet
description: >
  Use when the user asks for their total Pionex portfolio value, full balance
  overview across all account types (spot + bots + dual investment + trader
  account), or wants to know how much they have in bots vs spot.
  Read-only; requires API credentials. For spot coin list only, use
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
```

## CLI Command

```
pionex-trade-cli wallet balance_full [--app-lang <lang>]
```

- `--app-lang` — optional; `en` or `zh`. Controls display names in the response (e.g. `title` fields). Defaults to system language.
- No write operations → no `--dry-run` needed.

## Output JSON Structure

```json
{
  "result": true,
  "timestamp": 1778242190875,
  "data": {
    "totalInUsdt": "3958.79...",
    "totalInBtc": "0.04938...",
    "botAccount": {
      "totalInUsdt": "...",
      "detail": [
        { "type": "futures_lite", "title": "Futures Lite", "totalInUsdt": "...", "count": 1, "list": [...] },
        { "type": "spot",         "title": "Spot Balances", "totalInUsdt": "...", "list": [...] },
        { "type": "dual_manual",  "title": "Dual investment", "totalInUsdt": "...", "list": [...] },
        { "type": "pionex_card",  "title": "Pionex Card", "totalInUsdt": "...", "list": [...] }
      ]
    },
    "traderAccount": { "title": "...", "totalInUsdt": "...", "detail": [...] },
    "extractBalances": { "propTrading": {...}, "trialFundCoupon": {...} },
    "prices": { "usdt": "1", "btc": "...", ... }
  }
}
```

## Skill Routing Boundary

| Question | Skill |
|----------|-------|
| "Total portfolio value", "spot + bot total" | **pionex-wallet** |
| "How much USDT/BTC/coin in spot?" | **pionex-portfolio** |
| "Current price of BTC?" | **pionex-market** |

## Version

`1.0.0` — new skill (no prior version to bump from).
