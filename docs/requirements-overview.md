# Requirements Overview

This document summarizes the requirement history and current status of the Pionex Skills project.

## Last Updated

**Date:** 2026-04-03 (updated by iteration `2026040300_spot_grid`)

## Current Status

### Core Features

#### Skill: pionex-market
**Status:** Completed  
**Scope:** Public market data — no authentication required

- ✅ `market depth <symbol>` — Order book depth (bids/asks)
- ✅ `market trades <symbol>` — Recent public trades
- ✅ `market symbols` — Symbol metadata (precision, min size, filter rules)
- ✅ `market tickers` — 24h price ticker(s)
- ✅ `market book_tickers` — Best bid/ask ticker(s)
- ✅ `market klines <symbol> <interval>` — OHLCV candlestick data

#### Skill: pionex-portfolio
**Status:** Completed  
**Scope:** Spot account balance queries — requires API credentials

- ✅ `account balance` — All spot balances

#### Skill: pionex-trade
**Status:** Completed  
**Scope:** Spot order lifecycle — requires API credentials

- ✅ `orders new` — Place market/limit buy/sell orders
- ✅ `orders get` — Query a single order by ID
- ✅ `orders open` — List open orders for a symbol
- ✅ `orders all` — Order history (filled/cancelled)
- ✅ `orders fills` — Executed trade fills
- ✅ `orders fills_by_order_id` — Fills for one specific order
- ✅ `orders cancel` — Cancel a single order
- ✅ `orders cancel_all` — Cancel all open orders for a symbol

#### Skill: pionex-bot
**Status:** Completed  
**Scope:** Futures Grid and Spot Grid bot lifecycle — requires API credentials with bot permissions

- ✅ `bot order_list` — List bot orders across all types with filters and pagination
- ✅ `bot futures_grid get` — Query futures grid bot order status
- ✅ `bot futures_grid create` — Create a new futures grid bot
- ✅ `bot futures_grid adjust_params` — Add investment / modify range / trigger invest-in
- ✅ `bot futures_grid reduce` — Reduce futures grid bot position
- ✅ `bot futures_grid cancel` — Cancel and close futures grid bot
- ✅ `bot spot_grid get` — Query spot grid bot order status
- ✅ `bot spot_grid get_ai_strategy` — Fetch AI-recommended grid parameters for a trading pair
- ✅ `bot spot_grid create` — Create a new spot grid bot (no leverage/trend)
- ✅ `bot spot_grid adjust_params` — Modify spot grid price range
- ✅ `bot spot_grid invest_in` — Add funds to a running spot grid bot
- ✅ `bot spot_grid cancel` — Cancel and close spot grid bot
- ✅ `bot spot_grid profit` — Extract accumulated grid profits

#### Skill: pionex-earn-dual
**Status:** Planned (CLI implementation pending in `pionex-ai-kit#16`)
**Scope:** Dual Investment product lifecycle — public queries require no auth; write operations require `Earn` permission

Public (no auth):
- 📋 `earn dual symbols` — List supported trading pairs with min/max investment amounts
- 📋 `earn dual open_products` — List open products for a pair and type (DUAL_BASE / DUAL_CURRENCY)
- 📋 `earn dual prices` — Get current yield rate and investability per product ID
- 📋 `earn dual index` — Real-time index price for a pair
- 📋 `earn dual delivery_prices` — Historical settlement delivery prices

Private (View permission):
- 📋 `earn dual balances` — User's dual investment account balances
- 📋 `earn dual get_invests` — Batch query investment orders by client IDs
- 📋 `earn dual records` — Paginated investment history

Private (Earn permission):
- 📋 `earn dual invest` — Create a new investment order (requires fresh `profit` from `/prices`)
- 📋 `earn dual revoke_invest` — Revoke a pending investment order
- 📋 `earn dual collect` — Collect settled earnings into spot account

### Cross-Cutting Requirements

- ✅ All write operations support `--dry-run` flag
- ✅ Skills encode explicit safety rules (no guessing params, confirm before write)
- ✅ Skills define routing to prevent overlap between skill scopes
- ✅ Skills installable via `npx skills add pionex-official/pionex-skills`

## Acceptance Criteria

Each skill must:
1. Define clear routing (`description` frontmatter) so the skill router picks the right skill
2. Document all CLI commands with exact syntax in a command table
3. Include safety rules for any write operations
4. Include `--dry-run` instructions for destructive commands

## Iteration History

### 2026-04-03: Spot Grid Bot
**Iteration Directory:** `specs/2026040300_spot_grid/`
**Requirements:** Add 7 `bot spot_grid` subcommands to `pionex-bot` skill — get, get_ai_strategy, create, adjust_params, invest_in, cancel, profit
**Source:** CLI implementation in `pionex-ai-kit` PR #30

### 2026-04-02: Bot Order List
**Iteration Directory:** `specs/2026040200_bot_order_list/`
**Requirements:** Add `bot order_list` command to `pionex-bot` skill — list/paginate bot orders across futures_grid, spot_grid, smart_copy
**Source:** CLI implementation in `pionex-ai-kit` PR #27

### 2026-04-01: Earn Dual Skill
**Iteration Directory:** `specs/2026040100_earn_dual/`
**Requirements:** Add `pionex-earn-dual` skill for Dual Investment operations (Beta API)
**Dependency:** CLI implementation in `pionex-ai-kit#16` — skill file is created ahead of CLI
