# Tech Design: pionex-earn-dual Skill

## Overview

Add `skills/pionex-earn-dual/SKILL.md` as a new skill covering Pionex Dual Investment operations.

## Affected Files

| File | Change |
|------|--------|
| `skills/pionex-earn-dual/SKILL.md` | **New file** — full skill definition |
| `README.md` | **Update** — add row to skills table |
| `docs/requirements-overview.md` | **Update** — add earn dual section |
| `docs/tech-design-overview.md` | **Update** — add earn dual skill design notes |
| `docs/tech-memory-overview.md` | **Update** — add iteration entry |

## Skill File Design

### Frontmatter

```yaml
---
name: pionex-earn-dual
description: >
  Use when the user asks about Pionex Dual Investment (earn dual):
  listing products, checking yield rates, placing or revoking an investment,
  querying balances or history, or collecting settled earnings.
  Do NOT use for spot trading (pionex-trade), bot trading (pionex-bot),
  or market data only (pionex-market).
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
```

### Command Table Design

All commands follow the pattern `pionex-trade-cli earn dual <subcommand> [flags]`.

**Public (no auth):**

| Command | Flags | Type |
|---------|-------|------|
| `earn dual symbols` | `[--base <currency>]` | READ |
| `earn dual open-products` | `--base <c> --quote <c> --type DUAL_BASE\|DUAL_CURRENCY [--currency <c>]` | READ |
| `earn dual prices` | `--base <c> --quote <c> --product-ids <csv>` | READ |
| `earn dual index` | `--base <c> --quote <c>` | READ |
| `earn dual delivery-prices` | `--base <c> [--quote <c>] [--startTime <ms>] [--endTime <ms>]` | READ |

**Private:**

| Command | Flags | Type | Permission |
|---------|-------|------|-----------|
| `earn dual balances` | `[--merge]` | READ | View |
| `earn dual get-invests` | `[--base <c>] --client-dual-ids <id1,id2,...>` | READ | View |
| `earn dual records` | `--base <c> --end-time <ms> [--quote <c>] [--currency <c>] [--start-time <ms>] [--limit <n>]` | READ | View |
| `earn dual invest` | `--base <c> --product-id <id> --profit <rate> (--base-amount <n> \| --currency-amount <n>) [--client-dual-id <id>] [--dry-run]` | WRITE | Earn |
| `earn dual revoke-invest` | `--base <c> --product-id <id> --client-dual-id <id> [--dry-run]` | WRITE | Earn |
| `earn dual collect` | `--base <c> --client-dual-id <id> --product-id <id> [--dry-run]` | WRITE | Earn |

### Key Workflow Section: invest

The invest workflow must be presented as a mandatory 3-step process:

```
Step 1: earn dual open-products → get productId
Step 2: earn dual prices        → get fresh profit value
Step 3: earn dual invest        → pass profit from step 2 unchanged
```

This is the most critical part of the skill — an agent that skips step 2 will get API rejections.

### quote/currency Rule

Must be documented as a table in the skill:

| Base | quote param | currency options |
|------|------------|-----------------|
| BTC, ETH | USDXO | USDT, USDC |
| All others | USDT | USDT |

### Safety Rules

1. Never infer `profit` — always fetch fresh from `earn dual prices` immediately before investing.
2. Never provide both `--base-amount` and `--currency-amount` in one invest command.
3. Use `--dry-run` for `invest`, `revoke`, `collect`; confirm with user before real execution.
4. Never infer `clientDualId` — require explicit user value or generate a unique one with user confirmation.
5. `revoke` only works for pending orders; `collect` only for settled orders — check state via `earn dual invests` first.

## README.md Update

Add to skills table:

```markdown
| [pionex-earn-dual](skills/pionex-earn-dual/SKILL.md) | Dual Investment: products, prices, invest, revoke, collect | No (public) / Yes (private) |
```
