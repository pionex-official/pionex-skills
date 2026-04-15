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
  version: "0.5.0"
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

Use this skill for Pionex bot lifecycle actions: Futures Grid (get, create, adjust, reduce, cancel), Spot Grid (get, get_ai_strategy, create, adjust_params, invest_in, cancel, profit), and Smart Copy (get, create, check_params, cancel). Also handles pushing trading signals to the Pionex signal platform.

## Routing

- Bot lifecycle (futures grid) -> **pionex-bot** (this skill)
- Bot lifecycle (spot grid) -> **pionex-bot** (this skill)
- Bot lifecycle (smart copy) -> **pionex-bot** (this skill)
- Push trading signal to signal platform (signal provider role) -> **pionex-bot** (this skill)
- Market data -> **pionex-market**
- Spot balance -> **pionex-portfolio**
- Spot order placement/cancel -> **pionex-trade**

## Commands

| Command | Type | Description |
|---------|------|-------------|
| `pionex-trade-cli bot order_list [--status running\|finished] [--base BTC] [--quote USDT] [--page-token <token>] [--bu-order-types futures_grid,spot_grid,smart_copy]` | READ | List bot orders with optional filters and pagination |
| `pionex-trade-cli bot futures_grid get --bu-order-id <id>` | READ | Query one futures grid bot order |
| `pionex-trade-cli bot futures_grid create --base BTC --quote USDT --bu-order-data-json '<json>' [--dry-run]` | WRITE | Create futures grid bot |
| `pionex-trade-cli bot futures_grid check_params --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>'` | READ | Validate futures grid params before create. On FailedWithData, surfaces `min_investment` / `max_investment` / `slippage`. |
| `pionex-trade-cli bot futures_grid adjust_params --body-json '<json>' [--dry-run]` | WRITE | Add investment / modify range / trigger invest-in |
| `pionex-trade-cli bot futures_grid reduce --body-json '<json>' [--dry-run]` | WRITE | Reduce bot position |
| `pionex-trade-cli bot futures_grid cancel --bu-order-id <id> [--close-sell-model TO_QUOTE\\|TO_USDT] [--dry-run]` | WRITE | Cancel and close bot |
| `pionex-trade-cli bot spot_grid get --bu-order-id <id>` | READ | Query one spot grid bot order |
| `pionex-trade-cli bot spot_grid get_ai_strategy --base <BASE> --quote <QUOTE>` | READ | Fetch AI-recommended grid parameters for a pair |
| `pionex-trade-cli bot spot_grid create --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>' [--dry-run]` | WRITE | Create a new spot grid bot |
| `pionex-trade-cli bot spot_grid check_params --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>'` | READ | Validate spot grid params before create. On FailedWithData, surfaces `min_investment` / `max_investment` / `slippage`. |
| `pionex-trade-cli bot spot_grid adjust_params --body-json '<json>' [--dry-run]` | WRITE | Modify grid price range |
| `pionex-trade-cli bot spot_grid invest_in --body-json '<json>' [--dry-run]` | WRITE | Add funds to a running spot grid bot |
| `pionex-trade-cli bot spot_grid cancel --bu-order-id <id> [--dry-run]` | WRITE | Cancel and close spot grid bot |
| `pionex-trade-cli bot spot_grid profit --body-json '<json>' [--dry-run]` | WRITE | Extract accumulated grid profits |
| `pionex-trade-cli bot smart_copy get --bu-order-id <id>` | READ | Query one smart copy bot order |
| `pionex-trade-cli bot smart_copy check_params --base <BASE> --quote <QUOTE> --leverage <n> --quote-investment <amount> [--signal-type <uuid>] [--signal-param <json>]` | READ | Validate smart copy params. Use `--quote-investment 0` to get investment range only. On FailedWithData, surfaces constraints. |
| `pionex-trade-cli bot smart_copy create --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>' [--copy-from <id>] [--copy-type <type>] [--note <note>] [--dry-run]` | WRITE | Create a smart copy bot (portfolio model) |
| `pionex-trade-cli bot smart_copy cancel --bu-order-id <id> [--close-note <note>] [--convert-into-earn-coin] [--dry-run]` | WRITE | Cancel and close smart copy bot |
| `pionex-trade-cli bot signal listener --signal-type <uuid> --signal-param <json> --base <BASE> --quote <QUOTE> --time <iso> --price <price> --action <buy\|sell> --position-size <size> --contracts <n> [--direction <dir>] [--dry-run]` | WRITE | Push a trading signal to Pionex signal platform (signal provider role) |

