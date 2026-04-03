# Requirements: Spot Grid Bot

## Background

The `pionex-bot` skill currently documents only `futures_grid` lifecycle commands. The upstream `pionex-ai-kit` PR #30 added full support for the `spot_grid` bot type, introducing 7 new CLI subcommands. The skill must be updated to reflect this new capability so agents can correctly create, query, and manage spot grid bots.

## Source

- GitHub PR: https://github.com/pionex-official/pionex-ai-kit/pull/30
- Upstream CLI package: `@pionex/pionex-ai-kit`
- Related issue: pionex-official/pionex-ai-kit#15 — "MCP/CLI/Skills for spot grid bot"

## Requirements

### Functional

1. Add all 7 `bot spot_grid` subcommands to `pionex-bot` skill
2. Add `get_ai_strategy` — unique to spot grid, recommends grid parameters before creation
3. Document `invest_in` as a standalone command (differs from futures_grid where it is part of `adjust_params`)
4. Document `profit` command for extracting accumulated grid profits
5. Update routing description to explicitly mention "Spot Grid"
6. Add spot-grid-specific safety rules (balance check, AI strategy recommendation, no leverage)

### CLI Commands

| Command | Type | Description |
|---------|------|-------------|
| `bot spot_grid get --bu-order-id <id>` | READ | Query one spot grid bot order |
| `bot spot_grid get_ai_strategy --base <BASE> --quote <QUOTE>` | READ | Fetch AI-recommended grid parameters |
| `bot spot_grid create --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>' [--dry-run]` | WRITE | Create a new spot grid bot |
| `bot spot_grid adjust_params --body-json '<json>' [--dry-run]` | WRITE | Modify grid price range |
| `bot spot_grid invest_in --body-json '<json>' [--dry-run]` | WRITE | Add funds to a running bot |
| `bot spot_grid cancel --bu-order-id <id> [--dry-run]` | WRITE | Cancel and close bot |
| `bot spot_grid profit --body-json '<json>' [--dry-run]` | WRITE | Extract accumulated grid profits |

### `create` JSON Payload Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `top` | string | Yes | Upper price bound of grid range |
| `bottom` | string | Yes | Lower price bound of grid range |
| `row` | integer | Yes | Number of grid levels |
| `grid_type` | string | Yes | `arithmetic` or `geometric` |
| `quoteInvestment` | string | Yes | Quote currency investment amount |

**Spot grid has no leverage or trend fields** — it is a pure spot strategy.

### Key Differences from `futures_grid`

| Aspect | futures_grid | spot_grid |
|--------|-------------|-----------|
| Leverage | Yes | No |
| Trend (`long`/`short`/`neutral`) | Yes | No |
| AI strategy recommendation | No | Yes (`get_ai_strategy`) |
| Invest in (standalone command) | No (part of `adjust_params`) | Yes (`invest_in`) |
| Profit extraction | No | Yes (`profit`) |
| Position reduction | Yes (`reduce`) | No |

## Acceptance Criteria

1. `pionex-bot` skill command table includes all 7 `bot spot_grid` subcommands
2. Routing description updated to mention "Spot Grid"
3. `get_ai_strategy` usage documented with recommendation to call before `create`
4. Examples section includes at least one spot grid creation flow
5. Safety rules include spot-grid-specific constraints (no leverage, balance check)
6. Skill version bumped to `0.3.0`
7. `docs/` overview files updated
