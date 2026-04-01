# Tasks: pionex-earn-dual Skill

## Task List

### Task 1: Create `skills/pionex-earn-dual/SKILL.md`

**Output:** `skills/pionex-earn-dual/SKILL.md`

**Steps:**
1. Create directory `skills/pionex-earn-dual/`
2. Write `SKILL.md` with:
   - YAML frontmatter (name, description with routing exclusions, metadata)
   - Title and one-line purpose
   - Skill Routing section (cross-skill table)
   - Prerequisites section (install + auth setup)
   - Command Index table (all 11 commands, READ/WRITE types)
   - quote/currency rules table (BTC/ETH → USDXO vs others → USDT)
   - Safety Rules section (5 rules)
   - Invest Workflow section (3-step: open-products → prices → invest)
   - Examples section (at least: open-products, prices, invest with --dry-run, revoke with --dry-run, collect with --dry-run)

**Verify:** File exists, frontmatter parses as valid YAML, all commands present.

---

### Task 2: Update `README.md`

**Output:** Updated `README.md`

**Steps:**
1. Add `pionex-earn-dual` row to the skills table:
   ```
   | [pionex-earn-dual](skills/pionex-earn-dual/SKILL.md) | Dual Investment: products, prices, invest, revoke, collect | No (public) / Yes (private) |
   ```

**Verify:** `README.md` skills table includes the new row.

---

### Task 3: Update `docs/requirements-overview.md`

**Output:** Updated `docs/requirements-overview.md`

**Steps:**
1. Add `Skill: pionex-earn-dual` section listing all commands and their status (✅ planned / in progress)
2. Add iteration history entry for `2026040100_earn_dual`

**Verify:** Section exists in the file.

---

### Task 4: Update `docs/tech-design-overview.md`

**Output:** Updated `docs/tech-design-overview.md`

**Steps:**
1. Add `pionex-earn-dual` row to the Skill Scope Separation table
2. Add design notes for earn dual (command namespace, invest workflow, quote/currency rule)

**Verify:** Section exists in the file.

---

### Task 5: Update `docs/tech-memory-overview.md`

**Output:** Updated `docs/tech-memory-overview.md`

**Steps:**
1. Append new entry for iteration `2026040100_earn_dual` including:
   - New skill added: `pionex-earn-dual`
   - Key design decision: mandatory 2-step invest flow (prices → invest)
   - Key design decision: BTC/ETH use USDXO quote, others use USDT
   - Note: CLI commands pending implementation in `pionex-ai-kit#16`

**Verify:** Entry exists in the file.
