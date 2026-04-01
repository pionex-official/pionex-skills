# Technical Architecture Overview

This document describes the high-level architecture of the Pionex Skills project.

## Last Updated

**Date:** 2026-04-01

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                       AI Agent / LLM                         │
│  (Claude Code, Cursor, Claude Desktop, etc.)                 │
└───────────────────────┬──────────────────────────────────────┘
                        │ Skill routing (description frontmatter)
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    Pionex Skills                             │
│  skills/pionex-market/SKILL.md    → market data commands    │
│  skills/pionex-portfolio/SKILL.md → balance commands        │
│  skills/pionex-trade/SKILL.md     → order commands          │
│  skills/pionex-bot/SKILL.md       → bot lifecycle commands  │
└───────────────────────┬──────────────────────────────────────┘
                        │ CLI invocation (exact command strings)
                        ▼
┌──────────────────────────────────────────────────────────────┐
│         pionex-trade-cli  (@pionex/pionex-ai-kit)            │
│  - market <subcommand>   → public Pionex market data API    │
│  - account balance       → authenticated account API        │
│  - orders <subcommand>   → authenticated spot orders API    │
│  - bot futures_grid <cmd>→ authenticated bot API            │
└───────────────────────┬──────────────────────────────────────┘
                        │ REST API (HMAC-signed)
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                   Pionex REST API                            │
│           https://api.pionex.com                            │
└──────────────────────────────────────────────────────────────┘
```

## Core Design Decisions

### 1. Skills as Behavioral Playbooks

Skills are plain Markdown files — not code. They serve as behavioral specifications:
- **`description` frontmatter** → drives skill router selection
- **Routing section** → tells the agent which skill to use for what
- **Command table** → exact CLI syntax to copy-paste
- **Safety rules** → constraints enforced by the agent reading the skill

### 2. CLI as Single Source of Truth

All tool calls go through `pionex-trade-cli`. This means:
- No direct API calls in the skills (CLI handles auth, signing, error formatting)
- Skills only need to know CLI interface, not Pionex REST API internals
- CLI upgrades automatically improve skill behavior without editing skill files

### 3. Skill Scope Separation

Each skill covers a non-overlapping functional scope:

| Skill | Auth | Mutating |
|-------|------|---------|
| pionex-market | No | No |
| pionex-portfolio | Yes | No |
| pionex-trade | Yes | Yes (orders) |
| pionex-bot | Yes | Yes (bots) |

This separation prevents ambiguous routing and enables per-scope safety rules.

### 4. Safety-First for Financial Operations

Write operations (orders, bot create/adjust/cancel) always require:
1. `--dry-run` preview before real execution
2. Explicit user confirmation
3. No inference of critical parameters (symbol, side, amount, leverage)

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Skill format | Markdown with YAML frontmatter |
| Skill installer | `npx skills add pionex-official/pionex-skills` |
| CLI runtime | Node.js ≥18, `@pionex/pionex-ai-kit` |
| Credential storage | `~/.pionex/config.toml` (TOML) |
| Exchange API | Pionex REST API (HMAC-SHA256 signed) |

## Deployment / Distribution

- Skills are distributed as a GitHub repository (`pionex-official/pionex-skills`)
- Users install with `npx skills add pionex-official/pionex-skills`
- Update by re-running the same install command
- No build step required — pure Markdown
