# Technical Memory & Knowledge

This document records key decisions, lessons learned, and non-obvious technical knowledge accumulated across iterations.

## Last Updated

**Date:** 2026-04-14

---

## Initial State (2026-04-01)

**Context:** SDD initialization for the pionex-skills repository.

### Key Facts

- The repository is a **pure Markdown skills repo** — no build step, no compiled code, no HTTP service.
- `tech-api-overview.yaml` uses a non-standard `x-cli-interface` extension because there are no HTTP or gRPC endpoints; the "API" is a CLI.
- Skills are installed via `npx skills add pionex-official/pionex-skills` — an external skill manager, not a package.json script.

### Relationship to pionex-ai-kit

This repository (`pionex-skills`) depends on `@pionex/pionex-ai-kit` (the `pionex-ai-kit` repo) for the `pionex-trade-cli` binary. The two repositories are maintained separately:
- `pionex-ai-kit` — CLI implementation (TypeScript, published to npm)
- `pionex-skills` — Behavioral playbooks (Markdown, distributed as a git repo)

When `pionex-ai-kit` adds or changes CLI commands, the corresponding skill files in this repo must be updated to reflect the new syntax.

### CLI Command Changes (Unreleased / Recent)

The following updates were made to skills to align with recent CLI changes:
- `pionex-bot`: removed `openPrice`/`keyId` references; aligned to `adjust_params` / `reduce` naming
- `pionex-bot`: uses nested `bot futures_grid <cmd>` route (not flat `bot <cmd>`)
- `pionex-market`: added `market book_tickers` command
- `pionex-trade`: added `orders fills_by_order_id` command

### Safety Design Rationale

The safety rules in skills (dry-run, explicit params, no inference) exist because:
- These skills interact with real financial accounts
- Incorrect orders cannot always be undone instantly
- The agent must be a gatekeeper, not an executor that acts on ambiguous input

---

## Iteration: 2026040100_earn_dual (2026-04-01)

**Added:** `skills/pionex-earn-dual/SKILL.md` — Dual Investment skill (Beta API)

### Key Decisions

**1. Mandatory 2-step invest flow (prices → invest)**

The Pionex API rejects the `invest` call if the `profit` value is stale. The skill encodes this as a non-negotiable 3-step workflow: open_products → prices → invest. The agent must not insert other commands between steps 2 and 3.

**2. BTC/ETH use USDXO quote, all others use USDT**

This is an API quirk specific to Dual Investment. The internal quote for BTC/ETH pairs is `USDXO` (not `USDT`). The skill encodes a routing table for this rule to prevent `DUAL_PARAMETER_ERROR: invalid base quote`.

**3. Skill created ahead of CLI implementation**

The CLI commands (`pionex-trade-cli earn dual *`) do not yet exist in `pionex-ai-kit`. The skill is defined first so both tracks (skill spec in this repo, CLI implementation in `pionex-ai-kit#16`) can proceed in parallel. The command syntax in the skill defines the expected CLI interface.

**4. `clientDualId` as idempotency key**

The API uses `clientDualId` as an idempotency key for invest operations. The skill enforces that the agent never infers or auto-generates this value without user confirmation.

_Future iterations should append new entries here with date and context._

---

## Iteration: 2026040200_bot_order_list (2026-04-02)

**Added:** `bot order_list` command to `skills/pionex-bot/SKILL.md`

### Key Decisions

**1. `bot order_list` is top-level, not under `bot futures_grid`**

The CLI route is `pionex-trade-cli bot order_list`, not `bot futures_grid list`. This is intentional because `order_list` spans multiple bot types (futures_grid, spot_grid, smart_copy) and does not belong under a type-specific subgroup.

**2. `buOrderTypes` serialized as comma-separated string**

`URLSearchParams.set()` only handles one value per key. The CLI flag `--bu-order-types` accepts a comma-separated string (e.g. `futures_grid,spot_grid`) which is forwarded as-is to the API. When omitted, all bot types are returned.

**3. Read-only — no `--dry-run` needed**

`GET /api/v1/bot/orders` is read-only. No dry-run guard is required or appropriate.

**4. pionex-bot skill version bumped to 0.2.0**

Adding a new command (minor change) warrants a minor version bump per the versioning policy in `tech-design-overview.md`.

---

## Iteration: 2026040300_spot_grid (2026-04-03)

**Added:** 7 `bot spot_grid` subcommands to `skills/pionex-bot/SKILL.md`

### Key Decisions

**1. `spot_grid` follows the same nested route as `futures_grid`**

The CLI structure is `pionex-trade-cli bot spot_grid <subcommand>`, parallel to `bot futures_grid <subcommand>`. Cross-type listing still uses the top-level `bot order_list` command with `--bu-order-types spot_grid`.

**2. `invest_in` is a standalone command (not part of `adjust_params`)**

In futures_grid, adding investment is done via `adjust_params --body-json '{"type":"invest_in",...}'`. In spot_grid, there is a dedicated `invest_in` subcommand. This distinction must be documented clearly to prevent agents from using the wrong command.

