# Technical Rules & Conventions

This document defines the coding standards, formatting conventions, and behavioral rules for the Pionex Skills repository.

## Last Updated

**Date:** 2026-04-01

---

## Skill File Rules

### Frontmatter

1. `name` — must match the directory name exactly (e.g., `pionex-bot` in `skills/pionex-bot/SKILL.md`)
2. `description` — must cover:
   - Positive cases: what the skill IS used for
   - Negative exclusions: what it is NOT used for (to prevent wrong-skill routing)
3. `version` — semver, increment on every functional change
4. `metadata.agent.requires.bins` — list all binaries the skill uses

### Markdown Structure

Skills must have these sections in order:
1. Title (`# Skill Name`)
2. One-line purpose statement
3. Routing section (cross-skill table or bullets)
4. Prerequisites (install + credential setup)
5. Command table (all commands, types, flags)
6. Safety rules (for any write/mutating commands)
7. Examples (at least one dry-run example for write commands)

### Command Table Format

```markdown
| Command | Type | Description |
|---------|------|-------------|
| `pionex-trade-cli <cmd> [flags]` | READ | Description |
| `pionex-trade-cli <cmd> [flags]` | WRITE | Description |
```

- Use `READ` or `WRITE` for the type column
- Show optional flags with `[--flag]`, required with `--flag <value>`
- Never omit `--dry-run` from WRITE command rows

## Safety Rules (Non-Negotiable)

These rules apply to ALL skills with write operations and must not be removed or weakened:

1. **Always dry-run first** — WRITE commands must be shown with `--dry-run` in examples before the real invocation
2. **Never infer critical params** — symbol, side, size, leverage, order IDs must be explicitly provided by the user
3. **Confirm before execute** — show the user what will happen, get confirmation, then run without `--dry-run`
4. **Surface errors clearly** — if the API rejects params, show the exact error and suggest a corrected payload

## Changelog Rules

- Every functional change to a skill requires a `CHANGELOG.md` entry
- Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- Group changes under the correct skill name in the entry

## Versioning

- Skills use semver in `metadata.version`
- **patch** — Fix typos, inaccurate syntax, clarifications that don't change behavior
- **minor** — New commands, expanded routing scope, new safety rules
- **major** — Breaking change to skill interface or routing scope (rare)

## Cross-Skill Consistency

When adding a command to a skill:
1. Check if other skills reference this command — update their routing sections if needed
2. If a command belongs to a different skill scope, route there instead of duplicating
3. The `pionex-market` skill is the canonical source for symbol metadata (`market symbols`) — other skills should reference it rather than document the command again
