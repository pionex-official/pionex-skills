# Tasks: Bot Order List

## Task 1 — Update `skills/pionex-bot/SKILL.md`

**File:** `skills/pionex-bot/SKILL.md`

**Changes:**
- Bump version from `0.1.0` to `0.2.0`
- Update frontmatter `description` to include "list" use case
- Add `bot order_list` row to Commands table
- Add `bot order_list` examples to Examples section

**Verify:** Command table has `bot order_list` with all flags; version is `0.2.0`

## Task 2 — Update `docs/requirements-overview.md`

**File:** `docs/requirements-overview.md`

**Changes:**
- Add `bot order_list` to the pionex-bot feature list
- Add iteration entry to Iteration History section

**Verify:** `bot order_list` appears under pionex-bot with ✅

## Task 3 — Update `docs/tech-design-overview.md`

**File:** `docs/tech-design-overview.md`

**Changes:**
- Add note about `bot order_list` (cross-type, top-level route) vs `bot futures_grid <cmd>` (type-specific lifecycle)

**Verify:** Route distinction is documented

## Task 4 — Update `docs/tech-memory-overview.md`

**File:** `docs/tech-memory-overview.md`

**Changes:**
- Append new iteration entry for `2026040200_bot_order_list`
- Record key decisions: top-level route, buOrderTypes serialization, read-only no dry-run

**Verify:** New entry appears at bottom of file