**3. `get_ai_strategy` is a pre-create READ command unique to spot grid**

Agents should call `get_ai_strategy` to obtain AI-recommended `top`, `bottom`, and `row` values when the user hasn't explicitly provided a price range. This is a non-blocking recommendation — if the user provides explicit params, skip the AI step.

**4. Spot grid has no leverage, trend, or reduce**

Spot grid is a pure spot strategy. Payloads must never include `leverage`, `trend`, or `extraMargin`. There is no `reduce` subcommand because there is no leveraged position to reduce.

**5. `profit` command extracts accumulated grid profits**

This is unique to spot grid. The profits accumulate inside the bot; `profit` triggers an explicit extraction to the spot account. Requires `--dry-run` preview before execution.

**6. pionex-bot skill version bumped to 0.3.0**

Adding a new command group (spot_grid) is a minor change — warrants 0.2.0 → 0.3.0.

---

## Iteration: 2026040800_grid_check_params (2026-04-08)

**Added:** `bot futures_grid check_params` and `bot spot_grid check_params` to `skills/pionex-bot/SKILL.md`

### Key Decisions

**1. `check_params` is READ-only — no `--dry-run` needed**

The command calls the exchange's parameter validation API (`POST /api/v1/bot/orders/*/checkParams`) without creating any order. It is informational only, so `--dry-run` is not applicable.

**2. `FailedWithData` carries investment range and slippage**

When parameters are invalid, the API responds with a `FailedWithData` error that includes `min_investment`, `max_investment`, and `slippage`. The skill mandates that agents surface these values to the user — not just report "validation failed".

**3. `check_params` is inserted before `create --dry-run` in the creation flow**

The recommended creation flow is now: `check_params` → `create --dry-run` → confirm → `create`. This catches parameter errors before the dry-run step, avoiding a redundant API round-trip on invalid params.

**4. pionex-bot skill version bumped to 0.4.0**

Adding new READ commands to both `futures_grid` and `spot_grid` is a minor change — warrants 0.3.0 → 0.4.0.

**5. `tech-api-overview.yaml` also gained missing `spot_grid` commands**

The yaml only contained `futures_grid` commands. During this iteration the full `spot_grid` command set (added in iteration `2026040300_spot_grid`) was also backfilled, along with both new `check_params` entries.

---

## Iteration: 2026041400_bot_smart_copy (2026-04-14)

**Added:** `bot smart_copy` subcommands and `bot signal add_listener` to `skills/pionex-bot/SKILL.md`

### Key Decisions

**1. `signal` is a peer subgroup to `smart_copy`, not nested under it**

The CLI structure is `bot signal add_listener`, not `bot smart_copy signal add_listener`. The `signal` group is designed for future multi-bot signal support — other bot types may subscribe to signals later.

**2. `leverageType="fixed"` requires explicit `leverage` — enforced in safety rules**

The CLI's `parseSmartCopyBuOrderData()` rejects payloads where `leverageType="fixed"` but `leverage` is missing. The skill reflects this as a safety rule to prevent API rejections before they happen.

**3. `closeSellModel` for `cancel` adds `NOT_SELL` option**

Futures grid has `TO_QUOTE | TO_USDT`; spot grid has no close-sell-model flag; smart copy adds `NOT_SELL | TO_QUOTE | TO_USDT`. The skill documents the default (`NOT_SELL`) and mandates user confirmation.

**4. No `get_ai_strategy`, `reduce`, `invest_in`, or `profit` for smart copy**

Smart copy mirrors a signal provider's positions — investment sizing is handled at creation time via `copyMode` and `maxInvestPerOrder`, not through post-creation adjustments.

**5. pionex-bot skill version bumped to 0.5.0**

Adding a new command group (`smart_copy`) and a new subgroup (`signal`) is a minor change — warrants 0.4.0 → 0.5.0.

### Revision (2026-04-15): Corrected from commit f49998b

Initial docs were based on an earlier version of the PR. After reviewing commit f49998b, the following were corrected:

**`smart_copy check_params` interface changed** — no longer uses `--bu-order-data-json`. Now takes flat flags: `--leverage` (int, required), `--quote-investment` (required; `"0"` = range query only), `--signal-type` (optional), `--signal-param` (optional).

**`smart_copy create` buOrderData schema changed** — moved from single-provider model (leverageType/follow/fixed, camelCase) to **multi-signal portfolio model** (snake_case): `quote_total_investment` + `portfolio` array where each entry specifies `base`, `signal_type` (UUID), `leverage` (int), and optional `percent`, `profit_stop_ratio`, `loss_stop_ratio`. New flags: `--copy-type`, `--note`.

**`smart_copy cancel` completely redesigned** — `--close-sell-model` removed. New flags: `--close-note` (string) and `--convert-into-earn-coin` (boolean, no value).

**`bot signal add_listener` is provider-side, not consumer-side** — pushes a trading signal event to the Pionex signal platform. It is NOT a subscription command. Required fields: `--signal-type`, `--signal-param`, `--base`, `--quote`, `--time` (RFC 3339), `--price`, `--action`, `--position-size`, `--contracts`.
