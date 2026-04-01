---
name: pionex-earn-dual
description: >
  Use when the user asks about Pionex Dual Investment (earn dual):
  listing supported pairs or products, checking yield rates or index prices,
  querying balances or investment history, placing or revoking an investment,
  or collecting settled earnings.
  Do NOT use for spot trading (pionex-trade), futures grid bots (pionex-bot),
  or market price/depth data only (pionex-market).
license: MIT
metadata:
  author: pionex
  version: "0.1.0"
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

# Pionex Earn Dual Investment Skill

Dual Investment products on Pionex: browse products, check yields, invest, revoke, and collect settled earnings via `pionex-trade-cli`. Public queries require no credentials; write operations require API credentials with **Earn** permission.

> **Beta notice:** The Dual Investment API is currently in Beta. Contact [open@pionex.com](mailto:open@pionex.com) to request access.

**Product ID format:** `{BASE}-{QUOTE}-{YYMMDD}-{STRIKE}-{C|P}-{CURRENCY}`, where `C` = DUAL_BASE and `P` = DUAL_CURRENCY.

## Skill Routing

- Dual Investment products, prices, invest, revoke, collect → **pionex-earn-dual** (this skill)
- Spot market data (depth, tickers, klines) → **pionex-market**
- Spot account balance → **pionex-portfolio**
- Spot order placement/cancellation → **pionex-trade**
- Futures Grid Bot lifecycle → **pionex-bot**

## Prerequisites

1. Install CLI:
   ```bash
   npm install -g @pionex/pionex-ai-kit
   ```
2. For private commands (balances, invest, revoke-invest, collect), configure credentials:
   ```bash
   pionex-ai-kit onboard
   ```
   Ensure your API key has the required permissions:
   - **View** — for `balances`, `get-invests`, `records`
   - **Earn** — for `invest`, `revoke-invest`, `collect`
3. Verify (public, no auth needed):
   ```bash
   pionex-trade-cli earn dual symbols
   ```

---

## Command Index

### Public Commands (no authentication required)

| # | Command | Flags | Type |
|---|---------|-------|------|
| 1 | `pionex-trade-cli earn dual symbols` | `[--base <currency>]` | READ |
| 2 | `pionex-trade-cli earn dual open-products` | `--base <c> --quote <c> --type DUAL_BASE\|DUAL_CURRENCY [--currency <c>]` | READ |
| 3 | `pionex-trade-cli earn dual prices` | `--base <c> --quote <c> --product-ids <id1,id2,...>` | READ |
| 4 | `pionex-trade-cli earn dual index` | `--base <c> --quote <c>` | READ |
| 5 | `pionex-trade-cli earn dual delivery-prices` | `--base <c> [--quote <c>] [--start-time <ms>] [--end-time <ms>]` | READ |

### Private Commands — View permission

| # | Command | Flags | Type |
|---|---------|-------|------|
| 6 | `pionex-trade-cli earn dual balances` | `[--merge]` | READ |
| 7 | `pionex-trade-cli earn dual get-invests` | `[--base <c>] --client-dual-ids <id1,id2,...>` | READ |
| 8 | `pionex-trade-cli earn dual records` | `--base <c> --end-time <ms> [--quote <c>] [--currency <c>] [--start-time <ms>] [--limit <n>]` | READ |

### Private Commands — Earn permission

| # | Command | Flags | Type |
|---|---------|-------|------|
| 9 | `pionex-trade-cli earn dual invest` | `--base <c> --product-id <id> --profit <rate> (--base-amount <n> \| --currency-amount <n>) [--client-dual-id <id>] [--dry-run]` | WRITE |
| 10 | `pionex-trade-cli earn dual revoke-invest` | `--base <c> --product-id <id> --client-dual-id <id> [--dry-run]` | WRITE |
| 11 | `pionex-trade-cli earn dual collect` | `--base <c> --client-dual-id <id> --product-id <id> [--dry-run]` | WRITE |

---

## quote and currency Rules

The correct `--quote` value depends on the base currency:

| Base currency | `--quote` | `--currency` options |
|---------------|-----------|--------------------|
| `BTC`, `ETH` | `USDXO` | `USDT` or `USDC` |
| All other bases (XRP, SOL, LRC, etc.) | `USDT` | `USDT` |

**Incorrect `--quote` will return `DUAL_PARAMETER_ERROR: invalid base quote`.**

---

## Product Type Semantics

| Type | Invest in | Strike hit at expiry | Strike NOT hit |
|------|-----------|----------------------|----------------|
| `DUAL_BASE` (`C` in product ID) | Base currency (e.g. BTC) | Converted to investment currency + yield | Returned in base + yield |
| `DUAL_CURRENCY` (`P` in product ID) | Investment currency (e.g. USDT) | Converted to base currency + yield | Returned in investment currency + yield |

---

## Safety Rules

