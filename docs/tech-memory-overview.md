# Technical Memory & Knowledge

This document records key decisions, lessons learned, and non-obvious technical knowledge accumulated across iterations.

## Last Updated

**Date:** 2026-04-01

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
- `pionex-market`: added `market book-tickers` command
- `pionex-trade`: added `orders fills-by-order-id` command

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
