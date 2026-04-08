# Technical Design: Grid Bot Params Check

## Overview

Add `check_params` subcommands for `futures_grid` and `spot_grid`. These are READ-only validation commands — they call the exchange's parameter check API and return validation results without creating any bot order.

## Affected Files

| File | Change |
|------|--------|
| `skills/pionex-bot/SKILL.md` | Add 2 commands to command table; add 1 safety rule; bump version |
| `docs/requirements-overview.md` | Add 2 commands to bot section; update date; add iteration history |
| `docs/tech-design-overview.md` | Document `check_params` pattern; update date |
| `docs/tech-api-overview.yaml` | Add 2 CLI commands under `bot` subcommands |
| `docs/tech-memory-overview.md` | Append iteration entry |

## SKILL.md Changes

### Command Table Additions

Insert after `bot futures_grid create`:

```
| `pionex-trade-cli bot futures_grid check_params --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>'` | READ | Validate futures grid params before create. On FailedWithData, shows min_investment / max_investment / slippage. |
```

Insert after `bot spot_grid create`:

```
| `pionex-trade-cli bot spot_grid check_params --base <BASE> --quote <QUOTE> --bu-order-data-json '<json>'` | READ | Validate spot grid params before create. On FailedWithData, shows min_investment / max_investment / slippage. |
```

### Safety Rule Addition

Renumber existing rules and add as rule #2 (applies to both grid types):

```
2. Call `check_params` before `create` to validate parameters. If the response is FailedWithData, surface the returned `min_investment`, `max_investment`, and `slippage` values to the user before retrying.
```

### Version Bump

`0.3.0` → `0.4.0` (new READ commands added to both `futures_grid` and `spot_grid` — minor bump)

## API Endpoints (upstream, for reference)

These are implemented in `pionex-ai-kit`, not in this repo. Documented for context:

- `POST /api/v1/bot/orders/futuresGrid/checkParams`
- `POST /api/v1/bot/orders/spotGrid/checkParams`

Both accept the same JSON body as the corresponding `create` command and return:
- Success: parameters are valid, bot can be created
- `FailedWithData`: parameters invalid; body contains `min_investment`, `max_investment`, `slippage`

## Workflow Update

Updated recommended creation flow for both grid types:

1. `check_params` → validate parameters (new)
2. `create --dry-run` → preview
3. Confirm with user
4. `create` (without `--dry-run`)
