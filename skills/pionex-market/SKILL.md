---
name: pionex-market
description: >
  Use when the user asks for Pionex market data: price, ticker, order book depth,
  recent trades, symbol info (precision/min size), or OHLCV klines. All commands
  are read-only and do NOT require API credentials. Do NOT use for account
  balance (pionex-portfolio) or placing/cancelling orders (pionex-trade).
license: MIT
metadata:
  author: pionex
  version: "1.0.0"
  homepage: "https://www.pionex.com"
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

# Pionex Market Data CLI

Public market data for Pionex: order book depth, trades, tickers, symbol metadata, and OHLCV klines. All commands are **read-only** and do **not require API credentials**.  
API reference: [Pionex API Docs](https://pionex-doc.gitbook.io/apidocs/).

## Prerequisites

1. Install `pionex-trade-cli` CLI (from `@pionex/pionex-ai-kit`):
   ```bash
   npm install -g @pionex/pionex-ai-kit
   ```
2. No credentials needed for market data.
3. Verify:
   ```bash
   pionex-trade-cli market tickers --symbol BTC_USDT
   ```

## Skill Routing

- For market data (depth, tickers, symbols, klines, trades) → use **pionex-market** (this skill).
- For account balance → use **pionex-portfolio**.
- For placing/cancelling orders → use **pionex-trade**.
- For futures grid bot lifecycle → use **pionex-bot**.

## Quickstart

```bash
# Order book depth (bids/asks)
pionex-trade-cli market depth BTC_USDT --limit 5

# Recent trades
pionex-trade-cli market trades BTC_USDT --limit 10

# Symbol metadata (precision, min size) — use before placing orders
pionex-trade-cli market symbols --symbols BTC_USDT

# 24h ticker(s)
pionex-trade-cli market tickers --symbol BTC_USDT
pionex-trade-cli market tickers --type SPOT

# Best bid/ask ticker(s)
pionex-trade-cli market book_tickers --symbol BTC_USDT
pionex-trade-cli market book_tickers --type PERP

# OHLCV klines (candlestick)
pionex-trade-cli market klines BTC_USDT 60M --limit 24
pionex-trade-cli market klines BTC_USDT 1D
```

## Command Index

| # | Command | Type | Description |
|---|---------|------|--------------|
| 1 | `pionex-trade-cli market depth <symbol> [--limit <n>]` | READ | Order book depth (bids/asks); limit 1–100, default 5 |
| 2 | `pionex-trade-cli market trades <symbol> [--limit <n>]` | READ | Recent public trades; limit 1–100 |
| 3 | `pionex-trade-cli market symbols [--symbols <list>] [--type SPOT\|PERP]` | READ | Symbol metadata (precision, min size). Comma-separated symbols or type filter |
| 4 | `pionex-trade-cli market tickers [--symbol <s>] [--type SPOT\|PERP]` | READ | 24h ticker(s): open, close, high, low, volume |
| 5 | `pionex-trade-cli market book_tickers [--symbol <s>] [--type SPOT\|PERP]` | READ | Best bid/ask ticker(s) for one symbol or all symbols by type |
| 6 | `pionex-trade-cli market klines <symbol> <interval> [--endTime <ms>] [--limit <n>]` | READ | OHLCV klines. interval: 1M, 5M, 15M, 30M, 60M, 4H, 8H, 12H, 1D |

## Cross-Skill: Check price/symbol before order

Before placing an order, use this skill to get last price and symbol rules:

```bash
# 1. Current price / 24h range
pionex-trade-cli market tickers --symbol BTC_USDT

# 2. Min size / precision (avoid TRADE_AMOUNT_FILTER_DENIED)
pionex-trade-cli market symbols --symbols BTC_USDT
```

Then use **pionex-trade** to place the order (after checking balance with **pionex-portfolio** if needed).
