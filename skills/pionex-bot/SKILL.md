---
name: pionex-bot
description: >
  Use when the user asks to create, query, list, adjust, reduce, or cancel Pionex
  bot orders (Futures Grid, Spot Grid, Smart Copy). Includes listing/paginating
  through bot orders in bulk. Requires API credentials and bot permissions.
  Do NOT use for market data only (pionex-market), balance only (pionex-portfolio),
  or spot order placement/cancel (pionex-trade).
license: MIT
metadata:
  author: pionex
  version: "0.3.0"
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

# Pionex Bot Skill

Use this skill for Pionex bot lifecycle actions: Futures Grid (get, create, adjust, reduce, cancel) and Spot Grid (get, get_ai_strategy, create, adjust_params, invest_in, cancel, profit).

## Routing

- Bot lifecycle (futures grid) -> **pionex-bot** (this skill)
- Bot lifecycle (spot grid) -> **pionex-bot** (this skill)
- Market data -> **pionex-market**
- Spot balance -> **pionex-portfolio**
- Spot order placement/cancel -> **pionex-trade**

## Commands

| Command | Type | Description |
|---------|------|-------------|
| `pionex-trade-cli bot order_list [--status running\|finished] [--base BTC] [--quote USDT] [--page-token <token>] [--bu-order-types futures_grid,spot_grid,smart_copy]` | READ | List bot orders with optional filters and pagination |
| `pionex-trade-cli bot futures_grid get --bu-order-id <id>` | READ | Query one futures grid bot order |
| `pionex-trade-cli bot futures_grid create --base BTC --quote USDT --bu-order-data-json '<json>' [--dry-run]` | WRITE | Create futures grid bot |
| `pionex-trade-cli bot futures_grid adjust_params --body-json '<json>' [--dry-run]` | WRITE | Add investment / modify range / trigger invest-in |
| `pionex-trade-cli bot futures_grid reduce --body-json '<json>' [--dry-run]` | WRITE | Reduce bot position |
| `pionex-trade-cli bot futures_grid cancel --bu-order-id <id> [--close-sell-model TO_QUOTE\\|TO_USDT] [--dry-run]` | WRITE | Cancel and close bot |
| `pionex-trade-cli bot spot_grid get --bu-order-id <id>` | READ | Query one spot grid bot order |
| `pionex-trade-cli bot spot_grid get_ai_strategy --base <BASE> --quote <QUOTE>` | READ | Fetch AI-recommended grid parameters for a pair |
| `pionex-trade-cli bot spot_grid create --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>' [--dry-run]` | WRITE | Create a new spot grid bot |
| `pionex-trade-cli bot spot_grid adjust_params --body-json '<json>' [--dry-run]` | WRITE | Modify grid price range |
| `pionex-trade-cli bot spot_grid invest_in --body-json '<json>' [--dry-run]` | WRITE | Add funds to a running spot grid bot |
| `pionex-trade-cli bot spot_grid cancel --bu-order-id <id> [--dry-run]` | WRITE | Cancel and close spot grid bot |
| `pionex-trade-cli bot spot_grid profit --body-json '<json>' [--dry-run]` | WRITE | Extract accumulated grid profits |

## Safety Rules

1. Confirm write intent for create/adjust/reduce/cancel before running without `--dry-run`.
2. Never infer `buOrderId`, leverage, range, or amount; require explicit user values.
3. If API rejects params, surface exact error and propose a corrected payload.

### Spot Grid Specific

4. Call `get_ai_strategy` before `create` when the user has not provided explicit price range and row count.
5. Never add `leverage`, `trend`, or `extraMargin` fields to spot grid payloads — spot grid is leverage-free.
6. Verify account has sufficient base + quote balance before creating or adding investment.
7. `invest_in` and `profit` are standalone commands — do not confuse with `adjust_params`.

## Examples

```bash
# --- Futures Grid ---

# List running futures grid bot orders
pionex-trade-cli bot order_list --status running --bu-order-types futures_grid

# List all running bot orders across all types
pionex-trade-cli bot order_list --status running

# Filter by symbol
pionex-trade-cli bot order_list --base BTC --quote USDT

# Paginate to next page
pionex-trade-cli bot order_list --status finished --page-token <nextPageToken>

# Read one bot status
pionex-trade-cli bot futures_grid get --bu-order-id 123456789

# Dry-run create
pionex-trade-cli bot futures_grid create \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"top":"110000","bottom":"90000","row":100,"grid_type":"arithmetic","trend":"long","leverage":5,"extraMargin":"0","quoteInvestment":"100"}' \
  --dry-run

# Dry-run adjust
pionex-trade-cli bot futures_grid adjust_params --body-json '{"buOrderId":"123456789","type":"invest_in","quoteInvestment":50,"extraMargin":false}' --dry-run

# --- Spot Grid ---

# Get AI-recommended parameters for BTC/USDT spot grid
pionex-trade-cli bot spot_grid get_ai_strategy --base BTC --quote USDT

# Dry-run create spot grid (using AI-recommended or user-specified params)
pionex-trade-cli bot spot_grid create \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"top":"110000","bottom":"90000","row":50,"grid_type":"arithmetic","quoteInvestment":"200"}' \
  --dry-run

# Query spot grid bot status
pionex-trade-cli bot spot_grid get --bu-order-id 987654321

# Add investment to running spot grid bot
pionex-trade-cli bot spot_grid invest_in \
  --body-json '{"buOrderId":"987654321","quoteInvestment":"100"}' \
  --dry-run

# Extract accumulated grid profits
pionex-trade-cli bot spot_grid profit \
  --body-json '{"buOrderId":"987654321"}' \
  --dry-run

# Cancel spot grid bot
pionex-trade-cli bot spot_grid cancel --bu-order-id 987654321 --dry-run

# List running spot grid bots
pionex-trade-cli bot order_list --status running --bu-order-types spot_grid
```
