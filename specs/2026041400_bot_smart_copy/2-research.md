# Research: Bot Smart Copy

**Iteration:** `2026041400_bot_smart_copy`
**Date:** 2026-04-14
**Source:** `pionex-ai-kit` PR #38

## PR Analysis

PR #38 (`pionex-official/pionex-ai-kit`) adds complete CLI + MCP support for Smart Copy Trading.

### Files Changed (34 total)

| File | Change |
|------|--------|
| `packages/cli/src/commands/bot.ts` | Main CLI command registrations for `smart_copy` and `signal` subgroups |
| `packages/core/src/tools/bot.ts` | MCP tool definitions for the 5 new tools |
| `packages/cli/src/completion.ts` | Tab completion extended with `smart_copy` and `signal` subgroups |
| `docs/` (EN/zh-hans/zh-hant) | Trilingual documentation |
| `specs/2026041412_bot_smart_copy/` | SDD specs in `pionex-ai-kit` repo |

### New MCP Tools

| Tool | CLI Equivalent |
|------|----------------|
| `pionex_bot_smart_copy_get_order` | `bot smart_copy get` |
| `pionex_bot_smart_copy_create` | `bot smart_copy create` |
| `pionex_bot_smart_copy_cancel` | `bot smart_copy cancel` |
| `pionex_bot_smart_copy_check_params` | `bot smart_copy check_params` |
| `pionex_bot_signal_add_listener` | `bot signal add_listener` |

### Upstream API Endpoints

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/v1/bot/orders/smartCopy/order` | `get` |
| POST | `/api/v1/bot/orders/smartCopy/create` | `create` |
| POST | `/api/v1/bot/orders/smartCopy/cancel` | `cancel` |
| POST | `/api/v1/bot/orders/smartCopy/checkParams` | `check_params` |
| POST | `/api/v1/bot/signal/listener` | `add_listener` |

### Key Implementation Detail: `parseSmartCopyBuOrderData()`

The CLI defines a helper that enforces inline validation:
- If `leverageType="fixed"`, `leverage` field is required
- If `leverageType="follow"`, `leverage` is ignored

This constraint should be reflected in the skill's safety rules so agents do not construct payloads that will be rejected at the API level.

## Design Comparison with Existing Bot Types

| Aspect | futures_grid | spot_grid | smart_copy |
|--------|-------------|-----------|------------|
| Has `check_params` | ✅ | ✅ | ✅ |
| Has `get_ai_strategy` | ❌ | ✅ | ❌ |
| `cancel` flags | `--close-sell-model TO_QUOTE\|TO_USDT` | none | `--close-sell-model NOT_SELL\|TO_QUOTE\|TO_USDT` |
| Has `reduce` | ✅ | ❌ | ❌ |
| Has `invest_in` | via `adjust_params` | standalone | ❌ |
| Has `profit` | ❌ | ✅ | ❌ |
| Extra create flag | none | none | `--copy-from <id>` |
| Signal subscription | ❌ | ❌ | `bot signal add_listener` |

## Conclusion

The changes are additive to `pionex-bot/SKILL.md`:
1. Add `bot smart_copy` section to the command table
2. Add `bot signal add_listener` command
3. Add smart-copy-specific safety rules
4. Add examples for the new commands
5. Bump version to 0.5.0
