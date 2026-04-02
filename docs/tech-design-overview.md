# Technical Design Overview

This document describes the detailed technical design of the Pionex Skills project.

## Last Updated

**Date:** 2026-04-01 (updated by iteration `2026040100_earn_dual`)

## Skill File Structure

Each skill lives at `skills/<skill-name>/SKILL.md` and has two parts:

### 1. YAML Frontmatter

```yaml
---
name: skill-name
description: >
  Routing description — when the skill router should select this skill.
  Covers positive cases AND explicit exclusions.
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

**Key fields:**
- `description` — Used by the skill router. Must be precise about what the skill covers AND what it does NOT cover (exclusions prevent wrong-skill selection).
- `metadata.agent.requires.bins` — CLI binaries the agent must verify are present before running commands.
- `metadata.agent.install` — Install instructions surfaced to the user if the CLI is missing.

### 2. Markdown Body

Structured sections:

| Section | Purpose |
|---------|---------|
| `## Routing` / `## Skill Routing` | Cross-skill routing table — which skill for what |
| `## Prerequisites` | CLI install + credential setup |
| `## Commands` / `## Command Index` | Full command table with flags and types (READ/WRITE) |
| `## Safety Rules` | Behavioral constraints for write operations |
| `## Examples` | Copy-paste CLI examples |
| Optional workflow sections | Step-by-step flows (e.g., balance-aware order flow) |

## Skill-Specific Design Notes

### pionex-market

- All commands are **READ-only**, no authentication required
- Used as a **dependency** by other skills for symbol validation before placing orders
- `market symbols` is the canonical source for min size, precision, filter rules

### pionex-portfolio

- Single command: `account balance`
- Returns all currencies — agents filter the relevant asset from JSON
- Used as a pre-order check in `pionex-trade` flows

### pionex-trade

Contains a multi-step **balance-aware order flow**:
1. Check balance via `account balance`
2. Compare available vs. requested amount
3. Dry-run the order
4. Confirm with user
5. Execute without `--dry-run`

Market/LIMIT order distinction:
- Market buy → `--amount` (quote currency)
- Market sell / Limit → `--size` (base currency)
- Limit → additionally requires `--price`

### pionex-bot

Uses nested command structure: `pionex-trade-cli bot futures_grid <subcommand>`

`create` requires a JSON blob (`--bu-order-data-json`). Key fields:
- `top`, `bottom` — price range
- `row` — number of grids
- `grid_type` — `arithmetic` or `geometric`
- `trend` — `long`, `short`, or `neutral`
- `leverage`, `quoteInvestment`

`adjust_params` and `reduce` use `--body-json` for structured payload.

Safety: `buOrderId` must never be inferred — always require explicit user value.

### pionex-earn-dual

Command namespace: `earn dual <subcommand>` — mirrors the API path `/api/v1/earn/dual/`.

**quote/currency rule (must be encoded in skill):**

| Base | `--quote` | `--currency` options |
|------|-----------|----------------------|
| BTC, ETH | `USDXO` | `USDT` or `USDC` |
| All others | `USDT` | `USDT` |

**Mandatory invest workflow:**
1. `earn dual open_products` → get `productId`
2. `earn dual prices` → get fresh `profit` value (immediately before step 3)
3. `earn dual invest --profit <value-from-step-2>` → execute

The `profit` field is time-sensitive. Agents must not cache it or insert other commands between steps 2 and 3.

**State prerequisites for write commands:**
- `revoke`: only pending/unmatched orders
- `collect`: only settled orders
- Agent must call `earn dual invests` to verify state before attempting either

**Dry-run scope:** `invest`, `revoke`, `collect` all support `--dry-run`.

## File Naming and Organization

```
skills/
  pionex-market/
    SKILL.md        ← only file, complete skill definition
  pionex-portfolio/
    SKILL.md
  pionex-trade/
    SKILL.md
  pionex-bot/
    SKILL.md
  pionex-earn-dual/
    SKILL.md
```

One skill = one directory = one `SKILL.md`. No sub-files.

## Versioning

Skills follow semver in the `metadata.version` field. Increment on:
- **patch** — Fix inaccurate command syntax, typos in safety rules
- **minor** — Add new commands, expand routing scope
- **major** — Breaking change to skill interface or routing logic

All changes documented in `CHANGELOG.md`.
