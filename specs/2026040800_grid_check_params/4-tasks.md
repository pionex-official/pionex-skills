# Task List: Grid Bot Params Check

## Tasks

### Task 1: Update `skills/pionex-bot/SKILL.md`

**Changes:**
1. Bump version in YAML frontmatter: `0.3.0` → `0.4.0`
2. Add `bot futures_grid check_params` to command table (after `futures_grid create`)
3. Add `bot spot_grid check_params` to command table (after `spot_grid create`)
4. Add safety rule #2: call `check_params` before `create`; renumber subsequent rules
5. Add `check_params` examples to the Examples section

**Verify:** `check_params` appears in both the futures_grid and spot_grid sections of the command table; version is `0.4.0`.

---

### Task 2: Update `docs/requirements-overview.md`

**Changes:**
1. Add `bot futures_grid check_params` and `bot spot_grid check_params` to the pionex-bot commands list
2. Update `Last Updated` date to `2026-04-08`
3. Append iteration history entry for `2026040800_grid_check_params`

**Verify:** Both commands appear under `#### Skill: pionex-bot`.

---

### Task 3: Update `docs/tech-design-overview.md`

**Changes:**
1. Document `check_params` pattern in the `### pionex-bot` section
2. Update `Last Updated` date to `2026-04-08`

**Verify:** `check_params` workflow is documented; date is updated.

---

### Task 4: Update `docs/tech-api-overview.yaml`

**Changes:**
1. Add `bot futures_grid check_params` CLI command entry under `bot.commands`
2. Add `bot spot_grid check_params` CLI command entry

**Verify:** Both commands appear in the yaml `bot.commands` list.

---

### Task 5: Update `docs/tech-memory-overview.md`

**Changes:**
1. Append new iteration section for `2026040800_grid_check_params`

**Verify:** Iteration entry exists with key decisions documented.
