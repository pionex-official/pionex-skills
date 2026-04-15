# Requirements: Bot Smart Copy

**Iteration:** `2026041400_bot_smart_copy`
**Date:** 2026-04-14
**Source:** `pionex-ai-kit` PR #38

## Overview

Add Smart Copy bot lifecycle commands and a Signal subscriber command to the `pionex-bot` skill. Smart Copy is a copy-trading feature that lets users mirror positions from a signal provider.

## Scope

### New: `bot smart_copy` subcommands

| Command | Type | Description |
|---------|------|-------------|
| `bot smart_copy get` | READ | Retrieve a smart copy bot order by ID |
| `bot smart_copy create` | WRITE | Create a new smart copy bot order |
| `bot smart_copy check_params` | READ | Validate parameters before placing an order |
| `bot smart_copy cancel` | WRITE | Cancel and close a smart copy bot order |

### New: `bot signal` subcommands

| Command | Type | Description |
|---------|------|-------------|
| `bot signal add_listener` | WRITE | Subscribe to a signal provider |

### Changed: `pionex-bot` skill routing

The `description` frontmatter already mentions Smart Copy, but the command table and safety rules don't cover it yet. Both need updating.

## `buOrderData` JSON Schema

**Required fields:**
- `quoteInvestment` (string) — investment amount in quote currency
- `leverageType` (string) — `"follow"` (mirror the signal's leverage) or `"fixed"` (use a fixed leverage value)

**Optional fields:**
- `leverage` (number) — required when `leverageType="fixed"`; ignored when `"follow"`
- `maxInvestPerOrder` (string) — max investment per copied order; caps individual copy size
- `copyMode` (string) — `"fixed_amount"` (same dollar amount per order) or `"fixed_ratio"` (proportional to signal's position)

## `closeSellModel` for Cancel

Same enum as spot grid:
- `NOT_SELL` — hold all assets, do not sell
- `TO_QUOTE` — convert all base to quote currency
- `TO_USDT` — convert all assets to USDT

## `bot signal add_listener` Parameters

- `--signal-source-id <id>` (required) — ID of the signal provider to subscribe to
- `--listen-mode <mode>` (optional) — subscription mode (provider-specific values)

## Acceptance Criteria

1. `bot smart_copy get`, `create`, `check_params`, `cancel` are documented in the command table with exact flag syntax
2. `bot signal add_listener` is documented with exact flag syntax
3. `buOrderData` JSON structure and field constraints are documented in an examples section
4. Safety rules cover: confirm before write, `check_params` before `create`, no inference of `buOrderId` or signal source ID
5. `leverageType="fixed"` requires explicit `leverage` value — enforced in safety rules
6. `closeSellModel` defaults and valid values documented for `cancel`
7. Version bumped to 0.5.0
8. `docs/` updated: requirements, tech-design, tech-memory, tech-api-overview
