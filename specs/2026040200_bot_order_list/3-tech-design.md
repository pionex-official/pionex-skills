# Technical Design: Bot Order List

## Affected Files

| File | Change |
|---|---|
| `skills/pionex-bot/SKILL.md` | Add `bot order_list` to command table, update routing description, add example, bump version |
| `docs/requirements-overview.md` | Add `bot order_list` to pionex-bot feature list |
| `docs/tech-design-overview.md` | Document `order_list` command and route distinction |
| `docs/tech-memory-overview.md` | Add iteration entry with key decisions |

## Skill Changes (`skills/pionex-bot/SKILL.md`)

### 1. Version bump

`version: "0.1.0"` → `version: "0.2.0"` (minor: new command added)

### 2. Frontmatter description

Add "list" to the routing description:

```yaml
description: >
  Use when the user asks to create, query, list, adjust, reduce, or cancel Pionex
  Futures Grid Bot orders. Includes listing/paginating through bot orders in bulk.
  Requires API credentials and bot permissions.
  Do NOT use for market data only (pionex-market), balance only (pionex-portfolio),
  or spot order placement/cancel (pionex-trade).
```

### 3. Commands table — add new row

```markdown
| `pionex-trade-cli bot order_list [--status running|finished] [--base BTC] [--quote USDT] [--page-token <token>] [--bu-order-types futures_grid,spot_grid,smart_copy]` | READ | List bot orders with optional filters and pagination |
```

### 4. New example

```bash
# List running futures grid bot orders
pionex-trade-cli bot order_list --status running --bu-order-types futures_grid

# Paginate through finished orders
pionex-trade-cli bot order_list --status finished --page-token <nextPageToken>

# Filter by symbol
pionex-trade-cli bot order_list --base BTC --quote USDT
```

## Route Distinction

`bot order_list` is a **top-level** command under `bot`, unlike the `bot futures_grid <cmd>` nested structure. This is intentional — `order_list` spans multiple bot types (futures_grid, spot_grid, smart_copy), so it doesn't belong under a type-specific subgroup.

| Command structure | Scope |
|---|---|
| `bot futures_grid <cmd>` | Single bot type lifecycle (create/get/adjust/reduce/cancel) |
| `bot order_list` | Cross-type order listing |
