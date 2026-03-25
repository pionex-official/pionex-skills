---
name: pionex-portfolio
description: >
  Use when the user asks for Pionex account balance, available funds, or
  “how much USDT do I have”. Read-only; requires API credentials. Do NOT use
  for market data (pionex-market) or placing/cancelling orders (pionex-trade).
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

# Pionex Portfolio (Account) Skill

Query spot account balances on Pionex. Requires API credentials (`pionex-ai-kit onboard`).

## When to use

- User asks: balance, available USDT/other currency, “how much can I spend”, account overview.

## Command

| Command | Type | Description |
|---------|------|-------------|
| `pionex-trade-cli account balance` | READ | All spot balances. Output is JSON; filter by currency (e.g. USDT) as needed. |

## Prerequisites

```bash
npm install -g @pionex/pionex-ai-kit
pionex-ai-kit onboard
```

## Skill routing

- Balance / account → **pionex-portfolio** (this skill)
- Market data → **pionex-market**
- Orders (place/cancel) → **pionex-trade**
- Futures grid bot lifecycle → **pionex-bot**

## Example

- User: “How much USDT do I have on Pionex?”
- Agent: run `pionex-trade-cli account balance`, then from the JSON report the available (and total if present) balance for USDT.
