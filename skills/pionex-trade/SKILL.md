---
name: pionex-trade
description: >
  Use when the user asks to place orders, cancel orders, check open orders or
  fills on Pionex. Covers spot orders via `pionex-trade-cli` CLI. Requires API credentials.
  Do NOT use for market data only (pionex-market) or balance/portfolio (pionex-portfolio).
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

# Pionex Trading Skill

Spot order placement and management on Pionex via the `pionex-trade-cli` CLI. Requires API credentials in `~/.pionex/config.toml` (run `pionex-ai-kit onboard` first).  
Security: [Pionex API Docs](https://pionex-doc.gitbook.io/apidocs/) recommend IP whitelisting and never sharing your API Key/Secret.

## Prerequisites

1. Install CLI and configure credentials:
   ```bash
   npm install -g @pionex/pionex-ai-kit
   pionex-ai-kit onboard
   ```
2. Test (read-only):
   ```bash
   pionex-trade-cli account balance
   ```

## Skill Routing

- Market data (price, depth, klines, symbol info) → **pionex-market**
- Account balance → **pionex-portfolio** (or use `pionex-trade-cli account balance` here when checking before order)
- Place/cancel orders, open orders, fills → **pionex-trade** (this skill)
- Futures grid bot lifecycle (create/adjust/reduce/cancel) → **pionex-bot**

## Command Index (orders & account used by this skill)

| Command | Type | Description |
|---------|------|--------------|
| `pionex-trade-cli account balance` | READ | All spot balances (filter by currency from JSON if needed) |
| `pionex-trade-cli orders new --symbol <s> --side BUY\|SELL --type MARKET\|LIMIT [--amount \| --size] [--price] [--dry-run]` | WRITE | Create order. MARKET buy: use `--amount` (quote). MARKET sell / LIMIT: use `--size` (base). LIMIT: add `--price` |
| `pionex-trade-cli orders get --symbol <s> --order-id <id>` | READ | Get one order by ID |
| `pionex-trade-cli orders open --symbol <s>` | READ | List open orders for symbol |
| `pionex-trade-cli orders all --symbol <s> [--limit <n>]` | READ | Order history (filled/cancelled) |
| `pionex-trade-cli orders fills --symbol <s> [--startTime] [--endTime]` | READ | Fills (executed trades) |
| `pionex-trade-cli orders fills_by_order_id --symbol <s> --order-id <id>` | READ | Fills for one specific order |
| `pionex-trade-cli orders cancel --symbol <s> --order-id <id> [--dry-run]` | WRITE | Cancel one order |
| `pionex-trade-cli orders cancel_all --symbol <s> [--dry-run]` | WRITE | Cancel all open orders for symbol |

Symbol info (min size, precision) before placing orders: use **pionex-market** → `pionex-trade-cli market symbols --symbols BTC_USDT`.

---

## 1. When to use this skill

Use **pionex-trade** when the user wants to:

- Place a spot order (market or limit buy/sell).
- Cancel an order or all orders for a symbol.
- Query open orders, order history, or fills.

Do **not** use for: only checking prices or order book (use pionex-market); only checking balance (pionex-portfolio, or `pionex-trade-cli account balance` as part of a trade flow).

---

## 2. General rules

1. **Explicit parameters** — Do not guess symbol, side, or size. If unclear, ask the user for: symbol (e.g. `BTC_USDT`), side (BUY/SELL), type (MARKET/LIMIT), and amount or size.
2. **Prefer dry-run then confirm** — For any write (new order, cancel, cancel_all), run with `--dry-run` first when supported, show the user what would be done, then ask for confirmation before running without `--dry-run`.
3. **Do not increase risk without telling the user** — No larger size, no extra orders, without explicit user agreement.
4. **On errors** — Explain and suggest next steps (e.g. adjust size to min, or check balance).

---

## 3. Balance-aware order flow

When the user asks to buy with a quote amount (e.g. “buy BTC with 1000 USDT”):

1. **Check balance**
   ```bash
   pionex-trade-cli account balance
   ```
   From the JSON result, read the **available** balance for the quote asset (e.g. USDT). There is no `--asset` flag; the command returns all currencies.

2. **Compare to requested amount**
   - If available &lt; requested: do **not** place the order. Tell the user the available balance and requested amount; suggest reducing amount or skipping.
   - If available ≥ requested: proceed with order flow (still prefer dry-run + user confirm).

3. **Example**
   - User: “Buy BTC with 1000 USDT.”
   - Agent: run `pionex-trade-cli account balance` → if USDT available is 600, reply: “Your available USDT is 600, less than 1000. Should I place a market buy for 600 USDT instead? I’ll use --dry-run first.”
   - Only after user confirms, run e.g. `pionex-trade-cli orders new --symbol BTC_USDT --side BUY --type MARKET --amount 600` (and optionally run with `--dry-run` first, then without after confirm).

---

## 4. Min size / “amount too small” errors

If the API returns an error about minimum order size or notional (e.g. minimum notional 10 USDT):

1. **Get symbol rules**
   ```bash
   pionex-trade-cli market symbols --symbols BTC_USDT
   ```
   Use the result to see min size, min notional, step size.

2. **Suggest a valid size** — Round to the required precision and ensure notional ≥ min notional. Explain to the user: original request, exchange minimum, and suggested size.

3. **Confirm then retry** — After user agrees, place the order again (prefer `--dry-run` first).

---

## 5. Order commands (exact CLI)

- **Market buy (quote amount)**  
  `pionex-trade-cli orders new --symbol BTC_USDT --side BUY --type MARKET --amount 100`

- **Market sell (base quantity)**  
  `pionex-trade-cli orders new --symbol BTC_USDT --side SELL --type MARKET --size 0.01`

- **Limit order**  
  `pionex-trade-cli orders new --symbol BTC_USDT --side BUY --type LIMIT --price 50000 --size 0.01`

- **Cancel one**  
  `pionex-trade-cli orders cancel --symbol BTC_USDT --order-id 123456`

- **Cancel all for symbol**  
  `pionex-trade-cli orders cancel_all --symbol BTC_USDT`  
  Before running, list what will be cancelled: `pionex-trade-cli orders open --symbol BTC_USDT`, then confirm with the user.

---

## 6. Cancel_all and batch actions

- **Always preview** — Before `pionex-trade-cli orders cancel_all --symbol <s>`, run `pionex-trade-cli orders open --symbol <s>` and show the user how many orders and for which symbol.
- **Explicit confirmation** — e.g. “This will cancel 3 open orders on BTC_USDT. Confirm?” Only then run without `--dry-run` if applicable.

---

## 7. Summary

- **pionex-trade** defines how to safely place and cancel spot orders using the `pionex-trade-cli` CLI.
- Use **pionex-trade-cli account balance** to check funds; use **pionex-trade-cli market symbols** (pionex-market) to respect min size/notional.
- Prefer `--dry-run` and user confirmation for writes. Never increase risk without the user’s explicit agreement.
