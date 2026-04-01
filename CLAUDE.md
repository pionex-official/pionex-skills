# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Pionex Skills** is a collection of AI agent skill definitions for Pionex trading operations. Each skill is a Markdown document that:

- Describes **when** the skill should be used (routing)
- Specifies **how** an AI agent should call the underlying `pionex-trade-cli` CLI / MCP tools
- Encodes **risk controls and behavioral constraints** for financial trading

## Repository Structure

```
skills/
  pionex-market/    → Public market data (no auth required)
  pionex-portfolio/ → Account balance queries
  pionex-trade/     → Spot order placement, cancellation, fills
  pionex-bot/       → Futures Grid Bot lifecycle (create/adjust/reduce/cancel)
```

Each skill directory contains a single `SKILL.md` file with YAML frontmatter and Markdown body.

## Skill File Format

Skills use YAML frontmatter followed by Markdown:

```yaml
---
name: skill-name
description: >
  When to use this skill (used by skill router).
license: MIT
metadata:
  author: pionex
  version: "0.1.0"
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

## Skill Routing Map

| Skill | Scope | Auth |
|-------|-------|------|
| `pionex-market` | Market data: depth, tickers, symbols, klines, trades | No |
| `pionex-portfolio` | Account balance (spot) | Yes |
| `pionex-trade` | Spot orders: place, cancel, open orders, fills | Yes |
| `pionex-bot` | Futures Grid Bot lifecycle: get/create/adjust/reduce/cancel | Yes |

## CLI Dependency

All skills depend on `pionex-trade-cli` (installed via `npm install -g @pionex/pionex-ai-kit`). Credentials are stored in `~/.pionex/config.toml` (configured via `pionex-ai-kit onboard`).

## Development Guidelines

**When editing a skill:**
1. Preserve the YAML frontmatter exactly — it drives skill routing
2. Update `description` in frontmatter when the skill's routing scope changes
3. Keep command tables accurate — agents rely on them for exact CLI syntax
4. Safety rules are non-negotiable — never remove `--dry-run` instructions
5. Update `CHANGELOG.md` for any functional changes

**When adding a new skill:**
1. Create `skills/<skill-name>/SKILL.md`
2. Add entry to skills table in `README.md`
3. Update cross-skill routing sections in other skills if needed
4. Add changelog entry

## 第一性原则

从需求和问题本质出发，不从惯例或模板出发。

1. 不要假设我清楚自己想要什么。动机或目标不清晰就停下来讨论。
2. 目标清晰但路径不是最短的，直接告诉我并建议更好的办法。
3. 遇到问题追根因，不打补丁。每个决策都要能回答"为什么"。
4. 输出说重点，砍掉一切不改变决策的信息。

## Documentation Conventions

### specs/

历次迭代的文档，每次迭代一个文件夹，包含：

- `1-requirements.md` - 需求文档
- `2-research.md` - 调研文档（简单变更可省略）
- `3-tech-design.md` - 技术设计文档
- `4-tasks.md` - 任务清单
- `5-review.md` - 迭代复盘（迭代完成后编写）

### docs/

项目汇总文档，根据每次迭代整理，始终反映最新状态：

- `requirements-overview.md` - 需求概览
- `tech-arch-overview.md` - 技术架构概览
- `tech-design-overview.md` - 技术设计概览
- `tech-api-overview.yaml` - API 接口概览（OAS 3.1）
- `tech-memory-overview.md` - 技术记忆与知识
- `tech-rule-overview.md` - 技术规范