## Safety Rules

1. Confirm write intent for create/adjust/reduce/cancel before running without `--dry-run`.
2. Call `check_params` before `create` to validate parameters. If the response is `FailedWithData`, surface the returned `min_investment`, `max_investment`, and `slippage` values to the user before retrying.
3. Never infer `buOrderId`, leverage, range, or amount; require explicit user values.
4. If API rejects params, surface exact error and propose a corrected payload.

### Spot Grid Specific

5. Call `get_ai_strategy` before `create` when the user has not provided explicit price range and row count.
6. Never add `leverage`, `trend`, or `extraMargin` fields to spot grid payloads — spot grid is leverage-free.
7. Verify account has sufficient base + quote balance before creating or adding investment.
8. `invest_in` and `profit` are standalone commands — do not confuse with `adjust_params`.

### Smart Copy Specific

9. `portfolio` array in `buOrderData` must not be empty; each entry requires `base`, `signal_type` (UUID), and `leverage` (integer).
10. Never infer `signal_type` UUIDs; require explicit user values.
11. `--copy-from <id>` in `create` copies parameters from an existing smart copy order — use only when the user explicitly requests it.
12. `--convert-into-earn-coin` in `cancel` converts holdings into Earn products — confirm with user before using.
13. `check_params` takes flat flags (`--leverage`, `--quote-investment`), not `--bu-order-data-json`. Use `--quote-investment 0` to query the investment range without validating a specific amount.

### Signal Specific

14. `bot signal listener` **pushes** a trading signal to the Pionex signal platform as a signal provider — it is NOT a consumer subscription command.
15. All flags are required: `--signal-type`, `--signal-param`, `--base`, `--quote`, `--time` (RFC 3339), `--price`, `--action`, `--position-size`, `--contracts`. Never omit or infer any of them.

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

# Validate futures grid params before creating
pionex-trade-cli bot futures_grid check_params \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"top":"110000","bottom":"90000","row":100,"grid_type":"arithmetic","trend":"long","leverage":5,"extraMargin":"0","quoteInvestment":"100"}'

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

# Validate spot grid params before creating
pionex-trade-cli bot spot_grid check_params \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"top":"110000","bottom":"90000","row":50,"grid_type":"arithmetic","quoteInvestment":"200"}'

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

# --- Smart Copy ---

# Step 1: Get investment range for a signal (quote-investment 0 = range query only)
pionex-trade-cli bot smart_copy check_params \
  --base BTC \
  --quote USDT \
  --leverage 5 \
  --quote-investment 0

# Step 1b: Validate a specific investment amount
pionex-trade-cli bot smart_copy check_params \
  --base BTC \
  --quote USDT \
  --leverage 5 \
  --quote-investment 100

# Step 2: Dry-run create (single signal, leverage 5)
pionex-trade-cli bot smart_copy create \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"quote_total_investment":"100","portfolio":[{"base":"BTC","signal_type":"<signal-uuid>","leverage":5}]}' \
  --dry-run

# Dry-run create with stop-loss/take-profit and multi-signal portfolio
pionex-trade-cli bot smart_copy create \
  --base BTC \
  --quote USDT \
  --bu-order-data-json '{"quote_total_investment":"200","portfolio":[{"base":"BTC","signal_type":"<uuid1>","leverage":5,"percent":"0.5","profit_stop_ratio":"0.3","loss_stop_ratio":"0.1"},{"base":"ETH","signal_type":"<uuid2>","leverage":3,"percent":"0.5"}]}' \
  --dry-run

# Query smart copy bot status
pionex-trade-cli bot smart_copy get --bu-order-id 111222333

# Cancel smart copy bot
pionex-trade-cli bot smart_copy cancel \
  --bu-order-id 111222333 \
  --dry-run

# Cancel and convert holdings into Earn products
pionex-trade-cli bot smart_copy cancel \
  --bu-order-id 111222333 \
  --convert-into-earn-coin \
  --dry-run

# Push a trading signal to the Pionex signal platform (signal provider role)
pionex-trade-cli bot signal listener \
  --signal-type <uuid> \
  --signal-param '{}' \
  --base BTC \
  --quote USDT \
  --time "2026-04-15T10:00:00Z" \
  --price 85000 \
  --action buy \
  --position-size 1 \
  --contracts 1 \
  --dry-run

# List running smart copy bots
pionex-trade-cli bot order_list --status running --bu-order-types smart_copy
```
