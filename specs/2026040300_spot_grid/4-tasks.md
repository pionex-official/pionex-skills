# Tasks: Spot Grid Bot

## Task List

### Task 1: Update `skills/pionex-bot/SKILL.md`

**Deliverable:** Skill file updated with all spot_grid content  
**Verify:** File has 7 new command rows, updated routing, new examples, version `0.3.0`

Steps:
1. Bump version `0.2.0` → `0.3.0` in frontmatter
2. Update skill title from "Pionex Futures Grid Bot Skill" to "Pionex Bot Skill"
3. Add `spot_grid` to routing description (frontmatter `description` field already mentions Spot Grid — confirm it's there)
4. Add 7 `bot spot_grid` rows to the Commands table
5. Add spot grid safety rules (items 4–7)
6. Add spot grid examples section

---

### Task 2: Update `docs/requirements-overview.md`

**Deliverable:** pionex-bot section includes all 7 spot_grid commands  
**Verify:** Spot grid commands listed under `#### Skill: pionex-bot`

Steps:
1. Add 7 spot_grid command entries under `#### Skill: pionex-bot`
2. Update `Last Updated` date to 2026-04-03
3. Add iteration entry to `## Iteration History`

---

### Task 3: Update `docs/tech-design-overview.md`

**Deliverable:** pionex-bot section describes spot_grid structure and differences  
**Verify:** `### pionex-bot` section covers both futures_grid and spot_grid

Steps:
1. Add spot_grid command structure note to `### pionex-bot` section
2. Document key differences (invest_in standalone, profit command, no leverage/reduce)
3. Update `Last Updated` date to 2026-04-03

---

### Task 4: Update `docs/tech-memory-overview.md`

**Deliverable:** Iteration entry added  
**Verify:** 2026040300_spot_grid entry present with key decisions

Steps:
1. Append new iteration entry documenting the spot_grid addition and key design decisions
2. Update `Last Updated` date to 2026-04-03

---

### Task 5: Verify

**Deliverable:** All changes consistent and complete  
**Verify:** Manual review checklist

- [ ] `skills/pionex-bot/SKILL.md` version is `0.3.0`
- [ ] All 7 `bot spot_grid` commands appear in command table
- [ ] `get_ai_strategy` documented as pre-create recommendation
- [ ] Safety rules include no-leverage constraint for spot grid
- [ ] `docs/` files all have updated `Last Updated` date
