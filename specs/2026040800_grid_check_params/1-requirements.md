# Requirements: Grid Bot Params Check

## Iteration ID

`2026040800_grid_check_params`

## Source

- **PR:** [pionex-ai-kit#37](https://github.com/pionex-official/pionex-ai-kit/pull/37)
- **Related Issue:** Feature Request: Futures Grid Bot Params Check API (#17)

## Background

Before creating a grid bot, agents sometimes submit parameters that the exchange rejects (e.g. investment out of range, slippage constraint). The rejection only surfaces after `create`, which is a write operation. There was no way to pre-validate parameters without committing a bot creation request.

## Change

Add `check_params` subcommands to both `futures_grid` and `spot_grid` in the `pionex-bot` skill. These are **read-only validation** commands that verify bot parameters against exchange constraints without creating an order.

### Before

The `pionex-bot` skill had no parameter validation commands. Agents could only discover invalid params by running `create --dry-run`, which still makes an API call.

### After

Two new commands:

```
pionex-trade-cli bot futures_grid check_params --base <BASE> --quote <QUOTE> --bu-order-data-json '<JSON>'
pionex-trade-cli bot spot_grid check_params --base <BASE> --quote <QUOTE> --bu-order-data-json '<JSON>'
```

Both map to new Pionex API endpoints:
- `POST /api/v1/bot/orders/futuresGrid/checkParams`
- `POST /api/v1/bot/orders/spotGrid/checkParams`

### Error Guidance

When the API rejects the parameters, the response uses `FailedWithData` and includes:
- `min_investment` — minimum allowed investment amount
- `max_investment` — maximum allowed investment amount
- `slippage` — slippage constraint

Agents must surface these values to the user and suggest corrected parameters.

## Acceptance Criteria

1. `bot futures_grid check_params` command is documented in the command table in `skills/pionex-bot/SKILL.md`
2. `bot spot_grid check_params` command is documented in the command table
3. A safety rule is added: call `check_params` before `create` to validate parameters
4. `FailedWithData` guidance is documented (surface `min_investment`, `max_investment`, `slippage`)
5. `docs/requirements-overview.md` lists both commands as completed
6. `docs/tech-api-overview.yaml` includes both CLI commands
7. Skill version bumped to `0.4.0`