1. **Never use a stale `profit` value** — Always call `earn dual prices` immediately before `earn dual invest`. The API rejects mismatched profit values. Steps 2 and 3 of the invest workflow must be consecutive.
2. **`--profit` is required for `invest`** — There is no default; the exact value returned by `prices` must be passed.
3. **Never provide both `--base-amount` and `--currency-amount`** — They are mutually exclusive; use one or the other.
4. **Dry-run first, confirm before real execution** — For `invest`, `revoke-invest`, and `collect`, always run with `--dry-run`, show output to user, then confirm before running without it.
5. **Never infer `--client-dual-id`** — Require the user to provide it, or propose one and get confirmation. It acts as an idempotency key.
6. **Check order state before revoke/collect** — Use `earn dual get-invests` to verify state first: `revoke-invest` only works on pending orders; `collect` only works on settled orders.
7. **Never infer `--product-id`, strike, or expiry** — These must come from the API (`open-products` or `get-invests`), never assumed.

---

## Invest Workflow (Mandatory 3-Step Process)

### Step 1: Get available products

```bash
# DUAL_BASE: invest in BTC, payout converted if price rises above strike
pionex-trade-cli earn dual open-products \
  --base BTC \
  --quote USDXO \
  --type DUAL_BASE \
  --currency USDT

# DUAL_CURRENCY: invest in USDT, buy BTC if price drops below strike
pionex-trade-cli earn dual open-products \
  --base BTC \
  --quote USDXO \
  --type DUAL_CURRENCY \
  --currency USDT
```

Choose a `productId` from the response (e.g. `BTC-USDXO-260402-68000-P-USDT`).

### Step 2: Get current yield rate (must be done immediately before Step 3)

```bash
pionex-trade-cli earn dual prices \
  --base BTC \
  --quote USDXO \
  --product-ids BTC-USDXO-260402-68000-P-USDT
```

Check `canInvest: true` and record the `profit` value exactly as returned (e.g. `"0.0039"`).

### Step 3: Dry-run, confirm, then submit

```bash
# Dry-run first — shows the request payload without executing
pionex-trade-cli earn dual invest \
  --base BTC \
  --product-id BTC-USDXO-260402-68000-P-USDT \
  --client-dual-id my-order-001 \
  --currency-amount 100 \
  --profit 0.0039 \
  --dry-run

# After user confirmation, submit (same command without --dry-run)
pionex-trade-cli earn dual invest \
  --base BTC \
  --product-id BTC-USDXO-260402-68000-P-USDT \
  --client-dual-id my-order-001 \
  --currency-amount 100 \
  --profit 0.0039
```

> **Do not call other commands between Steps 2 and 3.** The `profit` value has a short validity window.

---

## Examples

### Browse products

```bash
# All supported pairs
pionex-trade-cli earn dual symbols

# BTC pairs only
pionex-trade-cli earn dual symbols --base BTC

# Open DUAL_BASE products for ETH (invest ETH, convert to USDT if price rises)
pionex-trade-cli earn dual open-products \
  --base ETH --quote USDXO --type DUAL_BASE --currency USDT

# Open products for XRP (non-BTC/ETH — use USDT quote)
pionex-trade-cli earn dual open-products \
  --base XRP --quote USDT --type DUAL_BASE
```

### Check prices and index

```bash
# Current yield for a specific product
pionex-trade-cli earn dual prices \
  --base BTC --quote USDXO \
  --product-ids BTC-USDXO-260402-68000-P-USDT

# Multiple product IDs (comma-separated, no spaces)
pionex-trade-cli earn dual prices \
  --base ETH --quote USDXO \
  --product-ids ETH-USDXO-260410-3000-C-USDT,ETH-USDXO-260410-2900-C-USDT

# Real-time index price
pionex-trade-cli earn dual index --base BTC --quote USDXO

# Historical delivery prices
pionex-trade-cli earn dual delivery-prices --base BTC --quote USDXO
```

### Account and history

```bash
# Balances
pionex-trade-cli earn dual balances

# Merged balances (same coin across different bases)
pionex-trade-cli earn dual balances --merge

# Batch query by client order IDs (comma-separated)
pionex-trade-cli earn dual get-invests \
  --base BTC \
  --client-dual-ids my-order-001,my-order-002

# Investment history (--base and --end-time required)
pionex-trade-cli earn dual records \
  --base BTC \
  --quote USDXO \
  --end-time 1775027817297 \
  --limit 20
```

### Revoke a pending order

```bash
# 1. Verify order is still pending
pionex-trade-cli earn dual get-invests --base BTC --client-dual-ids my-order-001

# 2. Dry-run
pionex-trade-cli earn dual revoke-invest \
  --base BTC \
  --product-id BTC-USDXO-260402-68000-P-USDT \
  --client-dual-id my-order-001 \
  --dry-run

# 3. Execute after user confirmation
pionex-trade-cli earn dual revoke-invest \
  --base BTC \
  --product-id BTC-USDXO-260402-68000-P-USDT \
  --client-dual-id my-order-001
```

### Collect settled earnings

```bash
# 1. Verify order is settled
pionex-trade-cli earn dual get-invests --base BTC --client-dual-ids my-order-001

# 2. Dry-run
pionex-trade-cli earn dual collect \
  --base BTC \
  --client-dual-id my-order-001 \
  --product-id BTC-USDXO-260402-68000-P-USDT \
  --dry-run

# 3. Execute after user confirmation
pionex-trade-cli earn dual collect \
  --base BTC \
  --client-dual-id my-order-001 \
  --product-id BTC-USDXO-260402-68000-P-USDT
```
