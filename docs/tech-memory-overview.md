# Technical Memory & Knowledge

This document records key decisions, lessons learned, and non-obvious technical knowledge accumulated across iterations.

## Last Updated

**Date:** 2026-04-03

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
