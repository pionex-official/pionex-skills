Pionex Skills
==============

This repository defines **Pionex Skills** for AI agents

Each skill is a Markdown document that:

- Describes **when** the skill should be used.
- Specifies **how** an AI agent should call the underlying CLI / MCP tools.
- Encodes **risk controls and behavioral constraints** for financial trading.

Architecture at a glance:

- `pionex-trade-cli` **CLI** — single source of truth for trading, market data, portfolio,
  and bot operations.
- **MCP servers** — expose selected CLI capabilities as structured tools to any
  MCP-compatible agent.
- **Skills** — high-level behavioral playbooks that tell an agent how to safely
  and effectively use these tools in financial workflows.

See `DESIGN-MCP-vs-SKILL.md` for a detailed comparison of **pure MCP** versus
the **Skill + MCP + CLI** architecture, including examples of how constraints
are enforced for order placement, balance checks, and minimum order sizes.

## Skills

| Skill | Description | Auth |
|-------|-------------|------|
| [pionex-market](skills/pionex-market/SKILL.md) | Public market data: depth, tickers, symbols, klines, trades | No |
| [pionex-portfolio](skills/pionex-portfolio/SKILL.md) | Account balance (spot) | Yes |
| [pionex-trade](skills/pionex-trade/SKILL.md) | Spot orders: place, cancel, open orders, fills | Yes |
| [pionex-bot](skills/pionex-bot/SKILL.md) | Futures Grid, Spot Grid & Smart Copy Bot lifecycle: get/create/check_params/adjust/reduce/cancel; Spot Grid also supports get_ai_strategy, invest_in, profit; Signal provider subscription via `bot signal add_listener` | Yes |
| [pionex-earn-dual](skills/pionex-earn-dual/SKILL.md) | Dual Investment: products, prices, invest, revoke, collect | No (public) / Yes (private) |

All skills assume the `pionex-trade-cli` CLI is installed (`npm install -g @pionex/pionex-ai-kit`).  
Pionex API overview: [Pionex API Docs](https://pionex-doc.gitbook.io/apidocs/) — use IP whitelisting and never share your API Key/Secret.

## Requirements

- Install the `pionex-trade-cli` CLI (from `pionex-ai-kit`):

  ```bash
  npm install -g @pionex/pionex-ai-kit
  ```

- Initialize credentials (writes `~/.pionex/config.toml`):

  ```bash
  pionex-ai-kit onboard
  ```

## Updates

- Update skills (re-run the same command):
  ```bash
  npx skills add pionex-official/pionex-skills
  ```

See `CHANGELOG.md` for a detailed change history.


