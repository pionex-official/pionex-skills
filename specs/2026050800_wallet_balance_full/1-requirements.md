# Requirements: pionex-wallet Skill (wallet balance_full)

## Background

The `pionex-trade-cli wallet balance_full` command was added in `pionex-ai-kit` (issue #31). It returns a unified view of the user's total Pionex portfolio across spot balances, bot accounts (futures lite, spot grid, dual investment, Pionex Card), trader accounts, and extract balances — including live USDT/BTC totals.

The existing `pionex-portfolio` skill only covers `account balance` (raw spot coin list). There is no skill for the cross-account total balance view, leaving agents without a way to answer questions like "what is my total Pionex value?" or "how much do I have in bots vs spot?"

## Requirements

### New Skill: `pionex-wallet`

Create `skills/pionex-wallet/SKILL.md` with:

1. **Routing description** — trigger on: total balance, full balance overview, portfolio value, bot account value, spot + futures total, "how much is my whole Pionex account worth".
2. **Single command table** — `pionex-trade-cli wallet balance_full [--app-lang <lang>]`
3. **Output interpretation guide** — explain the JSON structure so the agent can format a readable summary for the user:
   - `totalInUsdt` / `totalInBtc` — grand total
   - `botAccount.detail[]` — per-type breakdown (futures_lite, spot, dual_manual, pionex_card)
   - `traderAccount` — prop-trading account value
   - `extractBalances` — extra balance buckets (propTrading, trialFundCoupon)
   - `prices` — live coin prices used for calculation
4. **Skill routing** — clear boundary with `pionex-portfolio` (spot coins only) and when to use each.

### Documentation Updates

- `README.md` — add `pionex-wallet` row to the Skills table.
- `CLAUDE.md` — add `pionex-wallet` row to the Skill Routing Map table.
- `docs/requirements-overview.md` — append new skill section and iteration history entry.
- `docs/tech-memory-overview.md` — append iteration knowledge entry.
- `docs/tech-api-overview.yaml` — add `wallet balance_full` command entry.

## Acceptance Criteria

1. `skills/pionex-wallet/SKILL.md` exists with valid YAML frontmatter (`name: pionex-wallet`).
2. Skill routing description correctly distinguishes from `pionex-portfolio`.
3. README.md Skills table includes `pionex-wallet` row.
4. CLAUDE.md Skill Routing Map includes `pionex-wallet` row.
5. `docs/requirements-overview.md` has `pionex-wallet` skill section.
